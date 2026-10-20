"""Large team assignment matrix and checked-category expansion workflow."""
from pathlib import Path
import uuid

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QCheckBox, QPlainTextEdit, QSplitter)

from ..archive.manifests import OUTPUT
from ..modding import team_assets as backend


class TeamAssetsPanel(QWidget):
    def __init__(self, owner):
        super().__init__(); self.owner = owner; self.plan = None; self.rows = []
        layout = QVBoxLayout(self)
        heading = QLabel('Team assets'); heading.setStyleSheet('font-size:24px;font-weight:600')
        layout.addWidget(heading)
        explanation = QLabel('Load the assignment list from the top Preview source selector. Check categories to clone and link; gameplay and SELU menu files are paired automatically. Unchecked categories keep their assignments.')
        explanation.setWordWrap(True); layout.addWidget(explanation)
        toolbar = QHBoxLayout(); layout.addLayout(toolbar)
        self.refresh = QPushButton('Load / refresh teams'); toolbar.addWidget(self.refresh)
        self.refresh.clicked.connect(self.reload)
        self.use_roster = QCheckBox('Include roster editor changes'); self.use_roster.setChecked(True); toolbar.addWidget(self.use_roster)
        self.search = QLineEdit(); self.search.setPlaceholderText('Search teams, IDs, filenames or Active / Inactive / Missing')
        toolbar.addWidget(self.search, 1); self.search.textChanged.connect(self.filter)
        controls = QHBoxLayout(); layout.addLayout(controls)
        for text, callback in [('Check all types for selected teams', lambda:self.check_selected(True)),
                               ('Clear selected checks', lambda:self.check_selected(False)),
                               ('Check missing alternates for visible teams', self.check_missing)]:
            button = QPushButton(text); controls.addWidget(button); button.clicked.connect(callback)
        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(['Team ID / school', 'Asset ID', 'Uniform owner', 'Menu ID', 'Shared by teams',
                                             'S / stadium', 'UH / home', 'UA / away', 'UX', 'UY', 'UZ', 'Menu logo', 'New ID'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.verticalHeader().hide()
        self.table.setColumnWidth(0, 240)
        for column in range(5, 12):self.table.setColumnWidth(column, 150)
        for column in (1, 2, 3, 12):self.table.setColumnWidth(column, 85)
        self.table.setColumnWidth(4, 215)
        self.table.itemChanged.connect(self.invalidate)
        split = QSplitter(Qt.Orientation.Vertical); layout.addWidget(split, 1); split.addWidget(self.table)
        self.details = QPlainTextEdit(); self.details.setReadOnly(True); split.addWidget(self.details); split.setSizes([650, 130])
        bottom = QHBoxLayout(); layout.addLayout(bottom)
        self.preview = QPushButton('Review checked changes'); bottom.addWidget(self.preview); self.preview.clicked.connect(self.review)
        self.apply = QPushButton('Apply to new overrides folder'); bottom.addWidget(self.apply); self.apply.setEnabled(False); self.apply.clicked.connect(self.publish)
        self.state = QLabel('Open a College Hoops 2K8 JB, then load teams.'); layout.addWidget(self.state)

    def invalidate(self, *_):
        self.plan = None; self.apply.setEnabled(False)

    def reload(self):
        if not self.owner.archive:return self.owner.log('Open a College Hoops 2K8 JB first.')
        try:
            archive = self.owner.preview_archive()
            payload = bytes(self.owner.roster.data) if self.use_roster.isChecked() and self.owner.roster else None
        except ValueError as error:return self.owner.show_error(str(error))
        def load(job):
            _, model = backend.roster_model(archive)
            if payload is not None:
                from ..roster.adapters import load_bytes
                from ..roster.editor_model import EditorModel
                model = EditorModel(load_bytes(payload))
            return archive, model, backend.inventory(archive, model), backend.available_ids(archive, model)
        self.owner.run_job('Read team asset assignments', load, self.loaded)

    def loaded(self, result):
        self.asset_archive, self.model, self.rows, self.free = result
        self.source_key = (id(self.owner.archive), self.owner.mod_path.text(), self.owner.preview_overrides.isChecked())
        self.loaded_payload = bytes(self.owner.roster.data) if self.use_roster.isChecked() and self.owner.roster else None
        self.table.blockSignals(True); self.table.setRowCount(len(self.rows))
        for row, data in enumerate(self.rows):
            values = [f"{data['index']} — {data['school']}", data['asset_id'], data['owner_id'], data['menu_id'], data['shared']]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value)); item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable); self.table.setItem(row, column, item)
            for column, kind in enumerate(backend.KINDS, 5):
                key = 'menu_logo' if kind == 'menu_logo' else kind
                value = data[key]
                if kind in 'haxyz' and ' — ' in value:
                    value = value.split(' / ',1)[0] + ' · ' + value.split(' — ',1)[1]
                item = QTableWidgetItem(value); item.setToolTip(data[key] + '\nCheck to give this team its own linked copy. Missing prior alternate banks are also filled in order.')
                item.setFlags((item.flags() | Qt.ItemFlag.ItemIsUserCheckable) & ~Qt.ItemFlag.ItemIsEditable)
                item.setCheckState(Qt.CheckState.Unchecked); self.table.setItem(row, column, item)
            item = QTableWidgetItem('Auto'); item.setToolTip('Auto allocates an unused ID; type 0–1023 to choose one. A uniquely owned uniform ID can be retained when expanding only uniforms.')
            self.table.setItem(row, 12, item)
        self.table.blockSignals(False); self.invalidate(); self.filter(self.search.text())
        self.state.setText(f'{len(self.rows)} teams · {len(self.free)} entirely unused IDs · Active = linked, unlock conditions may still apply')
        self.details.setPlainText('Each checked uniform bank includes its SELU selection asset. Missing X/Y before a checked later bank are filled automatically because the game selects by list order.\nMenu logo creates a texture record inside teamselectlogo.iff + .cdf; it is not a standalone logo IFF.\nS clones the normal day/night stadium route and assigns an independent arena row. Special mode 2/3 arenas remain blocked.\nThe general Asset ID, team classification, conferences, players and coaches are preserved. Original artwork is copied as an editable starting point. Gameplay compatibility remains unverified.')

    def filter(self, text):
        for row, data in enumerate(self.rows):
            self.table.setRowHidden(row, text.casefold() not in ' '.join(str(v) for v in data.values()).casefold())

    def check_selected(self, checked):
        for index in self.table.selectionModel().selectedRows():
            for column in range(5, 12):
                self.table.item(index.row(), column).setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def check_missing(self):
        for row, data in enumerate(self.rows):
            if not self.table.isRowHidden(row) and 'Active' in data['h'] and 'Active' in data['a']:
                for column, bank in ((8, 'x'), (9, 'y'), (10, 'z')):
                    if data[bank].startswith('Inactive'):
                        self.table.item(row, column).setCheckState(Qt.CheckState.Checked)

    def requests(self):
        free = iter(self.free); reserved = set(); result = []
        checked = []
        for row, data in enumerate(self.rows):
            kinds = [k for column, k in enumerate(backend.KINDS, 5) if self.table.item(row, column).checkState() == Qt.CheckState.Checked]
            if kinds:checked.append((row, data, kinds, self.table.item(row, 12).text().strip()))
        # Reserve explicitly chosen IDs before allocating Auto values.
        for _, _, _, text in checked:
            if text.casefold() != 'auto':
                value = int(text)
                if value in reserved:raise ValueError('Each planned team requires a distinct target ID')
                reserved.add(value)
        for _, data, kinds, text in checked:
            if text.casefold() == 'auto':
                unique = sum(r['owner_id'] == data['owner_id'] for r in self.rows) == 1
                if unique and set(kinds).issubset(set('haxyz')) and data['owner_id'] not in reserved:
                    target = data['owner_id']
                else:target = next((i for i in free if i not in reserved), None)
                if target is None:raise ValueError('No entirely unused ID remains for these independent assets')
                reserved.add(target)
            else:target = int(text)
            result.append(dict(team=data['index'], id=target, assets=kinds))
        return result

    def unchanged_context(self):
        if self.source_key != (id(self.owner.archive), self.owner.mod_path.text(), self.owner.preview_overrides.isChecked()):
            raise ValueError('The JB or override source changed; refresh teams before applying')
        current = bytes(self.owner.roster.data) if self.use_roster.isChecked() and self.owner.roster else None
        if current != self.loaded_payload:raise ValueError('Roster editor changes changed; refresh teams before applying')

    def review(self):
        if not self.rows:return self.owner.log('Load the team list first.')
        try:
            self.unchanged_context(); requests = self.requests()
        except (ValueError, AttributeError) as error:return self.owner.show_error(str(error))
        self.invalidate()
        def complete(plan):
            self.plan = plan; self.apply.setEnabled(True)
            lines = [f"{len(plan['teams'])} teams · {len(plan['additions'])} new IFFs · {len(plan['replacements'])} updated containers"]
            lines += [f"Team {r['team']} {r['school']} → ID {r['id']}: {', '.join(r['assets'])}" for r in plan['teams']]
            lines += ['New files:', *plan['additions'], 'Updated files:', *plan['replacements'], 'Apply creates a separate overrides folder and selects it for normal previews / Build JB copy.']
            lines += ['Fallback: '+item['message'] for item in plan.get('fallbacks',[])]
            self.details.setPlainText('\n'.join(lines))
        payload = bytes(self.model.data)
        self.owner.run_job('Validate checked team asset changes', lambda job:backend.prepare(self.asset_archive, requests, roster_payload=payload, job=job), complete, cancellable=True)

    def publish(self):
        if self.plan is None:return
        try:self.unchanged_context()
        except ValueError as error:return self.owner.show_error(str(error))
        from .services import stage_folder
        source = self.owner.source; plan = self.plan
        folder = OUTPUT / 'overrides' / ('team_assets_' + uuid.uuid4().hex[:10])
        workspace = OUTPUT / 'builds' / ('team_assets_' + uuid.uuid4().hex[:10])
        archive = self.asset_archive
        def apply(job):
            # Carry existing selected overrides forward so expansion cannot drop them.
            if hasattr(archive, 'replacements'):
                for entry in archive.entries:
                    if entry['index'] in archive.replacements or entry['index'] >= len(archive.base.entries):
                        name = entry['name']
                        if entry['index'] >= len(archive.base.entries):plan['additions'].setdefault(name, archive.read(entry))
                        else:plan['replacements'].setdefault(name, archive.read(entry))
            backend.export_folder(plan, folder, source)
            return stage_folder(source, folder, workspace, job)
        def complete(result):
            self.owner.builder_completed(result, 'staging')
            self.state.setText('Applied. Editable folder: ' + str(folder) + ' · Build JB copy writes the selected assets into a new JB.')
            self.plan = None; self.apply.setEnabled(False)
        self.owner.run_job('Apply team assets to overrides', apply, complete, cancellable=True)

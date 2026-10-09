"""Qt model/view explorer. Binary work runs on bounded background workers."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    QRunnable,
    QSettings,
    QSortFilterProxyModel,
    Qt,
    QThreadPool,
    QTimer,
    Signal,
)
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTableView,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..archive.manifests import OUTPUT
from ..archive.usrdir_reader import Archive
from .services import JobContext, extract, inspect_asset, materialize, stage_folder


class Rows(QAbstractTableModel):
    def __init__(self, rows=None, columns=None):
        super().__init__()
        self.rows = rows or []
        self.columns = columns or []

    def rowCount(self, parent=QModelIndex()):  # noqa: B008 - Qt override signature
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):  # noqa: B008 - Qt override signature
        return 0 if parent.isValid() else len(self.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        key = self.columns[index.column()][0]
        value = self.rows[index.row()].get(key, "")
        if key == "hash":
            return f"{value:08X}"
        if key == "name" and not value:
            return f"hash_{self.rows[index.row()].get('hash', 0):08x}"
        return str(value if value is not None else "")

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.columns[section][1]
        return None


class Events(QObject):
    result = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int, str)
    finished = Signal()


class Worker(QRunnable):
    def __init__(self, function, job):
        super().__init__()
        self.function, self.job = function, job
        self.events = Events()
        self.last_progress = 0.0
        self.job.progress = self.progress

    def progress(self, done, total, text):
        now = time.monotonic()
        if now - self.last_progress > 0.1 or done == total:
            self.last_progress = now
            # Qt int is 32-bit: normalize large archive counts before emitting.
            self.events.progress.emit(int(1000 * done / max(1, total)), 1000, text)

    def run(self):
        try:
            self.events.result.emit(self.function(self.job))
        except Exception as error:  # noqa: BLE001 - worker boundary reports all failures
            self.events.failed.emit(f"{type(error).__name__}: {error}")
        finally:
            self.events.finished.emit()


def table():
    view = QTableView()
    view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
    view.setSortingEnabled(True)
    view.setAlternatingRowColors(True)
    return view


def set_rows(view, rows, columns, query=""):
    proxy = QSortFilterProxyModel(view)
    proxy.setSourceModel(Rows(rows, columns))
    proxy.setFilterKeyColumn(-1)
    proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    proxy.setFilterFixedString(query)
    view.setModel(proxy)
    view.resizeColumnsToContents()
    return proxy


def selected(view):
    proxy = view.model()
    if proxy is None:
        return []
    return [
        proxy.sourceModel().rows[proxy.mapToSource(i).row()]
        for i in view.selectionModel().selectedRows()
    ]


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHoops Modding Studio • 1.0beta development")
        self.resize(1420, 900)
        self.settings = QSettings("CHoops", "ModdingStudio")
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.active = None
        self.archive = None
        self.asset_path = None
        self.roster = None
        self.source = None
        self.pages = QStackedWidget()
        self.navigation = QTreeWidget()
        self.navigation.setHeaderLabel("CHoops Studio")
        for name in (
            "Explorer",
            "Texture Editor",
            "Roster Editor",
            "Models / Courts",
            "Mod Builder",
            "Research",
            "Diagnostics",
        ):
            self.navigation.addTopLevelItem(QTreeWidgetItem([name]))
        self.navigation.currentItemChanged.connect(self.navigate)
        split = QSplitter()
        split.addWidget(self.navigation)
        split.addWidget(self.pages)
        split.setSizes([190, 1230])
        self.setCentralWidget(split)
        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)
        self.logs.document().setMaximumBlockCount(1000)
        dock = QDockWidget("Tasks and diagnostics", self)
        dock.setWidget(self.logs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(280)
        self.cancel = QPushButton("Cancel extraction")
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(
            lambda: self.active.job.cancelled.set() if self.active else None
        )
        self.statusBar().addPermanentWidget(self.progress)
        self.statusBar().addPermanentWidget(self.cancel)
        menu = self.menuBar().addMenu("File")
        for text, handler, shortcut in [
            ("Open game…", self.choose_game, "Ctrl+O"),
            ("Open extracted asset…", self.choose_asset, "Ctrl+Shift+O"),
            ("Open roster…", self.choose_roster, ""),
            ("Exit", self.close, "Ctrl+Q"),
        ]:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(handler)
            menu.addAction(action)
        self.create_explorer()
        self.create_texture()
        self.create_roster()
        self.create_models()
        self.create_builder()
        self.create_research()
        self.create_diagnostics()
        self.navigation.setCurrentItem(self.navigation.topLevelItem(0))
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def navigate(self, item, previous):
        if item:
            self.pages.setCurrentIndex(self.navigation.indexOfTopLevelItem(item))

    def page(self, title, description):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 24px; font-weight: 600; padding: 8px 0;")
        layout.addWidget(heading)
        label = QLabel(description)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.pages.addWidget(widget)
        return layout

    def buttons(self, layout, items):
        row = QHBoxLayout()
        for label, handler in items:
            button = QPushButton(label)
            button.clicked.connect(handler)
            row.addWidget(button)
        row.addStretch()
        layout.addLayout(row)

    def run_job(self, label, function, callback=None, cancellable=False):
        if self.active:
            self.log("A task is already running. Wait for it to finish.")
            return
        worker = Worker(function, JobContext())
        self.active = worker
        self.cancel.setEnabled(cancellable)
        self.progress.setRange(0, 0)
        self.statusBar().showMessage(label)
        self.log(label)
        worker.events.progress.connect(self.job_progress)
        worker.events.failed.connect(self.show_error)
        worker.events.result.connect(
            callback
            or (lambda result: self.log(json.dumps(result, default=str)[:8000]))
        )
        worker.events.finished.connect(self.job_finished)
        self.pool.start(worker)

    def job_progress(self, done, total, text):
        self.progress.setRange(0, total)
        self.progress.setValue(done)
        self.statusBar().showMessage(text)

    def job_finished(self):
        self.active = None
        self.cancel.setEnabled(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.statusBar().showMessage("Ready")

    def log(self, text):
        self.logs.appendPlainText(str(text))

    def show_error(self, text):
        self.log(text)
        QMessageBox.warning(self, "Operation could not complete", text)

    def choose_game(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select original JB game or USRDIR", self.settings.value("game", "")
        )
        if path:
            self.open_game(Path(path))

    def open_game(self, path):
        def loaded(archive):
            self.archive = archive
            self.source = path
            self.settings.setValue("game", str(path))
            self.explorer_proxy = set_rows(
                self.explorer,
                archive.entries,
                [
                    ("name", "Asset"),
                    ("size", "Bytes"),
                    ("hash", "CRC32"),
                    ("index", "TOC index"),
                    ("offset", "Logical offset"),
                    ("size_derived", "Derived extent"),
                ],
                self.search.text(),
            )
            self.identity.setText(
                f"{len(archive.entries):,} entries • {len(archive.parts)} split parts • original source read-only"
            )
            self.log("Archive index loaded; payloads remain lazy.")

        self.run_job("Index original game", lambda job: Archive(path), loaded)

    def create_explorer(self):
        layout = self.page(
            "Archive explorer",
            "Select an original PS3 JB game. Browse assets without a full rip; double-click to inspect nested records.",
        )
        self.identity = QLabel("No game selected")
        layout.addWidget(self.identity)
        self.buttons(
            layout,
            [
                ("Open game…", self.choose_game),
                ("Extract selected…", self.extract_selected),
                ("Extract all raw…", lambda: self.extract_selected(True)),
            ],
        )
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter filename, CRC32, index or offset")
        self.search.textChanged.connect(
            lambda value: (
                self.explorer.model().setFilterFixedString(value)
                if self.explorer.model()
                else None
            )
        )
        layout.addWidget(self.search)
        self.explorer = table()
        self.explorer.doubleClicked.connect(self.inspect_selected)
        layout.addWidget(self.explorer)
        self.nested = QTreeWidget()
        self.nested.setHeaderLabels(["Nested record", "Type", "Index"])
        self.nested.header().setStretchLastSection(False)
        self.nested.setColumnWidth(0, 220)
        layout.addWidget(self.nested)

    def extract_selected(self, all_entries=False):
        if not self.archive:
            return self.log("Open a game first.")
        entries = list(self.archive.entries) if all_entries else selected(self.explorer)
        if not entries:
            return self.log("Select one or more rows to extract.")
        path = QFileDialog.getExistingDirectory(
            self, "Choose new output folder under output/", str(OUTPUT / "rips")
        )
        if path:
            self.run_job(
                "Extract raw assets",
                lambda job: extract(self.archive, entries, Path(path), job),
                cancellable=True,
            )

    def inspect_selected(self):
        entries = selected(self.explorer)
        if not entries:
            return
        entry = entries[0]
        self.run_job(
            "Read and inspect asset",
            lambda job: inspect_asset(materialize(self.archive, entry)),
            self.display_asset,
        )

    def choose_asset(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open extracted IFF/TXTR/DDS",
            "",
            "Assets (*.iff *.txtr *.dds *.scne);;All files (*)",
        )
        if path:
            self.run_job(
                "Inspect extracted asset",
                lambda job: inspect_asset(Path(path)),
                self.display_asset,
            )

    def display_asset(self, result):
        self.asset_path = result["path"]
        self.asset_label.setText(self.asset_path.name)
        self.nested.clear()
        for rec in result["records"]:
            QTreeWidgetItem(
                self.nested,
                [rec.get("name", ""), rec.get("type", ""), str(rec["index"])],
            )
        set_rows(
            self.textures,
            result["textures"],
            [
                ("name", "Texture"),
                ("kind", "Container"),
                ("editable", "Layout supported"),
                ("metadata", "Metadata"),
            ],
        )
        raw = result["hex"]
        self.hex.setPlainText(
            "\n".join(
                f"{i:08X}  "
                + raw[i : i + 16].hex(" ")
                + "  "
                + "".join(chr(b) if 32 <= b < 127 else "." for b in raw[i : i + 16])
                for i in range(0, len(raw), 16)
            )
        )
        self.image.clear()
        self.log(
            f"Inspected {self.asset_path.name}: {len(result['records'])} records, {len(result['textures'])} texture candidates. {result['warning']}"
        )

    def create_texture(self):
        layout = self.page(
            "Texture editor",
            "Export DDS, preserve dimensions/format/mips in your image editor, then import into a new container. Unsupported layouts stay raw-exportable.",
        )
        self.asset_label = QLabel("Open an archive asset or extracted file")
        layout.addWidget(self.asset_label)
        self.buttons(
            layout,
            [
                ("Open asset…", self.choose_asset),
                ("Export textures…", self.export_textures),
                ("Preview DDS…", self.preview_dds),
                ("Import edited DDS…", self.import_dds),
            ],
        )
        self.textures = table()
        self.textures.doubleClicked.connect(self.preview_texture)
        layout.addWidget(self.textures)
        self.image = QLabel("DDS previews appear here")
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.image)
        layout.addWidget(scroll)

    def export_textures(self):
        if not self.asset_path:
            return self.log("Open an asset first.")
        path = QFileDialog.getExistingDirectory(
            self, "Choose new texture export folder under output/", str(OUTPUT / "rips")
        )
        if path:
            from ..texture_tools.pipeline import export

            source = self.asset_path
            cdf = source.with_suffix(".cdf")
            self.run_job(
                "Export DDS and raw textures",
                lambda job: export(source, path, cdf if cdf.exists() else None),
            )

    def preview_dds(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select DDS or PNG preview", str(OUTPUT), "Images (*.dds *.png)"
        )
        if not path:
            return

        def decode(job):
            from PIL import Image

            with Image.open(path) as image:
                image.load()
                image.thumbnail((2048, 2048))
                rgba = image.convert("RGBA")
                return rgba.size, rgba.tobytes()

        def display(result):
            (w, h), raw = result
            image = QImage(raw, w, h, w * 4, QImage.Format.Format_RGBA8888).copy()
            self.image.setPixmap(QPixmap.fromImage(image))

        self.run_job("Decode image preview", decode, display)

    def preview_texture(self):
        rows = selected(self.textures)
        if not self.asset_path or len(rows) != 1:
            return
        source = self.asset_path
        selector = rows[0]["name"]

        def decode(job):
            import uuid

            from PIL import Image

            from ..archive.manifests import write_bytes
            from ..texture_tools.dds import linear_l8
            from ..texture_tools.external_converters import convert
            from ..texture_tools.pipeline import Container

            cdf = source.with_suffix(".cdf")
            container = Container(source, cdf if cdf.exists() else None)
            asset = container.select(selector)
            info = asset.texture.info()
            work = OUTPUT / "temp" / ("preview_" + uuid.uuid4().hex)
            gtf = work / "texture.gtf"
            dds = work / "texture.dds"
            write_bytes(gtf, asset.texture.gtf(), [source])
            if info["format"] == "L8" and info["linear"]:
                write_bytes(
                    dds,
                    linear_l8(
                        info["width"],
                        info["height"],
                        info["mip_count"],
                        asset.texture.image(),
                    ),
                    [source],
                )
            else:
                convert("gtf2dds", gtf, dds)
            with Image.open(dds) as image:
                image.load()
                image.thumbnail((2048, 2048))
                image = image.convert("RGBA")
                return image.size, image.tobytes()

        def display(result):
            (w, h), raw = result
            image = QImage(raw, w, h, w * 4, QImage.Format.Format_RGBA8888).copy()
            self.image.setPixmap(QPixmap.fromImage(image))

        self.run_job("Preview selected texture", decode, display)

    def import_dds(self):
        rows = selected(self.textures)
        if not self.asset_path or len(rows) != 1:
            return self.log("Select one texture row first.")
        dds, _ = QFileDialog.getOpenFileName(
            self, "Edited DDS with unchanged layout", str(OUTPUT), "DDS (*.dds)"
        )
        if not dds:
            return
        source = self.asset_path
        cdf = source.with_suffix(".cdf")
        if cdf.exists():
            output = QFileDialog.getExistingDirectory(
                self,
                "Choose new paired output folder under output/",
                str(OUTPUT / "temp"),
            )
        else:
            output, _ = QFileDialog.getSaveFileName(
                self,
                "Save new container under output/",
                str(OUTPUT / "temp" / source.name),
            )
        if output:
            from ..texture_tools.pipeline import import_texture

            self.run_job(
                "Validate and import texture",
                lambda job: import_texture(
                    source, rows[0]["name"], dds, output, cdf if cdf.exists() else None
                ),
            )

    def create_roster(self):
        layout = self.page(
            "Roster editor",
            "Confirmed player and team fields only. Save a copy, reopen it, then stage it for a separate JB build.",
        )
        self.buttons(
            layout,
            [
                ("Open roster…", self.choose_roster),
                ("Load game roster", self.load_game_roster),
                ("Edit selected…", self.edit_roster),
                ("Undo", self.undo_roster),
                ("Redo", self.redo_roster),
                ("Save copy…", self.save_roster),
            ],
        )
        self.roster_search = QLineEdit()
        self.roster_search.setPlaceholderText("Search current roster table")
        self.roster_search.textChanged.connect(lambda value: self.filter_roster(value))
        layout.addWidget(self.roster_search)
        self.roster_tabs = QTabWidget()
        self.roster_views = {}
        for name in ("players", "teams", "arenas", "coaches"):
            view = table()
            self.roster_views[name] = view
            self.roster_tabs.addTab(view, name.title())
        layout.addWidget(self.roster_tabs)
        self.roster_state = QLabel("No roster loaded")
        layout.addWidget(self.roster_state)

    def filter_roster(self, text):
        for view in self.roster_views.values():
            if view.model():
                view.model().setFilterFixedString(text)

    def choose_roster(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open roster or decrypted USERDATA", "", "All supported files (*)"
        )
        if path:
            from ..roster.editor_model import EditorModel

            self.run_job(
                "Load roster", lambda job: EditorModel.open(path), self.display_roster
            )

    def load_game_roster(self):
        if not self.archive:
            return self.log("Open a game first.")
        matches = [e for e in self.archive.entries if e["name"] == "roster_english.iff"]
        if len(matches) != 1:
            return self.log("Roster identity is missing or ambiguous.")
        from ..roster.editor_model import EditorModel

        self.run_job(
            "Load original game roster",
            lambda job: EditorModel.open(materialize(self.archive, matches[0])),
            self.display_roster,
        )

    def display_roster(self, model):
        self.roster = model
        for name, view in self.roster_views.items():
            rows = model.rows[name]
            columns = (
                [
                    (key, key.replace("_", " ").title())
                    for key in rows[0]
                    if key != "row_offset"
                ]
                if rows
                else []
            )
            set_rows(view, rows, columns, self.roster_search.text())
        self.roster_state.setText(
            f"{len(model.rows['players']):,} players • {len(model.edits)} unsaved edits"
        )

    def edit_roster(self):
        if not self.roster or self.active:
            return
        name = self.roster_tabs.tabText(self.roster_tabs.currentIndex()).lower()
        rows = selected(self.roster_views[name])
        if len(rows) != 1:
            return self.log("Select exactly one roster row.")
        if name not in ("players", "teams"):
            return self.log("Arena and coach records are read-only.")
        from ..roster.schema import EDITABLE, REFERENCES

        row = rows[0]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit {name} record {row['index']}")
        form = QFormLayout(dialog)
        field = QComboBox()
        field.addItems(EDITABLE[name])
        value = QLineEdit()
        slot = QComboBox()
        slot.addItems([str(i) for i in range(16)])
        choices = QComboBox()
        choices.setEditable(False)

        def changed(key):
            reference = key == "roster_slots" or key in REFERENCES
            value.setVisible(not reference)
            choices.setVisible(reference)
            slot.setVisible(key == "roster_slots")
            if reference:
                target = "players" if key == "roster_slots" else REFERENCES[key][1]
                choices.clear()
                choices.addItem("None", None)
                for candidate in self.roster.rows[target]:
                    label = (
                        candidate.get("display_name")
                        or candidate.get("name")
                        or candidate.get("team_name")
                        or ""
                    )
                    choices.addItem(
                        f"{candidate['index']}: {label}", candidate["index"]
                    )
            else:
                value.setText(str(row.get(key, "")))

        form.addRow("Confirmed field", field)
        form.addRow("Value", value)
        form.addRow("Reference", choices)
        form.addRow("Roster slot", slot)
        field.currentTextChanged.connect(changed)
        changed(field.currentText())
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = field.currentText()
            new = (
                choices.currentData()
                if key == "roster_slots" or key in REFERENCES
                else value.text()
            )

            def edit(job):
                self.roster.edit(
                    name,
                    row["index"],
                    key,
                    new,
                    int(slot.currentText()) if key == "roster_slots" else None,
                )
                return self.roster

            self.run_job("Apply validated roster edit", edit, self.display_roster)

    def undo_roster(self):
        if self.roster and not self.active:

            def undo(job):
                self.roster.undo()
                return self.roster

            self.run_job("Undo roster edit", undo, self.display_roster)

    def redo_roster(self):
        if self.roster and not self.active:

            def redo(job):
                self.roster.redo()
                return self.roster

            self.run_job("Redo roster edit", redo, self.display_roster)

    def save_roster(self):
        if not self.roster:
            return
        output, _ = QFileDialog.getSaveFileName(
            self,
            "Save roster copy under output/",
            str(OUTPUT / "temp" / "roster_english.iff"),
        )
        if output:
            from ..roster.workflow import save_model

            self.run_job(
                "Save and reparse roster copy",
                lambda job: save_model(self.roster, output),
            )

    def create_models(self):
        layout = self.page(
            "Models / Courts • read-only geometry",
            "SCNE part metadata is inspectable. Geometry export/import remains unavailable until vertex declarations and topology are validated. Court texture edits use the Texture Editor.",
        )
        self.buttons(layout, [("Inspect selected SCNE record", self.inspect_scene)])
        self.model_details = QPlainTextEdit()
        self.model_details.setReadOnly(True)
        layout.addWidget(self.model_details)

    def inspect_scene(self):
        if not self.asset_path:
            return self.log("Open a standard IFF in Explorer first.")
        items = self.nested.selectedItems()
        if not items or items[0].text(1) != "SCNE":
            return self.log("Select a SCNE record in the Explorer nested list.")
        index = int(items[0].text(2))

        def inspect(job):
            from ..formats.scne import inspect
            from ..formats.standard_iff import StandardIFF
            from ..formats.standard_iff_writer import record_blocks
            from ..formats.tool_wrapper import wrap

            iff = StandardIFF(self.asset_path.read_bytes())
            blocks = [b[3] for b in record_blocks(iff, iff.records[index])]
            return inspect(wrap(2, blocks))

        self.run_job(
            "Inspect scene parts",
            inspect,
            lambda result: self.model_details.setPlainText(
                json.dumps(result, indent=2)
            ),
        )

    def create_builder(self):
        layout = self.page(
            "Mod builder",
            "Stage existing compatible IFF/CDF replacements, preflight them, and build a separate JB copy. Growth and new archive entries are blocked.",
        )
        form = QFormLayout()
        self.mod_path = QLineEdit(str(OUTPUT / "builds" / "my_mod"))
        self.build_path = QLineEdit(str(OUTPUT / "builds" / "my_build"))
        form.addRow("Mod workspace", self.mod_path)
        form.addRow("New JB output", self.build_path)
        layout.addLayout(form)
        self.buttons(
            layout,
            [
                ("Stage replacement folder…", self.stage_replacements),
                ("Dry run", lambda: self.build_game(True)),
                ("Build JB copy", lambda: self.build_game(False)),
            ],
        )
        self.build_details = QPlainTextEdit()
        self.build_details.setReadOnly(True)
        layout.addWidget(self.build_details)

    def stage_replacements(self):
        if not self.source:
            return self.log("Open a game first.")
        path = QFileDialog.getExistingDirectory(
            self, "Edited extracted IFF/CDF folder", str(OUTPUT)
        )
        if path:
            mod = Path(self.mod_path.text())
            self.run_job(
                "Stage and preflight replacement folder",
                lambda job: stage_folder(self.source, Path(path), mod),
                lambda result: self.build_details.setPlainText(
                    json.dumps(result, indent=2)
                ),
            )

    def build_game(self, dry_run):
        if not self.source:
            return self.log("Open a game first.")
        from ..archive.build_copy import build

        mod, output = self.mod_path.text(), self.build_path.text()
        self.run_job(
            "Preflight mod" if dry_run else "Build separate JB copy",
            lambda job: build(self.source, mod, output, dry_run=dry_run),
            lambda result: self.build_details.setPlainText(
                json.dumps(result, indent=2)
            ),
        )

    def create_research(self):
        layout = self.page(
            "Research • raw inspection",
            "First 4 KiB of the selected asset. Unknown audio, CDAN and roster fields remain read-only; no codecs or geometry writers are inferred.",
        )
        self.hex = QPlainTextEdit()
        self.hex.setReadOnly(True)
        self.hex.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.hex)

    def create_diagnostics(self):
        layout = self.page(
            "Diagnostics",
            "Converter execution checks and synthetic round trips use generated files. Execution success does not establish redistribution rights or console compatibility.",
        )
        from ..texture_tools.external_converters import status, test_tools

        self.buttons(
            layout,
            [
                (
                    "Converter status",
                    lambda: self.run_job("Check converters", lambda job: status()),
                ),
                (
                    "Test converters",
                    lambda: self.run_job(
                        "Run generated converter round trip", lambda job: test_tools()
                    ),
                ),
            ],
        )
        layout.addStretch()

    def closeEvent(self, event):
        if self.active:
            self.show_error(
                "A task is running. Cancel extraction or wait for completion before closing."
            )
            event.ignore()
            return
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)


def main(argv=None):
    parser = argparse.ArgumentParser(description="CHoops native Qt studio")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Launch a real Qt window then close automatically",
    )
    parser.add_argument("--game", type=Path)
    parser.add_argument(
        "--verify-game",
        action="store_true",
        help="Run private packaged GUI fixture smoke",
    )
    args = parser.parse_args(argv)
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setStyle("Fusion")
    window = Window()
    window.show()
    if args.game:
        window.open_game(args.game)
    if args.verify_game:
        if not args.game:
            parser.error("--verify-game requires --game")
        state = {"step": 0, "failed": False}
        started = time.monotonic()
        from ..core.reports import save_json

        def fail(text):
            state["failed"] = True
            window.log(text)
            save_json(
                OUTPUT / "reports" / "packaged_gui_smoke.json",
                {"status": "failed", "reason": text},
            )
            window.active = None
            app.exit(1)

        # Suppress modal dialogs during automated smoke, retaining factual errors.
        window.show_error = fail

        def verify():
            if state["failed"]:
                return
            if time.monotonic() - started > 90:
                fail("GUI smoke timed out")
                return
            if window.active:
                QTimer.singleShot(100, verify)
                return
            try:
                if state["step"] == 0:
                    if not window.archive:
                        raise ValueError("Archive did not load")
                    window.search.setText("ua000.iff")
                    window.explorer.selectRow(0)
                    window.inspect_selected()
                elif state["step"] == 1:
                    if window.nested.topLevelItemCount() == 0:
                        raise ValueError("No nested IFF records")
                    window.navigation.setCurrentItem(window.navigation.topLevelItem(1))
                    window.textures.selectRow(0)
                    window.preview_texture()
                elif state["step"] == 2:
                    if window.image.pixmap().isNull():
                        raise ValueError("Texture preview did not decode")
                    window.load_game_roster()
                elif state["step"] == 3:
                    if not window.roster or len(window.roster.rows["players"]) != 5685:
                        raise ValueError("Roster table did not load")
                    window.roster_search.setText("Smith")
                    count = window.roster_views["players"].model().rowCount()
                    window.navigation.setCurrentItem(window.navigation.topLevelItem(0))
                    window.search.clear()
                    snapshot = OUTPUT / "reports" / "actual_explorer.png"
                    snapshot.parent.mkdir(parents=True, exist_ok=True)
                    window.grab().save(str(snapshot))
                    entry = next(
                        e for e in window.archive.entries if e["name"] == "uh000.iff"
                    )
                    import uuid

                    destination = OUTPUT / "temp" / ("gui_export_" + uuid.uuid4().hex)
                    window.run_job(
                        "Harmless packaged export",
                        lambda job: extract(window.archive, [entry], destination, job),
                    )
                    state["filtered_players"] = count
                else:
                    save_json(
                        OUTPUT / "reports" / "packaged_gui_smoke.json",
                        {
                            "status": "passed",
                            "entries": len(window.archive.entries),
                            "preview_decoded": True,
                            "players": len(window.roster.rows["players"]),
                            "search_rows": state["filtered_players"],
                            "harmless_export": True,
                        },
                    )
                    window.close()
                    app.quit()
                    return
                state["step"] += 1
            except Exception as error:  # noqa: BLE001 - smoke records all failures
                fail(str(error))
                return
            QTimer.singleShot(100, verify)

        QTimer.singleShot(100, verify)
    elif args.smoke:

        def finish():
            if window.active:
                QTimer.singleShot(100, finish)
            else:
                window.close()
                app.quit()

        QTimer.singleShot(800, finish)
    return app.exec()

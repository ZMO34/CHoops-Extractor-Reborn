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
from PySide6.QtGui import QAction, QImage, QPixmap, QColor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QSizePolicy,
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
from .services import (
    Cancelled,
    JobContext,
    extract,
    inspect_asset,
    materialize,
    stage_folder,
)


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
        if not index.isValid():
            return None
        key = self.columns[index.column()][0]
        value = self.rows[index.row()].get(key, "")
        if role == Qt.ItemDataRole.UserRole:
            return value if isinstance(value, (int, float)) else str(value or "")
        if role != Qt.ItemDataRole.DisplayRole:
            return None
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

        except Cancelled as error:
            self.events.result.emit({"status": "cancelled", "detail": str(error)})
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
    proxy.setSortRole(Qt.ItemDataRole.UserRole)

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


class TexturePreview(QLabel):
    """Keep the entire texture visible as the preview viewport changes size."""

    def __init__(self, text):
        super().__init__(text)
        self._original = QPixmap()
        self.setMinimumSize(1, 120)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setPixmap(self, pixmap):
        self._original = pixmap
        self._fit()

    def setText(self, text):
        self._original = QPixmap()
        super().setText(text)

    def clear(self):
        self._original = QPixmap()
        super().clear()

    def _fit(self):
        if not self._original.isNull():
            super().setPixmap(self._original.scaled(
                self.contentsRect().size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()


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

        self.cancel = QPushButton("Cancel task")

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
            # A newly selected JB folder must not inherit another source's roster.
            self.roster = None
            for view in self.roster_views.values():
                view.setModel(None)
            self.roster_state.setText('No roster loaded; load the current JB folder roster')
            self.scene_meshes = []
            self.scene_view.set_meshes([])
            self.scene_palette_state.setText("No roster associated; load the current JB folder roster")

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

        self.run_job("Index JB folder", lambda job: Archive(path), loaded)

    def create_explorer(self):

        layout = self.page(
            "Archive explorer",
            "Select a PS3 JB folder, including a modded rebuild. Browse assets without a full rip; double-click an IFF to inspect records and preview its textures.",
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

        self.explorer_texture = QComboBox()
        self.explorer_texture.setEnabled(False)
        self.explorer_texture.activated.connect(self.preview_explorer_texture)
        layout.addWidget(self.explorer_texture)
        self.explorer_image = TexturePreview("Open an IFF or double-click an archive entry to preview textures")
        self.explorer_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setWidget(self.explorer_image)
        layout.addWidget(preview_scroll)

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

        if path and Path(path).name == "0A":
            self.open_game(Path(path))
        elif path:
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
        self.explorer_image.setText(result["warning"] or "No supported textures in this asset")
        self.explorer_texture.clear()
        for texture in result["textures"]:
            if texture["editable"] and "reason" not in texture["metadata"]:
                info = texture["metadata"]
                self.explorer_texture.addItem(
                    f"{texture['name']} — {info.get('width', '?')} × {info.get('height', '?')} {info.get('format', '')}",
                    texture["name"],
                )
        self.explorer_texture.setEnabled(self.explorer_texture.count() > 0)
        if self.explorer_texture.count():
            self.explorer_image.setText("Loading texture preview…")
            # The inspection worker emits finished after its result callback.
            QTimer.singleShot(0, self.preview_explorer_texture)

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

        self.image = TexturePreview("DDS previews appear here")

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
                if image.width * image.height > 32 * 1024 * 1024:
                    raise ValueError("Image exceeds interactive pixel limit")
                image.load()

                image.thumbnail((2048, 2048))

                rgba = image.convert("RGBA")

                return rgba.size, rgba.tobytes()

        def display(result):

            (w, h), raw = result

            image = QImage(raw, w, h, w * 4, QImage.Format.Format_RGBA8888).copy()

            self.image.setPixmap(QPixmap.fromImage(image))

        self.run_job("Decode image preview", decode, display)

    def preview_explorer_texture(self, index=None):
        selector = self.explorer_texture.currentData()
        if selector and self.asset_path:
            if self.active:
                QTimer.singleShot(20, self.preview_explorer_texture)
                return
            self.decode_texture_preview(selector, self.explorer_image)

    def preview_texture(self):

        rows = selected(self.textures)

        if not self.asset_path or len(rows) != 1:
            return

        self.decode_texture_preview(rows[0]["name"], self.image)

    def decode_texture_preview(self, selector, target):
        source = self.asset_path
        target.setText("Loading texture preview…")

        def decode(job):
            from .services import decode_texture_preview
            return decode_texture_preview(source, selector)

        def display(result):

            (w, h), raw = result

            image = QImage(raw, w, h, w * 4, QImage.Format.Format_RGBA8888).copy()

            if self.asset_path == source:
                target.setPixmap(QPixmap.fromImage(image))

        def decode_with_status(job):
            try:
                return decode(job)
            except Exception as error:
                return str(error)

        def display_with_status(result):
            if isinstance(result, str):
                target.setText("Preview unavailable: " + result)
                self.log("Preview unavailable: " + result)
            else:
                display(result)

        self.run_job("Preview selected texture", decode_with_status, display_with_status)

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
                ("Team palette…", self.show_team_palette),
                ("Player attributes…", self.show_player_attributes),
                ("Player properties…", self.show_player_properties),
                ("Research layout…", self.research_roster),
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

        for name in ("players", "teams", "schools", "arenas", "coaches", "conferences"):
            view = table()

            self.roster_views[name] = view

            self.roster_tabs.addTab(view, "Edit Schools" if name=="schools" else name.title())

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
            "Load current JB folder roster",
            lambda job: EditorModel.open(materialize(self.archive, matches[0])),
            self.display_roster,
        )

    def display_roster(self, model):

        self.roster = model
        if getattr(self, "scene_meshes", None):
            self.select_scene_part()

        for name, view in self.roster_views.items():
            rows = model.rows.get("teams" if name=="schools" else name, [])

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

    def show_team_palette(self, team_index=None):
        if not self.roster:
            return self.log("Load a roster first.")
        if team_index is None or isinstance(team_index, bool):
            view=self.roster_views['schools'] if self.roster_tabs.currentWidget() is self.roster_views.get('schools') else self.roster_views['teams']
            rows = selected(view)
            if len(rows) != 1:
                return self.log("Select one team in the Teams tab.")
            team_index = rows[0]['index']
        from ..roster.research import palette_rows
        team = self.roster.rows['teams'][team_index]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{team['school_name']} • asset {team['asset_id']} • team palette")
        dialog.resize(760, 700)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("22 Edit Schools captions are verified. Other slot roles remain provisional; court material bindings are supported."))
        view = QTreeWidget()
        view.setHeaderLabels(['Palette slot','RGBA','Edit Schools control','Caption / provisional role'])
        layout.addWidget(view)
        def refresh():
            view.clear()
            for row in palette_rows(self.roster, team_index):
                item = QTreeWidgetItem(view,[str(row['slot']),row['rgba'],str(row['school_control']) if row['school_control'] is not None else 'Not in color callback list',row['role']])
                color = bytes.fromhex(row['rgba'][1:])
                item.setBackground(1,QColor(*color))
        def edit():
            items = view.selectedItems()
            if not items:
                return
            slot = int(items[0].text(0))
            value, ok = QInputDialog.getText(dialog, 'Edit palette RGBA', '#RRGGBBAA (eight hex digits)', text=items[0].text(1))
            if ok:
                try:
                    self.roster.edit('teams',team_index,'palette_colors',value,slot)
                    refresh()
                    self.display_roster(self.roster)
                except ValueError as error:
                    QMessageBox.warning(dialog,'Palette edit blocked',str(error))
        button = QPushButton('Edit selected color…');button.clicked.connect(edit);layout.addWidget(button)
        refresh();dialog.exec()

    def show_player_properties(self):
        if not self.roster:return
        rows=selected(self.roster_views['players'])
        if len(rows)!=1:return self.log("Select one player in the Players tab.")
        from ..roster.schema import TENDENCY_NAMES
        row=rows[0];dialog=QDialog(self);dialog.resize(650,650)
        dialog.setWindowTitle('Player properties • executable-backed storage')
        layout=QVBoxLayout(dialog)
        layout.addWidget(QLabel('Appearance values are raw enum codes; their choice labels are still being traced.'))
        view=QTreeWidget();view.setHeaderLabels(['Property','Value'])
        for name,value in row['properties'].items():QTreeWidgetItem(view,[name,str(value)])
        for name,value in zip(TENDENCY_NAMES,row['shot_tendencies']):QTreeWidgetItem(view,[name+' tendency',str(value)])
        layout.addWidget(view);dialog.exec()

    def show_player_attributes(self):
        if not self.roster or self.active:
            return
        rows = selected(self.roster_views['players'])
        if len(rows)!=1:
            return self.log("Select one player in the Players tab.")
        from ..roster.schema import RATING_HINTS,RATING_OFFSET
        from ..formats.binary import Binary
        player_index=rows[0]['index']
        dialog=QDialog(self);dialog.resize(780,700)
        dialog.setWindowTitle('Player attributes • executable and UI metadata verified')
        layout=QVBoxLayout(dialog)
        layout.addWidget(QLabel('30 named attributes; edits use the game setter encoding (rating × 100).'))
        view=QTreeWidget();view.setHeaderLabels(['Channel','Row offset','Rating','Stored u16','Attribute'])
        layout.addWidget(view)
        def refresh():
            view.clear();row=self.roster.rows['players'][player_index];binary=Binary(self.roster.data)
            for i,value in enumerate(row['attribute_ratings']):
                offset=RATING_OFFSET+i*2
                QTreeWidgetItem(view,[str(i),hex(offset),str(value),str(binary.u16(row['row_offset']+offset)),RATING_HINTS.get(i,'Unassigned attribute')])
        def edit():
            items=view.selectedItems()
            if not items:return
            channel=int(items[0].text(0))
            value,ok=QInputDialog.getInt(dialog,'Edit attribute channel','Rating',int(items[0].text(2)),35,99)
            if ok:
                try:
                    self.roster.edit('players',player_index,'attribute_ratings',value,channel)
                    self.display_roster(self.roster);refresh()
                except ValueError as error:QMessageBox.warning(dialog,'Rating edit blocked',str(error))
        button=QPushButton('Edit selected channel…');button.clicked.connect(edit);layout.addWidget(button)
        refresh();dialog.exec()

    def scene_team_palette(self):
        import re
        if not self.roster or not hasattr(self, 'scene_source'):
            return self.log("Load the game roster in Roster Editor, then open a stadium scene.")
        match = re.fullmatch(r's(\d+)', self.scene_source.stem, re.IGNORECASE)
        teams = [t for t in self.roster.rows['teams'] if match and t['asset_id'] == int(match[1])]
        if len(teams) != 1:
            return self.log("Stadium asset ID has no unique team match in the loaded roster.")
        self.show_team_palette(teams[0]['index'])

    def research_roster(self):
        if not self.roster:
            return self.log("Load a roster first.")
        from ..roster.research import analyze
        from ..core.reports import save_json
        import uuid
        path = OUTPUT / 'reports' / ('roster_layout_'+uuid.uuid4().hex+'.json')
        def research(job):
            report = analyze(self.roster)
            save_json(path,report)
            return {'report':str(path),'semantic_mapping_complete':False}
        self.run_job('Profile roster fields and unresolved regions',research)

    def edit_roster(self):

        if not self.roster or self.active:
            return

        view = self.roster_tabs.currentWidget()
        name = next(key for key,value in self.roster_views.items() if value is view)
        name = 'teams' if name == 'schools' else name

        rows = selected(view)

        if len(rows) != 1:
            return self.log("Select exactly one roster row.")


        from ..roster.schema import EDITABLE, POSITIONS, REFERENCES

        row = rows[0]

        dialog = QDialog(self)

        dialog.setWindowTitle(f"Edit {name} record {row['index']}")

        form = QFormLayout(dialog)

        field = QComboBox()
        field.setObjectName("rosterField")

        field.addItems(EDITABLE[name])

        value = QLineEdit()

        slot = QComboBox()

        slot.addItems([str(i) for i in range(16)])

        choices = QComboBox()
        choices.setObjectName("rosterValue")

        choices.setEditable(False)

        def changed(key):
            reference = key == "roster_slots" or key in REFERENCES
            menu = reference or key == "position_code"
            value.setVisible(not menu)
            choices.setVisible(menu)
            needed = 31 if key == 'palette_colors' else 30 if key == 'attribute_ratings' else 4 if key=='shot_tendencies' else 16
            if slot.count() != needed:
                slot.blockSignals(True)
                slot.clear()
                slot.addItems([str(i) for i in range(needed)])
                slot.blockSignals(False)
            slot.setVisible(key in ('roster_slots','palette_colors','attribute_ratings','shot_tendencies'))
            choices.clear()
            if key == "position_code":
                for code, label in POSITIONS.items():
                    choices.addItem(label, code)
                choices.setCurrentIndex(choices.findData(row[key]))
            elif reference:
                target = "players" if key == "roster_slots" else REFERENCES[key][1]
                choices.addItem("None", None)
                for candidate in self.roster.rows[target]:
                    label = (
                        candidate.get("display_name")
                        or candidate.get("school_name")
                        or candidate.get("arena_name")
                        or candidate.get("coach_name")
                        or ""
                    )
                    choices.addItem(
                        f"{candidate['index']}: {label}", candidate["index"]
                    )
                current = (
                    row[key][int(slot.currentText())]
                    if key == "roster_slots"
                    else row[key]
                )
                choices.setCurrentIndex(max(0, choices.findData(current)))
            else:
                value.setText(str(row[key][int(slot.currentText())]) if key in ('palette_colors','attribute_ratings','shot_tendencies') else str(row.get(key, "")))

        slot.currentTextChanged.connect(lambda value: changed(field.currentText()))
        form.addRow("Field (see palette dialog for verified captions)", field)

        form.addRow("Value", value)

        form.addRow("Reference", choices)

        form.addRow("Roster / palette slot", slot)

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
                if key == "roster_slots" or key in REFERENCES or key == "position_code"
                else value.text()
            )

            def edit(job):

                self.roster.edit(
                    name,
                    row["index"],
                    key,
                    new,
                    int(slot.currentText()) if key in ("roster_slots", "palette_colors", "attribute_ratings", "shot_tendencies") else None,
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
            "Models / Courts • 3D preview",
            "Select a SCNE record in Explorer, then Preview scene. Drag to orbit; wheel to zoom. Material textures load automatically. Use cutaway to see inside; game shader effects are not reproduced.",
        )
        self.buttons(layout, [("Preview selected SCNE", self.inspect_scene)])
        self.scene_complete = QCheckBox("Include all SCNE sections (arena and court)")
        self.scene_complete.setChecked(True)
        layout.addWidget(self.scene_complete)
        self.scene_cutaway = QCheckBox("Cutaway: hide roof and light-effect meshes")
        self.scene_cutaway.setChecked(True)
        self.scene_cutaway.toggled.connect(self.select_scene_part)
        layout.addWidget(self.scene_cutaway)
        self.scene_lift = QCheckBox("Lift court in preview")
        self.scene_lift.setChecked(True)
        self.scene_lift.toggled.connect(self.select_scene_part)
        layout.addWidget(self.scene_lift)
        self.scene_lift_amount = QDoubleSpinBox()
        self.scene_lift_amount.setRange(0., 100.)
        self.scene_lift_amount.setValue(10.)
        self.scene_lift_amount.setSuffix(" scene units")
        self.scene_lift_amount.valueChanged.connect(self.select_scene_part)
        layout.addWidget(self.scene_lift_amount)
        self.scene_parts = QComboBox()
        self.scene_parts.activated.connect(self.select_scene_part)
        layout.addWidget(self.scene_parts)
        self.scene_textures = QComboBox()
        self.scene_textures.activated.connect(self.select_scene_texture)
        layout.addWidget(self.scene_textures)
        from .scene_view import SceneView
        self.scene_view = SceneView()
        layout.addWidget(self.scene_view, 1)
        self.buttons(layout, [("Fit camera", self.scene_view.fit_camera), ("Linked roster palette…", self.scene_team_palette)])
        self.model_details = QPlainTextEdit()
        self.model_details.setReadOnly(True)
        self.model_details.setMaximumHeight(120)
        layout.addWidget(self.model_details)
        self.scene_meshes = []
        self.scene_palette_state = QLabel('No roster associated; embedded material textures only')
        layout.addWidget(self.scene_palette_state)

    def inspect_scene(self):
        if not self.asset_path:
            return self.log("Open a stadium IFF in Explorer first.")
        items = self.nested.selectedItems()
        if items and items[0].text(1) == "SCNE":
            index = int(items[0].text(2))
        elif self.asset_path.suffix.lower() == '.scne':
            index = 0
        else:
            return self.log("Select a SCNE record in the Explorer nested list.")
        source = self.asset_path
        self.navigation.setCurrentItem(self.navigation.topLevelItem(3))
        self.scene_meshes = []
        self.scene_view.set_meshes([])
        self.scene_view.set_material_images({})
        self.scene_view.set_image(None)
        self.scene_parts.clear()
        self.scene_textures.clear()
        self.model_details.setPlainText("Loading scene…")
        from .services import inspect_scene_preview
        def display(result):
            self.scene_source = source
            self.scene_meshes = result['meshes']
            self.scene_parts.addItem('All supported parts', -1)
            for i, mesh in enumerate(self.scene_meshes):
                self.scene_parts.addItem(mesh['name'], i)
            self.scene_textures.addItem('Automatic material textures', '__automatic__')
            self.scene_textures.addItem('Untextured', None)
            for name in result['textures']:
                self.scene_textures.addItem(name, name)
            images = {}
            for name, ((w,h), raw) in result['images'].items():
                images[name] = QImage(raw,w,h,w*4,QImage.Format.Format_RGBA8888).copy()
            self.scene_view.automatic = True
            self.scene_view.set_material_images(images)
            self.select_scene_part()
            self.model_details.setPlainText(
                f"{len(self.scene_meshes)} supported parts; {sum(len(m['vertices'])//3 for m in self.scene_meshes)} triangles. {len(result['images'])} material textures loaded; use dropdown for overrides.\n"
                + '\n'.join(result['warnings'])
            )
        include_all = self.scene_complete.isChecked()
        self.run_job('Decode scene geometry and textures', lambda job: inspect_scene_preview(source, index, include_all, job), display, cancellable=True)

    def select_scene_part(self, index=None):
        part = self.scene_parts.currentData()
        meshes = self.scene_meshes if part == -1 else [self.scene_meshes[part]] if part is not None else []
        if part == -1 and self.scene_cutaway.isChecked():
            meshes = [m for m in meshes if not m.get('hidden_by_default')]
        if self.scene_lift.isChecked():
            meshes = [{**mesh, 'vertices': [(v[0], v[1]+self.scene_lift_amount.value(), *v[2:]) for v in mesh['vertices']]}
                      if mesh['name'].split('/')[0].lower() == 'floor' else mesh for mesh in meshes]
        from ..formats.scene_palette import associate_palette
        import re
        match = re.fullmatch(r's(\d+)', self.scene_source.stem, re.IGNORECASE) if hasattr(self, 'scene_source') else None
        teams = [team for team in self.roster.rows['teams'] if match and team['asset_id'] == int(match[1])] if self.roster else []
        colors = teams[0]['palette_colors'] if len(teams) == 1 else None
        meshes = associate_palette(meshes, colors)
        if colors is not None:
            count = sum(batch['palette_tint'] is not None for mesh in meshes for batch in mesh['batches'])
            self.scene_palette_state.setText(f"Associated roster: {self.roster.source.source_path or 'current JB folder roster'}; {teams[0]['school_name']}; {count} court color bindings. Arena shader masks are unresolved.")
        else:
            self.scene_palette_state.setText('No unique roster/team association; embedded material textures only. Use Associate roster to select a matching roster.')
        self.scene_view.set_meshes(meshes)

    def select_scene_texture(self, index=None):
        name = self.scene_textures.currentData()
        self.scene_view.automatic = name == '__automatic__'
        self.scene_view.set_image(None)
        if name is None or name == '__automatic__':
            return
        from .services import decode_texture_preview
        def display(result):
            (w, h), raw = result
            self.scene_view.set_image(QImage(raw, w, h, w*4, QImage.Format.Format_RGBA8888).copy())
        self.run_job('Decode scene texture', lambda job: decode_texture_preview(self.scene_source, name), display)

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
                ("Export mod patch…", self.export_mod_patch),
                ("Import mod patch…", self.import_mod_patch),
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

    def export_mod_patch(self):

        if not self.source:
            return self.log("Open a game first.")

        output, _ = QFileDialog.getSaveFileName(
            self,
            "Export source-bound patch under output/",
            str(OUTPUT / "builds" / "my_mod.chpatch"),
            "CHoops patch (*.chpatch)",
        )

        if output:
            from ..modding.patch_package import export_patch

            source, mod = self.source, Path(self.mod_path.text())

            self.run_job(
                "Export mod differences",
                lambda job: export_patch(source, mod, Path(output)),
            )

    def import_mod_patch(self):

        if not self.source:
            return self.log("Open a game first.")

        package, _ = QFileDialog.getOpenFileName(
            self,
            "Import source-bound mod patch",
            str(OUTPUT),
            "CHoops patch (*.chpatch)",
        )

        if package:
            from ..modding.patch_package import import_patch

            source, mod = self.source, Path(self.mod_path.text())

            self.run_job(
                "Validate and stage mod patch",
                lambda job: import_patch(source, Path(package), mod),
            )

    def build_game(self, dry_run):

        if not self.source:
            return self.log("Open a game first.")

        from ..archive.build_copy import build

        mod, output = self.mod_path.text(), self.build_path.text()

        self.run_job(
            "Preflight mod" if dry_run else "Build separate JB copy",
            lambda job: build(self.source, mod, output, dry_run=dry_run, job=job),
            lambda result: self.build_details.setPlainText(
                json.dumps(result, indent=2)
            ),
            cancellable=True,
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

    window.showMaximized()

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

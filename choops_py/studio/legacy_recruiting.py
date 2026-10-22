"""Read-only recruiting diagnostics; no transfer or save mutation actions."""

from hashlib import sha256
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..research.recruit_pool import inspect_recruit_pool
from ..research.legacy_history import inspect_player_history
from ..research.legacy_schedule import inspect_conference_schedule
from ..research.legacy_backend import (
    AGGREGATE_SIZE,
    backend_overview,
    component_layout,
    inspect_legacy_aggregate,
)


class RecruitingDiagnostics(QDialog):
    def __init__(self, owner, source):
        super().__init__(owner)
        from .app import table

        self.owner = owner
        self.source = source
        self.payload = bytes(source.data)
        self.closed = False
        self.finished.connect(self.mark_closed)
        self.setWindowTitle("Legacy recruiting — read-only diagnostics")
        self.resize(1050, 650)
        layout = QVBoxLayout(self)
        notice = QLabel(
            "Inspect recruiting records only. "
            "The in-game transfer portal is not installed. "
            "Transfers must retain the original player's statistics and team history."
        )
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.status = QLabel("Inspecting recruit records…")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search recruit slots, classes, and diagnostics")
        self.search.textChanged.connect(self.filter_rows)
        layout.addWidget(self.search)
        self.view = table()
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        splitter = QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(self.details)
        splitter.setSizes([600, 450])
        tabs = QTabWidget()
        tabs.addTab(splitter, "Recruit records")
        backend = QWidget()
        backend_layout = QVBoxLayout(backend)
        overview = QPlainTextEdit(backend_overview())
        overview.setReadOnly(True)
        overview.setMaximumHeight(240)
        backend_layout.addWidget(overview)
        self.aggregate_button = QPushButton("Inspect native Legacy aggregate…")
        self.aggregate_button.clicked.connect(self.open_aggregate)
        backend_layout.addWidget(self.aggregate_button)
        self.aggregate_status = QLabel("Structure map only — no aggregate loaded.")
        self.aggregate_status.setWordWrap(True)
        backend_layout.addWidget(self.aggregate_status)
        self.backend_view = table()
        self.backend_details = QPlainTextEdit()
        self.backend_details.setReadOnly(True)
        backend_splitter = QSplitter()
        backend_splitter.addWidget(self.backend_view)
        backend_splitter.addWidget(self.backend_details)
        backend_layout.addWidget(backend_splitter, 1)
        tabs.addTab(backend, "Legacy backend")
        self.schedule_status, self.schedule_view, self.schedule_details = (
            self.research_page(
                tabs,
                "Scheduling / tournaments",
                "Membership changes do not regenerate the roster's fixtures. "
                "Counts below use current conference members; uneven counts alone do not prove a broken schedule. "
                "Tournament index 96 skips the native conference tournament event.",
            )
        )
        self.history_status, self.history_view, self.history_details = (
            self.research_page(
                tabs,
                "Player history",
                "Five statistics IDs belong to each player: current season plus four prior slots. "
                "School attribution belongs to the linked statistics record. "
                "These views inspect ownership; they do not certify in-game transfer continuity.",
            )
        )
        layout.addWidget(tabs)
        self.display_components(component_layout())

    def research_page(self, tabs, title, notice):
        from .app import table, selected

        page = QWidget()
        layout = QVBoxLayout(page)
        status = QLabel(notice)
        status.setWordWrap(True)
        layout.addWidget(status)
        search = QLineEdit()
        search.setPlaceholderText("Search results")
        layout.addWidget(search)
        view = table()
        details = QPlainTextEdit()
        details.setReadOnly(True)
        split = QSplitter()
        split.addWidget(view)
        split.addWidget(details)
        layout.addWidget(split, 1)

        def filter_rows(text):
            if view.model():
                view.model().setFilterFixedString(text)

        def show_details(*_):
            rows = selected(view)
            details.setPlainText(
                json.dumps(rows[0], indent=2) if len(rows) == 1 else ""
            )

        search.textChanged.connect(filter_rows)
        # Connect to the view's selection model after setting its source model.
        view.setProperty("research_title", title)
        view._research_selection = show_details
        tabs.addTab(page, title)
        return status, view, details

    def source_current(self):
        return (
            not self.closed
            and self.owner.roster is self.source
            and sha256(self.source.data).digest() == sha256(self.payload).digest()
        )

    def display_components(self, rows):
        from .app import set_rows

        display = [dict(row, offset_hex=f"0x{row['offset']:06X}") for row in rows]
        set_rows(
            self.backend_view,
            display,
            [
                ("component", "Native component"),
                ("offset_hex", "Aggregate offset"),
                ("bytes", "Bytes"),
                ("serializer", "Save routine"),
                ("loader", "Load routine"),
            ],
        )
        self.backend_view.selectionModel().selectionChanged.connect(self.show_component)

    def show_component(self, *_):
        from .app import selected

        rows = selected(self.backend_view)
        self.backend_details.setPlainText(
            json.dumps(rows[0], indent=2) if len(rows) == 1 else ""
        )

    def open_aggregate(self):
        if self.owner.active or not self.source_current():
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open an identified native Legacy aggregate (not a whole save)",
            "",
            "Native aggregate (*.bin);;All files (*)",
        )
        if not path:
            return
        payload = self.payload

        def inspect(_job):
            try:
                with Path(path).open("rb") as stream:
                    aggregate = stream.read(AGGREGATE_SIZE + 1)
                return inspect_legacy_aggregate(aggregate, payload)
            except (ValueError, OSError) as error:
                return {"error": str(error)}

        self.owner.run_job(
            "Inspect native Legacy backend", inspect, self.display_aggregate
        )

    def display_aggregate(self, report):
        if not self.source_current():
            if not self.closed:
                self.aggregate_status.setText(
                    "The source roster changed. Reopen diagnostics."
                )
                self.display_components(component_layout())
                self.backend_details.clear()
            return
        if "error" in report:
            self.aggregate_status.setText("Aggregate unavailable: " + report["error"])
            self.display_components(component_layout())
            self.backend_details.clear()
            return
        errors = sum("audit_error" in row for row in report["components"])
        self.aggregate_status.setText(
            f"17 native components · {errors} component audit errors. "
            "Roster/aggregate correspondence and full history continuity are unverified."
        )
        self.display_components(report["components"])
        self.backend_view.selectRow(0)

    def inspect(self, _job):
        # Captured immutable bytes, never a live EditorModel or Qt widget read.
        try:
            report = inspect_recruit_pool(self.payload)
        except ValueError as error:
            report = {"error": str(error)}
        for name, reader in [
            ("scheduling", inspect_conference_schedule),
            ("player_history", inspect_player_history),
        ]:
            try:
                report[name] = reader(self.payload)
            except ValueError as error:
                report[name] = {"error": str(error)}
        return report

    def display(self, report):
        from .app import set_rows

        if self.closed:
            return
        if (
            self.owner.roster is not self.source
            or sha256(self.source.data).digest() != sha256(self.payload).digest()
        ):
            self.status.setText(
                "The source roster changed. Reopen recruiting diagnostics."
            )
            return
        self.display_research(report)
        if "error" in report:
            self.status.setText("Recruiting records unavailable: " + report["error"])
            return
        self.status.setText(
            f"{report['allocated_slots']:,} reserved records · "
            f"{report['nonzero_records']:,} nonzero · "
            f"{report['blank_records']:,} blank. "
            "Blank records are not certified available for insertion. "
            "Interest chains and complete history continuity "
            "are not verified by this view."
        )
        rows = [
            dict(row, issues_text=", ".join(row["issues"])) for row in report["records"]
        ]
        set_rows(
            self.view,
            rows,
            [
                ("slot", "Recruit slot"),
                ("class_label", "HS / JC class"),
                ("class_code", "Raw class"),
                ("recruiting_filter_bit_2", "Recruiting filter"),
                ("committed_bit", "Committed"),
                ("location_id", "Location ID"),
                ("preference_index", "Preference profile"),
                ("issues_text", "Diagnostics"),
            ],
            self.search.text(),
        )
        self.view.selectionModel().selectionChanged.connect(self.show_details)
        if rows:
            self.view.selectRow(0)

    def display_research(self, report):
        from .app import set_rows

        self.schedule_details.clear()
        self.history_details.clear()
        tables = getattr(self.source, "rows", {})
        for name, status, view, rows_key, columns, label_table, index_key in [
            (
                "scheduling",
                self.schedule_status,
                self.schedule_view,
                "conferences",
                [
                    ("conference_index", "Conference"),
                    ("name", "Name"),
                    ("declared_members", "Members"),
                    ("fixture_count", "Internal fixtures"),
                    ("minimum_fixtures", "Min/team"),
                    ("maximum_fixtures", "Max/team"),
                    ("tournament_index", "Tournament"),
                    ("tournament_entrants", "Entrants"),
                    ("diagnostics", "Diagnostics"),
                ],
                "conferences",
                "conference_index",
            ),
            (
                "player_history",
                self.history_status,
                self.history_view,
                "players_with_history",
                [
                    ("player_index", "Player"),
                    ("name", "Name"),
                    ("stat_ids", "Current / previous statistics IDs"),
                ],
                "players",
                "player_index",
            ),
        ]:
            result = report.get(name, {"error": "Not inspected"})
            if "error" in result:
                status.setText("Unavailable: " + result["error"])
                set_rows(view, [], columns)
                continue
            if name == "scheduling":
                status.setText(
                    f"{result['scheduled_games']:,} roster fixtures. Membership changes do not regenerate them. "
                    "Tournament index 96 skips its event; current internal fixture counts are diagnostic, not certification."
                )
            else:
                status.setText(
                    f"{result['unique_referenced_records']:,} referenced statistics records · "
                    f"{len(result['issues'])} metadata issues · {len(result['shared_references'])} shared references. "
                    "Five player-owned history slots; school attribution is in each linked record. Runtime continuity unverified."
                )
            rows = []
            labels = tables.get(label_table, [])
            for row in result[rows_key]:
                index = row[index_key]
                label = labels[index] if index < len(labels) else {}
                name_text = (
                    label.get("conference_name", "")
                    if label_table == "conferences"
                    else " ".join(
                        label.get(k, "") for k in ("first_name", "last_name")
                    ).strip()
                )
                rows.append(dict(row, name=name_text))
            set_rows(view, rows, columns)
            view.selectionModel().selectionChanged.connect(view._research_selection)
            if rows:
                view.selectRow(0)

    def filter_rows(self, text):
        if self.view.model():
            self.view.model().setFilterFixedString(text)

    def show_details(self, *_):
        from .app import selected

        rows = selected(self.view)
        if len(rows) != 1:
            self.details.clear()
            return
        row = rows[0]
        lines = [f"Recruit slot {row['slot']}", "", "Native recruiting preferences"]
        preferences = row["preferences"]
        if preferences is None:
            lines.append("Uninitialized profile; preferences are unresolved.")
        else:
            for name, (rank, weight) in sorted(
                preferences.items(), key=lambda pair: pair[1][0]
            ):
                lines.append(
                    f"{rank + 1}. {name.replace('_', ' ')} (weight {weight:.2f})"
                )
        lines.extend(
            [
                "",
                f"Raw flags: 0x{row['flags_2d']:02X}",
                f"Interest head: 0x{row['interest_head']:04X}",
                "Location units and full interest-chain ownership are unresolved.",
                "Recruit class codes differ from college-player class codes.",
                "This view does not establish a recruit-to-existing-player binding.",
                "",
                "Diagnostics: "
                + (row["issues_text"] or "No metadata issues detected."),
            ]
        )
        self.details.setPlainText("\n".join(lines))

    def mark_closed(self, *_):
        self.closed = True


def open_recruiting_diagnostics(owner):
    if owner.active or owner.roster is None:
        return
    previous = getattr(owner, "recruiting_diagnostics", None)
    if previous is not None:
        previous.close()
        previous.deleteLater()
    dialog = RecruitingDiagnostics(owner, owner.roster)
    owner.recruiting_diagnostics = dialog
    dialog.show()
    owner.run_job("Inspect Legacy recruiting", dialog.inspect, dialog.display)

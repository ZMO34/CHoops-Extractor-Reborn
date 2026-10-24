"""Recruiting diagnostics and bounded edits; no transfer or allocation actions."""

from hashlib import sha256

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
)

from ..research.recruit_pool import inspect_recruit_pool


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
            "Inspect recruit records and edit the confirmed class field on active, "
            "uncommitted recruits. "
            "The in-game transfer portal is not installed. "
            "Other recruit fields and linked recruiting state remain read-only."
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
        self.edit_button = QPushButton("Edit selected recruit…")
        self.edit_button.clicked.connect(self.edit_selected)
        self.edit_button.setEnabled(False)
        layout.addWidget(self.edit_button)
        self.rows_by_slot = {}
        self.view = table()
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        splitter = QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(self.details)
        splitter.setSizes([600, 450])
        layout.addWidget(splitter)

    def inspect(self, _job):
        # Captured immutable bytes, never a live EditorModel or Qt widget read.
        try:
            return inspect_recruit_pool(self.payload)
        except ValueError as error:
            return {"error": str(error)}

    def display(self, report):
        from .app import set_rows

        if self.closed:
            return
        self.edit_button.setEnabled(False)
        if (
            self.owner.roster is not self.source
            or sha256(self.source.data).digest() != sha256(self.payload).digest()
        ):
            self.status.setText(
                "The source roster changed. Reopen recruiting diagnostics."
            )
            return
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
        self.rows_by_slot = {row["slot"]: row for row in rows}
        self.edit_button.setEnabled(bool(rows))
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

    def edit_selected(self):
        from .app import selected

        if self.owner.active:
            QMessageBox.information(
                self, "Recruiting table", "Wait for the current task to finish."
            )
            return
        if (
            self.owner.roster is not self.source
            or sha256(self.source.data).digest() != sha256(self.payload).digest()
        ):
            QMessageBox.warning(
                self,
                "Recruiting table changed",
                "The roster changed after this view opened. "
                "Reopen Recruiting diagnostics before editing.",
            )
            return
        rows = selected(self.view)
        if len(rows) != 1:
            QMessageBox.information(self, "Recruiting table", "Select exactly one recruit.")
            return
        slot = rows[0]["slot"]
        row = self.rows_by_slot.get(slot)
        if row is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit recruit slot {slot}")
        form = QFormLayout(dialog)
        class_choice = QComboBox()
        class_labels = ("HS FR", "HS SO", "HS JR", "HS SR", "JC FR", "JC SO")
        for code, label in enumerate(class_labels):
            class_choice.addItem(label, code)
        class_choice.setCurrentIndex(class_choice.findData(row["class_code"]))
        class_choice.setEnabled(
            not row["committed_bit"]
            and row["recruiting_filter_bit_2"]
            and row["class_code"] in range(6)
            and not row["issues"]
        )
        form.addRow("Recruit class", class_choice)
        if row["committed_bit"]:
            note = "Committed recruits are locked."
        elif row["issues"]:
            note = "This record has unresolved metadata and cannot be edited."
        elif not row["recruiting_filter_bit_2"]:
            note = "This record is not marked as an active recruiting entry."
        else:
            note = (
                "Only the confirmed class field is editable. Names, ratings, "
                "preferences, commitment, location and linked interest data "
                "remain read-only."
            )
        note_label = QLabel(note)
        note_label.setWordWrap(True)
        form.addRow(note_label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        changes = {}
        chosen_class = class_choice.currentData()
        if class_choice.isEnabled() and chosen_class != row["class_code"]:
            changes["class_code"] = chosen_class
        if not changes:
            return
        try:
            self.owner.roster.edit_recruit_fields(slot, **changes)
        except (ValueError, IndexError) as error:
            QMessageBox.warning(self, "Recruit edit blocked", str(error))
            return

        from .app import open_recruiting_diagnostics

        self.close()
        self.owner.display_roster(self.owner.roster)
        open_recruiting_diagnostics(self.owner)

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

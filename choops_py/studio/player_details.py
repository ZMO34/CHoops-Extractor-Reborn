"""Always-visible player details, ratings and scholarship editor."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ..roster.presentation import height_inches, height_text
from ..roster.schema import (
    ENUM_CHOICES,
    PROPERTY_CHOICES,
    PROPERTY_FIELDS,
    RATING_NAMES,
    TENDENCY_NAMES,
)


class PlayerDetails(QTabWidget):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.player_index = None
        self.loading = False
        self.details = QTreeWidget()
        self.details.setHeaderLabels(["Player detail", "Value (double-click to edit)"])
        self.details.itemDoubleClicked.connect(self.edit_item)
        self.addTab(self.details, "Player")
        self.ratings = QTreeWidget()
        self.ratings.setHeaderLabels(["Rating / tendency", "Value"])
        self.ratings.itemDoubleClicked.connect(self.edit_item)
        self.addTab(self.ratings, "Ratings")
        scholarship = QWidget()
        layout = QVBoxLayout(scholarship)
        layout.addWidget(QLabel("Selected player scholarship status"))
        self.status = QComboBox()
        self.status.setObjectName("scholarshipStatus")
        for value, label in ENUM_CHOICES["scholarship_status"].items():
            self.status.addItem(label, value)
        layout.addWidget(self.status)
        button = QPushButton("Apply scholarship status")
        button.clicked.connect(self.apply_status)
        layout.addWidget(button)
        note = QLabel(
            "Choose Scholarship or Walk-on, then save a roster copy. Legacy recruiting restrictions are not reproduced."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        self.addTab(scholarship, "Scholarship")
        self.setEnabled(False)

    def add(self, tree, label, value, key=None, slot=None):
        item = QTreeWidgetItem(tree, [label, str(value)])
        if key:
            item.setData(0, Qt.ItemDataRole.UserRole, (key, slot))
        else:
            item.setToolTip(1, "Read-only: no confirmed writer for this field")

    def show_player(self, row):
        self.loading = True
        self.details.clear()
        self.ratings.clear()
        self.player_index = row["index"] if row else None
        self.setEnabled(row is not None)
        if row:
            for key, label in [
                ("first_name", "First name"),
                ("last_name", "Last name"),
                ("jersey_number", "Number"),
                ("height_inches", "Height"),
                ("position_code", "Position"),
            ]:
                value = (
                    height_text(row[key])
                    if key == "height_inches"
                    else ENUM_CHOICES.get(key, {}).get(row[key], row[key])
                )
                self.add(self.details, label, value, key)
            for label, value in row["properties"].items():
                key = PROPERTY_FIELDS.get(label) or {
                    "Hand": "hand_code",
                    "Weight": "weight_lbs",
                    "Potential": "potential",
                }.get(label)
                options = PROPERTY_CHOICES.get(label, {})
                fallback = (
                    ("None" if value == 0 else f"Style {value}")
                    if any(k in label for k in ("Band", "Pad"))
                    else f"Unmapped option ({value})"
                    if options
                    else value
                )
                text = options.get(value, fallback)
                self.add(self.details, label, text, key)
            self.add(
                self.details,
                "Scholarship",
                ENUM_CHOICES["scholarship_status"][row["scholarship_status"]],
                "scholarship_status",
            )
            for slot, (label, value) in enumerate(
                zip(RATING_NAMES, row["attribute_ratings"])
            ):
                self.add(self.ratings, label, value, "attribute_ratings", slot)
            for slot, (label, value) in enumerate(
                zip(TENDENCY_NAMES, row["shot_tendencies"])
            ):
                self.add(
                    self.ratings, label + " tendency", value, "shot_tendencies", slot
                )
            self.status.setCurrentIndex(self.status.findData(row["scholarship_status"]))
        self.details.resizeColumnToContents(0)
        self.ratings.resizeColumnToContents(0)
        self.loading = False

    def apply(self, key, value, slot=None):
        if self.loading or self.player_index is None or self.owner.active:
            return
        try:
            self.owner.roster.edit("players", self.player_index, key, value, slot)
            self.owner.display_roster(self.owner.roster)
        except ValueError as error:
            QMessageBox.warning(self, "Player edit blocked", str(error))

    def apply_status(self):
        self.apply("scholarship_status", self.status.currentData())

    def edit_item(self, item, column):
        target = item.data(0, Qt.ItemDataRole.UserRole)
        if not target or self.player_index is None or self.owner.active:
            return
        key, slot = target
        row = self.owner.roster.rows["players"][self.player_index]
        if key in ENUM_CHOICES:
            options = dict(ENUM_CHOICES[key])
            if row[key] not in options:
                options[row[key]] = f"Unmapped option ({row[key]})"
            captions = list(options.values())
            labels = [
                label
                if captions.count(label) == 1
                else f"{label} (variant {chr(65 + captions[:i].count(label))})"
                for i, label in enumerate(captions)
            ]
            value, ok = QInputDialog.getItem(
                self,
                "Edit " + item.text(0),
                item.text(0),
                labels,
                max(0, list(options).index(row[key]) if row[key] in options else 0),
                False,
            )
            if ok:
                code = list(options)[labels.index(value)]
                if code != row[key]:
                    self.apply(key, code)
        elif key == "height_inches":
            value, ok = QInputDialog.getText(
                self, "Edit height", "Feet and inches", text=height_text(row[key])
            )
            if ok:
                try:
                    self.apply(key, height_inches(value))
                except ValueError as error:
                    QMessageBox.warning(self, "Height edit blocked", str(error))
        elif key in ("first_name", "last_name"):
            value, ok = QInputDialog.getText(
                self, "Edit " + item.text(0), "Same encoded name length", text=row[key]
            )
            if ok:
                self.apply(key, value)
        else:
            current = row[key][slot] if slot is not None else row[key]
            value, ok = QInputDialog.getInt(
                self,
                "Edit " + item.text(0),
                item.text(0),
                current,
                35 if key == "attribute_ratings" else 0,
                400 if key == "weight_lbs" else 99,
            )
            if ok:
                self.apply(key, value, slot)

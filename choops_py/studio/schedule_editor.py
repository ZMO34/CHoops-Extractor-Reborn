"""Season schedule editor: game list, single-game edits and conference rebuild."""

import datetime

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.errors import ToolError
from ..roster import schedule as backend

KEEP = -1  # spin-box value meaning "keep the stored games for this conference"


def team_choices(model):
    teams = model.rows['teams']
    conferences = {c['index']: c['abbreviation'].strip() for c in model.rows.get('conferences', [])}
    return sorted(
        ((f"{t['school_name']} ({conferences.get(t.get('conference_index'), 'None')})", t['index'])
         for t in teams if t.get('team_type_code') == backend.CURRENT_D1),
        key=lambda item: item[0].casefold())


class GameDialog(QDialog):
    def __init__(self, parent, model, game=None):
        super().__init__(parent)
        self.setWindowTitle('Edit game' if game else 'Add game')
        form = QFormLayout(self)
        date, minutes = (datetime.date(2008, 1, 5), backend.DEFAULT_MINUTES) if game is None else \
            (datetime.date.fromisoformat(game['date']), game['minutes'])
        self.date = QDateEdit(QDate(date.year, date.month, date.day))
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat('yyyy-MM-dd')
        self.time = QTimeEdit(QTime(minutes // 60, minutes % 60))
        self.time.setDisplayFormat('HH:mm')
        self.first, self.second = QComboBox(), QComboBox()
        for box, current in ((self.first, game and game['first']), (self.second, game and game['second'])):
            box.setEditable(True)
            box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            for label, index in team_choices(model):
                box.addItem(label, index)
            if current is not None:
                box.setCurrentIndex(box.findData(current))
        self.conference = QComboBox()
        self.conference.addItem('Automatic (same current conference)', None)
        self.conference.addItem('Conference game', True)
        self.conference.addItem('Non-conference game', False)
        if game is not None:
            self.conference.setCurrentIndex(1 if game['conference_game'] else 2)
        form.addRow('Date', self.date)
        form.addRow('Tip-off', self.time)
        form.addRow('Team 1 (stored first)', self.first)
        form.addRow('Team 2 (stored second)', self.second)
        form.addRow('Game type', self.conference)
        note = QLabel('Which stored team is home is not yet confirmed; the stored order is preserved.')
        note.setWordWrap(True)
        form.addRow(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        date, time = self.date.date(), self.time.time()
        return dict(date=datetime.date(date.year(), date.month(), date.day()),
                    minutes=time.hour() * 60 + time.minute(),
                    first=self.first.currentData(), second=self.second.currentData(),
                    conference_game=self.conference.currentData())


class RebuildDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle('Rebuild conference games')
        self.resize(720, 640)
        layout = QVBoxLayout(self)
        intro = QLabel(
            'Rebuilds conference games from current conference membership. Conference games between '
            'teams that are no longer conference-mates are removed, games between current conference-mates '
            'count toward the target, and missing round-robin games are placed on existing conference dates '
            'without double-booking. Conferences set to "Keep" are left as stored. Non-conference games are kept.')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.drop_former = QCheckBox('Remove conference games between former conference-mates')
        self.drop_former.setChecked(True)
        layout.addWidget(self.drop_former)
        _, plan = backend.plan_conference_rebuild(model)
        groups = backend.conference_groups(model)
        names = {c['index']: c['conference_name'].strip() for c in model.rows['conferences']}
        holder, form = QWidget(), QFormLayout()
        holder.setLayout(form)
        self.targets = {}
        for conf, members in sorted(groups.items()):
            box = QSpinBox()
            box.setRange(KEEP, 40)
            box.setSpecialValueText('Keep stored games')
            target = plan['conferences'][conf]['target_games']
            box.setValue(KEEP if target is None else target)
            box.setToolTip(f'Double round robin = {2 * (len(members) - 1)} games per team')
            self.targets[conf] = box
            form.addRow(f'{names[conf]} — {len(members)} teams', box)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        layout.addWidget(scroll, 1)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(170)
        layout.addWidget(self.preview)
        row = QHBoxLayout()
        preview = QPushButton('Preview')
        preview.clicked.connect(self.show_preview)
        row.addWidget(preview)
        row.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Rebuild')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        row.addWidget(buttons)
        layout.addLayout(row)
        self.show_preview()

    def chosen(self):
        return {conf: box.value() for conf, box in self.targets.items() if box.value() != KEEP}

    def options(self):
        return dict(targets=self.chosen(), drop_former=self.drop_former.isChecked())

    def show_preview(self):
        try:
            _, plan = backend.plan_conference_rebuild(self.model, **self.options(), keep_unlisted=True)
        except ToolError as error:
            return self.preview.setPlainText(str(error))
        self.preview.setPlainText(describe(plan))


def describe(plan):
    lines = [f"{plan['total']:,} games of {plan['capacity']:,} slots"
             + (' — OVER CAPACITY, lower some targets' if plan['total'] > plan['capacity'] else ''),
             f"Removed {plan['dropped_former_conference']} former-conference games, trimmed "
             f"{plan['trimmed_extra']} extra meetings, added {plan['added']} games, re-flagged {plan['reflagged']}.",
             ]
    if plan['unplaced']:
        lines.append(f"{plan['unplaced']} games could not be placed on a free conference date.")
    if plan['low_total_teams']:
        lines.append('Few total games: ' + ', '.join(f'{k} {v}' for k, v in plan['low_total_teams']))
    if plan['high_total_teams']:
        lines.append('Many total games: ' + ', '.join(f'{k} {v}' for k, v in plan['high_total_teams']))
    return '\n'.join(lines)


def describe_balance(plan):
    lines = [f"{plan['total']:,} games of {plan['capacity']:,} slots"
             + (' — OVER CAPACITY' if plan['total'] > plan['capacity'] else ''),
             f"Removed {plan['removed']} and added {plan['added']} non-conference games "
             f"for a {plan['minimum']}–{plan['maximum']} game season."]
    if plan['still_short']:
        lines.append('Still short: ' + ', '.join(f'{k} {v}' for k, v in plan['still_short']))
    if plan['still_long']:
        lines.append('Still long (conference games only): '
                     + ', '.join(f'{k} {v}' for k, v in plan['still_long']))
    return '\n'.join(lines)


class BalanceDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle('Balance game totals')
        layout = QVBoxLayout(self)
        intro = QLabel('Removes non-conference games from teams above the maximum (against the busiest '
                       'opponents first) and adds non-conference games for teams below the minimum on existing '
                       'non-conference dates. Conference games are never removed.')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        form = QFormLayout()
        self.minimum, self.maximum = QSpinBox(), QSpinBox()
        for box, value in ((self.minimum, backend.LOW_TOTAL + 2), (self.maximum, backend.HIGH_TOTAL - 1)):
            box.setRange(0, 60)
            box.setValue(value)
            box.valueChanged.connect(self.show_preview)
            form.addRow('Minimum games' if box is self.minimum else 'Maximum games', box)
        layout.addLayout(form)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Balance')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.show_preview()

    def limits(self):
        return self.minimum.value(), self.maximum.value()

    def show_preview(self):
        try:
            _, plan = backend.plan_balance(self.model, *self.limits())
        except ToolError as error:
            return self.preview.setPlainText(str(error))
        self.preview.setPlainText(describe_balance(plan))


class ScheduleEditor(QDialog):
    def __init__(self, owner):
        super().__init__(owner)
        from .app import table

        self.owner = owner
        self.model = owner.roster
        self.setWindowTitle('Season schedule')
        self.resize(1100, 720)
        layout = QVBoxLayout(self)
        notice = QLabel(
            'This is the season schedule stored in the roster. New Legacy-mode saves copy it, so edit it '
            'here and save the roster before starting a Legacy. Moving a school to another conference does '
            'not change these games until you rebuild conference games.')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        filters = QHBoxLayout()
        self.team = QComboBox()
        self.team.addItem('All teams', None)
        for label, index in team_choices(self.model):
            self.team.addItem(label, index)
        self.team.currentIndexChanged.connect(self.populate)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search dates, schools…')
        self.search.textChanged.connect(self.populate)
        self.problems = QCheckBox('Only conference mismatches')
        self.problems.toggled.connect(self.populate)
        filters.addWidget(QLabel('Team'))
        filters.addWidget(self.team, 1)
        filters.addWidget(self.search, 1)
        filters.addWidget(self.problems)
        layout.addLayout(filters)
        self.view = table()
        self.view.doubleClicked.connect(lambda *_: self.edit_game())
        layout.addWidget(self.view, 1)
        buttons = QHBoxLayout()
        for text, action in (('Add game…', self.add_game), ('Edit game…', self.edit_game),
                             ('Delete selected', self.delete_games),
                             ('Rebuild conference games…', self.rebuild),
                             ('Balance game totals…', self.balance), ('Season year…', self.season_year),
                             ('Undo', self.undo)):
            button = QPushButton(text)
            button.clicked.connect(action)
            buttons.addWidget(button)
        buttons.addStretch()
        close = QPushButton('Close')
        close.clicked.connect(self.accept)
        buttons.addWidget(close)
        layout.addLayout(buttons)
        self.populate()

    def busy(self):
        if self.owner.active or self.owner.roster is not self.model:
            QMessageBox.information(self, 'Schedule', 'Wait for the current job or reopen the schedule editor.')
            return True
        return False

    def populate(self):
        from .app import set_rows

        rows = backend.Schedule(self.model).rows()
        info = backend.report(self.model)
        start = backend.season_start_year(self.model) if rows else None
        self.status.setText(
            (f"Season {start}–{str(start + 1)[-2:]} • " if start else '') +
            f"{info['games']:,} games • {info['free_slots']:,} free slots • "
            f"{info['conference_flag_mismatches']} conference games between non-members • "
            f"{info['intra_conference_unflagged']} unflagged games between conference-mates • "
            f"{len(info['double_booked'])} double-booked team dates")
        team = self.team.currentData()
        if self.problems.isChecked():
            rows = [r for r in rows if r['conference_game'] != r['same_conference']]
        rows = [dict(r, school_indices=[r['first'], r['second']],
                     conference_text='Yes' if r['conference_game'] else 'No',
                     current_text='Yes' if r['same_conference'] else 'No') for r in rows]
        columns = [('date', 'Date'), ('time', 'Tip-off'), ('first_name', 'Team 1'), ('second_name', 'Team 2'),
                   ('conference_text', 'Conference game'), ('current_text', 'Same conference now')]
        proxy = set_rows(self.view, rows, columns, self.search.text())
        proxy.choose_school(team)

    def selected(self):
        from .app import selected

        return selected(self.view)

    def apply(self, title, operation):
        try:
            result = operation()
        except ToolError as error:
            QMessageBox.warning(self, title, str(error))
            return None
        self.owner.display_roster(self.model)
        self.populate()
        return result

    def add_game(self):
        if self.busy():
            return
        dialog = GameDialog(self, self.model)
        team = self.team.currentData()
        if team is not None:
            dialog.first.setCurrentIndex(dialog.first.findData(team))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply('Add game', lambda: backend.add_game(self.model, **dialog.values()))

    def edit_game(self):
        if self.busy():
            return
        rows = self.selected()
        if len(rows) != 1:
            return QMessageBox.information(self, 'Edit game', 'Select exactly one game.')
        dialog = GameDialog(self, self.model, rows[0])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply('Edit game', lambda: backend.edit_game(self.model, rows[0]['key'], **dialog.values()))

    def delete_games(self):
        if self.busy():
            return
        rows = self.selected()
        if not rows:
            return
        answer = QMessageBox.question(self, 'Delete games', f'Delete {len(rows)} selected game(s)?')
        if answer == QMessageBox.StandardButton.Yes:
            self.apply('Delete games', lambda: backend.delete_games(self.model, [r['key'] for r in rows]))

    def rebuild(self):
        if self.busy():
            return
        try:
            dialog = RebuildDialog(self, self.model)
        except ToolError as error:
            return QMessageBox.warning(self, 'Rebuild conference games', str(error))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            plan = self.apply('Rebuild conference games',
                              lambda: backend.rebuild_conference_games(self.model, **dialog.options(), keep_unlisted=True))
            if plan:
                QMessageBox.information(self, 'Conference games rebuilt',
                                        describe(plan) + '\n\nSave a roster copy to keep these changes.')

    def balance(self):
        if self.busy():
            return
        dialog = BalanceDialog(self, self.model)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            plan = self.apply('Balance game totals', lambda: backend.balance_totals(self.model, *dialog.limits()))
            if plan:
                QMessageBox.information(self, 'Game totals balanced',
                                        describe_balance(plan) + '\n\nSave a roster copy to keep these changes.')

    def season_year(self):
        if self.busy():
            return
        from PySide6.QtWidgets import QInputDialog
        current = backend.season_start_year(self.model)
        year, ok = QInputDialog.getInt(
            self, 'Season year',
            'Season starts in (month and day are kept; Feb 29 games move when needed).\n'
            'Use the year your game runs Legacy in, e.g. 2026 for a 2026-27 executable patch.',
            current, 2000, 2126)
        if ok and year != current:
            plan = self.apply('Season year', lambda: backend.set_season_year(self.model, year))
            if plan:
                QMessageBox.information(self, 'Season year changed',
                                        f"Moved {plan['games']:,} games from {plan['from_year']} to {plan['to_year']}; "
                                        f"{plan['leap_day_moves']} Feb 29 games moved.\n\n"
                                        'Save a roster copy to keep these changes.')

    def undo(self):
        if self.busy() or not self.model.history:
            return
        self.model.undo()
        self.owner.display_roster(self.model)
        self.populate()


def open_schedule_editor(owner):
    if not owner.roster or owner.active:
        return owner.log('Load a College Hoops roster first.')
    try:
        backend.Schedule(owner.roster)
    except ToolError as error:
        return QMessageBox.warning(owner, 'Season schedule', str(error))
    ScheduleEditor(owner).exec()

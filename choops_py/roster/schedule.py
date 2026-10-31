"""Season schedule table: parse, single-game edits and conference rebuilds.

Layout evidence is in docs/SCHEDULE_EDITOR.md. Header +0x30 holds the slot
count and +0x34 a relative pointer (bias 1) to 20-byte game records:

    +0x00 u32 key   year<<25 | month0<<21 | day<<16 | minutes<<5 | index
    +0x04 u16 first team index      +0x06 u16 second team index
    +0x08 u32 flags (bit 27 = conference game; other bits preserved)
    +0x0C u16 site (0xFFFF in stock rows)   +0x0E u16 / +0x10 u32 preserved

Dated games are stored first, sorted by unique key, followed by explicit empty
markers (teams 0x7FFF). Trailing all-zero records are never touched, so the
writable capacity is dated games plus empty markers. Which listed team is home
is unconfirmed; the editor keeps the stored order and calls them team 1/2.
Conference games are copied into Legacy mode from this table, so realignment
alone leaves the old conference pairings in place.
"""
import datetime
import struct
from collections import Counter, defaultdict

from ..core.errors import ToolError

HEADER_FIELD = 0x30
POINTER_BIAS = 1
RECORD_SIZE = 20
SLOT_LIMIT = 8192
EMPTY_TEAM = 0x7FFF
CONFERENCE_FLAG = 0x08000000
EMPTY_RECORD = struct.pack('>IHHIHHI', 0, EMPTY_TEAM, EMPTY_TEAM, 0, 0xFFFF, 0, 0)
DEFAULT_MINUTES = 19 * 60
# Fallback tip-off times when 32 games already share a date/time key.
SPARE_MINUTES = (1170, 1080, 1200, 1230, 1260, 1110, 960, 840, 780, 720, 900, 1020)
SPECIAL_CONFERENCE_TYPE = 4  # NCAA / Top 25 / Classics / Created / ABL groupings
CURRENT_D1 = 0
# Stock regular seasons run 23-31 games; outside this range is reported.
LOW_TOTAL, HIGH_TOTAL = 22, 32


def encode_key(date, minutes, index=0):
    if not 2000 <= date.year < 2128:
        raise ToolError('schedule_date_out_of_range', 'Year must be 2000–2127')
    if not 0 <= minutes < 24 * 60:
        raise ToolError('schedule_time_out_of_range', 'Time must be 00:00–23:59')
    if not 0 <= index < 32:
        raise ToolError('schedule_time_slot_full', 'Too many games share this date and time')
    return ((date.year - 2000) << 25 | (date.month - 1) << 21 | date.day << 16
            | minutes << 5 | index)


def decode_key(key):
    year, month, day = 2000 + (key >> 25), ((key >> 21) & 15) + 1, (key >> 16) & 31
    try:
        date = datetime.date(year, month, day)
    except ValueError:
        date = None
    return date, (key >> 5) & 0x7FF, key & 31


def locate(data):
    """Return (start, slot_count) or None when the roster has no game table."""
    if len(data) < HEADER_FIELD + 8:
        return None
    count = struct.unpack_from('>I', data, HEADER_FIELD)[0]
    delta = struct.unpack_from('>i', data, HEADER_FIELD + 4)[0]
    start = HEADER_FIELD + 4 + delta - POINTER_BIAS
    if not 0 < count <= SLOT_LIMIT or start <= HEADER_FIELD or start + count * RECORD_SIZE > len(data):
        return None
    return start, count


class Schedule:
    """Parsed view of the table. Writers rebuild only the dated/empty prefix."""

    def __init__(self, model):
        self.model = model
        found = locate(model.data)
        if found is None:
            raise ToolError('schedule_table_missing', 'This roster has no recognized season schedule table')
        self.start, self.slots = found
        team_count = len(model.rows.get('teams', []))
        self.games = []
        self.capacity = 0
        sentinel = False
        for slot in range(self.slots):
            raw = bytes(model.data[self.start + slot * RECORD_SIZE:self.start + (slot + 1) * RECORD_SIZE])
            key, first, second, flags, site, extra1, extra2 = struct.unpack('>IHHIHHI', raw)
            if raw == EMPTY_RECORD:
                sentinel = True
                self.capacity = slot + 1
                continue
            if not any(raw):
                break  # untouched tail; never written
            if sentinel:
                raise ToolError('schedule_layout_unsupported', 'Dated game found after empty slots; no changes are safe')
            date, minutes, _ = decode_key(key)
            if date is None or not (first < team_count and second < team_count) or first == second:
                raise ToolError('schedule_layout_unsupported', f'Unrecognized game record in slot {slot}')
            self.games.append(dict(key=key, first=first, second=second, flags=flags, site=site,
                                   extra1=extra1, extra2=extra2))
            self.capacity = slot + 1
        keys = [g['key'] for g in self.games]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            raise ToolError('schedule_layout_unsupported', 'Game keys are not sorted and unique')

    # ---- presentation -------------------------------------------------
    def rows(self):
        teams = self.model.rows['teams']
        out = []
        for game in self.games:
            date, minutes, index = decode_key(game['key'])
            a, b = teams[game['first']], teams[game['second']]
            out.append(dict(game, date=date.isoformat(), time=f'{minutes // 60:02d}:{minutes % 60:02d}',
                            minutes=minutes, key_index=index,
                            first_name=a['school_name'], second_name=b['school_name'],
                            conference_game=bool(game['flags'] & CONFERENCE_FLAG),
                            same_conference=same_conference(self.model, game['first'], game['second'])))
        return out

    # ---- writer --------------------------------------------------------
    def write(self, games):
        games = sorted(games, key=lambda g: g['key'])
        if len({g['key'] for g in games}) != len(games):
            raise ToolError('schedule_duplicate_key', 'Two games share the same date/time slot')
        if len(games) > self.capacity:
            raise ToolError('schedule_full', f'{len(games)} games exceed the table capacity of {self.capacity}; '
                            'lower conference game targets or delete games')
        team_count = len(self.model.rows['teams'])
        for slot in range(self.capacity):
            offset = self.start + slot * RECORD_SIZE
            if slot < len(games):
                g = games[slot]
                if not (0 <= g['first'] < team_count and 0 <= g['second'] < team_count) or g['first'] == g['second']:
                    raise ToolError('schedule_invalid_team', 'Choose two different existing teams')
                struct.pack_into('>IHHIHHI', self.model.data, offset, g['key'], g['first'], g['second'],
                                 g['flags'], g['site'], g['extra1'], g['extra2'])
            else:
                self.model.data[offset:offset + RECORD_SIZE] = EMPTY_RECORD
        self.games = games


def same_conference(model, a, b):
    teams = model.rows['teams']
    ca, cb = teams[a].get('conference_index'), teams[b].get('conference_index')
    return ca is not None and ca == cb


def schedule(model):
    return Schedule(model)


def _transaction(model, record, operation):
    before = bytes(model.data)
    edits, history, redo = list(model.edits), list(model.history), list(model.redo_history)
    try:
        operation()
        model.reload()
        if not model.validate()['valid']:
            raise ToolError('roster_validation_failed', 'Schedule edit failed roster validation')
        Schedule(model)  # reparse the written table
        untouched = _table_range(model)
        if before[:untouched[0]] != bytes(model.data[:untouched[0]]) or before[untouched[1]:] != bytes(model.data[untouched[1]:]):
            raise ToolError('schedule_outer_bytes_changed', 'Bytes outside the schedule table changed')
    except Exception:
        model.data = bytearray(before)
        model.edits, model.history, model.redo_history = edits, history, redo
        model.reload()
        raise
    if bytes(model.data) != before:
        model.history = history + [(before, edits)]
        model.redo_history = []
        model.edits = edits + [record]


def _table_range(model):
    start, slots = locate(model.data)
    return start, start + slots * RECORD_SIZE


def _free_key(used, date, minutes):
    for option in (minutes, *[m for m in SPARE_MINUTES if m != minutes]):
        for index in range(32):
            key = encode_key(date, option, index)
            if key not in used:
                return key
    raise ToolError('schedule_time_slot_full', f'No free time slot on {date.isoformat()}')


def _game(model, values, used):
    date = values['date']
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except ValueError as error:
            raise ToolError('schedule_invalid_date', 'Use YYYY-MM-DD') from error
    minutes = model.integer(values.get('minutes', DEFAULT_MINUTES))
    first, second = model.integer(values['first']), model.integer(values['second'])
    flags = model.integer(values.get('flags', 0))
    conference = values.get('conference_game')
    if conference is None:
        conference = first < len(model.rows['teams']) and second < len(model.rows['teams']) and same_conference(model, first, second)
    flags = flags | CONFERENCE_FLAG if conference else flags & ~CONFERENCE_FLAG
    return dict(key=_free_key(used, date, minutes), first=first, second=second, flags=flags,
                site=model.integer(values.get('site', 0xFFFF)), extra1=model.integer(values.get('extra1', 0)),
                extra2=model.integer(values.get('extra2', 0)))


def add_game(model, **values):
    table = Schedule(model)
    def apply():
        table.write(table.games + [_game(model, values, {g['key'] for g in table.games})])
    _transaction(model, dict(table='schedule', field='add_game', value={k: str(v) for k, v in values.items()}), apply)


def _find(table, key):
    matches = [g for g in table.games if g['key'] == key]
    if len(matches) != 1:
        raise ToolError('schedule_game_missing', 'The selected game no longer exists')
    return matches[0]


def edit_game(model, key, **values):
    table = Schedule(model)
    old = _find(table, key)
    def apply():
        rest = [g for g in table.games if g is not old]
        merged = dict(date=decode_key(old['key'])[0], minutes=decode_key(old['key'])[1], first=old['first'],
                      second=old['second'], flags=old['flags'], site=old['site'], extra1=old['extra1'],
                      extra2=old['extra2'], conference_game=bool(old['flags'] & CONFERENCE_FLAG))
        merged.update(values)
        table.write(rest + [_game(model, merged, {g['key'] for g in rest})])
    _transaction(model, dict(table='schedule', field='edit_game', old=key, value={k: str(v) for k, v in values.items()}), apply)


def delete_games(model, keys):
    table = Schedule(model)
    keys = set(keys)
    for key in keys:
        _find(table, key)
    def apply():
        table.write([g for g in table.games if g['key'] not in keys])
    _transaction(model, dict(table='schedule', field='delete_games', value=sorted(keys)), apply)


# ---- validation -------------------------------------------------------
def report(model):
    table = Schedule(model)
    teams = model.rows['teams']
    per_team = defaultdict(lambda: dict(games=0, conference_games=0, first=0, second=0))
    days = Counter()
    mismatched, unflagged = [], []
    for g in table.games:
        date = decode_key(g['key'])[0]
        for side, team in (('first', g['first']), ('second', g['second'])):
            per_team[team]['games'] += 1
            per_team[team][side] += 1
            if g['flags'] & CONFERENCE_FLAG:
                per_team[team]['conference_games'] += 1
            days[(team, date)] += 1
        same = same_conference(model, g['first'], g['second'])
        if g['flags'] & CONFERENCE_FLAG and not same:
            mismatched.append(g['key'])
        elif same and not g['flags'] & CONFERENCE_FLAG:
            unflagged.append(g['key'])
    double = sorted({(teams[t]['school_name'], d.isoformat()) for (t, d), n in days.items() if n > 1})
    return dict(games=len(table.games), capacity=table.capacity, free_slots=table.capacity - len(table.games),
                conference_flag_mismatches=len(mismatched), mismatched_keys=mismatched,
                intra_conference_unflagged=len(unflagged), unflagged_keys=unflagged,
                double_booked=double,
                teams=[dict(index=t, school_name=teams[t]['school_name'], **v) for t, v in sorted(per_team.items())])


# ---- conference rebuild ----------------------------------------------
def conference_groups(model):
    """D1 conferences and their current D1 members (reciprocal lists)."""
    teams = model.rows['teams']
    groups = {}
    for conf in model.rows.get('conferences', []):
        if conf.get('conference_type') == SPECIAL_CONFERENCE_TYPE:
            continue
        members = [t for t in conf.get('team_indices', []) if teams[t].get('team_type_code') == CURRENT_D1]
        if len(members) >= 2:
            groups[conf['index']] = sorted(members)
    return groups


def default_conference_games(size):
    if size < 2:
        return 0
    if size <= 10:
        return 2 * (size - 1)
    return min(20, max(size - 1, 18))


def _rounds(members):
    """Circle-method double round robin; odd sizes get a bye each round."""
    teams = list(members) + ([None] if len(members) % 2 else [])
    n = len(teams)
    first_leg = []
    for r in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a, b = teams[i], teams[n - 1 - i]
            if a is not None and b is not None:
                pairs.append((a, b) if (r + i) % 2 else (b, a))
        first_leg.append(pairs)
        teams = [teams[0], teams[-1], *teams[1:-1]]
    return first_leg + [[(b, a) for a, b in pairs] for pairs in first_leg]


def _conference_days(games, start_month_day=(12, 28)):
    counts = Counter(decode_key(g['key'])[0] for g in games if g['flags'] & CONFERENCE_FLAG)
    days = sorted(d for d, n in counts.items() if n >= 3) or sorted(counts)
    if not days:
        raise ToolError('schedule_no_conference_days', 'No existing conference game dates to schedule against')
    late = [d for d in days if (d.month, d.day) >= start_month_day or d.month < 6]
    return late if len(late) >= 20 else days


def plan_conference_rebuild(model, targets=None, drop_former=True, keep_unlisted=False):
    """Return (new_games, summary) without writing.

    targets maps conference index -> conference games per team. Unlisted
    changed conferences get default_conference_games unless keep_unlisted.
    """
    table = Schedule(model)
    groups = conference_groups(model)
    member_of = {t: c for c, members in groups.items() for t in members}
    days = _conference_days(table.games)

    kept, dropped, reflagged = [], 0, 0
    changed = set()  # conferences whose stored pairings no longer match membership
    for g in table.games:
        g = dict(g)
        same = member_of.get(g['first']) is not None and member_of.get(g['first']) == member_of.get(g['second'])
        was = bool(g['flags'] & CONFERENCE_FLAG)
        if same != was:
            changed.update(member_of[t] for t in (g['first'], g['second']) if t in member_of)
        if was and not same and drop_former:
            dropped += 1
            continue
        if same != was:
            reflagged += 1
        g['flags'] = g['flags'] | CONFERENCE_FLAG if same else g['flags'] & ~CONFERENCE_FLAG
        kept.append(g)
    # Untouched conferences keep their stock schedule unless a target is given.
    defaults = {} if keep_unlisted else {c: default_conference_games(len(groups[c])) for c in changed if c in groups}
    targets = defaults | {c: t for c, t in dict(targets or {}).items() if c in groups}

    added, unplaced, trimmed = [], [], 0
    summary = {}
    for conf, members in sorted(groups.items()):
        if conf not in targets:
            summary[conf] = dict(members=len(members), target_games=None, added=0, trimmed=0, unchanged=True)
            continue
        target = model.integer(targets[conf])
        if target < 0:
            raise ToolError('schedule_invalid_target', 'Conference game targets cannot be negative')
        # Meetings from a circle-method double round robin, cut at the target.
        meetings, limit = [], len(members) * target // 2
        cycle = _rounds(members)
        repeats = -(-target // max(1, 2 * (len(members) - 1))) if target else 0
        for r, pairs in enumerate(cycle * repeats):
            meetings += [(r, a, b) for a, b in pairs[:limit - len(meetings)]]
        remaining = Counter(frozenset((a, b)) for _, a, b in meetings)
        # Stored intra-conference games satisfy wanted meetings first.
        planned, extras, kept_count = Counter(), [], 0
        for g in [g for g in kept if g['flags'] & CONFERENCE_FLAG and g['first'] in members and g['second'] in members]:
            pair = frozenset((g['first'], g['second']))
            if remaining[pair]:
                remaining[pair] -= 1
                planned.update(pair)
                kept_count += 1
            else:
                extras.append(g)
        pending = []
        for r, a, b in meetings:
            pair = frozenset((a, b))
            if remaining[pair]:
                remaining[pair] -= 1
                planned.update(pair)
                pending.append((r, a, b))
        # Extra stored meetings stay only while both teams are under target.
        conf_trimmed = 0
        for g in extras:
            if planned[g['first']] < target and planned[g['second']] < target:
                planned.update((g['first'], g['second']))
                kept_count += 1
            else:
                kept.remove(g)
                conf_trimmed += 1
        trimmed += conf_trimmed
        summary[conf] = dict(members=len(members), target_games=target, kept_games=kept_count, added=0,
                             trimmed=conf_trimmed, unchanged=False, pending=pending)

    busy = defaultdict(set)
    for g in kept:
        date = decode_key(g['key'])[0]
        busy[g['first']].add(date)
        busy[g['second']].add(date)
    used = {g['key'] for g in kept}
    for conf, info in summary.items():
        pending = info.pop('pending', [])
        if not pending:
            continue
        span = max(1, max(r for r, _, _ in pending))
        for r, a, b in pending:
            ideal = round(r * (len(days) - 1) / span)
            date = _pick_day(days, ideal, busy[a], busy[b])
            if date is None:
                unplaced.append((a, b))
                continue
            key = _free_key(used, date, DEFAULT_MINUTES)
            used.add(key)
            busy[a].add(date)
            busy[b].add(date)
            added.append(dict(key=key, first=a, second=b, flags=CONFERENCE_FLAG, site=0xFFFF, extra1=0, extra2=0))
            info['added'] += 1
    totals = Counter()
    for g in kept + added:
        totals.update((g['first'], g['second']))
    names = model.rows['teams']
    d1 = [t for t in member_of]
    result = dict(kept=len(kept), dropped_former_conference=dropped, reflagged=reflagged, trimmed_extra=trimmed,
                  added=len(added), unplaced=len(unplaced), total=len(kept) + len(added),
                  capacity=table.capacity, conferences=summary,
                  low_total_teams=[[names[t]['school_name'], totals[t]] for t in d1 if totals[t] < LOW_TOTAL],
                  high_total_teams=[[names[t]['school_name'], totals[t]] for t in d1 if totals[t] > HIGH_TOTAL])
    return kept + added, result


def _pick_day(days, ideal, busy_a, busy_b):
    def rested(d, busy):
        return not any(d + datetime.timedelta(days=k) in busy for k in (-1, 0, 1))
    order = sorted(range(len(days)), key=lambda i: (abs(i - ideal), i))
    for strict in (True, False):
        for i in order:
            d = days[i]
            if strict and rested(d, busy_a) and rested(d, busy_b):
                return d
            if not strict and d not in busy_a and d not in busy_b:
                return d
    return None


def rebuild_conference_games(model, targets=None, drop_former=True, keep_unlisted=False):
    table = Schedule(model)
    games, summary = plan_conference_rebuild(model, targets, drop_former, keep_unlisted)
    if summary['total'] > table.capacity:
        raise ToolError('schedule_full', f"Rebuilt schedule needs {summary['total']} games but the table holds "
                        f"{table.capacity}; lower conference game targets")
    _transaction(model, dict(table='schedule', field='rebuild_conference_games',
                             value=dict(targets=dict(targets or {}), drop_former=drop_former, keep_unlisted=keep_unlisted)),
                 lambda: table.write(games))
    return summary


# ---- game-total balancing ---------------------------------------------
def _nonconference_days(games):
    counts = Counter(decode_key(g['key'])[0] for g in games if not g['flags'] & CONFERENCE_FLAG)
    return sorted(d for d, n in counts.items() if n >= 3) or sorted(counts)


def plan_balance(model, minimum=LOW_TOTAL + 2, maximum=HIGH_TOTAL - 1):
    """Trim/add non-conference games so current D1 teams land in [minimum, maximum].

    Conference games are never removed. Removals take the overloaded team's
    non-conference games against the busiest opponents, latest first. Additions
    pair short-schedule teams that are not conference-mates and have not met,
    on existing non-conference dates without double-booking.
    """
    minimum, maximum = model.integer(minimum), model.integer(maximum)
    if not 0 <= minimum <= maximum:
        raise ToolError('schedule_invalid_target', 'Minimum games must not exceed maximum games')
    table = Schedule(model)
    teams = model.rows['teams']
    d1 = [t['index'] for t in teams if t.get('team_type_code') == CURRENT_D1]
    games = [dict(g) for g in table.games]
    totals = Counter()
    for g in games:
        totals.update((g['first'], g['second']))

    removed = 0
    for team in sorted(d1, key=lambda t: -totals[t]):
        while totals[team] > maximum:
            options = [g for g in games if team in (g['first'], g['second']) and not g['flags'] & CONFERENCE_FLAG]
            if not options:
                break
            other = lambda g: g['second'] if g['first'] == team else g['first']
            victim = max(options, key=lambda g: (totals[other(g)], g['key']))
            games.remove(victim)
            totals.subtract((victim['first'], victim['second']))
            removed += 1

    days = _nonconference_days(games)
    busy = defaultdict(set)
    met = Counter()
    for g in games:
        date = decode_key(g['key'])[0]
        busy[g['first']].add(date)
        busy[g['second']].add(date)
        met[frozenset((g['first'], g['second']))] += 1
    used = {g['key'] for g in games}
    added, stuck = 0, set()
    while True:
        short = sorted((t for t in d1 if totals[t] < minimum and t not in stuck), key=lambda t: (totals[t], t))
        if not short:
            break
        team = short[0]
        pool = [t for t in short[1:]] + sorted((t for t in d1 if minimum <= totals[t] < maximum),
                                               key=lambda t: (totals[t], t))
        placed = False
        for opponent in pool:
            if opponent == team or same_conference(model, team, opponent) or met[frozenset((team, opponent))]:
                continue
            date = _pick_day(days, len(days) // 2, busy[team], busy[opponent])
            if date is None:
                continue
            key = _free_key(used, date, DEFAULT_MINUTES)
            used.add(key)
            busy[team].add(date)
            busy[opponent].add(date)
            met[frozenset((team, opponent))] += 1
            first, second = (team, opponent) if added % 2 else (opponent, team)
            games.append(dict(key=key, first=first, second=second, flags=0, site=0xFFFF, extra1=0, extra2=0))
            totals.update((team, opponent))
            added += 1
            placed = True
            break
        if not placed:
            stuck.add(team)
    summary = dict(removed=removed, added=added, total=len(games), capacity=table.capacity,
                   minimum=minimum, maximum=maximum,
                   still_short=[[teams[t]['school_name'], totals[t]] for t in d1 if totals[t] < minimum],
                   still_long=[[teams[t]['school_name'], totals[t]] for t in d1 if totals[t] > maximum])
    return games, summary


def balance_totals(model, minimum=LOW_TOTAL + 2, maximum=HIGH_TOTAL - 1):
    table = Schedule(model)
    games, summary = plan_balance(model, minimum, maximum)
    if summary['total'] > table.capacity:
        raise ToolError('schedule_full', f"Balanced schedule needs {summary['total']} games but the table holds "
                        f"{table.capacity}; raise the minimum less or lower the maximum")
    _transaction(model, dict(table='schedule', field='balance_totals', value=dict(minimum=minimum, maximum=maximum)),
                 lambda: table.write(games))
    return summary


def rebuild_file(source, output, targets=None, drop_former=True, balance=None, season_year=None, rebuild=True):
    """CLI: rebuild conference games, balance totals and/or set the season year in a copy."""
    from .editor_model import EditorModel
    from .workflow import save_model
    model = EditorModel.open(source)
    result = dict(rebuild=rebuild_conference_games(model, targets, drop_former)) if rebuild else {}
    if balance:
        result['balance'] = balance_totals(model, *balance)
    if season_year is not None:
        result['season_year'] = set_season_year(model, season_year)
    result['report'] = {k: v for k, v in report(model).items() if not k.endswith('_keys') and k != 'teams'}
    result['save'] = save_model(model, output)
    return result


def parse_targets(model, values):
    """CLI 'CONF=GAMES' entries; CONF is an index or abbreviation/name."""
    targets = {}
    for value in values or ():
        name, sep, games = value.partition('=')
        if not sep:
            raise ToolError('schedule_invalid_target', f'Expected CONFERENCE=GAMES, got {value!r}')
        matches = [c['index'] for c in model.rows['conferences']
                   if name.strip().casefold() in (str(c['index']), c['abbreviation'].strip().casefold(),
                                                  c['conference_name'].strip().casefold())]
        if len(matches) != 1:
            raise ToolError('schedule_invalid_target', f'No unique conference named {name!r}')
        targets[matches[0]] = model.integer(games)
    return targets


def parse_balance(value):
    if not value:
        return None
    low, sep, high = value.partition(':')
    try:
        return int(low), int(high)
    except ValueError as error:
        raise ToolError('schedule_invalid_target', 'Use --balance MIN:MAX, e.g. 24:31') from error


# ---- season year ------------------------------------------------------
def season_start_year(model):
    """Calendar year of the earliest stored game (the season's opening year)."""
    table = Schedule(model)
    if not table.games:
        raise ToolError('schedule_empty', 'The schedule has no games')
    return decode_key(table.games[0]['key'])[0].year


def plan_season_year(model, start_year):
    """Move every game to the season starting in start_year, keeping month/day.

    Patched executables run Legacy in a later season and generate their own
    tournament games with the same month/day in that season, so stored games
    must use the same years. Feb 29 games move to Feb 28 or Mar 1 when the
    target year is not a leap year, avoiding double-booking where possible.
    """
    start_year = model.integer(start_year)
    table = Schedule(model)
    delta = start_year - season_start_year(model)
    games = [dict(g) for g in table.games]
    moved = []
    busy = defaultdict(set)
    targets = []
    for g in games:
        date, minutes, _ = decode_key(g['key'])
        year = date.year + delta
        try:
            target = date.replace(year=year)
        except ValueError:  # Feb 29 in a non-leap target year
            target = None
        targets.append((target, date, minutes))
        if target:
            busy[g['first']].add(target)
            busy[g['second']].add(target)
    used = set()
    for g, (target, date, minutes) in zip(games, targets):
        if target is None:
            options = [datetime.date(date.year + delta, 2, 28), datetime.date(date.year + delta, 3, 1)]
            free = [d for d in options if d not in busy[g['first']] and d not in busy[g['second']]]
            target = (free or options)[0]
            busy[g['first']].add(target)
            busy[g['second']].add(target)
            moved.append(target.isoformat())
        g['key'] = _free_key(used, target, minutes)
        used.add(g['key'])
    return games, dict(from_year=start_year - delta, to_year=start_year, shifted_years=delta,
                       leap_day_moves=len(moved), games=len(games))


def set_season_year(model, start_year):
    table = Schedule(model)
    games, summary = plan_season_year(model, start_year)
    if summary['shifted_years']:
        _transaction(model, dict(table='schedule', field='season_year', old=summary['from_year'], value=start_year),
                     lambda: table.write(games))
    return summary

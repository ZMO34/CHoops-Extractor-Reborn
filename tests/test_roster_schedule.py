"""Season schedule table: exact writes, undo, bounds and conference rebuild."""
import datetime
import struct

import pytest
from test_roster_semantics import header_roster

from choops_py.core.errors import ToolError
from choops_py.roster import schedule as S
from choops_py.roster.adapters import load_bytes
from choops_py.roster.editor_model import EditorModel

pytestmark = pytest.mark.unit
START, SLOTS = 0x5400, 8


def key(day, minutes=1140, index=0):
    return S.encode_key(datetime.date(2008, 1, day), minutes, index)


def fixture(games, empties=3, both_members=True):
    data, starts = header_roster()
    struct.pack_into('>I', data, S.HEADER_FIELD, SLOTS)
    struct.pack_into('>i', data, S.HEADER_FIELD + 4, START + S.POINTER_BIAS - (S.HEADER_FIELD + 4))
    if both_members:  # team 1 joins conference 0 with reciprocal links
        field = starts['teams'] + 704 + 0x48
        struct.pack_into('>i', data, field, starts['conferences'] + 1 - field)
        field = starts['conferences'] + 0x6e0 + 4
        struct.pack_into('>i', data, field, starts['teams'] + 704 + 0x31 - field)
        struct.pack_into('>H', data, starts['conferences'] + 0x870, 2)
    for slot, (k, a, b, flags) in enumerate(games):
        struct.pack_into('>IHHIHHI', data, START + slot * 20, k, a, b, flags, 0xFFFF, 0, 0)
    for slot in range(len(games), len(games) + empties):
        data[START + slot * 20:START + slot * 20 + 20] = S.EMPTY_RECORD
    return EditorModel(load_bytes(bytes(data)))


def test_key_round_trip():
    k = S.encode_key(datetime.date(2007, 11, 9), 13 * 60 + 15, 3)
    assert S.decode_key(k) == (datetime.date(2007, 11, 9), 795, 3)
    assert k >> 16 == 0x0F49


def test_parse_capacity_and_untouched_tail():
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG)])
    table = S.Schedule(model)
    assert len(table.games) == 1 and table.capacity == 4
    assert table.rows()[0]['conference_game'] and table.rows()[0]['same_conference']


def test_add_edit_delete_preserve_outside_bytes_and_undo():
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG)])
    before = bytes(model.data)
    S.add_game(model, date='2008-01-02', first=1, second=0)
    games = S.Schedule(model).games
    assert [g['key'] for g in games] == sorted(g['key'] for g in games)
    assert games[0]['flags'] & S.CONFERENCE_FLAG  # automatic: same conference
    outside = START + SLOTS * 20
    assert bytes(model.data[:START]) == before[:START] and bytes(model.data[outside:]) == before[outside:]
    S.edit_game(model, games[0]['key'], date='2008-01-03', conference_game=False)
    assert not S.Schedule(model).games[0]['flags'] & S.CONFERENCE_FLAG
    S.delete_games(model, [S.Schedule(model).games[0]['key']])
    assert len(S.Schedule(model).games) == 1
    for _ in range(3):
        model.undo()
    assert bytes(model.data) == before
    reopened = EditorModel(load_bytes(bytes(model.data)))
    assert len(S.Schedule(reopened).games) == 1


@pytest.mark.parametrize('values', [dict(first=0, second=0), dict(first=0, second=9), dict(date='2008-13-01')])
def test_invalid_games_rejected_atomically(values):
    model = fixture([(key(5), 0, 1, 0)])
    before = bytes(model.data)
    with pytest.raises(ToolError):
        S.add_game(model, **{'date': '2008-01-02', 'first': 0, 'second': 1, **values})
    assert bytes(model.data) == before and not model.history


def test_capacity_full_is_rejected():
    model = fixture([(key(5), 0, 1, 0)], empties=0)
    with pytest.raises(ToolError) as error:
        S.add_game(model, date='2008-01-02', first=0, second=1)
    assert error.value.code == 'schedule_full'


def test_unsorted_layout_is_read_only():
    model = fixture([(key(9), 0, 1, 0), (key(5), 1, 0, 0)])
    with pytest.raises(ToolError) as error:
        S.Schedule(model)
    assert error.value.code == 'schedule_layout_unsupported'


def test_rebuild_drops_former_mates_and_schedules_current_members():
    # Team 1 is no longer in conference 0: its stored conference game is removed.
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG), (key(8), 1, 0, S.CONFERENCE_FLAG)], both_members=False)
    plan = S.rebuild_conference_games(model)
    assert plan['dropped_former_conference'] == 2 and not S.Schedule(model).games
    # Both members again: a double round robin of two teams is two games, no double booking.
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG), (key(8), 0, 1, 0)])
    S.rebuild_conference_games(model, targets={0: 2})
    report = S.report(model)
    assert report['games'] == 2 and report['conference_flag_mismatches'] == 0
    assert report['intra_conference_unflagged'] == 0 and not report['double_booked']


def test_rebuild_is_idempotent():
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG), (key(8), 0, 1, 0)])
    S.rebuild_conference_games(model, targets={0: 2})
    after = bytes(model.data)
    plan = S.rebuild_conference_games(model, targets={0: 2})
    assert plan['added'] == plan['dropped_former_conference'] == plan['trimmed_extra'] == 0
    assert bytes(model.data) == after


def test_balance_trims_nonconference_only_and_undoes():
    games = [(key(d), 0, 1, S.CONFERENCE_FLAG if d == 5 else 0) for d in (2, 5, 9)]
    model = fixture(games)
    before = bytes(model.data)
    summary = S.balance_totals(model, 0, 1)
    remaining = S.Schedule(model).games
    assert summary['removed'] == 2 and len(remaining) == 1
    assert remaining[0]['flags'] & S.CONFERENCE_FLAG
    model.undo()
    assert bytes(model.data) == before
    with pytest.raises(ToolError):
        S.balance_totals(model, 3, 2)
    assert bytes(model.data) == before


def test_balance_reports_teams_it_cannot_fill():
    # Only two teams and they are conference-mates: no legal opponent exists.
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG)])
    _, summary = S.plan_balance(model, 3, 10)
    assert summary['added'] == 0 and len(summary['still_short']) == 2


def test_cli_targets_accept_index_and_reject_unknown():
    model = fixture([(key(5), 0, 1, S.CONFERENCE_FLAG)])
    assert S.parse_targets(model, ['0=4']) == {0: 4}
    with pytest.raises(ToolError):
        S.parse_targets(model, ['nope=4'])
    with pytest.raises(ToolError):
        S.parse_targets(model, ['0'])
    assert S.parse_balance('24:31') == (24, 31) and S.parse_balance(None) is None


def test_season_year_keeps_month_day_and_moves_leap_day():
    leap = S.encode_key(datetime.date(2008, 2, 29), 1140)
    model = fixture([(S.encode_key(datetime.date(2007, 11, 9), 795), 0, 1, 0), (leap, 1, 0, S.CONFERENCE_FLAG)])
    before = bytes(model.data)
    assert S.season_start_year(model) == 2007
    summary = S.set_season_year(model, 2026)
    assert summary['shifted_years'] == 19 and summary['leap_day_moves'] == 1
    dates = [S.decode_key(g['key'])[:2] for g in S.Schedule(model).games]
    assert dates == [(datetime.date(2026, 11, 9), 795), (datetime.date(2027, 2, 28), 1140)]
    assert S.Schedule(model).games[1]['flags'] & S.CONFERENCE_FLAG
    assert S.set_season_year(model, 2026)['shifted_years'] == 0  # no-op, no extra undo step
    model.undo()
    assert bytes(model.data) == before

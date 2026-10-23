"""Synthetic schedule and persistent statistics ownership contracts."""

import struct
from hashlib import sha256

import pytest

from choops_py.research.legacy_backend import _roster_tables
from choops_py.research.legacy_history import FREE_STATE_SIZE, inspect_player_history
from choops_py.research.legacy_schedule import inspect_conference_schedule
from choops_py.roster.schema import HEADER_TABLES, detect_tables


def native_fixture(team_count=4):
    data = bytearray(0x10000)
    cursor = 0x100
    for name, (field, bias, stride, _) in HEADER_TABLES.items():
        count = {"players": 2, "teams": team_count, "conferences": 2}.get(name, 1)
        struct.pack_into(">Ii", data, field, count, cursor - field - 4 + 1)
        cursor += count * stride
        cursor = (cursor + 3) & ~3
    tables = detect_tables(data)

    def add_table(field, count, stride):
        nonlocal cursor
        start = cursor
        struct.pack_into(">Ii", data, field, count, start - field - 4 + 1)
        cursor += count * stride
        cursor = (cursor + 3) & ~3
        return start

    stats = add_table(0x40, 8, 24)
    recruits = add_table(0x48, 2, 0xD8)
    games = add_table(0x30, 5, 20)
    teams, _, team_stride = tables["teams"]
    conferences, _, conf_stride = tables["conferences"]
    groups = ((0, 1), (2, 3)) if team_count == 4 else (tuple(range(team_count)), ())
    for conference, members in enumerate(groups):
        at = conferences + conference * conf_stride
        struct.pack_into(
            ">HH",
            data,
            at + 0x1A,
            55 if conference == 0 else 96,
            2 if conference == 0 else 0,
        )
        struct.pack_into(">H", data, at + 0x870, len(members))
        for slot, team in enumerate(members):
            field = at + 0x6E0 + slot * 4
            struct.pack_into(
                ">i", data, field, teams + team * team_stride + 48 - field + 1
            )
            field = teams + team * team_stride + 0x48
            struct.pack_into(">i", data, field, at - field + 1)
    for slot, pair in enumerate(((0, 1), (1, 0), (2, 3), (3, 2), (1, 2))):
        struct.pack_into(">Ihh", data, games + slot * 20, slot + 1, *pair)
    players, _, player_stride = tables["players"]
    struct.pack_into(">5H", data, players + 0x28, 1, 2, 0, 0, 0)
    struct.pack_into(">5H", data, players + player_stride + 0x28, 3, 0, 0, 0, 0)
    for stat_id, school in ((1, 0), (2, 1), (3, 3), (4, 2)):
        struct.pack_into(">I", data, stats + stat_id * 24 + 20, school << 14)
        struct.pack_into(">I", data, stats + stat_id * 24, (stat_id + 2) << 26)
    struct.pack_into(">H", data, recruits + 0x2E, 4)
    return data[:cursor]


def test_logical_adjacent_tables_accept_biased_physical_overlap():
    data = native_fixture()
    tables = _roster_tables(data)
    arena, count, stride = tables["arenas"]
    assert arena + count * stride > tables["teams"][0]
    assert inspect_player_history(data)["unique_referenced_records"] == 4


def test_history_ids_school_attribution_and_packed_records_are_owned_independently():
    data = native_fixture()
    before = bytes(data)
    result = inspect_player_history(data)
    assert result["player_history_slots"] == 5
    assert result["unique_referenced_records"] == 4  # Includes the recruit's ID.
    years = result["players_with_history"][0]["years"]
    assert [(y["stat_id"], y["school_index"]) for y in years] == [(1, 0), (2, 1)]
    assert not result["issues"] and not result["shared_references"]
    tables = detect_tables(data)
    # Current membership can change without changing old-year school attribution.
    field = tables["teams"][0] + 0x48
    struct.pack_into(
        ">i",
        data,
        field,
        tables["conferences"][0] + tables["conferences"][2] - field + 1,
    )
    after = inspect_player_history(data)
    assert after["players_with_history"][0]["years"] == years
    assert (
        bytes(data[:field]) + before[field : field + 4] + bytes(data[field + 4 :])
        == before
    )


def test_empty_source_and_runtime_sentinels_are_not_28425_false_errors():
    data = native_fixture()
    players, count, stride = detect_tables(data)["players"]
    for player in range(count):
        struct.pack_into(">5H", data, players + player * stride + 0x28, *([0xFFFF] * 5))
    result = inspect_player_history(data)
    assert result["players_with_history"] == [] and not result["issues"]
    struct.pack_into(">H", data, players + 0x28, 16000)
    assert inspect_player_history(data)["issues"][0]["kind"] == "invalid_stat_id"


def test_stats_free_stack_detects_referenced_duplicate_and_out_of_range_ids():
    data = native_fixture()
    state = bytearray(FREE_STATE_SIZE)
    struct.pack_into(">i4H", state, 0, 4, 1, 5, 5, 8)
    result = inspect_player_history(data, state)
    assert result["free_stack"]["referenced_ids"] == [1]
    assert result["free_stack"]["duplicate_ids"] == [5]
    assert result["free_stack"]["invalid_ids"] == [8]
    assert result["runtime_continuity_verified"] is False
    for count in (-1, 16000):
        struct.pack_into(">i", state, 0, count)
        with pytest.raises(ValueError, match="15999"):
            inspect_player_history(data, state)


def test_aliases_across_player_years_and_recruits_are_reported_without_mutation():
    data = native_fixture()
    recruit_field = 0x4C + struct.unpack_from(">i", data, 0x4C)[0] - 1
    struct.pack_into(">H", data, recruit_field + 0x2E, 2)
    before = sha256(data).digest()
    result = inspect_player_history(data)
    assert result["shared_references"][0]["stat_id"] == 2
    assert {o["kind"] for o in result["shared_references"][0]["references"]} == {
        "player",
        "recruit",
    }
    assert sha256(data).digest() == before


def test_schedule_fixture_counts_and_native_no_tournament_sentinel():
    data = native_fixture()
    before = bytes(data)
    result = inspect_conference_schedule(data)
    assert result["scheduled_games"] == 5
    assert result["conferences"][0]["fixture_count"] == 2
    assert result["conferences"][0]["minimum_fixtures"] == 2
    assert result["conferences"][1]["tournament_event_enabled"] is False
    assert "native_tournament_event_skipped" in result["conferences"][1]["issues"]
    assert bytes(data) == before and not result["schedule_regenerated"]


def test_blank_reserved_games_are_not_self_matches_or_new_scheduling_capacity():
    data = native_fixture()
    start = 0x34 + struct.unpack_from(">i", data, 0x34)[0] - 1
    data[start + 80 : start + 100] = bytes(20)
    result = inspect_conference_schedule(data)
    assert result["scheduled_games"] == 4
    assert result["allocated_game_records"] == 5
    assert result["blank_game_records"] == 1
    assert not result["invalid_or_unresolved_games"]
    assert not result["blank_records_certified_available"]


def test_realignment_retains_fixture_bytes_and_exposes_missing_new_opponents():
    from choops_py.roster.editor_model import EditorModel
    from choops_py.roster.adapters import load_bytes

    data = native_fixture()
    model = EditorModel(load_bytes(data))
    at = 0x34 + struct.unpack_from(">i", data, 0x34)[0] - 1
    before = bytes(data[at : at + 100])
    model.move_team_to_conference(0, 1)
    result = inspect_conference_schedule(bytes(model.data))
    assert result["conferences"][1]["minimum_fixtures"] == 0
    assert (
        "members_without_current_conference_fixtures"
        in result["conferences"][1]["issues"]
    )
    assert bytes(model.data[at : at + 100]) == before
    model.undo()
    assert bytes(model.data) == bytes(data)


def test_bracket_and_directory_problems_are_explicit_not_silently_repaired():
    data = native_fixture()
    at = detect_tables(data)["conferences"][0]
    struct.pack_into(">HH", data, at + 0x1A, 97, 20)
    issues = inspect_conference_schedule(data)["conferences"][0]["issues"]
    assert "tournament_index_outside_native_table" in issues
    assert "tournament_entrants_exceed_native_capacity" in issues
    struct.pack_into(">i", data, 0x44, at - 0x44 + 1)
    with pytest.raises(ValueError, match="overlaps"):
        inspect_player_history(data)


@pytest.mark.parametrize("entrants", [3, 17, 20])
def test_explicit_unsafe_qualifier_edit_is_rejected_without_changing_any_bytes(
    entrants,
):
    from choops_py.roster.editor_model import EditorModel
    from choops_py.roster.adapters import load_bytes
    from choops_py.core.errors import ToolError

    data = native_fixture(20 if entrants >= 17 else 4)
    model = EditorModel(load_bytes(data))
    with pytest.raises(ToolError, match="native 16-slot bracket"):
        model.edit("conferences", 0, "tourney_slots", entrants)
    assert bytes(model.data) == bytes(data) and not model.history


def test_twenty_members_can_retain_a_sixteen_team_qualifying_bracket():
    from choops_py.roster.editor_model import EditorModel
    from choops_py.roster.adapters import load_bytes

    data = native_fixture(20)
    model = EditorModel(load_bytes(data))
    model.edit("conferences", 0, "tourney_slots", 16)
    assert model.rows["conferences"][0]["tourney_slots"] == 16
    assert len(model.rows["conferences"][0]["team_indices"]) == 20
    model.undo()
    assert bytes(model.data) == bytes(data)


def test_cli_reports_and_protects_history_free_stack_dependency(tmp_path, monkeypatch):
    from choops_py import cli
    from choops_py.archive import manifests

    monkeypatch.setattr(manifests, "OUTPUT", tmp_path)
    source = tmp_path / "source.rost"
    source.write_bytes(native_fixture())
    free = tmp_path / "free.bin"
    free.write_bytes(bytes(FREE_STATE_SIZE))
    output = tmp_path / "report.json"
    args = [
        "inspect-legacy-history",
        str(source),
        str(output),
        "--free-state",
        str(free),
    ]
    report = cli.execute(cli.parser().parse_args(args))
    assert report["unique_referenced_records"] == 4
    args[2] = str(free)
    with pytest.raises(ValueError, match="overwrite"):
        cli.execute(cli.parser().parse_args(args))
    assert free.read_bytes() == bytes(FREE_STATE_SIZE)
    args = ["inspect-legacy-schedule", str(source), str(output)]
    assert cli.execute(cli.parser().parse_args(args))["scheduled_games"] == 5


def test_unknown_directory_target_inside_statistics_pool_is_rejected():
    data = native_fixture()
    stats = 0x44 + struct.unpack_from(">i", data, 0x44)[0] - 1
    struct.pack_into(">Ii", data, 0x10, 1, stats + 24 - 0x14 + 1)
    with pytest.raises(ValueError, match="another table target"):
        inspect_player_history(data)


def test_aggregate_statistics_component_crosschecks_actual_history_owners():
    from test_legacy_backend import aggregate_fixture
    from choops_py.research.legacy_backend import inspect_legacy_aggregate

    aggregate = aggregate_fixture()
    struct.pack_into(">iH", aggregate, 0x57C8C, 1, 1)
    result = inspect_legacy_aggregate(aggregate, native_fixture())
    stack = result["components"][7]
    assert stack["component"] == "statistics_free_stack"
    assert stack["audit"]["ownership_crosscheck_available"]
    assert stack["audit"]["referenced_ids"] == [1]

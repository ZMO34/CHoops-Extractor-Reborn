"""Native poll component identity, Top-25 bounds and stale-season handling."""

import struct

import pytest
from test_legacy_schedule_history import native_fixture

from choops_py.research.legacy_backend import inspect_legacy_aggregate
from choops_py.research.legacy_polls import POLL_STATE_SIZE, inspect_poll_section
from choops_py.roster.schema import detect_tables


def fixture():
    roster = native_fixture()
    school, _, stride = detect_tables(roster)["teams"]
    state = bytearray(POLL_STATE_SIZE)
    struct.pack_into(">i", state, 0, 19)
    for start, index in [(0xC94 + 19 * 0xD0, 3), (0xAF4, 1), (0xBC4, 2), (4, 0)]:
        struct.pack_into(">II", state, start, school + index * stride + 48, 123)
    return roster, state, school + 48


def test_rank_sources_are_separate_school_references_and_keep_slot_order():
    roster, state, school = fixture()
    before = bytes(state), bytes(roster)
    struct.pack_into(">II", state, 0xAF4 + 3 * 8, school, 456)
    report = inspect_poll_section(state, roster)
    assert report["current_media"][0]["school"]["index"] == 3
    assert report["coaches"][0]["school"]["index"] == 1
    assert report["coaches"][1]["rank"] == 4
    assert report["mid_major"][0]["school"]["index"] == 2
    assert report["rpi"][0]["school"]["index"] == 0
    assert report["issue_count"] == 0
    assert not report["phase_and_roster_correspondence_verified"]
    assert bytes(roster) == before[1]
    assert bytes(state) != before[0]  # Only the fixture edit above changed it.
    frozen = bytes(state)
    inspect_poll_section(state, roster)
    assert bytes(state) == frozen


def test_uninitialized_week_does_not_present_old_media_rows_as_current():
    roster, state, _ = fixture()
    struct.pack_into(">i", state, 0, -1)
    report = inspect_poll_section(state, roster)
    assert not report["media_snapshot_available"]
    assert report["current_media"] == []


def test_26th_storage_row_is_not_an_extra_rank_or_a_duplicate_error():
    roster, state, school = fixture()
    struct.pack_into(">II", state, 0xAF4 + 25 * 8, school + 1, 999)
    report = inspect_poll_section(state, roster)
    assert len(report["coaches"]) == 1
    assert not report["issues"]


def test_wrong_anchor_and_repeated_school_are_reported_without_relabeling():
    roster, state, school = fixture()
    struct.pack_into(">II", state, 0xAF4 + 8, school + 1, 0)
    struct.pack_into(">II", state, 0xAF4 + 16, school, 0)
    struct.pack_into(">II", state, 0xAF4 + 24, school, 0)
    report = inspect_poll_section(state, roster)
    assert [r["issue"] for r in report["issues"]] == [
        "invalid_record_anchor",
        "duplicate_school",
    ]


@pytest.mark.parametrize("week", [-2, 20, 0x7FFFFFFF])
def test_invalid_week_never_indexes_another_component(week):
    roster, state, _ = fixture()
    struct.pack_into(">i", state, 0, week)
    with pytest.raises(ValueError, match="20 stored"):
        inspect_poll_section(state, roster)


def test_native_aggregate_reuses_the_reader_without_hiding_other_components():
    from test_legacy_backend import aggregate_fixture

    roster, state, _ = fixture()
    aggregate = aggregate_fixture()
    aggregate[0xF1994:0xF36E8] = state
    report = inspect_legacy_aggregate(aggregate, roster)
    assert report["components"][9]["audit"]["media_snapshot_index"] == 19
    assert report["components"][9]["audit"]["current_media"][0]["school"]["index"] == 3

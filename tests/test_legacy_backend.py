"""Native component boundaries and transfer identity checks use synthetic data."""

import json
import struct

import pytest
from test_recruit_pool import pool_fixture, state_fixture

from choops_py.research.legacy_backend import (
    AGGREGATE_SIZE,
    component_layout,
    inspect_legacy_aggregate,
    inspect_record_bank,
    inspect_transfer_section,
)
from choops_py.roster.schema import detect_tables


def aggregate_fixture():
    data = bytearray(0x15D1CC)
    data[0x11418:0x529BC] = state_fixture()
    return data


def transfer_fixture(count=1):
    roster = pool_fixture()[0]
    tables = detect_tables(roster)
    player = tables["players"][0] + 16
    school = tables["teams"][0] + 48
    state = bytearray(0x12D0)
    struct.pack_into(">i", state, 0, count)
    if count:
        struct.pack_into(">3I", state, 4, player, school, 0)
    return roster, state, player, school


def test_native_aggregate_exact_boundaries_and_source_preservation():
    roster = pool_fixture()[0]
    data = aggregate_fixture()
    before = bytes(data), bytes(roster)
    report = inspect_legacy_aggregate(data, roster)
    layout = report["components"]
    assert len(layout) == 17
    assert AGGREGATE_SIZE == 0x15D1CC
    assert layout[4]["offset"] == 0x11418
    assert layout[8]["offset"] == 0x5F990
    assert layout[13]["offset"] == 0xF7E04
    assert layout[-1]["offset"] + layout[-1]["bytes"] == 0x15D1CC
    assert layout[1]["bytes"] == 0
    assert layout[1]["offset"] == layout[2]["offset"]
    assert not any("audit_error" in row for row in layout)
    assert layout[4]["audit"]["interest_graph"]["free_nodes_traced"] == 16000
    assert report["userdata_offset_established"] is False
    assert report["matching_pair_verified"] is False
    assert report["native_portal_installed"] is False
    assert (bytes(data), bytes(roster)) == before


@pytest.mark.parametrize(
    "data",
    [None, 10**100, b"", bytes(0x15D1CB), bytes(0x15D1CD)],
    ids=["none", "integer", "empty", "short", "long"],
)
def test_wrong_size_or_type_does_not_scan_for_a_plausible_aggregate(data):
    with pytest.raises(ValueError, match="exactly"):
        inspect_legacy_aggregate(data, pool_fixture()[0])


def test_transfer_reference_bias_and_unsigned_player_are_not_lost():
    roster, state, player, school = transfer_fixture()
    before = bytes(state)
    row = inspect_transfer_section(state, roster)["records"][0]
    assert row["player"] == dict(raw=player, index=0, status="resolved")
    assert row["source"] == dict(raw=school, index=0, status="resolved")
    assert row["destination"]["status"] == "null"
    assert row["unsigned"] and not row["issues"]
    # An in-bounds pointer to the wrong byte is not a valid typed reference.
    struct.pack_into(">I", state, 4, player + 1)
    assert (
        "player_invalid_record_anchor"
        in inspect_transfer_section(state, roster)["records"][0]["issues"]
    )
    assert before != bytes(state)  # Only our fixture mutation changed it.


def test_transfer_duplicates_null_source_and_same_school_are_diagnosed():
    roster, state, player, school = transfer_fixture(2)
    struct.pack_into(">3I", state, 4, player, school, school)
    struct.pack_into(">3I", state, 16, player, 0, 0xFFFFFFFF)
    result = inspect_transfer_section(state, roster)
    assert result["records"][0]["issues"] == ["same_source_and_destination"]
    assert result["records"][1]["issues"] == [
        "source_null",
        "destination_invalid_record_anchor",
        "duplicate_player",
    ]
    assert result["issue_count"] == 4


def test_overlapping_roster_tables_cannot_resolve_typed_transfer_identities():
    roster, state, _, _ = transfer_fixture()
    # Put the team table inside the player table while keeping both in bounds.
    start = detect_tables(roster)["players"][0]
    struct.pack_into(">i", roster, 0x2C, start - 0x2C + 49)
    with pytest.raises(ValueError, match="overlapping"):
        inspect_transfer_section(state, roster)


@pytest.mark.parametrize("count", [-1, 401, 0x7FFFFFFF])
def test_sorting_scratch_record_does_not_expand_active_transfer_capacity(count):
    roster, state, _, _ = transfer_fixture(0)
    struct.pack_into(">i", state, 0, count)
    with pytest.raises(ValueError, match="400-active"):
        inspect_transfer_section(state, roster)


def test_all_400_active_records_fit_and_scratch_is_retained_as_opaque_hash():
    roster, state, player, school = transfer_fixture(400)
    for row in range(400):
        struct.pack_into(">3I", state, 4 + row * 12, player, school, 0)
    state[-12:] = b"opaque-tail!"
    result = inspect_transfer_section(state, roster)
    assert len(result["records"]) == 400
    assert result["stored_capacity"] == 401
    assert result["records"][-1]["issues"] == ["duplicate_player"]


def test_component_failure_is_local_and_does_not_hide_other_components():
    data = aggregate_fixture()
    struct.pack_into(">i", data, 0xF7E04, 401)
    report = inspect_legacy_aggregate(data, pool_fixture()[0])
    assert "400-active" in report["components"][13]["audit_error"]
    assert "audit_error" not in report["components"][4]
    assert len(report["components"]) == 17


def test_record_bank_exact_reference_columns_and_bounds_do_not_certify_history():
    roster = pool_fixture()[0]
    state = bytearray(0x92004)
    struct.pack_into(">i", state, 0, 1024)
    struct.pack_into(">I", state, 4 + 1023 * 0x248 + 8 + 0x120 + 11 * 24, len(roster))
    # Adjacent raw words are not interpreted as references.
    struct.pack_into(">I", state, 4 + 12, 0xFFFFFFFF)
    result = inspect_record_bank(state, roster)
    assert result["nonnull_references"] == result["references_outside_roster"] == 1
    assert not result["history_semantics_established"]
    struct.pack_into(">i", state, 0, 1025)
    with pytest.raises(ValueError, match="1024"):
        inspect_record_bank(state, roster)


def test_cli_uses_the_same_reader_and_protects_both_inputs(tmp_path, monkeypatch):
    from choops_py import cli
    from choops_py.archive import manifests

    monkeypatch.setattr(manifests, "OUTPUT", tmp_path)
    source = tmp_path / "source.rost"
    dependency = tmp_path / "aggregate.bin"
    source.write_bytes(pool_fixture()[0])
    dependency.write_bytes(aggregate_fixture())
    output = tmp_path / "report.json"
    args = ["inspect-legacy-backend", str(source), str(dependency), str(output)]
    result = cli.execute(cli.parser().parse_args(args))
    assert json.loads(output.read_text())["bytes"] == result["bytes"]
    args[-1] = str(dependency)
    before = dependency.read_bytes()
    with pytest.raises(ValueError, match="overwrite"):
        cli.execute(cli.parser().parse_args(args))
    assert dependency.read_bytes() == before
    assert component_layout()[13]["serializer"] == "0x5BC660"

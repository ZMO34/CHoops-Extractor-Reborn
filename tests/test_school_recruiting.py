"""School-list ownership, exact recruit identities and native capacity boundaries."""

import struct

import pytest

from choops_py.research.recruit_pool import inspect_recruiting_section
from choops_py.research.school_recruiting import CAPACITY, inspect_school_recruit_graph
from choops_py.roster.schema import detect_tables
from test_recruit_pool import pool_fixture, state_fixture


def graph_fixture():
    nodes = bytearray(CAPACITY * 8)
    for index in range(CAPACITY):
        struct.pack_into(
            ">IhH", nodes, index * 8, 0, index + 1 if index < CAPACITY - 1 else -1, 0
        )
    # Two schools may pursue the SAME recruit using different owned nodes.
    struct.pack_into(">IhH", nodes, 0, 0x1000 + 0xD8, -1, 0xAB80)
    struct.pack_into(">IhH", nodes, 8, 0x1000 + 0xD8, -1, 1)
    return nodes, {0: 0, 1: 1}


def inspect(nodes, heads, free_head=2):
    return inspect_school_recruit_graph(
        nodes, heads, recruit_start=0x1000, recruit_count=3, free_head=free_head
    )


def test_complete_dual_school_ownership_and_preserved_unknown_flags():
    nodes, heads = graph_fixture()
    before = bytes(nodes)
    report = inspect(nodes, heads)
    assert report["all_nodes_owned"]
    assert report["live_nodes"] == 2
    assert report["free_nodes_traced"] == CAPACITY - 2
    assert report["unowned_nodes"] == 0
    first = report["chains"][0]["nodes"][0]
    assert first["recruit_slot"] == 1
    assert first["word_6_raw"] == 0xAB80
    assert first["scholarship_offer_bit_7"]
    assert not report["chains"][1]["nodes"][0]["scholarship_offer_bit_7"]
    assert bytes(nodes) == before


@pytest.mark.parametrize(
    "case",
    [
        "live_cycle",
        "free_cycle",
        "schools_alias",
        "free_alias",
        "wrong_anchor",
        "null_live",
        "duplicate_recruit",
        "live_next",
        "free_pointer",
        "free_flags",
    ],
)
def test_corruption_cannot_certify_native_capacity(case):
    nodes, heads = graph_fixture()
    free = 2
    if case == "live_cycle":
        struct.pack_into(">h", nodes, 4, 0)
    elif case == "free_cycle":
        struct.pack_into(">h", nodes, (CAPACITY - 1) * 8 + 4, 2)
    elif case == "schools_alias":
        heads[1] = 0
    elif case == "free_alias":
        free = 0
    elif case == "wrong_anchor":
        struct.pack_into(">I", nodes, 0, 0x1001)
    elif case == "null_live":
        struct.pack_into(">I", nodes, 0, 0)
    elif case == "duplicate_recruit":
        struct.pack_into(">h", nodes, 4, 1)
        del heads[1]
    elif case == "live_next":
        struct.pack_into(">h", nodes, 4, CAPACITY)
    elif case == "free_pointer":
        struct.pack_into(">I", nodes, 16, 0x1000)
    else:
        struct.pack_into(">H", nodes, 16 + 6, 0x80)
    with pytest.raises(ValueError):
        inspect(nodes, heads, free)


def test_saturation_does_not_invent_free_nodes():
    nodes = bytearray(CAPACITY * 8)
    for index in range(CAPACITY):
        struct.pack_into(
            ">IhH",
            nodes,
            index * 8,
            0x1000 + index * 0xD8,
            index + 1 if index < CAPACITY - 1 else -1,
            0,
        )
    result = inspect_school_recruit_graph(
        nodes, {0: 0}, recruit_start=0x1000, recruit_count=CAPACITY, free_head=-1
    )
    assert result["all_nodes_owned"]
    assert result["free_nodes_traced"] == 0
    assert result["live_nodes"] == CAPACITY


def test_unowned_storage_prevents_complete_coverage_claim():
    nodes, heads = graph_fixture()
    result = inspect(nodes, heads, -1)
    assert result["unowned_nodes"] == CAPACITY - 2
    assert not result["all_nodes_owned"]


@pytest.mark.parametrize(
    "case",
    [
        "size",
        "bool_school",
        "bool_head",
        "bool_free",
        "bad_free",
        "empty_schools",
        "unaligned_pool",
        "bool_count",
        "zero_count",
        "huge_pool",
    ],
)
def test_invalid_graph_parameters(case):
    nodes, heads = graph_fixture()
    start, count, free = 0x1000, 3, 2
    if case == "size":
        nodes = nodes[:-1]
    elif case == "bool_school":
        heads = {True: -1}
    elif case == "bool_head":
        heads = {0: False}
    elif case == "bool_free":
        free = True
    elif case == "bad_free":
        free = CAPACITY
    elif case == "empty_schools":
        heads = {}
    elif case == "unaligned_pool":
        start += 1
    elif case == "bool_count":
        count = True
    elif case == "zero_count":
        count = 0
    else:
        start = 64 * 1024 * 1024
    with pytest.raises(ValueError):
        inspect_school_recruit_graph(
            nodes, heads, recruit_start=start, recruit_count=count, free_head=free
        )


def complete_state():
    roster, start = pool_fixture()
    state = state_fixture()
    # One actual school. Read its native +0x260 field using editor anchor +48.
    team_start, _, _ = detect_tables(roster)["teams"]
    struct.pack_into(">h", roster, team_start + 48 + 0x260, -1)
    struct.pack_into(">i", state, 4, 0)
    for index in range(CAPACITY):
        struct.pack_into(
            ">IhH",
            state,
            0x1F428 + index * 8,
            0,
            index + 1 if index < CAPACITY - 1 else -1,
            0,
        )
    return roster, state, start, team_start


def test_component_integration_uses_native_school_head_and_exact_saved_references():
    roster, state, start, team_start = complete_state()
    struct.pack_into(">h", roster, team_start + 48 + 0x260, 0)
    struct.pack_into(">i", state, 4, 1)
    struct.pack_into(">IhH", state, 0x1F428, start + 0xD8, -1, 0x80)
    before = bytes(roster), bytes(state)
    result = inspect_recruiting_section(state, roster)
    assert result["secondary_node_ownership_validated"]
    assert result["dual_pool_ownership_validated"]
    assert result["node_availability"]["interest_free_nodes_traced"] == CAPACITY
    assert result["node_availability"]["school_free_nodes_traced"] == CAPACITY - 1
    assert result["school_recruit_graph"]["chains"][0]["nodes"][0]["recruit_slot"] == 1
    assert not result["node_availability"]["native_reservation_installed"]
    assert (bytes(roster), bytes(state)) == before


def test_second_graph_error_keeps_primary_graph_and_other_diagnostics():
    roster, state, _, team_start = complete_state()
    struct.pack_into(">h", roster, team_start + 48 + 0x260, 0)
    result = inspect_recruiting_section(state, roster)
    assert result["interest_graph"]["all_nodes_owned"]
    assert "error" in result["school_recruit_graph"]
    assert not result["secondary_node_ownership_validated"]
    assert not result["dual_pool_ownership_validated"]
    assert result["node_availability"]["school_free_nodes_traced"] is None
    assert result["tail_bytes_sha256"]

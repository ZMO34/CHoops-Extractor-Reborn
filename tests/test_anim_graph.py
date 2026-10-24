import struct

import pytest

from choops_py.research.anim_graph import (
    POINTER_FIELDS,
    STRIDES,
    STYLE_SLOTS,
    graph_style_gate,
    inspect_graph,
    lookup_graph_key,
)


def fixture(nodes=2):
    counts = [nodes] + [1] * 15
    raw = bytearray(128 + sum(c * s for c, s in zip(counts, STRIDES)) + 8)
    next_offset = 128
    for i, (count, stride, fields) in enumerate(zip(counts, STRIDES, POINTER_FIELDS)):
        struct.pack_into(">I", raw, i * 4, count)
        struct.pack_into(">I", raw, 64 + i * 4, next_offset - (64 + i * 4) + 1)
        for row in range(count):
            at = next_offset + row * stride
            for field in fields:
                # Backward references exercise signed offsets, with zero nulls.
                value = 129 - (at + field) if field != fields[-1] else 0
                struct.pack_into(">i", raw, at + field, value)
            if i == 0:
                struct.pack_into(">I", raw, at + 16, row & 1)
                struct.pack_into(">I", raw, at + 12, 0xABCDEF01)
        next_offset += count * stride
    return raw


def test_graph_retains_both_binding_paths_unknown_words_and_signed_links():
    raw = fixture()
    before = bytes(raw)
    result = inspect_graph(raw)
    assert bytes(raw) == before
    assert [n["binding_kind"] for n in result["nodes"]] == [
        "direct-motion",
        "group-first-member",
    ]
    assert [n["executable_binding_slot"] for n in result["nodes"]] == [0, 1]
    assert all(n["raw_words"][3] == 0xABCDEF01 for n in result["nodes"])
    assert any(
        p["field"] > p["target"]
        for p in result["pointer_fixups"]
        if p["target"] is not None
    )
    assert result["compatible_on_court_conversion_count"] is None
    assert result["target_compatibility_established"] is False
    assert result["transition_semantics_established"] is False


def test_empty_tables_allow_null_or_end_pointer_but_not_external():
    raw = bytearray(128)
    struct.pack_into(">I", raw, 64, 128 - 64 + 1)
    result = inspect_graph(raw)
    assert result["tables"][0]["offset"] == 128
    assert result["nodes"] == []
    struct.pack_into(">I", raw, 64, 130 - 64 + 1)
    with pytest.raises(ValueError, match="outside record"):
        inspect_graph(raw)


@pytest.mark.parametrize(
    "field,value,message",
    [
        (0, 1_000_001, "row count"),
        (0, 200_000, "pointer count"),
        (64, 0, "null pointer"),
        (64, 1, "overlaps header"),
        (68, 128 - 68 + 1, "tables overlap"),
        (128 + 24, 0x7FFFFFFF, "outside record"),
        (128 + 24, 0x80000000, "outside record"),
    ],
)
def test_bad_graph_counts_tables_and_internal_links_reject(field, value, message):
    raw = fixture()
    struct.pack_into(">I", raw, field, value)
    with pytest.raises(ValueError, match=message):
        inspect_graph(raw)


def test_graph_profile_and_truncation_are_not_guessed():
    with pytest.raises(ValueError, match="only established"):
        inspect_graph(fixture(), "college-hoops-2k8")
    with pytest.raises(ValueError, match="128 bytes"):
        inspect_graph(bytes(127))
    with pytest.raises(ValueError):
        inspect_graph(fixture()[:130])


@pytest.mark.parametrize("family", range(9))
def test_keyed_lookup_all_families_and_missing(family):
    raw = fixture()
    result = inspect_graph(raw)
    offset = result["tables"][7 + family]["offset"]
    struct.pack_into(">I", raw, offset, 0xFFFFFFFF)
    found = lookup_graph_key(raw, 0xFFFFFFFF, family)
    assert found["offset"] == offset
    assert found["raw_words"][0] == 0xFFFFFFFF
    assert found["pointer_targets"] == [128, 128, None]
    assert lookup_graph_key(raw, 0xFFFFFFFE, family) is None


def test_duplicate_key_lookup_preserves_first_row():
    raw = bytearray(160)
    struct.pack_into(">I", raw, 28, 2)
    struct.pack_into(">I", raw, 92, 128 - 92 + 1)
    for at in (128, 144):
        struct.pack_into(">I", raw, at, 9)
    assert lookup_graph_key(raw, 9, 0)["offset"] == 128
    assert lookup_graph_key(raw, 9, 1) is None


@pytest.mark.parametrize(
    "key,family", [(-1, 0), (2**32, 0), (True, 0), (0, -1), (0, 9), (0, True)]
)
def test_lookup_rejects_invalid_word_or_family(key, family):
    with pytest.raises(ValueError, match="lookup"):
        lookup_graph_key(fixture(), key, family)


@pytest.mark.parametrize("selector", range(1, 18))
def test_style_gate_routes_exact_family_and_slot(selector):
    raw = fixture()
    struct.pack_into(">I", raw, 128 + 20, selector)
    report = inspect_graph(raw)
    family, slot = STYLE_SLOTS[selector]
    for table in report["keyed_tables"]:
        row = table["rows"][0]
        for field in (4, 8, 12):
            struct.pack_into(
                ">i", raw, row["offset"] + field, 164 - row["offset"] - field + 1
            )
    row = report["keyed_tables"][family]["rows"][0]
    field = row["offset"] + 4 + slot * 4
    struct.pack_into(">i", raw, field, 128 - field + 1)
    keys = [0] * 9
    assert graph_style_gate(raw, keys, 0)
    keys[family] = 99
    assert not graph_style_gate(raw, keys, 0)
    keys[family] = 0
    struct.pack_into(">I", raw, field, 0)
    assert not graph_style_gate(raw, keys, 0)
    assert graph_style_gate(raw, keys, 0, bypass=True)


def test_style_gate_zero_null_unsupported_and_explicit_inputs():
    raw = fixture()
    assert graph_style_gate(raw, [9] * 9, 0)
    struct.pack_into(">I", raw, 148, 18)
    assert not graph_style_gate(raw, [0] * 9, 0)
    assert graph_style_gate(raw, [0] * 9, None)
    for keys, candidate, bypass in [
        ([0], 0, False),
        ([True] * 9, 0, False),
        ([0] * 9, True, False),
        ([0] * 9, 2, False),
        ([0] * 9, 0, 1),
    ]:
        with pytest.raises(ValueError, match="Style gate"):
            graph_style_gate(raw, keys, candidate, bypass=bypass)


def test_keyed_node_targets_cannot_point_inside_nodes_or_other_tables():
    raw = fixture()
    report = inspect_graph(raw)
    field = report["keyed_tables"][0]["rows"][0]["offset"] + 4
    for target in [129, report["tables"][1]["offset"]]:
        struct.pack_into(">i", raw, field, target - field + 1)
        with pytest.raises(ValueError, match="node boundary"):
            inspect_graph(raw)

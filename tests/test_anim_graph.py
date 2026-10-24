import struct

import pytest

from choops_py.research.anim_graph import POINTER_FIELDS, STRIDES, inspect_graph


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

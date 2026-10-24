import struct

import pytest
from test_target_motion import fixture as motion_fixture

from choops_py.formats.embedded_motion import NativeELF
from choops_py.research.motion_bundle import (
    DRIBBLE_TABLE_SLOT,
    inspect_bundle_rows,
    inspect_dribble_bundle,
    select_bundle_rows,
)


def rows():
    raw = bytearray(144)
    for i, threshold in enumerate([0, 0.4, 0.625, 0.9, 0.9]):
        struct.pack_into(
            ">II3fI",
            raw,
            i * 24,
            0x50000000 + i * 256,
            0x50000040 + i * 256,
            threshold,
            1 + i / 8,
            2 + i / 8,
            int(i == 4),
        )
    return raw


def test_selection_preserves_native_threshold_order_lane_and_next_scalar():
    raw = rows()
    before = bytes(raw)
    selected = select_bundle_rows(raw, 0.8, False, True, False)
    assert selected == dict(
        index=2,
        next_index=3,
        lane=1,
        motion=0x50000240,
        next_motion=0x50000340,
        scalar=2.25,
    )
    assert select_bundle_rows(raw, 0.9, False, True, True) == dict(
        index=3,
        next_index=3,
        lane=0,
        motion=0x50000300,
        next_motion=0x50000300,
        scalar=1.375,
    )
    assert select_bundle_rows(raw, 0.9, True, False, False)["index"] == 4
    assert select_bundle_rows(raw, 0.4, False, False, False)["index"] == 1
    assert select_bundle_rows(raw, -0.1, False, True, True)["motion"] == 0
    assert bytes(raw) == before


def test_descending_scan_is_not_sorted_and_null_motion_is_not_substituted():
    raw = rows()
    struct.pack_into(">f", raw, 3 * 24 + 8, 0.2)
    struct.pack_into(">I", raw, 3 * 24, 0)
    result = select_bundle_rows(raw, 0.3, False, False, False)
    assert result["index"] == 3 and result["motion"] == 0
    struct.pack_into(">I", raw, 140, 1)
    assert select_bundle_rows(raw, 1, True, False, False)["next_index"] == 4


@pytest.mark.parametrize(
    "mutate,message",
    [
        (lambda b: b.pop(), "lookahead"),
        (lambda b: struct.pack_into(">f", b, 8, float("nan")), "nonfinite"),
        (lambda b: struct.pack_into(">I", b, 0, 3), "unaligned"),
    ],
)
def test_bundle_bytes_are_bounded(mutate, message):
    raw = rows()
    mutate(raw)
    with pytest.raises(ValueError, match=message):
        inspect_bundle_rows(raw)


@pytest.mark.parametrize(
    "value,allow,policy,flag",
    [
        (float("inf"), True, True, True),
        (1e100, True, True, True),
        (True, True, True, True),
        (0, 1, True, True),
        (0, True, 1, True),
    ],
)
def test_context_is_explicit_and_float32_bounded(value, allow, policy, flag):
    with pytest.raises(ValueError):
        select_bundle_rows(rows(), value, allow, policy, flag)


def native_fixture():
    original = motion_fixture()
    raw = bytearray(0x5000)
    raw[:64] = original[:64]
    raw[0x1000:0x1800] = original[0x100:0x900]
    ranges = [
        (0x10000, 0x1000, 0x800, 0x900, 6),
        (0x345000, 0x2000, 0x1000, 0x1000, 5),
        (0xA5A000, 0x3000, 0x1000, 0x1000, 6),
        (0x20000000, 0x4000, 0x1000, 0x1000, 6),
    ]
    struct.pack_into(">H", raw, 56, len(ranges))
    for i, (va, offset, size, memory, flags) in enumerate(ranges):
        struct.pack_into(
            ">II6Q", raw, 64 + 56 * i, 1, flags, offset, va, va, size, memory, 16
        )
    elf = NativeELF(raw)

    def word(address, value):
        struct.pack_into(">I", raw, elf.target(address)["file_offset"], value)

    for address, value in [
        (0x345B18, 0x80E244A4),
        (0x345B88, 0xC00A0008),
        (0x345FDC, 0x8009002C),
        (DRIBBLE_TABLE_SLOT, 0x20000000),
    ]:
        word(address, value)
    data = rows()
    for i in range(5):
        struct.pack_into(">II", data, 24 * i, 0x10000, 0x10040)
    raw[0x4000:0x4090] = data
    return raw, word


def test_native_dependency_inspection_is_read_only_and_does_not_claim_table_count():
    raw, _ = native_fixture()
    before = bytes(raw)
    report = inspect_dribble_bundle(raw, 0)
    assert len(report["native_dependencies"]) == 2
    assert not report["registered_count_established"]
    assert report["compatible_conversion_count"] is None
    assert report["lookahead_bytes"] == 24
    assert bytes(raw) == before


def test_native_revision_and_unbacked_index_are_rejected():
    raw, word = native_fixture()
    with pytest.raises(ValueError):
        inspect_dribble_bundle(raw, 65535)
    word(0x345FDC, 0)
    with pytest.raises(ValueError, match="revision"):
        inspect_dribble_bundle(raw, 0)


@pytest.mark.parametrize("index", [-1, 65536, True])
def test_index_requires_a_bounded_caller_proof(index):
    with pytest.raises(ValueError, match="Caller-proven"):
        inspect_dribble_bundle(b"", index)

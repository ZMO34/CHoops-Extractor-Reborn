import struct
import zlib

import pytest

from choops_py.research.scorebug_pose import inspect_contract


def fixture():
    h = bytearray(0x1000)

    def u(q, v):
        struct.pack_into(">I", h, q, v)

    def ptr(q, p):
        struct.pack_into(">i", h, q, p - q + 1)

    def string(q, s):
        h[q : q + len(s) * 2 + 2] = s.encode("utf-16-be") + bytes(2)

    u(0x44, 1)
    ptr(0x48, 0x100)
    u(0x3C, 1)
    ptr(0x40, 0x200)
    string(0x700, "Owner")
    string(0x720, "root")
    string(0x740, "label")
    ptr(0x100, 0x700)
    u(0x104, 0xABC)
    u(0x160, 2)
    ptr(0x164, 0x300)
    ptr(0x240, 0x700)
    u(0x244, 0xABC)
    ptr(0x274, 0x500)
    for j, name in enumerate(["root", "label"]):
        q = 0x300 + j * 48
        struct.pack_into(">8f", h, q, 0, 0, 0, 1, 0, 0, 0, 1)
        ptr(q + 32, 0x720 + j * 32)
        u(q + 36, zlib.crc32(name.encode()) & 0xFFFFFFFF)
        u(q + 40, (65535 if j == 0 else 0) << 16 | 65535)
        u(q + 44, 0xFFFF0000)
    identity = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    struct.pack_into(">16f", h, 0x200, *identity)
    for j in range(2):
        struct.pack_into(">16f", h, 0x500 + j * 64, *identity)
    return [bytes(h), b"unchanged GPU data"]


@pytest.mark.parametrize(
    "case", ["extra_bone", "bad_affine", "bad_hash", "bad_parent", "unaligned"]
)
def test_rejects_pose_extent_and_native_identity_corruption(case):
    p = fixture()
    h = bytearray(p[0])
    if case == "extra_bone":
        struct.pack_into(">I", h, 0x160, 3)
    if case == "bad_affine":
        struct.pack_into(">f", h, 0x57C, 0)
    if case == "bad_hash":
        struct.pack_into(">I", h, 0x354, 0)
    if case == "bad_parent":
        struct.pack_into(">I", h, 0x358, 1 << 16 | 65535)
    if case == "unaligned":
        struct.pack_into(">i", h, 0x274, 0x504 - 0x274 + 1)
    with pytest.raises(ValueError):
        inspect_contract(bytes(h))


def test_stock_like_fixture_is_read_only():
    parts = fixture()
    before = list(parts)
    rows = inspect_contract(parts[0])
    assert rows[0]["bone_count"] == 2
    assert rows[0]["model"]["bones"][1]["name"] == "label"
    assert parts == before


@pytest.mark.parametrize("field", [0x44, 0x3C, 0x160])
def test_rejects_unbounded_table_counts(field):
    parts = fixture()
    h = bytearray(parts[0])
    struct.pack_into(">I", h, field, 0xFFFFFFFF)
    with pytest.raises(ValueError):
        inspect_contract(bytes(h))

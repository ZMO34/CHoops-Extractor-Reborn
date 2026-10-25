import json
import struct
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
keystone = pytest.importorskip("keystone")
ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "docs/examples/scorebug-main-text-draw.json").read_text())
BASE = PROFILE["entry"]
CODE = bytes(
    keystone.Ks(
        keystone.KS_ARCH_PPC, keystone.KS_MODE_PPC64 | keystone.KS_MODE_BIG_ENDIAN
    ).asm((ROOT / "docs/examples/scorebug-main-text-draw.ppc").read_text(), addr=BASE)[
        0
    ]
)
INS = {
    i.address: i
    for i in capstone.Cs(
        capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN
    ).disasm(CODE, BASE)
}


def table():
    result = bytearray()
    for row in PROFILE["registry_rows"]:
        s = row["scale"]
        result.extend(
            struct.pack(
                ">20f",
                s,
                0,
                0,
                0,
                0,
                s,
                0,
                0,
                0,
                0,
                s,
                0,
                row["x"],
                row["y"],
                row["z"],
                1,
                0,
                0,
                0,
                0,
            )
        )
    return bytes(result)


@pytest.mark.parametrize("row", range(-1, 15))
def test_native_draw_uses_live_transform_and_preserves_provider_string(row):
    data = table()
    font = bytearray([0x5A] * 192)
    before = bytes(font)
    original = {f"r{i}": 0x100000 + i * 256 for i in range(32)}
    original.update(r3=0x200000, r4=0x300000, r27=row)
    r = original.copy()
    vectors = {}
    f = {}
    cr = {}
    pc = BASE

    def value(s):
        return r[s] if s in r else int(s, 0)

    def read(address, size):
        if PROFILE["data"] <= address < PROFILE["data"] + len(data):
            start = address - PROFILE["data"]
            assert start + size <= len(data)
            return data[start : start + size]
        raise AssertionError(hex(address))

    for _ in range(100):
        i = INS[pc]
        op = i.mnemonic
        a = [s.strip() for s in i.op_str.split(",")]
        target = pc + 4
        if op == "cmpwi":
            x, y = value(a[1]), value(a[2])
            cr[a[0]] = (x > y) - (x < y)
        elif op in ("bgt", "blt"):
            if cr[a[0]] > 0 if op == "bgt" else cr[a[0]] < 0:
                target = int(a[1], 0)
        elif op == "mulli":
            r[a[0]] = value(a[1]) * value(a[2])
        elif op == "lis":
            r[a[0]] = value(a[1]) << 16
        elif op == "li":
            r[a[0]] = value(a[1])
        elif op == "ori":
            r[a[0]] = value(a[1]) | value(a[2])
        elif op == "add":
            r[a[0]] = value(a[1]) + value(a[2])
        elif op == "lvx":
            vectors[a[0]] = read(value(a[1]) + value(a[2]), 16)
        elif op == "stvx":
            address = value(a[1]) + value(a[2])
            at = address - original["r3"]
            assert 0 <= at <= 64 and at % 16 == 0
            font[at : at + 16] = vectors[a[0]]
        elif op in ("lfs", "stfs"):
            displacement, register = a[1].split("(")
            address = value(displacement) + value(register[:-1])
            if op == "lfs":
                f[a[0]] = read(address, 4)
            else:
                assert address == original["r3"] + 0x64
                font[0x64:0x68] = f[a[0]]
        elif op == "b":
            assert int(a[0], 0) == PROFILE["tail_target"]
            break
        else:
            raise AssertionError((op, a))
        pc = target
    else:
        raise AssertionError("draw wrapper did not tail-call")
    assert all(r[k] == original[k] for k in original if k not in ("r9", "r10"))
    if 0 <= row <= 11:
        assert font[:80] == data[row * 80 : (row + 1) * 80]
        assert struct.unpack_from(">f", font, 0x64)[0] == 1
        assert font[80:100] == before[80:100]
        assert font[104:] == before[104:]
    else:
        assert bytes(font) == before

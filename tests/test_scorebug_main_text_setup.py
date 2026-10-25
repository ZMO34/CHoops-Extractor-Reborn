import json
import struct
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
keystone = pytest.importorskip("keystone")
ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "docs/examples/scorebug-main-text-setup.json").read_text())
BASE = PROFILE["entry"]
CODE = bytes(
    keystone.Ks(
        keystone.KS_ARCH_PPC, keystone.KS_MODE_PPC64 | keystone.KS_MODE_BIG_ENDIAN
    ).asm((ROOT / "docs/examples/scorebug-main-text-setup.ppc").read_text(), addr=BASE)[
        0
    ]
)
INS = {
    i.address: i
    for i in capstone.Cs(
        capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN
    ).disasm(CODE, BASE)
}


def packets():
    result = bytearray()
    for row in PROFILE["registry_rows"]:
        s = row["scale"]
        result.extend(
            struct.pack(
                ">24f",
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
                0,
                0,
                0,
                1,
                row["x"],
                row["y"],
                row["z"],
                0,
                1,
                0,
                0,
                0,
            )
        )
    return bytes(result)


@pytest.mark.parametrize("row", range(-1, 15))
@pytest.mark.parametrize("custom", [0, 0xA30F18])
def test_setup_reaches_both_draw_routes_and_native_position_consumer(row, custom):
    data = packets()
    font = bytearray([0x5A] * 192)
    before = bytes(font)
    original = {f"r{i}": 0x100000 + i * 256 for i in range(32)}
    original.update(r3=0x300000, r4=0x310000, r26=0x220004, r27=row, r30=0x200000)
    r = original.copy()
    cr = {}
    pc = BASE

    def value(s):
        return r[s] if s in r else int(s, 0)

    def address(s):
        displacement, register = s.split("(")
        return value(displacement) + value(register[:-1])

    for _ in range(100):
        i = INS[pc]
        a = [s.strip() for s in i.op_str.split(",")]
        target = pc + 4
        if i.mnemonic == "cmpwi":
            x, y = value(a[1]), value(a[2])
            cr[a[0]] = (x > y) - (x < y)
        elif i.mnemonic in ("blt", "bgt"):
            if cr[a[0]] < 0 if i.mnemonic == "blt" else cr[a[0]] > 0:
                target = int(a[1], 0)
        elif i.mnemonic == "mulli":
            r[a[0]] = value(a[1]) * value(a[2])
        elif i.mnemonic == "lis":
            r[a[0]] = value(a[1]) << 16
        elif i.mnemonic == "ori":
            r[a[0]] = value(a[1]) | value(a[2])
        elif i.mnemonic == "add":
            r[a[0]] = value(a[1]) + value(a[2])
        elif i.mnemonic == "lwz":
            at = address(a[1])
            if at == original["r26"] + 4:
                r[a[0]] = custom
            else:
                at -= PROFILE["data"]
                assert 0 <= at <= len(data) - 4
                r[a[0]] = struct.unpack_from(">I", data, at)[0]
        elif i.mnemonic == "stw":
            at = address(a[1]) - original["r30"]
            assert 0 <= at <= 0x64
            struct.pack_into(">I", font, at, value(a[0]))
        elif i.mnemonic == "b":
            assert (
                int(a[0], 0)
                == PROFILE["draw_target" if 0 <= row <= 11 else "return_target"]
            )
            break
        else:
            raise AssertionError(i.mnemonic)
        pc = target
    else:
        raise AssertionError("setup did not resume dispatch")
    if not 0 <= row <= 11:
        assert r["r9"] == custom  # Event rows retain the displaced callback load.
    assert all(r[k] == original[k] for k in original if k not in ("r9", "r10"))
    if not 0 <= row <= 11:
        assert bytes(font) == before
        return
    expected = PROFILE["registry_rows"][row]
    # Native 9BEB8 consumes matrix translation +30 and extra position +40.
    anchor = [
        struct.unpack_from(">f", font, 0x30 + 4 * i)[0]
        + struct.unpack_from(">f", font, 0x40 + 4 * i)[0]
        for i in range(3)
    ]
    assert anchor == pytest.approx([expected["x"], expected["y"], expected["z"]])
    assert struct.unpack_from(">3f", font, 0x30) == (0, 0, 0)
    assert struct.unpack_from(">f", font, 0x64)[0] == 1
    assert font[80:100] == before[80:100]  # External matrix, font height, width.
    assert font[104:] == before[104:]  # Colors, style flags, provider metadata.
    if row not in (5, 6):
        assert anchor[1] < -180  # Active labels must not fall at screen origin.


def test_hook_is_before_custom_default_branch_and_scratch_is_bounded():
    assert PROFILE["site"] == 0x4F4A48
    assert PROFILE["return_target"] == PROFILE["site"] + 4
    assert PROFILE["displaced"] == "lwz r9, 4(r26)"
    assert BASE + len(CODE) < PROFILE["data"]
    assert PROFILE["data"] + len(packets()) < 0x8A0000

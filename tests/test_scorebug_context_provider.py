import json
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
keystone = pytest.importorskip("keystone")
ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads(
    (ROOT / "docs/examples/scorebug-context-provider.json").read_text()
)
STATIC_STRINGS = b"".join(
    (v.encode("utf-16-be") + bytes(2)) for v in PROFILE["strings"].values()
)
Cs = capstone.Cs
CS_ARCH_PPC = capstone.CS_ARCH_PPC
CS_MODE_64 = capstone.CS_MODE_64
CS_MODE_BIG_ENDIAN = capstone.CS_MODE_BIG_ENDIAN
Ks = keystone.Ks
KS_ARCH_PPC = keystone.KS_ARCH_PPC
KS_MODE_PPC64 = keystone.KS_MODE_PPC64
KS_MODE_BIG_ENDIAN = keystone.KS_MODE_BIG_ENDIAN
BASE = 0x899D40
TOC = 0xA64A94
code = bytes(
    Ks(KS_ARCH_PPC, KS_MODE_PPC64 | KS_MODE_BIG_ENDIAN).asm(
        (ROOT / "docs/examples/scorebug-context-provider.ppc").read_text(), addr=BASE
    )[0]
)
ins = {
    i.address: i
    for i in Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN).disasm(code, BASE)
}


def run(case, old="stale prior game"):
    mem = {}
    r = {f"r{i}": 0xABC00000 + i for i in range(32)}
    r.update(r1=0x900000, r2=TOC, r3=0x61000)
    original = r.copy()
    cr = {i: (i % 3) - 1 for i in range(8)}
    origcr = cr.copy()
    crsaved = {}
    lr = 0xDEAD1234
    calls = []
    strings = {0x61000: old}
    constructed = 0
    destroyed = 0

    def put(a, v, n=4):
        for i, x in enumerate(int(v & ((1 << (8 * n)) - 1)).to_bytes(n, "big")):
            mem[a + i] = x

    def get(a, n=4):
        assert all(a + i in mem for i in range(n)), (case, hex(pc), hex(a), n)
        return int.from_bytes(bytes(mem[a + i] for i in range(n)), "big")

    def wide(a, s):
        for i, x in enumerate(s.encode("utf-16-be") + b"\0\0"):
            mem[a + i] = x

    def readwide(a):
        out = []
        for i in range(80):
            c = get(a + i * 2, 2)
            if not c:
                return "".join(out)
            out.append(chr(c))
        raise AssertionError("wide string unterminated")

    put(TOC - 0x6D70, 0x10000 if not case.get("missing_mode") else 0)
    put(0x10000, case.get("mode", 0))
    put(0x100D0, case.get("legacy_submode", 0))
    put(TOC + 0x4664, 0x11000)
    put(0x11000, 14 if case.get("timeout") else 1)
    put(TOC + 0x4618, 0x12000)
    put(0x12000, case.get("suppressed", 0))
    put(0x21018, 0x31000 if not case.get("missing_conf") else 0)
    put(0x22018, 0x32000 if case.get("cross_conf") else 0x31000)
    put(0x3100C, 3, 2)
    put(0x3101A, case.get("conference_bracket", 9), 2)
    put(0x31004, 0x51000 if not case.get("missing_name") else 0)
    wide(0x51000, case.get("name", "SEC"))
    put(0x41000, case.get("key", 123))
    put(0x42000, 123)
    teams = (11, 10) if case.get("swapped") else (10, 11)
    if case.get("wrong_participant"):
        teams = (10, 12)
    put(0x42004, teams[0], 2)
    put(0x42006, teams[1], 2)
    for i, x in enumerate(STATIC_STRINGS):
        mem[0x89A640 + i] = x
    if case.get("null_output"):
        r["r3"] = 0
        original = r.copy()

    def val(s):
        return r[s] if s in r else int(s, 0)

    def addr(s):
        d, rr = s[:-1].split("(")
        return (int(d, 0) + (0 if rr == "0" else r[rr])) & 0xFFFFFFFF

    def signed(x):
        x &= 0xFFFFFFFF
        return x - (1 << 32) if x & 0x80000000 else x

    def native(t):
        nonlocal constructed, destroyed
        args = [r[f"r{i}"] for i in range(3, 6)]
        calls.append(t)
        v = 0
        if t == 0x57F050:
            v = 0 if case.get("missing_home") else 0x21000
        elif t == 0x57F064:
            v = 0 if case.get("missing_away") else 0x22000
        elif t == 0x4A3924:
            v = case.get("category", 0)
        elif t == 0x57F49C:
            v = 0 if case.get("missing_key") else 0x41000
        elif t == 0x5AAB80:
            assert args[0] == case.get("key", 123)
            v = 0 if case.get("missing_record") else 0x42000
        elif t == 0x4A3174:
            v = {10: 0x21000, 11: 0x22000, 12: 0x23000}.get(args[0], 0)
        elif t == 0x58BC60:
            assert args[0] == case.get("key", 123)
            v = case.get("bracket", -1) & 0xFFFFFFFF
        elif t == 0x4A1FF4:
            assert args[0] == 3
            v = 0x32000 if case.get("conf_table_mismatch") else 0x31000
        elif t == 0x719E98:
            assert case.get("timeout") and not case.get("suppressed")
            strings[args[0]] = "TIMEOUT: " + case.get("timeout_team", "HOME")
        elif t == 0x49E1B4:
            assert signed(args[2]) == -1
            assert not r["r1"] <= args[1] < original["r1"], (
                "borrowed character buffer escapes callback stack"
            )
            strings[args[0]] = readwide(args[1])
            constructed += 1
        elif t == 0x49E0E4:
            assert (
                get(args[1]) == 0x36A37FBF
                and get(args[2]) == 0
                and get(args[2] + 4) == 2
            )
            values = []
            for j in range(2):
                row = args[2] + 8 + j * 12
                assert get(row) == 0 and get(row + 8) == 0xA18CD8
                values.append(strings[get(row + 4)])
            strings[args[0]] = "\n".join(values)
        elif t == 0x49D604:
            assert args[2] == 1
            strings[args[0]] = strings[args[1]]
        elif t == 0x49F3A4:
            assert args[0] in strings
            del strings[args[0]]
            destroyed += 1
        else:
            raise AssertionError(hex(t))
        for j in [0, *range(3, 13)]:
            r[f"r{j}"] = 0xF0000000 + j
        for j in (0, 1, 5, 7):
            cr[j] = 1
        r["r3"] = v
        if t in (0x4A3924, 0x4A3174, 0x4A1FF4, 0x49E1B4, 0x49D604, 0x49F3A4, 0x49E0E4):
            put(r["r1"] + 0x28, TOC, 8)
            r["r2"] = 0xA54AC8

    pc = BASE
    for step in range(3000):
        i = ins[pc]
        op = i.mnemonic
        a = [x.strip() for x in i.op_str.split(",")]
        n = pc + 4
        if op in ("std", "stw", "sth"):
            put(addr(a[1]), val(a[0]), {"std": 8, "stw": 4, "sth": 2}[op])
        elif op == "stdu":
            p = addr(a[1])
            put(p, val(a[0]), 8)
            r["r1"] = p
        elif op in ("ld", "lwz", "lhz"):
            r[a[0]] = get(addr(a[1]), {"ld": 8, "lwz": 4, "lhz": 2}[op])
        elif op == "mflr":
            r[a[0]] = lr
        elif op == "mtlr":
            lr = r[a[0]]
        elif op == "mfcr":
            crsaved = cr.copy()
            r[a[0]] = 0x1234
        elif op in ("mtcr", "mtcrf"):
            cr = crsaved.copy()
        elif op == "mr":
            r[a[0]] = val(a[1])
        elif op == "li":
            r[a[0]] = val(a[1]) & 0xFFFFFFFFFFFFFFFF
        elif op == "lis":
            r[a[0]] = (val(a[1]) << 16) & 0xFFFFFFFF
        elif op == "ori":
            r[a[0]] = val(a[1]) | val(a[2])
        elif op == "addi":
            r[a[0]] = val(a[1]) + val(a[2])
        elif op in ("cmpwi", "cmpdi", "cmpw"):
            field = int(a[0][2:]) if len(a) == 3 else 0
            x, y = signed(val(a[-2])), signed(val(a[-1]))
            cr[field] = (x > y) - (x < y)
        elif op in ("b", "ble", "bge", "beq", "bne", "bgt", "blt"):
            c = cr[int(a[0][2:])] if len(a) == 2 else cr[0]
            yes = op == "b" or {
                "ble": c <= 0,
                "bge": c >= 0,
                "beq": c == 0,
                "bne": c != 0,
                "bgt": c > 0,
                "blt": c < 0,
            }.get(op, False)
            if yes:
                n = int(a[-1], 0)
        elif op == "bl":
            lr = pc + 4
            native(int(a[0], 0))
        elif op == "blr":
            assert lr == 0xDEAD1234
            break
        elif op != "nop":
            raise AssertionError((hex(pc), op, a))
        pc = n
    else:
        raise AssertionError("callback failed to return")
    assert all(
        r[k] == original[k] for k in ["r1", "r2", *[f"r{j}" for j in range(14, 32)]]
    ), r
    assert cr == origcr and constructed == destroyed
    assert r["r3"] == original["r3"]
    return strings.get(0x61000), calls


brand = "College Hoops\nReborn"
cases = [
    ({}, "SEC\nMatchup"),
    ({"cross_conf": True}, brand),
    ({"timeout": True}, "TIMEOUT: HOME"),
    ({"timeout": True, "timeout_team": "AWAY"}, "TIMEOUT: AWAY"),
    ({"timeout": True, "suppressed": 1}, "SEC\nMatchup"),
    ({"category": 2, "bracket": 0x5A}, "March\nMadness"),
    ({"category": 2, "bracket": 0x5F, "swapped": True}, "March\nMadness"),
    ({"category": 1, "bracket": 0x55}, "NIT\nTournament"),
    ({"category": 2, "bracket": 0x59}, "NIT\nTournament"),
    ({"category": 2, "bracket": 9}, "SEC\nTournament"),
    ({"category": 2, "bracket": 8}, brand),
    ({"category": 2, "bracket": 0x60}, brand),
    ({"category": 2, "bracket": -1}, "SEC\nMatchup"),
    ({"category": 2, "bracket": 0x5A, "wrong_participant": True}, brand),
    ({"category": 2, "missing_record": True}, brand),
    ({"category": 2, "missing_key": True}, brand),
    ({"category": 2, "key": 0}, brand),
    ({"missing_home": True}, brand),
    ({"missing_away": True}, brand),
    ({"missing_conf": True}, brand),
    ({"conf_table_mismatch": True}, brand),
    ({"name": "ACC"}, "ACC\nMatchup"),
    ({"name": ""}, brand),
    ({"name": "a" * 24}, "a" * 24 + "\nMatchup"),
    ({"name": "a" * 25}, brand),
    ({"name": "SEC\nBAD"}, brand),
    ({"missing_name": True}, brand),
    ({"mode": 4}, brand),
    ({"mode": 7, "legacy_submode": 2}, brand),
    ({"mode": 8, "legacy_submode": 2}, brand),
    ({"missing_mode": True}, brand),
    ({"null_output": True}, "stale prior game"),
    ({"timeout": True, "missing_home": True}, brand),
    ({"timeout": True, "missing_away": True}, brand),
]


@pytest.mark.parametrize("case,expected", cases)
def test_native_provider_instruction_path(case, expected):
    actual, calls = run(case)
    assert actual == expected


def test_native_provider_overwrites_stale_context_across_transitions():
    old = "stale prior game"
    for case, expected in [cases[i] for i in [5, 2, 21, 14, 0, 1, 8, 3, 28]]:
        old, _ = run(case, old)
        assert old == expected

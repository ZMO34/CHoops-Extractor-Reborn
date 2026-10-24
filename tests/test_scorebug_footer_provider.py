from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
keystone = pytest.importorskip("keystone")
ROOT = Path(__file__).resolve().parents[1]
BASE = 0x89A900
TOC = 0xA64A94
code = bytes(
    keystone.Ks(
        keystone.KS_ARCH_PPC, keystone.KS_MODE_PPC64 | keystone.KS_MODE_BIG_ENDIAN
    ).asm(
        (ROOT / "docs/examples/scorebug-footer-provider.ppc").read_text(
            encoding="utf-8"
        ),
        addr=BASE,
    )[0]
)
ins = {
    i.address: i
    for i in capstone.Cs(
        capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN
    ).disasm(code, BASE)
}


def run(case, old="stale prior game"):
    mem = {}
    r = {f"r{i}": 0xABC00000 + i for i in range(32)}
    r.update(
        r1=0x900000,
        r2=TOC,
        r3=0x61000,
        r4=case.get("side", 0),
        r5=case.get("action", 0),
    )
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

    put(TOC - 0x6768, 0x31000 if not case.get("missing_home_state") else 0)
    put(TOC - 0x6764, 0x32000 if not case.get("missing_away_state") else 0)
    put(0x31028, 0x41000 if not case.get("missing_home_counter") else 0)
    put(0x32028, 0x42000 if not case.get("missing_away_counter") else 0)
    put(0x41008, case.get("home_fouls", 4))
    put(0x42008, case.get("away_fouls", 8))
    put(TOC - 0x6D70, 0x10000 if not case.get("missing_rules") else 0)
    put(0x10168, case.get("threshold", 7))
    put(0x21004, 0 if case.get("missing_name") else 0x51000)
    put(0x22004, 0 if case.get("missing_name") else 0x52000)
    wide(0x51000, "DUKE")
    wide(0x52000, "TCU")
    for a, s in [
        (0x89B900, "FOULS:{0}  {1}"),
        (0x89B940, ""),
        (0x89B960, "BONUS"),
        (0x89B980, "BONUS+"),
    ]:
        wide(a, s)
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
        assert r["r2"] == TOC, (hex(pc), hex(t))
        args = [r[f"r{j}"] for j in range(3, 6)]
        calls.append((t, args))
        v = 0
        if t == 0x57F050:
            v = 0 if case.get("missing_home") else 0x21000
        elif t == 0x57F064:
            v = (
                0
                if case.get("missing_away")
                else (0x21000 if case.get("same_teams") else 0x22000)
            )
        elif t == 0x49CAE4:
            expected = 0x31000 if case.get("side", 0) == 0 else 0x32000
            assert args[0] == expected, "bonus must use opponent foul state"
            v = case.get("double_bonus", 0)
        elif t == 0x4EF92C:
            strings[args[0]] = readwide(get(args[1] + 4))
        elif t == 0x49E1B4:
            assert signed(args[2]) == -1
            assert not r["r1"] <= args[1] < original["r1"], (
                "stack character buffer escaped"
            )
            strings[args[0]] = readwide(args[1])
            constructed += 1
        elif t == 0x49E0E4:
            assert strings[args[1]] == "FOULS:{0}  {1}"
            assert get(args[2]) == 0 and get(args[2] + 4) == 2
            rows = args[2] + 8
            assert get(rows) == 0 and get(rows + 8) == 0xA18CA0
            assert get(rows + 12) == 0 and get(rows + 20) == 0xA18CD8
            count = get(get(rows + 4))
            suffix = strings[get(rows + 16)]
            strings[args[0]] = f"FOULS:{count}  {suffix}"
        elif t == 0x49D604:
            assert args[2] == 1
            strings[args[0]] = strings[args[1]]
        elif t == 0x49F3A4:
            del strings[args[0]]
            destroyed += 1
        else:
            raise AssertionError(hex(t))
        for j in [0, *range(3, 13)]:
            r[f"r{j}"] = 0xF0000000 + j
        for j in (0, 1, 5, 7):
            cr[j] = 1
        r["r3"] = v
        if t in (0x49CAE4, 0x49E1B4, 0x49D604, 0x49F3A4, 0x49E0E4):
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


@pytest.mark.parametrize(
    "case,expected",
    [
        ({}, "FOULS:8  "),
        ({"side": 1}, "FOULS:4  BONUS"),
        ({"double_bonus": 1}, "FOULS:8  BONUS+"),
        ({"home_fouls": 7}, "FOULS:8  BONUS"),
        ({"home_fouls": 6}, "FOULS:8  "),
        ({"home_fouls": 5, "threshold": 5}, "FOULS:8  BONUS"),
        ({"threshold": 0}, "FOULS:8  "),
        ({"away_fouls": 0}, "FOULS:0  "),
        ({"away_fouls": 99}, "FOULS:99  "),
        ({"away_fouls": -1}, ""),
        ({"away_fouls": 100}, ""),
        ({"home_fouls": -1}, ""),
        ({"home_fouls": 100}, ""),
        ({"missing_home": True}, ""),
        ({"missing_away": True}, ""),
        ({"same_teams": True}, ""),
        ({"missing_home_state": True}, ""),
        ({"missing_away_state": True}, ""),
        ({"missing_home_counter": True}, ""),
        ({"missing_away_counter": True}, ""),
        ({"missing_rules": True}, ""),
        ({"null_output": True}, "stale prior game"),
        ({"action": 1}, "TCU"),
        ({"action": 1, "side": 1}, "DUKE"),
        ({"action": 1, "missing_name": True}, ""),
    ],
)
def test_footer_native_instructions(case, expected):
    actual, _ = run(case)
    assert actual == expected


def test_footer_resets_across_halftime_and_side_changes():
    value = "stale prior game"
    for case, expected in [
        ({}, "FOULS:8  "),
        ({"side": 1}, "FOULS:4  BONUS"),
        ({"side": 1, "away_fouls": 0, "home_fouls": 0}, "FOULS:0  "),
        ({"missing_home": True}, ""),
    ]:
        value, _ = run(case, value)
        assert value == expected

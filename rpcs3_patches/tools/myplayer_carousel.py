"""DEBUG probe: Legacy coaching carousel (offers and accepting a job) -> TTY.log.

Goal: learn what the user's job offers are and what accepting one changes, so a
patch can offer the school a MyPlayer transfers to. Static facts used:

  offers      0x12D9EA00, 8 bytes each (word0, score float); 0x592B08(i) returns word0
              (built by 0x5934A0)
  user list   0x12D9CE88, 0x14 bytes each; current index *0x12D9E9E4, count *0x12D9E9E0
  profiles    0x12E30DC8: count halfword +0x22, profile i at +0x28 + i * 0x3260
              (profile +4 = the team that user controls, 0x599ABC)
  team row    +0x30 coach, +0x15C team index (halfword); coach +8 team index (0x73905C)

Hooks (each logs, then runs the original instruction):
  0x592B08  offer getter (r3 = index); logs only when index or result changes
      OFFR idx word0 score w0+0 w0+4 w0+8 w0+0x30 team_index(w0+0x15C)
  0x594378  accept path start (r26 = offered word0)
      AC1R r26 r28 r29 r30 r31 r26+0x30 r26+0x15C r26+8
  0x5948D4  accept path end (r31 new team?, r30, r28 old team?)
      AC2R r26 r28 r29 r30 r31 r31+0x30 r28+0x30 r30+8
  both accept hooks also write:
      UENT cur count e[cur]+0 +4 +8 +0xC +0x10 e[0]+0
      PROF count p0+0 p0+4 p0+8 p0+0xC p1+4 p0+4 -> +0x30 p0+4 -> +0x15C
"""
import os
import sys

import myplayer_probe as P
import myplayer_court as C
import rank_hook_asm as H
import myplayer_bench as B

TITLE = 'DEBUG probe: coaching carousel offers and job accept -> TTY.log'
OFFERS, ULIST, UCUR, UCOUNT, PROF = 0x12D9EA00, 0x12D9CE88, 0x12D9E9E4, 0x12D9E9E0, 0x12E30DC8
HOOKS = (0x592B08, 0x594378, 0x5948D4)
_n = [0]


def lab():
    _n[0] += 1
    return f'g{_n[0]}'


def absw(addr):
    h, l = P.hi_lo(addr)
    return f"    lis 8, {h}\n    ori 8, 8, {l}\n    lwz 8, 0(8)\n"


def deref(start, offs, half_last=False):
    """r8 = start code; then follow offsets (skipping if r8 is not a pointer)."""
    code = start
    for k, off in enumerate(offs):
        l = lab()
        op = 'lhz' if (half_last and k == len(offs) - 1) else 'lwz'
        code += f"    cmplwi 7, 8, 0xffff\n    ble 7, {l}\n    srwi 0, 8, 30\n    cmpwi 7, 0, 0\n    bne 7, {l}\n    {op} 8, {off}(8)\n{l}:\n"
    return code


def reg(r):
    return f"    mr 8, {r}\n"


def common(g):
    h, l = P.hi_lo(ULIST)
    entry = (f"    lis 8, {P.hi_lo(UCUR)[0]}\n    ori 8, 8, {P.hi_lo(UCUR)[1]}\n    lwz 8, 0(8)\n"
             f"    mulli 8, 8, 0x14\n    lis 0, {h}\n    ori 0, 0, {l}\n    add 8, 8, 0\n")
    src = g.line('UENT', [absw(UCUR), absw(UCOUNT)] + [entry + f"    lwz 8, {o}(8)\n" for o in (0, 4, 8, 0xC, 0x10)] + [absw(ULIST)])
    p0 = PROF + 0x28; p1 = p0 + 0x3260
    cnt = f"    lis 8, {P.hi_lo(PROF)[0]}\n    ori 8, 8, {P.hi_lo(PROF)[1]}\n    lhz 8, 0x22(8)\n"
    src += g.line('PROF', [cnt, absw(p0), absw(p0 + 4), absw(p0 + 8), absw(p0 + 0xC), absw(p1 + 4),
                          deref(absw(p0 + 4), [0x30]), deref(absw(p0 + 4), [0x15C], True)])
    return src


def body(i):
    g = C.Gen()
    if i == 0:
        oh, ol = P.hi_lo(OFFERS)
        w0 = f"    ld 8, 0x88(1)\n    slwi 8, 8, 3\n    lis 0, {oh}\n    ori 0, 0, {ol}\n    add 8, 8, 0\n    lwz 8, 0(8)\n"
        sc = f"    ld 8, 0x88(1)\n    slwi 8, 8, 3\n    lis 0, {oh}\n    ori 0, 0, {ol}\n    add 8, 8, 0\n    lwz 8, 4(8)\n"
        src = P.SAVE + f"""    bl st
    .long -1
    .long -1
st:
    mflr 11
    ld 9, 0x88(1)
    slwi 9, 9, 3
    lis 0, {oh}
    ori 0, 0, {ol}
    add 9, 9, 0
    lwz 9, 0(9)
    ld 10, 0x88(1)
    lwz 0, 0(11)
    cmpw 7, 0, 10
    bne 7, chg
    lwz 0, 4(11)
    cmpw 7, 0, 9
    beq 7, out
chg:
    stw 10, 0(11)
    stw 9, 4(11)
"""
        src += g.line('OFFR', ["    ld 8, 0x88(1)\n", w0, sc, deref(w0, [0]), deref(w0, [4]), deref(w0, [8]),
                              deref(w0, [0x30]), deref(w0, [0x15C], True)])
        return src + "out:\n" + P.RESTORE
    tag = 'AC1R' if i == 1 else 'AC2R'
    extra = ([deref(reg(26), [0x30]), deref(reg(26), [0x15C], True), deref(reg(26), [8])] if i == 1 else
             [deref(reg(31), [0x30]), deref(reg(28), [0x30]), deref(reg(30), [8])])
    src = P.SAVE + g.line(tag, [reg(r) for r in (26, 28, 29, 30, 31)] + extra) + common(g)
    return src + P.RESTORE


def build(i):
    _n[0] = 0; code = B.assemble(body(i))
    _n[0] = 0; assert code == B.assemble(body(i), 0x40010000), 'not position independent'
    first = P.original(HOOKS[i])
    assert first >> 26 not in (16, 18, 19)
    return code + first.to_bytes(4, 'big')


def entry():
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "Diagnostic only. In Legacy\'s coaching carousel, logs each job offer the dialog reads and what accepting a job changes (user list, profile, coaches) to log/TTY.log. Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:']
    for i, hook in enumerate(HOOKS):
        code = build(i); words = [int.from_bytes(code[k:k + 4], 'big') for k in range(0, len(code), 4)]
        lines.append(f'      - [ calloc, 0x{hook:08x}, {len(words)} ] # CAR{i}')
        lines += [f'      - [ be32, 0x{hook:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

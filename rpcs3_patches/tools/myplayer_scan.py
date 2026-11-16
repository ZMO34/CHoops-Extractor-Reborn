"""DEBUG probe: find the in-memory copy of the game settings (the STG save).

The STG save (1076 bytes) starts 00000000 00000004 00000001 00000001 ... and has the
floats 75.0, 0.5, 0.5 at +0x20/+0x24/+0x28. Player Lock is the word at +0xF8 (it was
the only 0->1 flag between two saves). This probe scans the executable's static
read-write range (0x124F0000..0x13076138) for that header when play starts or resumes
(0x52FB8) and writes, per match:

    SCAN address word+0xF8 word+0xBC word+0xC0

to TTY.log. Registers, LR and CR are preserved; the original instruction runs after.
"""
import os
import sys

import myplayer_probe as P
import rank_hook_asm as H

LO, HI = 0x124F0000, 0x13076138 - 0x100
HOOK = 0x52FB8


def body():
    lo_h, lo_l = P.hi_lo(LO); hi_h, hi_l = P.hi_lo(HI)
    t = int.from_bytes(b'SCAN', 'big'); th, tl = P.hi_lo(t)
    src = P.SAVE + f"""    std 15, 0xD8(1)
    std 14, 0x158(1)
    lis 14, {lo_h}
    ori 14, 14, {lo_l}
    lis 15, {hi_h}
    ori 15, 15, {hi_l}
scan:
    lwz 0, 0x20(14)
    lis 12, 0x4296
    cmpw 7, 0, 12
    bne 7, nxt
    lwz 0, 0x24(14)
    lis 12, 0x3f00
    cmpw 7, 0, 12
    bne 7, nxt
    lwz 0, 0x28(14)
    cmpw 7, 0, 12
    bne 7, nxt
    lwz 0, 4(14)
    cmpwi 7, 0, 4
    bne 7, nxt
    lis 0, {th}
    ori 0, 0, {tl}
    stw 0, 0xE0(1)
    addi 10, 1, 0xE4
"""
    src += P.hex8(0, "    mr 8, 14\n")
    src += P.hex8(1, "    lwz 8, 0xF8(14)\n")
    src += P.hex8(2, "    lwz 8, 0xBC(14)\n")
    src += P.hex8(3, "    lwz 8, 0xC0(14)\n")
    src += """    li 0, 10
    stb 0, 0(10)
    addi 10, 10, 1
    addi 4, 1, 0xE0
    subf 5, 4, 10
    li 3, 0
    addi 6, 1, 0x150
    li 11, 403
    sc
nxt:
    addi 14, 14, 4
    cmplw 7, 14, 15
    blt 7, scan
    ld 15, 0xD8(1)
    ld 14, 0x158(1)
"""
    return src + P.RESTORE


def build():
    code = H.assemble(body(), 0x30000000)
    first = P.original(HOOK)
    assert first >> 26 not in (16, 18, 19)
    return code + first.to_bytes(4, 'big')


TITLE = 'DEBUG probe: find game settings in memory -> TTY.log'


def entry():
    code = build(); words = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "Diagnostic only. When a game starts or resumes, scans static memory for the game-settings block and writes its address and the Player Lock word to log/TTY.log. Do not combine with the MyPlayer lock probes (same hook). Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # SCAN']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    P.TITLE_SAVE = P.TITLE
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

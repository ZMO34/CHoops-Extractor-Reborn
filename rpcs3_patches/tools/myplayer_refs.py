"""DEBUG probe: find records that point at the user's roster entry (to locate his game stats).

Hook 0x29F344 (per-frame control update, r3 = court slot; MyPlayer / Player Lock ON).
For the user-controlled slot, about every 3.4 s it reads his roster entry (slot+0x64)
and scans static read-write memory 0x124F0000..0x13076000 for words equal to it.
For up to 24 hits it writes to TTY.log 0xC0 bytes starting 0x40 before the hit:

    RFnn hit w0..w7        nn = 0x20-byte part (0..5), first part starts at hit-0x40

Matching the samples with the box score shows which record holds his game stats.
"""
import os
import sys

import myplayer_probe as P
import myplayer_court as C
import rank_hook_asm as H

HOOK = 0x29F344
TITLE = 'DEBUG probe: records pointing at the user player -> TTY.log'
LO, HI = 0x124F0000, 0x13076000


def body():
    g = C.Gen()
    lo_h, lo_l = P.hi_lo(LO); hi_h, hi_l = P.hi_lo(HI)
    src = P.SAVE + f"""    std 14, 0xD8(1)
    std 15, 0x158(1)
    std 16, 0x60(1)
    std 17, 0x68(1)
    ld 14, 0x88(1)
    cmplwi 7, 14, 0xffff
    ble 7, early
    lwz 15, 0x10(14)
    cmplwi 7, 15, 0xffff
    ble 7, early
    lwz 0, 0(15)
    cmpwi 7, 0, -1
    beq 7, early
    mftb 0
    rlwinm. 0, 0, 12, 24, 31
    bne 0, early
    lwz 14, 0x64(14)
    cmplwi 7, 14, 0xffff
    ble 7, early
    b go
early:
    b out
go:
    lis 15, {lo_h}
    ori 15, 15, {lo_l}
    lis 16, {hi_h}
    ori 16, 16, {hi_l}
    li 17, 24
scan:
    lwz 0, 0(15)
    cmpw 7, 0, 14
    bne 7, next
"""
    for part in range(6):
        src += g.line(f'RF{part:02x}', ["    mr 8, 15\n"] + [f"    lwz 8, {part * 0x20 - 0x40 + 4 * k}(15)\n" for k in range(8)])
    src += """    addi 17, 17, -1
    cmpwi 7, 17, 0
    beq 7, out
next:
    addi 15, 15, 4
    cmplw 7, 15, 16
    blt 7, scan
out:
    ld 14, 0xD8(1)
    ld 15, 0x158(1)
    ld 16, 0x60(1)
    ld 17, 0x68(1)
"""
    return src + P.RESTORE


def build():
    code = H.assemble(body(), 0x30000000)
    first = P.original(HOOK)
    assert first >> 26 not in (16, 18, 19)
    return code + first.to_bytes(4, 'big')


def entry():
    code = build(); words = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "Diagnostic only (MyPlayer / Player Lock ON). About every 3 seconds during play, finds records in static memory that point at the user player\'s roster entry and dumps them to log/TTY.log. Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # REFS']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

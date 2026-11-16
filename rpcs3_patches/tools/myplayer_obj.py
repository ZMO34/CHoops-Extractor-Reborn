"""DEBUG probe: dump the user's whole in-game player object (slot+0x64), to find his game stats.

The object slot+0x64 points to is 0x1140 bytes long (a team's objects are 0x1140 apart,
e.g. 0x12D737C0, 0x12D74900, ...); its 30 ratings (x100) are at +0x2C. The box score
counters are expected inside it. Hook 0x29F344 (per-frame control update, r3 = court
slot; MyPlayer / Player Lock ON). For the user-controlled slot, about every 6.9 s
(timebase bits 20..28 zero) it writes the object to TTY.log:

    Onnn obj w0..w7      nnn = 0x20-byte part (0x000..0x089)
"""
import os
import sys

import myplayer_probe as P
import myplayer_court as C
import rank_hook_asm as H

HOOK = 0x29F344
TITLE = 'DEBUG probe: user player object dump -> TTY.log'
SIZE = 0x1140
TEAM = 0x800             # also the in-game team object (slot+0x3C), for the lineup: Tnnn team w0..w7


def body():
    g = C.Gen()
    src = P.SAVE + """    std 14, 0xD8(1)
    std 15, 0x158(1)
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
    rlwinm. 0, 0, 12, 23, 31
    bne 0, early
    lwz 15, 0x3C(14)
    lwz 14, 0x64(14)
    cmplwi 7, 14, 0xffff
    ble 7, early
    b go
early:
    b out
go:
"""
    for part in range(SIZE // 0x20):
        src += g.line(f'O{part:03x}', ["    mr 8, 14\n"] + [f"    lwz 8, {part * 0x20 + 4 * k}(14)\n" for k in range(8)])
    src += """    cmplwi 7, 15, 0xffff
    ble 7, noteam
    b team
noteam:
    b out
team:
"""
    for part in range(TEAM // 0x20):
        src += g.line(f'T{part:03x}', ["    mr 8, 15\n"] + [f"    lwz 8, {part * 0x20 + 4 * k}(15)\n" for k in range(8)])
    src += """out:
    ld 14, 0xD8(1)
    ld 15, 0x158(1)
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
             '    Notes: "Diagnostic only (MyPlayer / Player Lock ON). About every 7 seconds during play, dumps the user player\'s whole in-game player object to log/TTY.log. Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # OBJ']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

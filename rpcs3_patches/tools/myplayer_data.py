"""DEBUG probe: dump what the user's court slot points to, to find his roster row and game stats.

Hook 0x29F344 (per-frame control update, r3 = court slot; runs with Player Lock /
MyPlayer ON). For the user-controlled slot, about every 3.4 s (timebase bits 20..27
zero, no state kept) it writes to TTY.log the slot words +0x60..+0xDF (SLT0..3) and, for
each slot field +0x60..+0xDC that
points into static memory (0x10000000..0x1306FFFF), 0x60 bytes at its target:

    Sffp target w0..w7     ff = slot field / 4, p = 0x20-byte part (0..2)

(v1 dumped slot+0x04 itself, the animation skeleton; v2 fields +0x04..+0x5C held
physics, AI and fatigue state but no box score or roster row.)
Comparing samples with the player's box score shows the stat record; a record whose
first words point to name strings is the roster row.
"""
import os
import sys

import myplayer_probe as P
import myplayer_court as C
import rank_hook_asm as H

HOOK = 0x29F344
TITLE = 'DEBUG probe: user player data and stats -> TTY.log'


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
    rlwinm. 0, 0, 12, 24, 31
    bne 0, early
    b go
early:
    b out
go:
"""
    for n, base in enumerate((0x60, 0x80, 0xA0, 0xC0)):
        src += g.line(f'SLT{n}', ["    mr 8, 14\n"] + [f"    lwz 8, {base + 4 * k}(14)\n" for k in range(8)])
    for f in range(24, 56):
        src += f"""    lwz 15, {4 * f}(14)
    lis 0, 0x1000
    cmplw 7, 15, 0
    blt 7, skip{f}
    lis 0, 0x1307
    cmplw 7, 15, 0
    bge 7, skip{f}
"""
        for part in range(3):
            src += g.line(f'S{f:02x}{part}', ["    mr 8, 15\n"] + [f"    lwz 8, {part * 0x20 + 4 * k}(15)\n" for k in range(8)])
        src += f"skip{f}:\n"
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
             '    Notes: "Diagnostic only (MyPlayer / Player Lock ON). About every 3 seconds during play, dumps what the user-controlled court slot points to (0x60 bytes per field) to log/TTY.log. Leave disabled normally."',
             '    Patch Version: 3.0', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # PDAT']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

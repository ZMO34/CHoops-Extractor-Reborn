"""DEBUG probe: camera state while MyPlayer is on (to make the camera follow your player).

The game's camera table (*TOC-0x7A8C = 0x12C75498, 31 entries of 0x2C: +0 camera mode,
+4 caption) ends with mode 0x20, caption 0xC80F7FBB ("Player Lock", shown as
"MyPlayer" since the english.iff relabel). The current camera state is at
0x12C759EC (+0 table index, +4 / +8 / +0xC / +0x10 set by 0x4C079C).

Hook 0x29F344 (per-frame control update, r3 = court slot; MyPlayer ON). For the
user-controlled slot, about every 3.4 s it writes to TTY.log:

    CAMn  w0..w7          n = 0..7: 0x12C759EC + 0x20 * n (state and what follows)
    USR   slot  slot+0x04 slot+0x3C slot+0x64  obj+0 obj+4  MyPlayer value  0
"""
import os
import sys

import myplayer_probe as P
import myplayer_court as C
import rank_hook_asm as H

HOOK = 0x29F344
TITLE = 'DEBUG probe: camera state with MyPlayer -> TTY.log'
CAM = 0x12C759EC
FLAG = 0x1283958C + 0xF8


def body():
    g = C.Gen()
    ch, cl = P.hi_lo(CAM); fh, fl = P.hi_lo(FLAG)
    src = P.SAVE + f"""    std 14, 0xD8(1)
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
    lis 15, {ch}
    ori 15, 15, {cl}
"""
    for n in range(8):
        src += g.line(f'CAM{n}', ["    mr 8, 15\n"] + [f"    lwz 8, {n * 0x20 + 4 * k}(15)\n" for k in range(8)])
    usr = ["    mr 8, 14\n", "    lwz 8, 4(14)\n", "    lwz 8, 0x3C(14)\n", "    lwz 8, 0x64(14)\n",
           "    lwz 8, 0x64(14)\n    cmplwi 7, 8, 0xffff\n    ble 7, u0\n    lwz 8, 0(8)\nu0:\n",
           "    lwz 8, 0x64(14)\n    cmplwi 7, 8, 0xffff\n    ble 7, u1\n    lwz 8, 4(8)\nu1:\n",
           f"    lis 8, {fh}\n    ori 8, 8, {fl}\n    lwz 8, 0(8)\n", "    li 8, 0\n"]
    src += g.line('USR', usr)
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
             '    Notes: "Diagnostic only (MyPlayer ON). About every 3 seconds during play, writes the camera state and the user player to log/TTY.log. Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # CAM']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

"""DEBUG probe: what changes in the user's in-game player object across a substitution.

Hook: 0x29F344, the per-player control update (r3 = player object; player+0x10 is its
controller record, whose first word is the user number or -1 for CPU). For a
user-controlled player, about every 3.4 s (when timebase bits 20..27 are zero, so no
state is kept) it writes to TTY.log:

    PLA0 obj ctrlid team w0 w1 w2 w3 w4 w5 w6 w7      (obj+0x00..0x1C)
    PLA1 obj w8 .. w15                                 (obj+0x20..0x3C)
    PLA2 obj w16 .. w23                                (obj+0x40..0x5C)
    TEAM obj p0 p1 p2 p3 p4 p5 p6                      (team+0x20 list, next = +0x60)

Registers, LR and CR are preserved; the original first instruction runs after.
"""
import os
import sys

import myplayer_probe as P
import rank_hook_asm as H

HOOK = 0x29F344
TITLE = 'DEBUG probe: user player object across substitutions -> TTY.log'


class Gen:
    def __init__(self):
        self.n = 0

    def hexv(self, load):
        self.n += 1
        return P.hex8(f'c{self.n}', load)

    def line(self, tag, loads):
        t = int.from_bytes(tag.encode(), 'big'); th, tl = P.hi_lo(t)
        src = f"    lis 0, {th}\n    ori 0, 0, {tl}\n    stw 0, 0xE0(1)\n    addi 10, 1, 0xE4\n"
        for ld in loads:
            src += self.hexv(ld)
        src += """    li 0, 10
    stb 0, 0(10)
    addi 10, 10, 1
    addi 4, 1, 0xE0
    subf 5, 4, 10
    li 3, 0
    addi 6, 1, 0x150
    li 11, 403
    sc
"""
        return src


def body():
    g = Gen()
    src = P.SAVE + """    std 14, 0xD8(1)
    std 15, 0x158(1)
    ld 14, 0x88(1)
    cmplwi 7, 14, 0xffff
    ble 7, out
    lwz 15, 0x10(14)
    cmplwi 7, 15, 0xffff
    ble 7, out
    lwz 0, 0(15)
    cmpwi 7, 0, -1
    beq 7, out
    mftb 0
    rlwinm. 0, 0, 12, 24, 31
    bne 0, out
"""
    obj = "    mr 8, 14\n"
    src += g.line('PLA0', [obj, "    lwz 8, 0(15)\n", "    lwz 8, 0x3C(14)\n"] + [f"    lwz 8, {4 * k}(14)\n" for k in range(8)])
    src += g.line('PLA1', [obj] + [f"    lwz 8, {4 * k}(14)\n" for k in range(8, 16)])
    src += g.line('PLA2', [obj] + [f"    lwz 8, {4 * k}(14)\n" for k in range(16, 24)])
    # team list: r15 walks team+0x20, +0x60 ... (up to 7); missing entries print 0
    team = ["    mr 8, 14\n"]
    walk = """    lwz 15, 0x3C(14)
    cmplwi 7, 15, 0xffff
    ble 7, z{k}
    lwz 15, 0x20(15)
"""
    loads = []
    for k in range(7):
        if k == 0:
            loads.append("    lwz 15, 0x3C(14)\n    li 8, 0\n    cmplwi 7, 15, 0xffff\n    ble 7, s0\n    lwz 15, 0x20(15)\n    mr 8, 15\ns0:\n")
        else:
            loads.append(f"    li 8, 0\n    cmplwi 7, 15, 0xffff\n    ble 7, s{k}\n    lwz 15, 0x60(15)\n    mr 8, 15\ns{k}:\n")
    src += g.line('TEAM', team + loads)
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
             '    Notes: "Diagnostic only. About every 3 seconds during play, writes the user-controlled player object, its first 0x60 bytes and the team on-court list to log/TTY.log. Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # PLAY']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

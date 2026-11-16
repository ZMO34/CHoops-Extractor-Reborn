"""MyPlayer bench patch: with Player Lock ON, sit out with your player.

How the game works (BLUS30078, 2026-27 year-patched EBOOT):
  * 0x29DCBC runs once per gameplay frame. It walks every on-court player slot
    (head pointer at 0x12ACCDC0, next slot at +0x5C) and processes controller input
    for slots whose controller record (slot+0x10) has a user number in its first
    word (-1 = CPU). With Player Lock ON (settings 0x1283958C + 0xF8) the game never
    moves control on its own.
  * A slot's player is identified by slot+0x64, his roster entry (anchor = roster row
    + 16; the 30 ratings, x100, are at anchor+0x2C). v1.0 used slot+0x04, which is the
    animation skeleton and can change while the player stays on court. A
    substitution swaps the player data into the same slot, so control stays with the
    slot and passes to whoever subs in.
  * 0x29CA70(a, b) swaps two controller records (user number and input state); the
    game uses it for every hand-over of control.

This patch hooks the start of 0x29DCBC. For controller 1 (user 0), while Player Lock
is ON:
  * Your player is captured as the player you control on the first frame after a
    pause or a stoppage of at least ~0.2 s, but only if you are now on a different
    slot (you picked someone) or none was captured yet.
  * If your player is not in any on-court slot, the controller record of whoever
    holds your controller is swapped into a spare record kept in this block, so no
    one on court is user-controlled and the CPU plays (you watch, or sim to the next
    dead ball).
  * If your player is on court and someone else holds your controller (or it is
    parked), control is swapped back to him.

Data kept at the start of the block (jumped over):
  +0x00 my roster entry   +0x04 slot I last controlled   +0x08 parked flag
  +0x0C last timebase     +0x10 spare controller record (0x40 bytes, user -1)
"""
import os
import struct
import sys

import keystone

import myplayer_probe as P
from rank_asm import BRANCH_BO_BI

HOOK = 0x29DCBC
SWAP = 0x29CA70
LOCK_FLAG = 0x1283958C + 0xF8
PLAYERS = 0x12ACCDC0
GAP = 0x01000000          # timebase ticks (~0.21 s at 79.8 MHz)
TITLE = 'MyPlayer: sit on the bench with your player (requires Player Lock ON)'

ME, LAST, PARK, TB, SPARE = 0x00, 0x04, 0x08, 0x0C, 0x10
ID = 0x64                 # slot field: the player's roster entry (anchor = row + 16)

SRC = f"""
    stdu 1, -0x160(1)
    std 0, 0x70(1)
    mflr 0
    std 0, 0x78(1)
    mfcr 0
    stw 0, 0x80(1)
    std 3, 0x88(1)
    std 4, 0x90(1)
    std 5, 0x98(1)
    std 6, 0xA0(1)
    std 7, 0xA8(1)
    std 8, 0xB0(1)
    std 9, 0xB8(1)
    std 10, 0xC0(1)
    std 11, 0xC8(1)
    std 12, 0xD0(1)
    std 14, 0xD8(1)
    std 15, 0xE0(1)
    std 16, 0xE8(1)
    std 17, 0xF0(1)
    std 18, 0xF8(1)
    std 19, 0x100(1)
    bl getdata
data:
{chr(10).join(['    .long 0'] * 4 + ['    .long -1'] + ['    .long 0'] * 15)}
getdata:
    mflr 14
    lis 9, {P.hi_lo(LOCK_FLAG)[0]}
    ori 9, 9, {P.hi_lo(LOCK_FLAG)[1]}
    lwz 0, 0(9)
    cmpwi 7, 0, 0
    beq 7, out
    mftb 0
    lwz 9, {TB}(14)
    stw 0, {TB}(14)
    subf 9, 9, 0
    lis 0, {P.hi_lo(GAP)[0]}
    cmplw 7, 9, 0
    li 19, 0
    blt 7, nogap
    li 19, 1
nogap:
    li 16, 0
    li 17, 0
    lwz 18, {ME}(14)
    lis 9, {P.hi_lo(PLAYERS)[0]}
    ori 9, 9, {P.hi_lo(PLAYERS)[1]}
    lwz 15, 0(9)
walk:
    cmplwi 7, 15, 0xffff
    ble 7, walked
    lwz 9, 0x10(15)
    cmplwi 7, 9, 0xffff
    ble 7, nxt
    lwz 0, 0(9)
    cmpwi 7, 0, 0
    bne 7, notu
    mr 16, 15
notu:
    cmpwi 7, 18, 0
    beq 7, nxt
    lwz 0, {ID}(15)
    cmpw 7, 0, 18
    bne 7, nxt
    mr 17, 15
nxt:
    lwz 15, 0x5C(15)
    b walk
walked:
@BEAT
    lwz 0, {PARK}(14)
    cmpwi 7, 0, 0
    bne 7, decide
    cmpwi 7, 16, 0
    beq 7, decide
    cmpwi 7, 18, 0
    beq 7, capture
    cmpwi 7, 19, 0
    beq 7, decide
    lwz 0, {LAST}(14)
    cmpw 7, 0, 16
    beq 7, decide
capture:
    lwz 18, {ID}(16)
    stw 18, {ME}(14)
    mr 17, 16
@LOG CAPT
decide:
    cmpwi 7, 18, 0
    beq 7, out
    cmpwi 7, 17, 0
    bne 7, oncourt
    cmpwi 7, 16, 0
    beq 7, out
    lwz 0, {PARK}(14)
    cmpwi 7, 0, 0
    bne 7, reclaim
@LOG PARK
    lwz 3, 0x10(16)
    addi 4, 14, {SPARE}
    bla {hex(SWAP)}
    li 0, 1
    stw 0, {PARK}(14)
    li 0, 0
    stw 0, {LAST}(14)
    b out
reclaim:
@LOG RCLM
    lwz 9, 0x10(16)
    li 0, -1
    stw 0, 0(9)
    b out
oncourt:
    cmpw 7, 16, 17
    beq 7, settle
    cmpwi 7, 16, 0
    beq 7, fromspare
@LOG SWAP
    lwz 3, 0x10(16)
    lwz 4, 0x10(17)
    bla {hex(SWAP)}
    b settle
fromspare:
    lwz 0, {PARK}(14)
    cmpwi 7, 0, 0
    beq 7, out
@LOG UNPK
    addi 3, 14, {SPARE}
    lwz 4, 0x10(17)
    bla {hex(SWAP)}
    li 0, 0
    stw 0, {PARK}(14)
settle:
    stw 17, {LAST}(14)
out:
    ld 14, 0xD8(1)
    ld 15, 0xE0(1)
    ld 16, 0xE8(1)
    ld 17, 0xF0(1)
    ld 18, 0xF8(1)
    ld 19, 0x100(1)
    lwz 0, 0x80(1)
    mtcrf 0xff, 0
    ld 0, 0x78(1)
    mtlr 0
    ld 0, 0x70(1)
    ld 3, 0x88(1)
    ld 4, 0x90(1)
    ld 5, 0x98(1)
    ld 6, 0xA0(1)
    ld 7, 0xA8(1)
    ld 8, 0xB0(1)
    ld 9, 0xB8(1)
    ld 10, 0xC0(1)
    ld 11, 0xC8(1)
    ld 12, 0xD0(1)
    addi 1, 1, 0x160
"""


def assemble(src, base=0x30000000):
    """Like rank_hook_asm.assemble, plus `bl label` and `.long N`."""
    ks = keystone.Ks(keystone.KS_ARCH_PPC, keystone.KS_MODE_PPC64 | keystone.KS_MODE_BIG_ENDIAN)
    lines = [l.strip() for l in src.strip().splitlines() if l.strip()]
    local, pc = {}, base
    for l in lines:
        if l.endswith(':'):
            local[l[:-1]] = pc
        else:
            pc += 4
    out, pc = b'', base
    for l in lines:
        if l.endswith(':'):
            continue
        mn, _, rest = l.partition(' ')
        args = [a.strip() for a in rest.split(',')] if rest else []
        if mn == '.long':
            word = int(args[0], 0) & 0xFFFFFFFF
        elif mn == 'bla':
            t = int(args[0], 0); assert 0 <= t < (1 << 25) and t % 4 == 0
            word = (18 << 26) | t | 3
        elif mn in ('b', 'bl'):
            off = local[args[-1]] - pc
            word = (18 << 26) | (off & 0x3FFFFFC) | (1 if mn == 'bl' else 0)
        elif mn in BRANCH_BO_BI:
            off = local[args[-1]] - pc
            bo, bit = BRANCH_BO_BI[mn]
            field = int(args[0]) if len(args) == 2 else 0
            word = (16 << 26) | (bo << 21) | ((field * 4 + bit) << 16) | (off & 0xFFFC)
        else:
            enc, _ = ks.asm(l, pc)
            assert len(enc) == 4, l
            word = int.from_bytes(bytes(enc), 'big')
        out += word.to_bytes(4, 'big')
        pc += 4
    return out


LOG_NOTE = """
Debug build (`debug=True`): the frame grows to 0x200 and each decision writes a line
to TTY.log through sys_tty_write (buffer at sp+0x140):

    CAPT/PARK/RCLM/SWAP/UNPK  U M me U.data park gap last
    BEAT (about every 3.4 s)  same fields

U = slot holding controller 1, M = slot of my player, me = my player data.
"""


def expand(src, debug):
    """Turn the @LOG/@BEAT markers into TTY logging (debug) or nothing."""
    out = []; n = 0
    for line in src.splitlines():
        t = line.strip()
        if not t.startswith('@'):
            out.append(line); continue
        if not debug:
            continue
        n += 1
        tag = 'BEAT' if t == '@BEAT' else t.split()[1]
        if t == '@BEAT':
            out += ['    mftb 0', '    rlwinm. 0, 0, 12, 24, 31', f'    bne 0, nolog{n}']
        th, tl = P.hi_lo(int.from_bytes(tag.encode(), 'big'))
        out += [f'    lis 0, {th}', f'    ori 0, 0, {tl}', '    stw 0, 0x140(1)', '    addi 10, 1, 0x144']
        NL = chr(10)
        loads = ['    mr 8, 16', '    mr 8, 17', '    mr 8, 18',
                 NL.join(['    li 8, 0', '    cmpwi 7, 16, 0', f'    beq 7, ud{n}', f'    lwz 8, {ID}(16)', f'ud{n}:']),
                 f'    lwz 8, {PARK}(14)', '    mr 8, 19', f'    lwz 8, {LAST}(14)']
        for k, ld in enumerate(loads):
            out += P.hex8(f'L{n}_{k}', ld + NL).splitlines()
        out += ['    li 0, 10', '    stb 0, 0(10)', '    addi 10, 10, 1', '    addi 4, 1, 0x140',
                '    subf 5, 4, 10', '    li 3, 0', '    addi 6, 1, 0x1D0', '    li 11, 403', '    sc',
                f'nolog{n}:']
    text = chr(10).join(out) + chr(10)
    if debug:
        text = text.replace('stdu 1, -0x160(1)', 'stdu 1, -0x200(1)').replace('addi 1, 1, 0x160', 'addi 1, 1, 0x200')
    return text


def build(debug=False):
    src = expand(SRC, debug)
    code = assemble(src)
    assert code == assemble(src, 0x40010000), 'not position independent'
    first = P.original(HOOK)
    assert first == 0xF821FE71, hex(first)           # stdu r1,-0x190(r1)
    return code + first.to_bytes(4, 'big')


DEBUG = False


def entry():
    code = build(DEBUG); words = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "Needs Player Lock ON (Options > Game Settings). Controller 1 only. Your player is the one you are locked to when play starts or resumes after you pick someone. When the CPU subs him out, nobody on the court is yours and the CPU plays (watch, or sim to the next dead ball); when he checks back in, you control him again. The game would otherwise hand you the sub who took his spot. Code cave (RPCS3 calloc) at the start of the per-frame control update 0x29DCBC; uses the game\'s own control hand-over 0x29CA70."',
             '    Patch Version: 1.1', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # MyPlayer bench']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

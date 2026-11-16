"""DEBUG probes for the MyPlayer bench patch: log controller-1 lock state to TTY.log.

Each probe is an RPCS3 calloc block at a function's first instruction. It writes one
line through sys_tty_write (syscall 403) and then runs the original instruction:

    TAG caller r3 r4 lock ctrl locked ctrlword name

  caller   return address of the probed call
  r3, r4   the call's first two arguments (user index, actor pointer for setters)
  lock     word at settings+0x14 (0x57B438 reads it as the Player Lock switch)
  ctrl     user 0's controlled actor   (user table 0x128397EC + 0x4C)
  locked   user 0's locked actor       (user table + 0x50)
  ctrlword first word of the controlled actor
  name     up to 16 ASCII bytes at controlled actor + 4 (0x1E8DD8 returns that as text)

Every volatile register, LR and CR are preserved.
"""
import os
import re
import struct
import sys

import yaml

import rank_hook_asm as H

EBOOT = r'D:/RPCS3 2026/dev_hdd0/game/BLUS30078/USRDIR/EBOOT.elf'
SETTINGS = 0x12D731B0          # settings object (TOC 0xA64A94 - 0x40F0 holds this address)
USERS = 0x128397EC             # user table (TOC 0xA54AC8 - 0x6FF4 holds this address)
CTRL0, LOCKED0 = USERS + 0x4C, USERS + 0x50

PROBES = [
    ('SETC', 0x74EB4),   # set user's controlled actor (r3 user, r4 actor)
    ('SETL', 0x74EDC),   # set user's locked actor
    ('LOCK', 0x52FB8),   # lock every user to his current actor (runs when play resumes)
    ('UPDT', 0x52AAC),   # re-pick a user's actor (controller setup / side changes)
]

SAVE = """
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
"""
RESTORE = """
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


def hi_lo(v):
    return hex((v >> 16) & 0xFFFF), hex(v & 0xFFFF)


def load_abs(reg, addr):
    """reg = word at absolute address."""
    h, l = hi_lo(addr)
    return f"    lis {reg}, {h}\n    ori {reg}, {reg}, {l}\n    lwz {reg}, 0({reg})\n"


def hex8(n, load):
    """Append ' ' + 8 hex digits of r8 (loaded by `load`) at r10; r10 ends after them."""
    return (load + f"""    li 0, 0x20
    stb 0, 0(10)
    addi 10, 10, 8
    li 9, 8
h{n}:
    andi. 12, 8, 15
    addi 12, 12, 48
    cmpwi 7, 12, 57
    ble 7, d{n}
    addi 12, 12, 39
d{n}:
    stb 12, 0(10)
    addi 10, 10, -1
    srdi 8, 8, 4
    addi 9, 9, -1
    cmpwi 7, 9, 0
    bne 7, h{n}
    addi 10, 10, 9
""")


def body(tag):
    t = int.from_bytes(tag.encode(), 'big'); th, tl = hi_lo(t)
    src = SAVE + f"    lis 0, {th}\n    ori 0, 0, {tl}\n    stw 0, 0xE0(1)\n    addi 10, 1, 0xE4\n"
    src += hex8(0, "    ld 8, 0x78(1)\n")
    src += hex8(1, "    ld 8, 0x88(1)\n")
    src += hex8(2, "    ld 8, 0x90(1)\n")
    src += hex8(3, load_abs('8', SETTINGS + 0x14))
    src += hex8(4, load_abs('8', CTRL0))
    src += hex8(5, load_abs('8', LOCKED0))
    # ctrlword + name only when user 0 controls an actor
    src += load_abs('7', CTRL0) + "    cmplwi 7, 7, 0xffff\n    ble 7, fin\n"
    src += hex8(6, "    lwz 8, 0(7)\n")
    src += """    li 0, 0x20
    stb 0, 0(10)
    addi 10, 10, 1
    addi 7, 7, 4
    li 9, 16
nm:
    lbz 12, 0(7)
    cmpwi 7, 12, 0
    beq 7, fin
    cmpwi 7, 12, 0x20
    blt 7, q
    cmpwi 7, 12, 0x7e
    ble 7, ok
q:
    li 12, 0x3f
ok:
    stb 12, 0(10)
    addi 10, 10, 1
    addi 7, 7, 1
    addi 9, 9, -1
    cmpwi 7, 9, 0
    bne 7, nm
fin:
    li 0, 10
    stb 0, 0(10)
    addi 10, 10, 1
    addi 4, 1, 0xE0
    subf 5, 4, 10
    li 3, 0
    addi 6, 1, 0x150
    li 11, 403
    sc
"""
    return src + RESTORE


def original(addr):
    with open(EBOOT, 'rb') as f:
        f.seek(addr - 0x10000)
        return struct.unpack('>I', f.read(4))[0]


def build(tag, addr):
    code = H.assemble(body(tag), 0x30000000)
    first = original(addr)
    assert first >> 26 not in (16, 18, 19), f'{addr:#x}: first instruction is a branch'
    return code + first.to_bytes(4, 'big')


TITLE = 'DEBUG probes: MyPlayer lock and substitutions -> TTY.log'


def entry():
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "Diagnostic only. Logs controller 1 player-lock state to log/TTY.log whenever the game sets, locks or re-picks a controlled player. Leave disabled normally."',
             '    Patch Version: 1.0', '    Patch:']
    for tag, addr in PROBES:
        code = build(tag, addr)
        words = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
        lines.append(f'      - [ calloc, 0x{addr:08x}, {len(words)} ] # {tag}')
        lines += [f'      - [ be32, 0x{addr:08x}, 0x{w:08x} ]' for w in words]
    return '\n'.join(lines) + '\n'


def install(path):
    """Add or replace the entry in the first PPU section of a patch file."""
    txt = open(path, encoding='utf-8').read(); block = entry()
    key = f'  "{TITLE}":'
    if key in txt:
        i = txt.index(key); m = re.compile(r'^  "|^PPU-', re.M).search(txt, i + 5)
        txt = txt[:i] + block + txt[m.start() if m else len(txt):]
    else:
        m = re.compile(r'^PPU-', re.M); first = m.search(txt); second = m.search(txt, first.end())
        at = second.start() if second else len(txt)
        txt = txt[:at].rstrip('\n') + '\n\n' + block + '\n' + txt[at:]
    open(path, 'w', encoding='utf-8', newline='\n').write(txt)
    d = yaml.safe_load(open(path, encoding='utf-8'))
    root = [k for k in d if k.startswith('PPU')][0]
    e = d[root][TITLE]['Patch']
    print(path, 'probe lines', len(e), 'callocs', sum(x[0] == 'calloc' for x in e))


if __name__ == '__main__':
    for p in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        install(p)

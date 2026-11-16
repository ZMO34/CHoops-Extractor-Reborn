"""Write the modern three-point boundary entry into the RPCS3 patch file.

The court initializer (0x534FCC) clamps two globals with one constant, 612.14 cm
(the 19 ft 9 in line plus the game's own 4 in): 0x12CAB9A4 is the arc radius and
0x12CAB9A0 the straight side limit used behind the basket line (predicate
0x3CA128, signed distance 0x3CBE08). The tail of the initializer (0x535054 ..
0x5350B8) is rewritten to clamp them separately with constants built in the red
zone: arc 22 ft 1 3/4 in and corners 21 ft 7 7/8 in, each plus the same 4 in.
"""
import os
import struct
import sys

ELF = r'D:/RPCS3 2026/dev_hdd0/game/BLUS30078/USRDIR/EBOOT.elf'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, '..', 'BLUS30078_imported_patch.yml')
NAME = 'Three-point line: modern NCAA distance (22 ft 1 3/4 in, was 19 ft 9 in)'
ANCHOR = '  "NCAA Tournament: 68 teams with a four-game First Four (Stage 1)":'
OLD = 612.1399536132812
ARC = OLD + (22 * 12 + 1.75 - (19 * 12 + 9)) * 2.54
SIDE = OLD + (21 * 12 + 7.875 - (19 * 12 + 9)) * 2.54
START = 0x535054


def f32(x):
    return struct.unpack('>I', struct.pack('>f', x))[0]


def d_form(op, rt, ra, disp):
    return op << 26 | rt << 21 | ra << 16 | (disp & 0xffff)


def const(x, note):
    w = f32(x)
    return [(0x3C000000 | 9 << 21 | w >> 16, 'lis r9 (%s = %.4f cm)' % (note, x)),
            (0x60000000 | 9 << 21 | 9 << 16 | (w & 0xffff), 'ori r9'),
            (d_form(36, 9, 1, -8), 'stw r9,-8(r1)'),
            (d_form(48, 12, 1, -8), 'lfs f12,-8(r1)')]


CLAMP = [(63 << 26 | 7 << 23 | 12 << 11, 'fcmpu cr7,f0,f12'), (0x409C0008, 'bge cr7,+8'), (0xFD800090, 'fmr f12,f0 (small court: keep width limit)')]
CODE = ([(d_form(48, 13, 2, -0x5e90), 'lfs f13,-0x5e90(r2)'), (d_form(48, 0, 10, 0), 'lfs f0,0(r10)'), (0xEC006828, 'fsubs f0,f0,f13')]
        + const(ARC, 'arc radius') + CLAMP + [(d_form(32, 9, 2, -0x5e88), 'lwz r9,-0x5e88(r2) (0x12CAB9A4)'), (d_form(52, 12, 9, 0), 'stfs f12,0(r9)')]
        + const(SIDE, 'corner limit') + CLAMP + [(d_form(32, 9, 2, -0x5e84), 'lwz r9,-0x5e84(r2) (0x12CAB9A0)'), (d_form(52, 12, 9, 0), 'stfs f12,0(r9)')]
        + [(0xE8010090, 'ld r0,0x90(r1)'), (0xEBE10078, 'ld r31,0x78(r1)'), (0x38210080, 'addi r1,r1,0x80'), (0x7C0803A6, 'mtlr r0'), (0x4E800020, 'blr')])
assert len(CODE) == 26


def entry():
    elf = open(ELF, 'rb').read()
    assert struct.unpack_from('>I', elf, 0xa5b01c - 0x8a0000 + 0x890000)[0] == f32(OLD)
    out = ['  "%s":' % NAME, '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]', '    Author: "Claude Code"',
           '    Notes: "Moves the scoring boundary, not the painted line: use court art with the modern line. The court initializer (0x534FCC) set the arc radius (0x12CAB9A4) and the straight corner limit (0x12CAB9A0) from one constant, 612.14 cm = 19 ft 9 in plus 4 in. They are now set separately to 685.16 cm (22 ft 1 3/4 in + 4 in) and 670.24 cm (21 ft 7 7/8 in + 4 in). The game switches from corner line to arc at the basket line, so a strip up to 15 cm wide just in front of it counts as two. Also raises the one other use of the old distance (shot check at 0x3BEB14)."',
           '    Patch Version: 1.0', '    Patch:']
    for i, (w, note) in enumerate(CODE):
        a = START + i * 4
        if struct.unpack_from('>I', elf, a - 0x10000)[0] != w:
            out.append('      - [ be32, 0x%08x, 0x%08x ] # %s' % (a, w, note))
    out.append('      - [ be32, 0x00a5b01c, 0x%08x ] # shot-distance check at 0x3BEB14: 612.14 -> %.2f cm' % (f32(ARC), ARC))
    return '\n'.join(out) + '\n\n'


def main(path):
    txt = open(path, encoding='utf-8').read()
    key = '  "%s":' % NAME
    if key in txt:
        a = txt.index(key); b = txt.index('\n  "', a + 1) + 1
        txt = txt[:a] + txt[b:]
    a = txt.index(ANCHOR)
    txt = txt[:a] + entry() + txt[a:]
    open(path, 'w', encoding='utf-8', newline='\n').write(txt)
    import yaml
    d = yaml.safe_load(open(path, encoding='utf-8'))
    grp = next(v for k, v in d.items() if k.startswith('PPU-'))
    print(len(grp), 'entries;', len(grp[NAME]['Patch']), 'writes in', NAME)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)

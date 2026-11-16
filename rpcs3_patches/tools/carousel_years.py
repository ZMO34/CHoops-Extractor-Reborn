"""Coach Carousel: no minimum years at your school before you can get job offers.

The coach's years at his school are coach +0x24 (bit field read by 0x73A07C).
Two checks require more than 1 year for a coach who has a job:

  0x5937C8  carousel candidate builder (0x5934A0): `cmpwi cr7,r3,1; ble skip`
            leaves an employed coach out of every opening's candidate list.
            A cave makes the test pass when the coach (r31) is user 0's coach
            (profile 0x12E30DC8 + 0x28, +4), so CPU coaches keep the game's rule.
  0x63616C  Coach Carousel screen, user rows: `bgt` past the message
            "you have not been with your current team long enough to get any
            offers"; made unconditional (the loop only lists users' coaches).
"""
import os
import sys

import myplayer_probe as P
import myplayer_bench as B

TITLE = 'Coach Carousel: no minimum years at your school before job offers'
CANDIDATE = 0x5937C8                  # cmpwi cr7,r3,1 (r3 = years, r31 = coach)
SCREEN = (0x63616C, 0x419DFF48, 0x4BFFFF48)   # bgt cr7,0x6360B4 -> b 0x6360B4
PROF_COACH = 0x12E30DC8 + 0x28 + 4


def cave():
    h, l = P.hi_lo(PROF_COACH)
    src = f"""
    lis 11, {h}
    ori 11, 11, {l}
    lwz 11, 0(11)
    cmpw 7, 11, 31
    bne 7, keep
    li 3, 2
keep:
    cmpwi 7, 3, 1
"""
    assert P.original(CANDIDATE) == 0x2F830001
    code = B.assemble(src)
    assert code == B.assemble(src, 0x40010000)
    return code


def entry():
    code = cave(); words = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
    at, old, new = SCREEN
    assert P.original(at) == old
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "Legacy: your coach can be offered jobs in the Coach Carousel after any number of years at his school (the game requires more than 1). Only your coach (user 1); CPU coaches keep the normal rule."',
             '    Patch Version: 1.0', '    Patch:',
             f'      - [ calloc, 0x{CANDIDATE:08x}, {len(words)} ] # candidate list: years check passes for your coach']
    lines += [f'      - [ be32, 0x{CANDIDATE:08x}, 0x{w:08x} ]' for w in words]
    lines.append(f'      - [ be32, 0x{at:08x}, 0x{new:08x} ] # carousel screen: no "not long enough" message')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

"""Write the 'team names with poll rank and record' entry into an RPCS3 patch file.

Usage: python record_write.py [patch.yml]   (default: the repo's BLUS30078_imported_patch.yml)
The entry is inserted after the existing poll-rank scorebug entry, or replaced in place.
"""
import os
import re
import sys

import yaml

import record_asm as R

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, '..', 'BLUS30078_imported_patch.yml')
TITLE = 'Scorebug: team names with poll rank and record (#5 DUKE 12-3)'
AFTER = 'Scorebug: team names with poll rank (#5 DUKE)'
NOTES = ("Replaces the scorebug home/away team-name providers (0x4EF9A4 / 0x4EFABC) with RPCS3 calloc blocks "
         "that return straight to the caller. Text: team name, '#N ' poll rank as in the poll-rank entry "
         "(media poll 0x5BDB44 slots 0-24, matched by team ID +0x15E; ID 0 never matched), then the season record "
         "with the game's formatter (0x49E0E4) and English template 0x4F6600F7 '{0} {1}-{2}'. The record is the "
         "wins/losses pair the pregame matchup card shows natively (team +0x1FC / +0x1FD, 0x70F5D0), added only "
         "when the game-mode word (0x4A3924) is 2, the same check the matchup card makes, and only after the team's "
         "first game (wins + losses > 0). Do NOT enable together with 'Scorebug: team names' or "
         "'Scorebug: team names with poll rank (#5 DUKE)', which patch the same providers. Drops the provider's "
         "game-mode-4 special text, like the poll-rank entry.")


def block():
    out = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
           '    Author: "Claude Code"', '    Notes: "' + NOTES.replace('"', "'") + '"',
           '    Patch Version: 1.0', '    Patch:']
    words = {}
    for side, (hook, _) in R.HOOKS.items():
        code = R.build(side)
        w = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
        words[side] = w
        out.append(f'      - [ calloc, 0x{hook:08x}, {len(w)} ] # {side} provider')
        out += [f'      - [ be32, 0x{hook:08x}, 0x{x:08x} ]' for x in w]
    return '\n'.join(out) + '\n', words


def entry_span(txt, title):
    i = txt.index(f'  "{title}":')
    m = re.compile(r'^  "', re.M).search(txt, i + 5)
    return i, m.start() if m else len(txt)


def main(path):
    txt = open(path, encoding='utf-8').read()
    blk, words = block()
    if f'  "{TITLE}":' in txt:
        i, j = entry_span(txt, TITLE)
    else:
        _, i = entry_span(txt, AFTER); j = i
        blk += '\n'
    txt = txt[:i] + blk + txt[j:]
    open(path, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n')
    d = yaml.safe_load(open(path, encoding='utf-8'))
    root = [k for k in d if k.startswith('PPU')][0]
    e = d[root][TITLE]['Patch']; pos = 0
    for side, (hook, _) in R.HOOKS.items():
        w = words[side]
        assert e[pos] == ['calloc', hook, len(w)], e[pos]
        assert [x[2] for x in e[pos + 1:pos + 1 + len(w)]] == w and all(x[:2] == ['be32', hook] for x in e[pos + 1:pos + 1 + len(w)])
        pos += 1 + len(w)
    assert pos == len(e)
    print('wrote', TITLE, '| words', {k: len(v) for k, v in words.items()}, '| entries', len(d[root]))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)

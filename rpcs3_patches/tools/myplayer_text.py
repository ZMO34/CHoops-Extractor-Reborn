"""Rename the game's Player Lock option to MyPlayer in english.iff (Game Settings).

The MyPlayer bench patch acts while the Player Lock setting (settings +0xF8) is ON,
so the existing option becomes the in-game MyPlayer switch. This relabels it and
rewrites its help text; the setting, its values and the menu are unchanged.

English loc table (TXT loc system, the sole record of english.iff): rows of
(odd ID, relative pointer to a token stream). Tokens are 2 bytes; 0x01 cc is the
ASCII character cc. Changed strings are appended to the end of the token pool and
only those rows are re-pointed; every other row and every existing token byte stay
as they were (the old strings remain, unreferenced). The ReelMaker camera's own
"Player Lock" (0x7CACDCE5, built in code at 0xB9080) is left alone.

Usage: myplayer_text.py <english.iff in> <english.iff out>
"""
import struct
import sys

from choops_py.archive.add_assets import StandardIFF
from choops_py.formats import loc_system
from choops_py.formats.binary import Binary
from choops_py.formats.compression import decode
from choops_py.formats.standard_iff_writer import record_blocks

LABELS = (0x75CC61BF, 0xA0A5EFB9, 0xC80F7FBB)     # "Player Lock" option captions
KEEP = 0x7CACDCE5                                  # ReelMaker camera "Player Lock"
NAME = 'MyPlayer'
OLD_SENTENCES = ('When set to ON, with or without the ball, you will be in control of the same player.',
                 'When set to ON, with our without the ball, you will be in control of the same player.')
NEW_SENTENCE = ('When set to ON, you control only your own player, with or without the ball. '
                'When the CPU subs him out, the CPU plays your team while he sits; when he checks back in, '
                'you control him again (needs the MyPlayer patch).')


def to_text(raw):
    """Token stream (without terminator) -> str; non-ASCII tokens become private-use chars."""
    out = []
    for k in range(0, len(raw), 2):
        hi, lo = raw[k], raw[k + 1]
        out.append(chr(lo) if hi == 1 else chr(0xF0000 + (hi << 8 | lo)))
    return ''.join(out)


def to_tokens(text):
    out = bytearray()
    for c in text:
        o = ord(c)
        if o >= 0xF0000:
            v = o - 0xF0000; out += bytes((v >> 8, v & 0xFF))
        else:
            assert 32 <= o <= 126 or o == 10, repr(c)
            out += bytes((1, o))
    return bytes(out) + bytes(2)


def stream(data, target):
    """Token stream at target, terminator included (same rule as loc_system.tokens)."""
    end = target
    while data[end:end + 2] != b'\0\0':
        end += 2
    return data[target:end + 2]


def rewrite(block):
    rows = loc_system.entries(block)
    new = {}
    for key, target in rows:
        if target is None or key == KEEP:
            continue
        raw = stream(block, target)[:-2]
        text = to_text(raw)
        if key in LABELS:
            assert text == 'Player Lock', (hex(key), text)
            new[key] = NAME
        elif 'Player Lock' in text and any(s in text for s in OLD_SENTENCES):
            t = text.replace('Player Lock\n', NAME + '\n')
            for s in OLD_SENTENCES:
                t = t.replace(s, NEW_SENTENCE)
            new[key] = t
    pool_end = len(block)
    out = bytearray(block)
    if len(out) % 2:
        out += b'\0'
    index = {key: n for n, (key, _) in enumerate(rows)}
    for key, text in sorted(new.items()):
        at = len(out); out += to_tokens(text)
        field = 32 + index[key] * 8 + 4
        struct.pack_into('>I', out, field, at - field + 1)
    result = bytes(out)
    # checks: same IDs, unchanged rows keep their bytes, changed rows read back
    check = dict(loc_system.entries(result)); old = dict(rows)
    assert set(check) == set(old)
    assert result[:pool_end] == bytes(block[:32]) + result[32:32 + len(rows) * 8] + block[32 + len(rows) * 8:pool_end]
    for key in old:
        if key in new:
            assert to_text(stream(result, check[key])[:-2]) == new[key]
        elif old[key] is not None:
            assert check[key] == old[key], hex(key)
    return result, new


HELP_START = 'Player Lock\nWhen set to '
HELP_END = 'will the player you will be locked to.'
HELP_NEW = ('MyPlayer\nWhen set to ON, you control only your own player (picked when play resumes). '
            'When he is subbed out, the CPU plays while he sits; when he checks back in, you control him.')


def rewrite_in_place(block):
    """Same edits without growing the table: overwrite the old tokens in place.

    Labels: 'MyPlayer' + terminator inside the old 'Player Lock' tokens. Help pages:
    the Player Lock paragraph is replaced by HELP_NEW padded with spaces to the same
    token count. The file size and every pointer stay the same."""
    rows = loc_system.entries(block)
    out = bytearray(block); changed = {}; done = set()
    for key, target in rows:
        if target is None or key == KEEP or target in done:
            continue
        raw = stream(block, target)[:-2]; text = to_text(raw)
        if key in LABELS:
            assert text == 'Player Lock', (hex(key), text)
            new = to_tokens(NAME)
            out[target:target + len(new)] = new
            changed[key] = NAME; done.add(target)
            continue
        a = text.find(HELP_START)
        if a < 0:
            continue
        b = text.find(HELP_END, a)
        assert b > a, hex(key)
        b += len(HELP_END)
        room = b - a
        assert len(HELP_NEW) <= room, (hex(key), len(HELP_NEW), room)
        repl = HELP_NEW + ' ' * (room - len(HELP_NEW))
        new_text = text[:a] + repl + text[b:]
        tok = to_tokens(new_text)
        assert len(tok) == len(raw) + 2
        out[target:target + len(tok)] = tok
        changed[key] = new_text; done.add(target)
    result = bytes(out)
    assert len(result) == len(block) and loc_system.entries(result) == rows
    return result, changed


def write(src, dst, in_place=True):
    raw = open(src, 'rb').read(); iff = StandardIFF(raw)
    assert len(iff.records) == 1 and len(iff.blocks) == 1 and iff.records[0]['type_hash'] == 0xA423B39E and iff.records[0]['offsets'] == [0]
    blk = iff.blocks[0]
    old = decode(raw[blk['start']:blk['start'] + blk['size']], blk['logical_size'])
    new, changed = rewrite_in_place(old) if in_place else rewrite(old)
    # Same layout the Studio's localization writer produces: the sole block stored
    # uncompressed, outer metadata and NAME trailer kept.
    trailer = raw[iff.file_length:]; meaningful = 0
    if trailer[:4] == bytes.fromhex('aa171516'):
        meaningful = 8 + Binary(trailer).u32(4, '<')
    assert meaningful <= len(trailer) and not any(trailer[meaningful:])
    header = bytearray(raw[:iff.header_size]); end = blk['start'] + len(new)
    suffix = raw[blk['start'] + blk['size']:iff.file_length]
    struct.pack_into('>I', header, 8, end + len(suffix))
    struct.pack_into('>I', header, 44, len(new))
    struct.pack_into('>I', header, 56, len(new))
    result = bytes(header) + raw[iff.header_size:blk['start']] + new + suffix + trailer[:meaningful]
    chk = StandardIFF(result)
    assert chk.records == iff.records and bytes(record_blocks(chk, chk.records[0])[0][3]) == new
    open(dst, 'wb').write(result)
    for key, text in sorted(changed.items()):
        print(hex(key), repr(text[:90] + ('...' if len(text) > 90 else '')))
    print('rows changed', len(changed), 'size', len(raw), '->', len(result))


if __name__ == '__main__':
    write(sys.argv[1], sys.argv[2])

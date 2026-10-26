"""Read-only observed MRKS text styles; not a generic MRKS writer.

Vanilla streetdata score_bug and gamedataextra scorebug_xenon contain this
wrapper. Native 9B2D0 looks up the uppercase CRC at style +A0, stride B0.
Parsing a binding does not establish that its gameplay controller invokes it.
"""

import math
import struct
import zlib

from choops_py.formats.binary import Binary

_BINDINGS = (
    "home_city",
    "away_city",
    "home_rank",
    "away_rank",
    "quarter",
    "gameclock",
    "shotclock",
    "home_score",
    "away_score",
    "drop_specialinfo",
    "text_nba",
    "text_2k6",
    "drop_small_titleinfo",
    "drop_small_team1info",
    "drop_small_team2info",
    "drop_big_titleinfo",
    "drop_big_team1info",
    "drop_big_team2info",
    "player1name",
    "player2name",
    "player3name",
    "player4name",
    "player1score",
    "player2score",
    "player3score",
    "player4score",
)
_NAMES = {zlib.crc32(n.upper().encode("ascii")): n for n in _BINDINGS}


def inspect_styles(header):
    """Inspect a decoded first MRKS part; reject truncated/overlapping tables.

    Unknown header arrays and the style's +AC word are reported without assigning
    semantics. Embedded SCNE is only located, not fully validated by this reader.
    """
    b = Binary(header)
    b.slice(0, 32)
    scene = b.relative(0)
    if scene < 32 or scene % 4:
        raise ValueError("Unsupported embedded SCNE position")
    b.slice(scene, 0x54)
    count = b.u32(4)
    if count > 4096:
        raise ValueError("MRKS style count exceeds inspection budget")
    table = b.relative(8) if count else None
    if count:
        if table < 32 or table % 4 or table + count * 176 > scene:
            raise ValueError("MRKS styles overlap header or embedded SCNE")
        b.slice(table, count * 176)
    styles = []
    seen = {}
    duplicates = set()
    for i in range(count):
        at = table + i * 176
        key = b.u32(at + 0xA0)
        if key in seen:
            duplicates.add(key)
        seen.setdefault(key, i)
        matrix = list(struct.unpack_from(">16f", header, at))
        position = list(struct.unpack_from(">3f", header, at + 0x40))
        width, alpha, red, green, blue = struct.unpack_from(">5f", header, at + 0x60)
        if not all(
            math.isfinite(v)
            for v in matrix + position + [width, alpha, red, green, blue]
        ):
            raise ValueError("Non-finite MRKS text geometry/color")
        name = _NAMES.get(key)
        case_hash = b.u32(at + 0xA4)
        styles.append(
            dict(
                index=i,
                at=at,
                binding=name,
                lookup_hash=key,
                first_lookup_index=seen[key],
                case_hash=case_hash,
                case_hash_matches=(case_hash == zlib.crc32(name.encode("ascii")))
                if name
                else None,
                matrix=matrix,
                position=position,
                max_width=width,
                rgba=[red, green, blue, alpha],
                model_hash=b.u32(at + 0x54),
                bone_hash=b.u32(at + 0x58),
                font_hash=b.u32(at + 0x90),
                flags=b.u32(at + 0x94),
                alignment=b.u32(at + 0x98),
                effect=b.u32(at + 0x9C),
                literal_id=b.u32(at + 0xA8),
                unknown_ac=b.u32(at + 0xAC),
            )
        )
    return dict(
        scene_offset=scene,
        style_table=table,
        style_count=count,
        styles=styles,
        duplicate_lookup_hashes=sorted(duplicates),
        unknown_header_words=[b.u32(i) for i in range(12, 32, 4)],
    )

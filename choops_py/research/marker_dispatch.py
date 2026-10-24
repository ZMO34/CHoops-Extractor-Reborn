"""Read-only inventory of the two observed native motion-marker dispatch tables.

Callback identity and dispatch flags are evidence, not cross-game event semantics.
In particular a no-op callback does not make a queried timing marker disposable.
"""

from __future__ import annotations

import hashlib
import struct
from collections import Counter

from ..formats.embedded_motion import NativeELF

PROFILES = {
    "nba-2k11": {
        "base": 0x3E85474,
        "count": 192,
        "toc": 0x40F2A98,
        "anchors": {0x18334: 0x812B0000, 0x18344: 0x81690004, 0x18354: 0x4E800421},
        "arguments": {"r3": "event-row-pointer", "r4": "motion-header", "r5": "actor"},
    },
    "college-hoops-2k8": {
        "base": 0x8AC024,
        "count": 185,
        "toc": 0xA54AC8,
        "anchors": {0x27174: 0x806B0000, 0x27188: 0x81690004, 0x2719C: 0x4E800421},
        "arguments": {"r3": "marker-id", "r4": "motion-header", "r6": "actor", "f1": "marker-time"},
    },
}


def inspect_dispatch(raw, profile):
    """Validate the observed revision and enumerate flags/OPD callbacks, without writes."""
    if profile not in PROFILES:
        raise ValueError("Marker dispatch profile is not established for this game")
    layout = PROFILES[profile]
    elf = NativeELF(raw)
    for address, word in layout["anchors"].items():
        if elf.read(address, 4) != struct.pack(">I", word):
            raise ValueError("Unsupported native marker dispatch revision")
    data = elf.read(layout["base"], layout["count"] * 8)
    rows = []
    for identity in range(layout["count"]):
        flags, descriptor = struct.unpack_from(">II", data, identity * 8)
        if descriptor % 4:
            raise ValueError("Unaligned marker callback descriptor")
        entry, toc = struct.unpack(">II", elf.read(descriptor, 8))
        if toc != layout["toc"]:
            raise ValueError("Unexpected marker callback TOC")
        if entry % 4 or not any(
            segment["flags"] & 1
            and segment["address"] <= entry
            and entry + 4 <= segment["address"] + segment["file_bytes"]
            for segment in elf.segments
        ):
            raise ValueError("Marker callback is not file-backed executable code")
        rows.append({"id": identity, "flags": flags, "descriptor": descriptor, "entry": entry, "toc": toc})
    groups = {}
    for row in rows:
        groups.setdefault(row["entry"], []).append(row["id"])
    return {
        "profile": profile,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "table_address": layout["base"],
        "stride": 8,
        "fields": ["dispatch-flags", "callback-opd-pointer"],
        "callback_arguments": dict(layout["arguments"]),
        "rows": rows,
        "callback_groups": [{"entry": entry, "ids": ids} for entry, ids in groups.items()],
        "flag_counts": dict(sorted(Counter(row["flags"] for row in rows).items())),
        "flags_semantically_mapped": False,
        "cross_game_events_mapped": False,
        "payload_abi_portable": False,
        "complete_playback_validation": False,
    }

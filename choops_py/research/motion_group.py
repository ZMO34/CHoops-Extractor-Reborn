"""Bounded NBA11 group envelopes and member-wise alias ownership.

Native 0x1602C relocates group +4 and each 16-byte member's first pointer,
then fixes its motion. Resolver 0x1C700 uses the FIRST member's reference ID
to locate a group and copies dependencies member by member through 0x11DD0.
Other members' zero reference IDs must not become direct SingleMoCap lookups.
"""

import hashlib
import struct
from collections import defaultdict
from itertools import pairwise

from ..formats.binary import Binary
from ..formats.motion_envelope import relative
from .donor_registry import GROUP, MAX_BANK_BYTES

MAX_MEMBERS = 4096


def inspect_group(raw):
    if len(raw) > MAX_BANK_BYTES:
        raise ValueError("Motion group exceeds inspection bounds")
    b = Binary(raw)
    b.slice(0, 12)
    count = b.u32(8)
    if not 1 <= count <= MAX_MEMBERS:
        raise ValueError("Motion group member count exceeds 1..4096 bounds")
    table_end = 12 + count * 16
    b.slice(12, count * 16)
    members, spans = [], []
    for member in range(count):
        field = 12 + member * 16
        offset = relative(b, field)
        if offset is None or offset % 4 or offset < table_end:
            raise ValueError("Group motion pointer is null, unaligned or overlaps its table")
        b.slice(offset, 56)
        size = 56 + (b.u32(offset + 16) & 63) * 4
        b.slice(offset, size)
        spans.append((offset, offset + size))
        members.append({
            "member": member, "header_offset": offset, "header_bytes": size,
            "placement_words": [b.u32(field + i * 4) for i in (1, 2, 3)],
            "resolved_field_nonzero": bool(b.u32(offset + 48)),
            "reference_word": b.u32(offset + 40),
        })
    unique = sorted(set(spans))
    if any(a[1] > z[0] for a, z in pairwise(unique)):
        raise ValueError("Group motion headers partially overlap")
    return {
        "identity": b.u32(0), "link_pointer": relative(b, 4), "members": members,
        "member_count": count, "table_bytes": table_end,
        "record_sha256": hashlib.sha256(raw).hexdigest(),
        "placement_semantics_established": False, "native_group_installed": False,
    }


class MotionGroupSource:
    """Share the bounded bank reader; never reinterpret a group ID as a clip ID."""

    def __init__(self, source):
        self.source = source
        self.index = defaultdict(list)
        self.cache = {}
        self.resolutions = {}
        for bank, iff in enumerate(source.banks):
            for record in iff.records:
                if record["type_hash"] == GROUP:
                    self.index[record["id"]].append((bank, record["index"]))

    def _group(self, location):
        if location not in self.cache:
            raw = self.source._record(*location, type_hash=GROUP)
            self.cache[location] = raw, inspect_group(raw)
        return self.cache[location]

    def _resolve(self, bank, record):
        location = bank, record
        if location in self.resolutions:
            return self.resolutions[location]
        origin, original = self._group(location)
        current, seen, path = location, set(), []
        while True:
            if current in seen or len(path) >= 4096:
                raise ValueError("Motion group alias cycle or chain exceeds bounds")
            seen.add(current)
            raw, info = self._group(current)
            path.append({
                "bank": current[0], "record": current[1],
                "bank_sha256": self.source.fingerprints[current[0]],
                "record_sha256": info["record_sha256"],
            })
            states = [member["resolved_field_nonzero"] for member in info["members"]]
            if all(states):
                break
            if any(states):
                raise ValueError("Mixed packed/alias group members are not established")
            key = info["members"][0]["reference_word"]
            candidates = self.index.get(key, [])
            if len(candidates) != 1:
                raise ValueError("Group alias identity is missing or ambiguous")
            current = candidates[0]
        for entry in path[:-1]:
            alias, other = self._group((entry["bank"], entry["record"]))
            if other["member_count"] != info["member_count"]:
                raise ValueError("Group alias member counts disagree")
            for a, z in zip(other["members"], info["members"], strict=True):
                ah = alias[a["header_offset"]:]
                zh = raw[z["header_offset"]:]
                if ah[8:20] != zh[8:20] or (
                    (struct.unpack_from(">I", ah, 20)[0] ^ struct.unpack_from(">I", zh, 20)[0])
                    & 0x8000FFFF
                ):
                    raise ValueError("Group alias member channel/count/packing metadata disagrees")
        result = origin, original, raw, info, path
        self.resolutions[location] = result
        return result

    def inspect_member(self, bank, record, member, *, canonical=False):
        if type(canonical) is not bool:
            raise ValueError("Canonical group inspection must be an explicit boolean")
        origin, original, raw, owner, path = self._resolve(bank, record)
        if type(member) is not int or not 0 <= member < original["member_count"]:
            raise ValueError("Choose an existing motion group member")
        start = original["members"][member]["header_offset"]
        payload_start = owner["members"][member]["header_offset"]
        data, report = self.source._read_tracks(
            origin[start:], raw[payload_start:], [dict(entry) for entry in path],
            canonical=canonical, source_record=origin,
        )
        for extent in report["extents"]:
            a = payload_start + extent["offset"]
            z = a + extent["bytes"]
            if extent["bytes"] and (
                a < owner["table_bytes"] or any(
                    a < m["header_offset"] + m["header_bytes"] and m["header_offset"] < z
                    for m in owner["members"]
                )
            ):
                raise ValueError("Group motion dependency overlaps group metadata or a member header")
        report.update(
            source_kind="nba11-group-member", member=member,
            group_member_count=original["member_count"],
            group_header_offset=start, payload_header_offset=payload_start,
            group_record_sha256=original["record_sha256"],
            payload_group_record_sha256=owner["record_sha256"],
            placement_words=original["members"][member]["placement_words"],
            placement_semantics_established=False, native_group_installed=False,
            on_court_compatibility_established=False,
            counts_toward_on_court_conversion=False,
        )
        return data, report

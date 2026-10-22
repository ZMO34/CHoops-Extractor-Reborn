"""Revision-specific, read-only native Legacy component and transfer audits.

An explicitly identified 0x595D64 aggregate is required. These offsets are NOT
USERDATA offsets; no scanning, save mutation or portal installation is performed.
"""

from hashlib import sha256
from struct import unpack_from

from ..roster.schema import detect_tables
from .recruit_pool import inspect_recruiting_section

# Order independently corroborated by 0x595C20, 0x595D64 and 0x595FB0.
# Names deliberately do not assign semantics to unidentified native components.
COMPONENTS = (
    ("legacy_context", 0xC9F8, 0x5A122C, 0x5A1244, 0x5A15A8),
    ("empty_component", 0, 0x73D888, 0x73D89C, 0x73D8AC),
    ("component_58ca40", 0x4228, 0x58CA2C, 0x58CA40, 0x58CA9C),
    ("component_5b8290", 0x7F8, 0x5B827C, 0x5B8290, 0x5B82C8),
    ("recruiting", 0x415A4, 0x5C5450, 0x5C5468, 0x5C57B0),
    ("component_5cd7e8", 0x5210, 0x5CD7D4, 0x5CD7E8, 0x5CD99C),
    ("component_5c29cc", 0xC0, 0x5C29B8, 0x5C29CC, 0x5C2BEC),
    ("component_75e2b8", 0x7D04, 0x75E2A4, 0x75E2B8, 0x75E314),
    ("record_bank_597f94", 0x92004, 0x597F7C, 0x597F94, 0x598178),
    ("component_5bdcd8", 0x1D54, 0x5BDCC4, 0x5BDCD8, 0x5BE02C),
    ("component_590b50", 0xA28, 0x590B3C, 0x590B50, 0x591294),
    ("component_592c20", 0x1B5C, 0x592C0C, 0x592C20, 0x592E80),
    ("component_770280", 0x2198, 0x770638, 0x770280, 0x7704B8),
    ("transfers", 0x12D0, 0x5BC64C, 0x5BC660, 0x5BC854),
    ("component_5aeef0", 0x63D80, 0x5AEED8, 0x5AEEF0, 0x5AF088),
    ("component_5fa838", 0x358, 0x5FA824, 0x5FA838, 0x5FA960),
    ("component_5b9208", 0x20, 0x5B91F4, 0x5B9208, 0x5B9240),
)
AGGREGATE_SIZE = sum(row[1] for row in COMPONENTS)
TRANSFER_SIZE = 0x12D0


def _roster_tables(roster):
    if (
        not isinstance(roster, (bytes, bytearray))
        or not 0xB0 <= len(roster) <= 64 * 1024 * 1024
    ):
        raise ValueError("Legacy audit requires a bounded decoded CH roster")
    tables = detect_tables(roster)
    spans = sorted(
        (start, start + count * stride, name)
        for name, (start, count, stride) in tables.items()
    )
    for index, (start, end, name) in enumerate(spans):
        if start < 0xB0 or start % 4:
            raise ValueError(f"invalid {name} table start")
        if index and start < spans[index - 1][1]:
            raise ValueError(
                "overlapping roster tables cannot establish typed references"
            )
    return tables


def component_layout():
    offset = 0
    rows = []
    for name, size, getter, writer, reader in COMPONENTS:
        rows.append(
            dict(
                component=name,
                offset=offset,
                bytes=size,
                size_getter=f"0x{getter:06X}",
                serializer=f"0x{writer:06X}",
                loader=f"0x{reader:06X}",
            )
        )
        offset += size
    return rows


def _reference(value, table, bias):
    if value == 0:
        return dict(raw=0, index=None, status="null")
    start, count, stride = table
    index, remainder = divmod(value - start - bias, stride)
    if remainder or not 0 <= index < count:
        return dict(raw=value, index=None, status="invalid_record_anchor")
    return dict(raw=value, index=index, status="resolved")


def inspect_transfer_section(section: bytes, roster: bytes):
    """Resolve serialized base-relative player/team anchors, not live pointers."""
    if not isinstance(section, (bytes, bytearray)) or len(section) != TRANSFER_SIZE:
        raise ValueError("transfer section must be exactly 0x12D0 bytes")
    tables = _roster_tables(roster)
    count = unpack_from(">i", section)[0]
    if not 0 <= count <= 400:
        raise ValueError("transfer count exceeds the native 400-active-entry limit")
    records, seen = [], set()
    for slot in range(count):
        player, source, destination = unpack_from(">3I", section, 4 + slot * 12)
        references = dict(
            player=_reference(player, tables["players"], 16),
            source=_reference(source, tables["teams"], 48),
            destination=_reference(destination, tables["teams"], 48),
        )
        issues = []
        for name, ref in references.items():
            if ref["status"] == "invalid_record_anchor" or (
                name != "destination" and ref["status"] == "null"
            ):
                issues.append(f"{name}_{ref['status']}")
        if player and player in seen:
            issues.append("duplicate_player")
        seen.add(player)
        if source and source == destination:
            issues.append("same_source_and_destination")
        records.append(
            dict(slot=slot, **references, issues=issues, unsigned=destination == 0)
        )
    return dict(
        schema=1,
        source_sha256=sha256(section).hexdigest(),
        active_count=count,
        active_capacity=400,
        stored_capacity=401,
        records=records,
        issue_count=sum(len(row["issues"]) for row in records),
        unsigned_count=sum(row["unsigned"] for row in records),
        inactive_storage_sha256=sha256(section[4 + count * 12 :]).hexdigest(),
        historical_continuity_verified=False,
        native_portal_installed=False,
    )


def inspect_record_bank(section: bytes, roster: bytes):
    """Audit only the serializer-established reference columns; meaning unknown."""
    if len(section) != 0x92004:
        raise ValueError("record bank must be exactly 0x92004 bytes")
    count = unpack_from(">i", section)[0]
    if not 0 <= count <= 1024:
        raise ValueError("record bank count exceeds its 1024-record storage")
    nonnull = outside = 0
    for row in range(count):
        for side in range(2):
            for slot in range(12):
                at = 4 + row * 0x248 + 8 + side * 0x120 + slot * 24
                value = unpack_from(">I", section, at)[0]
                nonnull += bool(value)
                outside += bool(value and value >= len(roster))
    return dict(
        active_count=count,
        capacity=1024,
        record_stride=0x248,
        nonnull_references=nonnull,
        references_outside_roster=outside,
        referent_types_established=False,
        history_semantics_established=False,
    )


def inspect_legacy_aggregate(aggregate: bytes, roster: bytes):
    if (
        not isinstance(aggregate, (bytes, bytearray))
        or len(aggregate) != AGGREGATE_SIZE
    ):
        raise ValueError(
            f"native Legacy aggregate must be exactly 0x{AGGREGATE_SIZE:X} bytes; do not supply a whole save"
        )
    _roster_tables(roster)
    components = []
    inspectors = dict(
        recruiting=inspect_recruiting_section,
        transfers=inspect_transfer_section,
        record_bank_597f94=inspect_record_bank,
    )
    for row in component_layout():
        start, size = row["offset"], row["bytes"]
        raw = aggregate[start : start + size]
        item = dict(
            row,
            sha256=sha256(raw).hexdigest(),
            nonzero=any(raw),
            field_semantics_complete=False,
        )
        if row["component"] in inspectors:
            try:
                item["audit"] = inspectors[row["component"]](raw, roster)
            except ValueError as error:
                item["audit_error"] = str(error)
        components.append(item)
    return dict(
        schema=1,
        revision="CH2K8 PS3 supplied native revision",
        bytes=AGGREGATE_SIZE,
        source_sha256=sha256(aggregate).hexdigest(),
        roster_sha256=sha256(roster).hexdigest(),
        components=components,
        userdata_offset_established=False,
        matching_pair_verified=False,
        full_backend_understood=False,
        native_portal_installed=False,
    )


def backend_overview():
    return (
        "Legacy backend — established structures and open contracts\n\n"
        "Save/load: 17 ordered native components. Offsets below are relative to "
        "the native aggregate, not USERDATA. Several component meanings remain unknown.\n\n"
        "Recruit generation: annual traversal replaces older/unflagged prospects; "
        "blank storage is not a proven transfer allocator.\n"
        "Recruiting: 0xD8 records, two 16,000-node pools, four queues and 96 "
        "preference profiles. Commitment is separate from membership signing.\n"
        "Transfers: 400 active entries plus one insertion/sorting record; each "
        "links the original player, source school and optional destination.\n"
        "Signing: ordinary recruit conversion rebuilds a player. Transfers must "
        "retain the original player and bypass that conversion. An unsigned "
        "transfer must not reach the reusable-player-pool finalizer.\n"
        "Continuity: career stats, historical school ownership, persistent proxy "
        "binding and calendar interception still need native tracing.\n\n"
        "Goal: in-game offseason transfer recruiting, TR class/redshirt labels, "
        "playing-time/home-distance/team-ranking priorities, CPU and user signing, "
        "scholarship checks and preserved statistics/history. No playable portal "
        "or executable patch is installed.\n\n"
        "An optional separately identified aggregate can be inspected read-only. "
        "Exact size alone does not establish revision or correspondence to this roster."
    )

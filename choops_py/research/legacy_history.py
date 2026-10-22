"""Native player/recruit statistics ownership; no allocation or save writes."""

from collections import defaultdict
from hashlib import sha256
from struct import unpack_from

from ..roster.schema import HEADER_TABLES
from .legacy_backend import _roster_tables

STAT_CAPACITY = 16000
STAT_STRIDE = 24
FREE_STATE_SIZE = 0x7D04


def read_free_stack(free_state, count=STAT_CAPACITY, owners=None):
    if (
        not isinstance(free_state, (bytes, bytearray))
        or len(free_state) != FREE_STATE_SIZE
    ):
        raise ValueError("Statistics free stack must be exactly 0x7D04 bytes")
    n = unpack_from(">i", free_state)[0]
    if not 0 <= n < STAT_CAPACITY:
        raise ValueError("Statistics free-stack count exceeds 15999 usable records")
    ids = unpack_from(f">{n}H", free_state, 4)
    seen, duplicates = set(), set()
    for stat_id in ids:
        if stat_id in seen:
            duplicates.add(stat_id)
        seen.add(stat_id)
    return dict(
        count=n,
        invalid_ids=sorted(x for x in seen if not 1 <= x < min(count, STAT_CAPACITY)),
        duplicate_ids=sorted(duplicates),
        referenced_ids=sorted(seen.intersection(owners or {})),
        ownership_crosscheck_available=owners is not None,
        unused_storage_sha256=sha256(free_state[4 + n * 2 :]).hexdigest(),
        native_reclamation_can_drop_history=True,
    )


def inspect_statistics_free_stack(section, roster):
    report = read_free_stack(section)
    try:
        history = inspect_player_history(roster, section)
    except ValueError as error:
        report["ownership_error"] = str(error)
    else:
        report = history["free_stack"]
        report["shared_reference_count"] = len(history["shared_references"])
        report["recruit_owners_included"] = history["recruit_owners_included"]
    return report


def directory(payload, field, stride, limit, protected):
    count, delta = unpack_from(">Ii", payload, field)
    start = field + 4 + delta - 1
    end = start + count * stride
    if (
        not delta
        or not 0 < count <= limit
        or start < 0xB0
        or start % 4
        or end > len(payload)
    ):
        raise ValueError(f"Invalid native directory at 0x{field:X}")
    for name, (other, n, size) in protected.items():
        other += HEADER_TABLES[name][1] - 1
        if start < other + n * size and other < end:
            raise ValueError(f"Native directory overlaps {name}")
    for other_field in range(0, 0xB0, 8):
        if other_field == field:
            continue
        n, relative = unpack_from(">Ii", payload, other_field)
        target = other_field + 4 + relative - 1
        if n and relative and start <= target < end:
            raise ValueError("Native directory contains another table target")
    return start, count, stride


def inspect_player_history(payload: bytes, free_state: bytes | None = None):
    tables = _roster_tables(payload)
    base, count, stride = directory(payload, 0x40, STAT_STRIDE, STAT_CAPACITY, tables)
    owners = defaultdict(list)
    records, issues = [], []
    player_base, players, player_stride = tables["players"]
    for player in range(players):
        # Player logical anchor is physical row +16; five IDs are logical +0x18.
        ids = unpack_from(">5H", payload, player_base + player * player_stride + 0x28)
        if all(value in (0, 0xFFFF) for value in ids):
            continue
        years = []
        for age, stat_id in enumerate(ids):
            if stat_id in (0, 0xFFFF):
                continue
            owner = dict(kind="player", index=player, history_slot=age)
            if not 1 <= stat_id < min(count, STAT_CAPACITY):
                issues.append(
                    dict(kind="invalid_stat_id", stat_id=stat_id, owner=owner)
                )
                continue
            owners[stat_id].append(owner)
            raw = payload[base + stat_id * stride : base + (stat_id + 1) * stride]
            school = (unpack_from(">I", raw, 20)[0] >> 14) & 511
            if school >= tables["teams"][1]:
                issues.append(
                    dict(
                        kind="school_out_of_range",
                        stat_id=stat_id,
                        school_index=school,
                        owner=owner,
                    )
                )
            years.append(
                dict(
                    history_slot=age,
                    stat_id=stat_id,
                    school_index=school,
                    packed_record_sha256=sha256(raw).hexdigest(),
                    packed_words=unpack_from(">6I", raw),
                )
            )
        records.append(dict(player_index=player, stat_ids=list(ids), years=years))
    # Recruits use the same pool; ignoring them would misclassify ownership/free IDs.
    recruit_count, recruit_delta = unpack_from(">Ii", payload, 0x48)
    recruit_owners_established = False
    if recruit_count and recruit_delta:
        recruit_base, recruit_count, _ = directory(payload, 0x48, 0xD8, 16384, tables)
        if (
            recruit_base < base + count * stride
            and base < recruit_base + recruit_count * 0xD8
        ):
            raise ValueError("Recruit and statistics tables overlap")
        for recruit in range(recruit_count):
            stat_id = unpack_from(">H", payload, recruit_base + recruit * 0xD8 + 0x2E)[
                0
            ]
            if stat_id in (0, 0xFFFF):
                continue
            owner = dict(kind="recruit", index=recruit)
            if not 1 <= stat_id < min(count, STAT_CAPACITY):
                issues.append(
                    dict(kind="invalid_stat_id", stat_id=stat_id, owner=owner)
                )
            else:
                owners[stat_id].append(owner)
        recruit_owners_established = True
    elif recruit_count or recruit_delta:
        raise ValueError("Incomplete recruit directory")
    aliases = [
        dict(stat_id=key, references=value)
        for key, value in owners.items()
        if len(value) > 1
    ]
    free = None
    if free_state is not None:
        free = read_free_stack(free_state, count, owners)
    return dict(
        schema=1,
        source_sha256=sha256(payload).hexdigest(),
        statistics_base=base,
        statistics_records=count,
        record_stride=stride,
        usable_id_range=[1, min(count, STAT_CAPACITY) - 1],
        player_history_slots=5,
        players_with_history=records,
        unique_referenced_records=len(owners),
        recruit_owners_included=recruit_owners_established,
        shared_references=aliases,
        issues=issues,
        free_stack=free,
        lifetime_graph_complete=False,
        empty_stat_sentinels=[0, 65535],
        stored_school_attribution_established=True,
        current_slot_attribution_may_be_unfinalized=True,
        runtime_continuity_verified=False,
        native_portal_installed=False,
    )

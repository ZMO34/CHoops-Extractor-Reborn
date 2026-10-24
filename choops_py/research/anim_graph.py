"""Read-only NBA11 graph fixups established by native 0x37FC60.

This describes storage dependencies, not node operations or target compatibility.
Executable motion bindings are positional and must not be inferred from node IDs.
"""

import hashlib
import struct
from itertools import pairwise

from ..formats.binary import Binary

MAX_GRAPH = 64 * 1024 * 1024
MAX_ROWS = 1_000_000
MAX_FIXUPS = 300_000
PLAYER_KEY_FIELDS = (0x100, 0x108, 0x110, 0x10C, 0x104, 0x11C, 0x114, 0x118, 0x120)
STRIDES = (36, 24, 4, 8, 12, 4, 16) + (16,) * 9
POINTER_FIELDS = ((24, 32), (12, 20), (), (4,), (0,), (0,), (0,)) + ((4, 8, 12),) * 9


def inspect_graph(raw, profile="nba-2k11"):
    """Validate the observed serialized graph, retaining unknown node words.

    Relative pointers use signed32 field-relative offsets with a +1 bias; zero
    remains null. Empty tables can point one byte past the record. Internal
    pointer targets are bounded only: their payload semantics remain unknown.
    No target graph, writer, playback, or compatible-conversion claim follows.
    """
    if profile != "nba-2k11":
        raise ValueError("Animation graph layout is only established for NBA2K11")
    if not 128 <= len(raw) <= MAX_GRAPH:
        raise ValueError("Animation graph must be 128 bytes..64 MiB")
    b = Binary(raw)
    counts = [b.u32(i * 4) for i in range(16)]
    if sum(counts) > MAX_ROWS:
        raise ValueError("Animation graph row count exceeds inspection bounds")
    total_fixups = 16 + sum(
        n * len(fields) for n, fields in zip(counts, POINTER_FIELDS)
    )
    if total_fixups > MAX_FIXUPS:
        raise ValueError("Animation graph pointer count exceeds inspection bounds")
    pointers = []

    def pointer(field, *, empty=False):
        value = struct.unpack(">i", b.slice(field, 4))[0]
        target = field + value - 1 if value else None
        if target is not None and not 0 <= target < len(raw) + int(empty):
            raise ValueError("Animation graph pointer outside record bounds")
        pointers.append(dict(field=field, target=target))
        return target

    tables, spans = [], []
    for i, (count, stride) in enumerate(zip(counts, STRIDES)):
        offset = pointer(64 + i * 4, empty=not count)
        if count and offset is None:
            raise ValueError("Nonempty animation graph table has null pointer")
        if offset is not None:
            if offset < 128 or offset % 4:
                raise ValueError("Graph table overlaps header or is unaligned")
            b.slice(offset, count * stride)
            if count:
                spans.append((offset, offset + count * stride))
        tables.append(dict(index=i, count=count, stride=stride, offset=offset))
    if any(a[1] > z[0] for a, z in pairwise(sorted(spans))):
        raise ValueError("Animation graph tables overlap")
    nodes = []
    keyed_tables = [
        dict(
            family=i,
            player_key_offset=PLAYER_KEY_FIELDS[i],
            actor_state_cache_offset=0x4C + i * 4,
            rows=[],
        )
        for i in range(9)
    ]
    for table, fields in zip(tables, POINTER_FIELDS):
        if not fields:
            continue
        for row in range(table["count"]):
            offset = table["offset"] + row * table["stride"]
            targets = [pointer(offset + field) for field in fields]
            if table["index"] >= 7:
                words = list(struct.unpack(">4I", b.slice(offset, 16)))
                keyed_tables[table["index"] - 7]["rows"].append(
                    dict(
                        index=row,
                        offset=offset,
                        raw_key=words[0],
                        raw_words=words,
                        pointer_targets=targets,
                    )
                )
            if table["index"] == 0:
                words = list(struct.unpack(">9I", b.slice(offset, 36)))
                nodes.append(
                    dict(
                        index=row,
                        offset=offset,
                        raw_words=words,
                        executable_binding_slot=row,
                        binding_kind="group-first-member"
                        if words[4] & 1
                        else "direct-motion",
                    )
                )
    return dict(
        profile=profile,
        record_sha256=hashlib.sha256(raw).hexdigest(),
        bytes=len(raw),
        tables=tables,
        nodes=nodes,
        keyed_tables=keyed_tables,
        keyed_lookup_policy="first-matching-raw-key-or-null",
        cached_rows_require_graph_lifetime=True,
        pointer_fixups=pointers,
        node_operation_semantics_established=False,
        transition_semantics_established=False,
        target_compatibility_established=False,
        compatible_on_court_conversion_count=None,
        native_target_dispatch_installed=False,
    )


def lookup_graph_key(raw, key, family):
    """Model native0x4691F8 ordering; family meanings remain unresolved.

    Keys compare as32-bit words. Duplicate keys preserve the first native match,
    and missing keys returnNone. Do not substitute another family or row.
    """
    if type(key) is not int or not 0 <= key <= 0xFFFFFFFF:
        raise ValueError("Graph lookup key must be an unsigned32-bit word")
    if type(family) is not int or not 0 <= family < 9:
        raise ValueError("Graph lookup family must be0..8")
    report = inspect_graph(raw)
    return next(
        (r for r in report["keyed_tables"][family]["rows"] if r["raw_key"] == key), None
    )

"""Read-only NBA11 graph fixups established by native 0x37FC60.

This describes storage dependencies, not node operations or target compatibility.
Executable motion bindings are positional and must not be inferred from node IDs.
"""

import hashlib
import struct
from itertools import pairwise

from ..formats.binary import Binary
from .signature_provider import signature_binding

STYLE_SLOTS = (
    None,
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (1, 2),
    (2, 0),
    (2, 1),
    (2, 2),
    (3, 0),
    (3, 1),
    (3, 2),
    (4, 0),
    (4, 1),
    (5, 0),
    (6, 0),
    (7, 0),
    (8, 0),
)

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
    for family in keyed_tables:
        bindings = [
            signature_binding(i)
            for i in range(41)
            if signature_binding(i)["player_key_offset"] == family["player_key_offset"]
        ]
        if len(bindings) != 1:
            raise ValueError("Graph player field has no unique native provider binding")
        family["shared_player_key_binding"] = bindings[0]
    for table, fields in zip(tables, POINTER_FIELDS):
        if not fields:
            continue
        for row in range(table["count"]):
            offset = table["offset"] + row * table["stride"]
            targets = [pointer(offset + field) for field in fields]
            if table["index"] >= 7:
                words = list(struct.unpack(">4I", b.slice(offset, 16)))
                node_indices = []
                for target in targets:
                    delta = (
                        None if target is None else target - (tables[0]["offset"] or 0)
                    )
                    if delta is not None and (
                        delta < 0 or delta % 36 or delta // 36 >= counts[0]
                    ):
                        raise ValueError(
                            "Graph keyed payload does not target a node boundary"
                        )
                    node_indices.append(None if delta is None else delta // 36)
                keyed_tables[table["index"] - 7]["rows"].append(
                    dict(
                        index=row,
                        offset=offset,
                        raw_key=words[0],
                        raw_words=words,
                        pointer_targets=targets,
                        node_indices=node_indices,
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
                        raw_style_selector=words[5],
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
        style_selector_semantics_context="NBA11-dribbler-0x46C0D4",
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


def graph_style_gate(raw, player_keys, candidate, *, bypass=False):
    """Read-only reference for ONLY native0x46C0D4 style eligibility.

    Bounded synthetic native instruction cases establish this gate. All nine
    native player keys are explicit. A null candidate, selector zero, or the observed
    transition-flag bypass passes. Positive selectors1..17 compare the cached
    row's corresponding node pointer; absent rows and unsupported selectors
    reject. Other native transition predicates still apply; this is not playback.
    """
    if (
        not isinstance(player_keys, (tuple, list))
        or len(player_keys) != 9
        or any(type(k) is not int or not 0 <= k <= 0xFFFFFFFF for k in player_keys)
    ):
        raise ValueError("Style gate requires nine explicit unsigned32-bit player keys")
    if type(bypass) is not bool:
        raise ValueError("Style gate bypass must be an explicit boolean")
    report = inspect_graph(raw)
    if candidate is not None and (
        type(candidate) is not int or not 0 <= candidate < len(report["nodes"])
    ):
        raise ValueError("Style gate candidate must be a graph node index or None")
    if bypass or candidate is None:
        return True
    selector = report["nodes"][candidate]["raw_style_selector"]
    if selector == 0:
        return True
    if selector >= len(STYLE_SLOTS):
        return False
    family, slot = STYLE_SLOTS[selector]
    row = next(
        (
            r
            for r in report["keyed_tables"][family]["rows"]
            if r["raw_key"] == player_keys[family]
        ),
        None,
    )
    return row is not None and row["node_indices"][slot] == candidate

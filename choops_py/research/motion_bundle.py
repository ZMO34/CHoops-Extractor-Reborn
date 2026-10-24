"""Read-only CH motion-bundle selection prefix at0x345ABC.

Rows contain two motion pointers, three scalars and raw flags. This models only
variant/lane choice before native timing, blending, event and playback updates.
"""

import hashlib
import math
import struct

from ..formats.embedded_motion import NativeELF
from .target_motion import inspect_target_motion

ROW_BYTES = 24
DRIBBLE_VARIANTS = 5
DRIBBLE_TABLE_SLOT = 0xA5A718


def inspect_bundle_rows(raw, count=DRIBBLE_VARIANTS):
    """The native prefix reads the following row's flags, even at the last row.

    An owned future bundle must provide24 lookahead bytes. Reading beyond its
    last declared variant is not permission to select an adjacent bundle.
    """
    if type(count) is not int or not 1 <= count <= 4096:
        raise ValueError("Motion bundle variant count must be1..4096")
    if len(raw) != (count + 1) * ROW_BYTES:
        raise ValueError("Bundle needs exact variant bytes and one lookahead row")
    rows = []
    for index in range(count):
        words = struct.unpack_from(">6I", raw, index * ROW_BYTES)
        scalars = struct.unpack_from(">3f", raw, index * ROW_BYTES + 8)
        if not all(math.isfinite(f) for f in scalars):
            raise ValueError("Bundle contains nonfinite variant metadata")
        if any(p % 4 for p in words[:2]):
            raise ValueError("Bundle motion pointer is unaligned")
        rows.append(
            dict(
                index=index,
                motion_pointers=list(words[:2]),
                threshold=scalars[0],
                lane_scalars=list(scalars[1:]),
                raw_flags=words[5],
                raw_words=list(words),
            )
        )
    return dict(
        rows=rows,
        lookahead_flags=struct.unpack_from(">I", raw, count * ROW_BYTES + 20)[0],
        lookahead_bytes=ROW_BYTES,
        record_sha256=hashlib.sha256(raw).hexdigest(),
        complete_playback_semantics_established=False,
    )


def select_bundle_rows(raw, value, allow_flagged, lane_policy, actor_flag, *, count=5):
    """Model ONLY the established native prefix, with explicit context booleans.

    The selected/current and next pointers share the SELECTED row's scalar.
    Remaining native timing/blending rules and the flag's gameplay role are not
    inferred. Null motions and no eligible row remain null, without substitution.
    """
    if any(type(v) is not bool for v in (allow_flagged, lane_policy, actor_flag)):
        raise ValueError("Bundle context flags must be explicit booleans")
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("Bundle selection value must be finite")
    try:
        value = struct.unpack(">f", struct.pack(">f", value))[0]
    except (OverflowError, struct.error) as error:
        raise ValueError("Bundle selection value exceeds float32") from error
    if not math.isfinite(value):
        raise ValueError("Bundle selection value exceeds float32")
    report = inspect_bundle_rows(raw, count)
    lane = int(lane_policy and not actor_flag)
    for row in reversed(report["rows"]):
        if row["threshold"] <= value and (allow_flagged or not row["raw_flags"] & 1):
            index = row["index"]
            following = (
                report["rows"][index + 1]["raw_flags"]
                if index + 1 < count
                else report["lookahead_flags"]
            )
            next_index = min(count - 1, index + int(allow_flagged or not following & 1))
            return dict(
                index=index,
                next_index=next_index,
                lane=lane,
                motion=row["motion_pointers"][lane],
                next_motion=report["rows"][next_index]["motion_pointers"][lane],
                scalar=row["lane_scalars"][lane],
            )
    return dict(
        index=-1, next_index=None, lane=lane, motion=0, next_motion=0, scalar=1.0
    )


def inspect_dribble_bundle(raw, index):
    """Inspect one native caller-selected bundle; does not establish table count."""
    if type(index) is not int or not 0 <= index <= 65535:
        raise ValueError("Caller-proven dribble bundle index must be0..65535")
    elf = raw if isinstance(raw, NativeELF) else NativeELF(raw)
    for address, expected in (
        (0x345B18, 0x80E244A4),
        (0x345B88, 0xC00A0008),
        (0x345FDC, 0x8009002C),
    ):
        if struct.unpack(">I", elf.read(address, 4))[0] != expected:
            raise ValueError("Unestablished target motion bundle reader revision")
    table = struct.unpack(">I", elf.read(DRIBBLE_TABLE_SLOT, 4))[0]
    if not table or table % 4:
        raise ValueError("Dribble bundle table pointer must be nonnull and aligned")
    address = table + index * DRIBBLE_VARIANTS * ROW_BYTES
    data = elf.read(address, (DRIBBLE_VARIANTS + 1) * ROW_BYTES)
    report = inspect_bundle_rows(data)
    dependencies = {}
    for row in report["rows"]:
        for pointer in row["motion_pointers"]:
            if pointer and pointer not in dependencies:
                dependencies[pointer] = inspect_target_motion(elf, pointer)
    return dict(
        **report,
        table_address=table,
        bundle_address=address,
        index=index,
        native_dependencies=list(dependencies.values()),
        source_elf_sha256=hashlib.sha256(elf.raw).hexdigest(),
        registered_count_established=False,
        target_donor_mapping_established=False,
        compatible_conversion_count=None,
        native_installation=False,
    )

"""Bounded NBA11 shot-cache fallback model; no target dispatch is installed.

Inputs are resolved motion handles, never guessed cross-game identities.
The random service and context predicate are caller inputs, not reimplementations
of their unproven game semantics. Addresses/evidence are in the runtime notes.
"""

import math
import struct


def _u32(value):
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError(
            "Motion handles/control values must be unsigned 32-bit integers"
        )
    return value


def _f32(value):
    try:
        result = struct.unpack(">f", struct.pack(">f", value))[0]
    except (OverflowError, struct.error):
        raise ValueError("Native float32 fallback arithmetic overflow") from None
    if not math.isfinite(result):
        raise ValueError("Fallback arithmetic must remain finite")
    return result


def _handles(values, count, *, nonzero=False):
    if not isinstance(values, (list, tuple)) or len(values) != count:
        raise ValueError(f"Expected exactly {count} resolved motion handles")
    result = [_u32(v) for v in values]
    if nonzero and not all(result):
        raise ValueError("Fallback resources must be resolved nonzero handles")
    return result


def shot_cache_matches(cached_player, cached_revision, player, revision):
    """Native 0x6533C0 identity/+0xD4 revision key; context/hand are not keys."""
    for v in (cached_player, cached_revision, player, revision):
        _u32(v)
    if not player:
        raise ValueError("A live player handle is required")
    return cached_player == player and cached_revision == revision


def resolve_shot_fallbacks(
    selected,
    selector_bit,
    player_bucket,
    control_value,
    *,
    weighted_rows,
    bucket_rows,
    fixed_pair2,
    fixed_pair3,
    random_samples,
    context_override=False,
):
    """Resolve four selected handles using the proven native fallback graph.

    Row lanes are [bit-one, bit-zero]. Eight weighted rows contain (handle,
    handle, positive weight). Eighteen bucket rows contain pair1's two handles
    followed by pair2's two handles. The bucket is the raw player +0x1C halfword.
    random_samples is empty with an original pair0, otherwise exactly eight
    already-produced finite RNG results. context_override is the resolved result
    of the optional native predicate; its basketball meaning is not established.
    """
    motions = _handles(selected, 4)
    if type(selector_bit) is not int or selector_bit not in (0, 1):
        raise ValueError("Supply selector bit 0 or 1")
    if type(player_bucket) is not int or not 0 <= player_bucket <= 0xFFFF:
        raise ValueError("Player bucket must be an unsigned halfword")
    if type(context_override) is not bool:
        raise ValueError(
            "Context override must be an explicit boolean predicate result"
        )
    _u32(control_value)
    if not isinstance(weighted_rows, (list, tuple)) or len(weighted_rows) != 8:
        raise ValueError("Supply all eight weighted rows")
    weights, pool = [], []
    for row in weighted_rows:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise ValueError("Weighted rows need two handles and a positive weight")
        pool.append(_handles(row[:2], 2))
        weight = row[2]
        if (
            type(weight) not in (int, float)
            or abs(weight) > 3.4028234663852886e38
            or not math.isfinite(weight)
        ):
            raise ValueError("Weight must be finite and positive")
        weight = _f32(weight)
        if weight <= 0:
            raise ValueError("Weight must be finite and positive")
        weights.append(weight)
    if not isinstance(bucket_rows, (list, tuple)) or len(bucket_rows) != 18:
        raise ValueError("Supply all eighteen bucket rows")
    buckets = [_handles(row, 4) for row in bucket_rows]
    fixed2 = _handles(fixed_pair2, 2, nonzero=True)
    fixed3 = _handles(fixed_pair3, 2, nonzero=True)
    original = [bool(v) for v in motions]
    count = 0 if original[0] else 8
    if not isinstance(random_samples, (list, tuple)) or len(random_samples) != count:
        raise ValueError(f"Exactly {count} native RNG samples are required")
    if any(
        type(v) not in (int, float)
        or abs(v) > 1.7976931348623157e308
        or not math.isfinite(v)
        for v in random_samples
    ):
        raise ValueError("Native RNG samples must be finite numbers")
    origins = ["source" if v else "empty" for v in motions]
    lane = 0 if selector_bit else 1
    weighted_index = None
    if not original[0]:
        total = 0.0
        for i, (weight, sample) in enumerate(zip(weights, random_samples)):
            total = _f32(total + weight)
            if _f32(weight / total) > sample:
                weighted_index = i
        if weighted_index is None:
            raise ValueError("Native weighted pool selected no valid row")
        motions[0] = pool[weighted_index][lane]
        origins[0] = "weighted-fallback"
    bucket_index = None
    if not original[1]:
        bucket_index = player_bucket % 18
        motions[1] = buckets[bucket_index][lane]
        motions[2] = buckets[bucket_index][2 + lane]
        origins[1] = origins[2] = "bucket-fallback"
    if not motions[2]:
        motions[2] = fixed2[lane]
        origins[2] = "fixed-pair2"
    if not motions[3] or context_override:
        motions[3] = fixed3[lane]
        control_value = 0
        origins[3] = "fixed-pair3-context" if context_override else "fixed-pair3"
    return dict(
        motions=motions,
        original_pair0_present=original[0],
        original_pair1_present=original[1],
        pair_origins=origins,
        control_value=control_value,
        weighted_index=weighted_index,
        bucket_index=bucket_index,
        random_draws=count,
        unresolved_motion_pairs=[i for i, value in enumerate(motions) if not value],
        context_predicate_semantics_established=False,
        target_dispatch_installed=False,
        gameplay_ready=False,
    )


def inspect_shot_fallbacks(donor, source=None):
    """Read revision-bound native fallback tables without initializing resources.

    Raw table pointers are retained. Serialized IDs resolve only by exact unique
    identity in the caller's bounded SignatureMotionSource; embedded pointers
    remain executable addresses. Empty entries are explicit, not missing files.
    """
    import hashlib

    from ..formats.embedded_motion import NativeELF

    elf = NativeELF(donor)
    guards = {0x6536C8: 0x911F001C, 0x6536DC: 0x913F0020, 0x6538C0: 0x4BFFFE78}
    for address, expected in guards.items():
        if struct.unpack(">I", elf.read(address, 4))[0] != expected:
            raise ValueError("Unsupported NBA11 shot fallback revision")

    def embedded(address):
        header = elf.read(address, 56)
        if address % 4 or struct.unpack_from(">I", header, 8)[0] != 0x1DF7DD:
            raise ValueError("Fallback pointer is not an established full-body header")
        return dict(
            kind="embedded",
            address=address,
            source_header_sha256=hashlib.sha256(header).hexdigest(),
        )

    def reference(at):
        identity, pointer = struct.unpack(">2I", elf.read(at, 8))
        result = dict(field_address=at, resource_id=identity, initial_pointer=pointer)
        if identity and pointer:
            result.update(kind="unestablished-dual-identity", status="unestablished")
        elif identity:
            candidates = [] if source is None else source.index.get(identity, [])
            result.update(
                kind="serialized",
                candidates=[dict(bank=a, record=b) for a, b in candidates],
                status="resolved-identity"
                if len(candidates) == 1
                else "ambiguous"
                if candidates
                else "external-or-missing",
            )
        elif pointer:
            result.update(embedded(pointer), status="embedded-header")
        else:
            result.update(kind="empty", status="empty")
        return result

    weighted = []
    for i in range(8):
        at = 0x434F1D0 + 20 * i
        bits = elf.read(at + 16, 4)
        weight = struct.unpack(">f", bits)[0]
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError("Weighted fallback row needs a finite positive weight")
        weighted.append(
            dict(
                row=i,
                lanes=[reference(at), reference(at + 8)],
                weight=weight,
                weight_bits=int.from_bytes(bits, "big"),
            )
        )
    buckets = [
        dict(
            row=i,
            pair1=[reference(0x434F270 + 32 * i + j) for j in (0, 8)],
            pair2=[reference(0x434F270 + 32 * i + j) for j in (16, 24)],
        )
        for i in range(18)
    ]
    return dict(
        schema=1,
        source_sha256=hashlib.sha256(donor).hexdigest(),
        source_banks_sha256=None if source is None else list(source.fingerprints),
        lane_order=[1, 0],
        weighted_rows=weighted,
        bucket_rows=buckets,
        fixed_pair2=[embedded(a) for a in (0x3F8C798, 0x3F8C7D0)],
        fixed_pair3=[reference(a) for a in (0x434F1C0, 0x434F1C8)],
        runtime_resources_initialized=False,
        target_dispatch_installed=False,
        gameplay_ready=False,
    )

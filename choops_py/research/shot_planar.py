"""Root-derived planar proposals for the paired on-court shot context.

These are represented-trajectory averages, not recovered authoring values or
automatic compatibility approval. Native root sampling uses 1/8 units and the
header's rate/time-scale, with mirror bit 30 negating X. Sample at playback end,
which can precede the final padded CH root key. Cyclic interpretation is gated.
"""

import hashlib
import math
import struct
from bisect import bisect_left

from ..formats.embedded_motion import NativeELF
from ..formats.motion_bind import canonical_channels
from ..formats.motion_frames import nba11_key_ticks
from .shot_family import _entry
from .shot_registration import inspect_registration


def _planar(header, roots, profile, *, timing=None):
    canonical_channels(header, profile)
    flags, mode = struct.unpack_from(">II", header, 16)
    if mode & 0x10000000:
        raise ValueError("Cyclic root interpretation is not established for this proposal")
    scale, duration = struct.unpack_from(">ff", header, 28)
    rate = flags >> 24
    if not rate or not all(math.isfinite(x) and x > 0 for x in (scale, duration)):
        raise ValueError("Planar proposal requires positive finite rate, scale and duration")
    if profile == "nba-2k11":
        if mode & 0x8000:
            raise ValueError("Unpacked root timing is not established")
        count = mode & 0x7FFF
        if timing is None or len(timing) != count:
            raise ValueError("Source root proposal requires exact key timing")
        ticks = nba11_key_ticks(timing)
    elif profile == "college-hoops-2k8":
        count = mode & 0xFFFF
        ticks = range(count)
    else:
        raise ValueError("Planar profile is not established")
    stride = 6 if mode & 0x80000000 else 8
    if count < 2 or len(roots) != count * stride:
        raise ValueError("Root extent/count is invalid for a planar proposal")
    end_tick = duration * rate * scale
    tolerance = max(0.002, ticks[-1] * 2e-6)
    if end_tick > ticks[-1] + tolerance:
        raise ValueError("Playback end exceeds available root key coverage")
    end_tick = min(end_tick, ticks[-1])
    right = bisect_left(ticks, end_tick)
    left = max(0, right - 1)
    fraction = (end_tick - ticks[left]) / (ticks[right] - ticks[left]) if right != left else 0
    first = struct.unpack_from(">3h", roots, 0)
    a = struct.unpack_from(">3h", roots, left * stride)
    z = struct.unpack_from(">3h", roots, right * stride)
    end = [a[i] + fraction * (z[i] - a[i]) for i in range(3)]
    x = (end[0] - first[0]) / (8 * duration)
    forward = (end[2] - first[2]) / (8 * duration)
    if mode & 0x40000000:
        x = -x
    velocity = (math.hypot(x, forward), x, forward)
    if any(not math.isfinite(v) or abs(v) > 3.4028234663852886e38 for v in velocity):
        raise ValueError("Planar proposal exceeds finite float32 metadata")
    values = struct.unpack(">3f", struct.pack(">3f", *velocity))
    return {
        "proposal_float32": list(values), "end_tick": end_tick,
        "root_quantum_native_units": 0.125,
        "one_root_step_velocity_resolution": 0.125 / duration,
        "mirror_x_applied": bool(mode & 0x40000000),
        "header_sha256": hashlib.sha256(header).hexdigest(),
        "root_sha256": hashlib.sha256(roots).hexdigest(),
        "timing_sha256": hashlib.sha256(timing).hexdigest() if timing is not None else None,
        "estimated_not_authored": True, "automatic_metadata_contract": False,
        "native_vmx_bit_exact": False, "target_compatibility_established": False,
    }


def inspect_pair_planar(source, bank, collection, index):
    """Propose represented root averages only for the established category-14 pair."""
    row = _entry(source, bank, collection, index, category=14)
    if row["tail_bytes"] != 36 or row["paired_jump_shot"] is None:
        raise ValueError("Unknown paired-shot row layout blocks planar inspection")
    proposals = []
    for ref in row["references"]:
        if ref["empty"] or ref["raw_kind"] != 0:
            raise ValueError("Paired planar inspection requires both direct lanes")
        candidates = source.index.get(ref["resource_id"], [])
        if len(candidates) != 1:
            raise ValueError("Paired-shot source identity is missing or ambiguous")
        location = candidates[0]
        tracks, report = source.tracks(*location)
        proposal = _planar(bytes.fromhex(report["header_hex"]), tracks["root"], "nba-2k11", timing=tracks["timing"])
        proposals.append({"slot": ref["slot"], "bank": location[0], "record": location[1], **proposal})
    return {
        "intended_port_scope": "on-court-5v5", "registry_category": 14,
        "source_banks_sha256": list(source.fingerprints), "lanes": proposals,
        "compatible_conversion_count": None, "gameplay_ready": False,
    }


def audit_stock_planar(raw):
    """Compare the proposal with existing CH paired-shot authoring values, read-only."""
    elf = NativeELF(raw)
    registration = inspect_registration(raw, motion_extents=True)
    headers = sorted({h for entry in registration["entries"] for h in entry["motions"]})
    rows = []
    for address in headers:
        header = elf.read(address, 64)
        mode = struct.unpack_from(">I", header, 20)[0]
        stride = 6 if mode & 0x80000000 else 8
        pointer = struct.unpack_from(">I", header, 52)[0]
        proposal = _planar(header, elf.read(pointer, (mode & 0xFFFF) * stride), "college-hoops-2k8")
        authored = struct.unpack_from(">3f", header, 36)
        error = max(abs(a - b) for a, b in zip(authored[1:], proposal["proposal_float32"][1:], strict=True))
        rows.append({
            "header": address, "authored_float32": list(authored),
            "per_axis_error": error,
            "within_one_root_step_resolution": error <= proposal["one_root_step_velocity_resolution"] + 1e-5,
            **proposal,
        })
    return {
        "scope": "existing-on-court-paired-shot-headers", "headers": len(rows),
        "within_one_root_step_resolution": sum(r["within_one_root_step_resolution"] for r in rows),
        "rows": rows, "authoring_algorithm_proven": False, "gameplay_ready": False,
    }

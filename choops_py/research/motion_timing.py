"""Native-tested duration inputs to paired playback-rate adjustment.

NBA11 0x119DC and CH 0x24F94 share these inputs. This does not establish
complete mode/state semantics, playback installation or clip compatibility.
"""

import math
import struct


def duration_divisor(mode):
    """Zero and one both select divisor1; other nibble values select themselves."""
    if type(mode) is not int or not 0 <= mode <= 0xFFFFFFFF:
        raise ValueError("Motion mode must be an unsigned32-bit integer")
    return max(1, (mode >> 24) & 15)


def inspect_rate_timing(header):
    """Read shared native timing fields without guessing an action or loop count."""
    if len(header) < 36:
        raise ValueError("Motion rate timing needs36 header bytes")
    mode, state = struct.unpack_from(">2I", header, 20)
    duration = struct.unpack_from(">f", header, 32)[0]
    if not math.isfinite(duration) or duration < 0:
        raise ValueError("Motion duration must be finite and nonnegative")
    divisor = duration_divisor(mode)
    normalized = struct.unpack(">f", struct.pack(">f", duration / divisor))[0]
    return dict(
        raw_divisor_nibble=(mode >> 24) & 15,
        duration_divisor=divisor,
        duration=duration,
        normalized_duration=normalized,
        bypasses_duration_rate_adjustment=bool(state & 16),
        normalization_division_safe=normalized > 0,
    )


def compare_rate_timing(source_header, target_header):
    """Report established inputs only; neither header is rewritten."""
    source, target = map(inspect_rate_timing, (source_header, target_header))
    keys = ("duration_divisor", "duration", "bypasses_duration_rate_adjustment")
    changed = [key for key in keys if source[key] != target[key]]
    return dict(
        schema=1,
        source=source,
        target=target,
        changed_inputs=changed,
        observed_rate_inputs_preserved=not changed,
        source_consumer="0x119DC",
        target_consumer="0x24F94",
        complete_playback_semantics_established=False,
        target_compatibility_established=False,
    )

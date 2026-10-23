"""Read-only 300-Hz selector-curve evidence from native motion samplers.

CH 0x203AC and NBA11 0x1B764 use low signed 24-bit ticks and upper-byte
selectors. Selector identities are not established cross-game semantics.
"""

import math
import struct


def inspect_selector_curve(raw, *, duration, time_scale=1):
    """Inspect a caller-established complete curve region; never infer its end.

    Padding/adjacent data must not be guessed as knots. There is no count field
    or sentinel established here; the containing record must supply the bounds.
    """
    if (
        not isinstance(raw, (bytes, bytearray))
        or not 8 <= len(raw) <= 256 * 1024
        or len(raw) % 4
    ):
        raise ValueError("Choose a bounded complete selector-curve region")
    if (
        any(
            type(v) not in (int, float)
            or abs(v) > 3.4028234663852886e38
            or not math.isfinite(v)
            for v in (duration, time_scale)
        )
        or duration < 0
        or time_scale <= 0
    ):
        raise ValueError("Selector curve timing must be finite and valid")
    knots = []
    for offset in range(0, len(raw), 4):
        word = struct.unpack_from(">I", raw, offset)[0]
        tick = word & 0xFFFFFF
        if tick & 0x800000:
            tick -= 0x1000000
        if knots and tick < knots[-1]["tick"]:
            raise ValueError(
                "Curve region has decreasing ticks or includes unproven padding"
            )
        knots.append(dict(tick=tick, selector=word >> 24, raw_word=word))
    last_query = math.ceil(duration * time_scale * 300)
    if knots[0]["tick"] > 0 or knots[-1]["tick"] < last_query:
        raise ValueError("Curve region does not bracket declared sample times")
    return dict(
        tick_rate=300,
        knots=knots,
        bytes=len(raw),
        declared_last_query_tick=last_query,
        equal_tick_pairs=sum(a["tick"] == b["tick"] for a, b in zip(knots, knots[1:])),
        selector_semantics_established=False,
        cross_game_translation_allowed=False,
        gameplay_ready=False,
    )


def sample_selector_curve(raw, seconds, *, duration, time_scale=1):
    """Reference the native bracketing/weighted-selector operation, not state IDs.

    CH 0x203AC / NBA11 0x1B764 choose the first upper knot at or after ceil(query),
    then emit one constant state or two byte-weighted states, heavier first.
    Arithmetic here is mathematical; VMX reciprocal estimates are not certified.
    A complete caller-established region and in-domain query are mandatory.
    """
    report = inspect_selector_curve(raw, duration=duration, time_scale=time_scale)
    if type(seconds) not in (int, float) or not 0 <= seconds <= duration:
        raise ValueError("Selector sample must be finite and inside declared duration")
    query = seconds * time_scale * 300
    upper = 1
    knots = report["knots"]
    while upper < len(knots) and knots[upper]["tick"] < math.ceil(query):
        upper += 1
    if upper == len(knots):
        raise ValueError("Selector query exceeds the established curve region")
    a, b = knots[upper - 1], knots[upper]
    if a["selector"] == b["selector"]:
        weights = [dict(selector=a["selector"], weight=255)]
    else:
        if a["tick"] == b["tick"]:
            raise ValueError(
                "Coincident different selectors have no established weight"
            )
        fraction = (query - a["tick"]) / (b["tick"] - a["tick"])
        if not 0 <= fraction <= 1:
            raise ValueError("Selector sample is outside its established bracket")
        right = math.floor(fraction * 255 + 0.5)
        weights = [
            dict(selector=a["selector"], weight=255 - right),
            dict(selector=b["selector"], weight=right),
        ]
        weights.sort(key=lambda row: -row["weight"])
        weights = [row for row in weights if row["weight"]]
    return dict(
        query_tick=query,
        bracket=[upper - 1, upper],
        weights=weights,
        operation="byte-weighted-selector-channel",
        weight_sum=255,
        interpolation="mathematical-reference",
        native_vmx_bit_exact=False,
        selector_semantics_established=False,
        gameplay_ready=False,
    )

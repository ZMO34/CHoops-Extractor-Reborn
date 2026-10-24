"""Read-only 300-Hz selector-curve evidence from native motion samplers.

CH 0x203AC and NBA11 0x1B764 use low signed 24-bit ticks and upper-byte
selectors. Selector identities are not established cross-game semantics.
"""

import hashlib
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


def read_selector_prefix(read, start, *, duration, time_scale=1):
    """Read the minimum knots consumed over the declared interval, not padding.

    The native sampler always loads the first two knots. Bound both mathematical
    and native single-precision endpoint queries before following later knots.
    The supplied reader must enforce the containing record/file-backed boundary.
    """
    inspect_selector_curve(
        struct.pack(">II", 0, 0x007FFFFF),
        duration=duration,
        time_scale=time_scale,
    )
    if type(start) is not int or start < 0 or start % 4:
        raise ValueError("Selector pointer must be word aligned")

    def single(value):
        try:
            return struct.unpack(">f", struct.pack(">f", value))[0]
        except (OverflowError, struct.error) as error:
            raise ValueError("Selector query exceeds native float range") from error

    query = max(
        math.ceil(duration * time_scale * 300),
        math.ceil(single(single(duration * time_scale) * 300)),
    )
    if query > 0x7FFFFF:
        raise ValueError("Selector endpoint exceeds signed 24-bit ticks")
    result = bytearray()
    last_tick = None
    for i in range(65536):
        data = read(start + i * 4, 4)
        if len(data) != 4:
            raise ValueError("Truncated selector knot")
        word = struct.unpack(">I", data)[0]
        tick = word & 0xFFFFFF
        if tick & 0x800000:
            tick -= 0x1000000
        if last_tick is not None and tick < last_tick:
            raise ValueError("Decreasing selector ticks before terminal bracket")
        result.extend(data)
        last_tick = tick
        if i and tick >= query:
            inspect_selector_curve(result, duration=duration, time_scale=time_scale)
            return bytes(result)
    raise ValueError("Selector prefix exceeds bounded knot count")


def transcode_selector_curve(
    raw, contract, *, channel, target_elf_sha256, duration, time_scale=1
):
    """Translate selector bytes only under an explicit input-bound research map.

    No identity mapping is implied. Preserve every signed tick bit and knot;
    channel/resource semantics remain explicit caller assertions.
    """
    report = inspect_selector_curve(raw, duration=duration, time_scale=time_scale)
    if (
        not isinstance(contract, dict)
        or type(contract.get("schema")) is not int
        or contract["schema"] != 1
        or type(channel) is not int
        or not 0 <= channel < 63
        or type(contract.get("source_channel")) is not int
        or contract["source_channel"] != channel
        or contract.get("source_curve_sha256") != hashlib.sha256(raw).hexdigest()
        or not isinstance(target_elf_sha256, str)
        or len(target_elf_sha256) != 64
        or contract.get("target_elf_sha256") != target_elf_sha256
    ):
        raise ValueError("Selector contract identity/fingerprints changed")
    evidence = contract.get("channel_evidence")
    rules = contract.get("rules")
    if (
        not isinstance(evidence, str)
        or not evidence.strip()
        or len(evidence) > 2048
        or not isinstance(rules, list)
        or not 1 <= len(rules) <= 256
    ):
        raise ValueError("Selector channel needs bounded evidence and explicit rules")
    mapping = {}
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("Invalid selector rule")
        a, b, text = (rule.get(k) for k in ("source", "target", "evidence"))
        if (
            any(type(v) is not int or not 0 <= v <= 255 for v in (a, b))
            or a in mapping
            or not isinstance(text, str)
            or not text.strip()
            or len(text) > 2048
        ):
            raise ValueError("Invalid, duplicate or unproven selector rule")
        mapping[a] = b, text
    used = sorted({v["selector"] for v in report["knots"]})
    if any(v not in mapping for v in used):
        raise ValueError("Selector curve contains unmapped identities")
    output = b"".join(
        struct.pack(">I", mapping[k["selector"]][0] << 24 | k["raw_word"] & 0xFFFFFF)
        for k in report["knots"]
    )
    check = inspect_selector_curve(output, duration=duration, time_scale=time_scale)
    if [v["tick"] for v in check["knots"]] != [v["tick"] for v in report["knots"]]:
        raise ValueError("Selector tick preservation failed")
    return output, dict(
        source_channel=channel,
        source_curve_sha256=hashlib.sha256(raw).hexdigest(),
        target_elf_sha256=target_elf_sha256,
        channel_evidence=evidence,
        rules=[
            dict(source=v, target=mapping[v][0], evidence=mapping[v][1]) for v in used
        ],
        signed_tick_bits_preserved=True,
        mapping_provenance="explicit-caller-research-assertions",
        semantics_automatically_established=False,
        gameplay_ready=False,
    )

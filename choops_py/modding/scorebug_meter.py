"""Narrow IFF-only recolor of the observed 19-segment sixth-man meter.

Native 82E3B0 selects channels; 82E194 samples cubic coefficient tuples using
N intervals / N+1 boundaries. Only the observed constant-polynomial RGB tracks
are writable here. The native timeline, alpha, activation and gameplay stay owned
by the game; this does not add any scorebug text providers.
"""

import bisect
import math
import struct

from choops_py.formats.binary import Binary


def _floats(data, at, count):
    raw = Binary(data).slice(at, count * 4)
    values = struct.unpack(">" + str(count) + "f", raw)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("Non-finite meter animation data")
    return values


def inspect_meter(header):
    """Validate the observed color-only binding contract, without writing."""
    if len(header) > 32 * 1024 * 1024:
        raise ValueError("Meter header exceeds inspection budget")
    b = Binary(header)
    if b.u32(0x18) != 19 or b.u32(0x30) != 19 or b.u32(0x44) != 1:
        raise ValueError("Not the observed 19-segment meter")
    model = b.relative(0x48)
    b.slice(model, 176)
    if b.utf16(b.relative(model), "be") != "sixth_man_meter":
        raise ValueError("Unexpected meter model identity")
    if b.u32(model + 0x60) != 21 or b.u32(0x28) != 1:
        raise ValueError("Unexpected meter skeleton/shader layout")
    shader = b.relative(0x2C)
    if b.u32(shader + 8) >> 16 != 2:
        raise ValueError("Unexpected meter uniform declarations")
    uniform = b.relative(shader + 24)
    b.slice(uniform, 88)
    if b.u32(uniform) != 0x9015351F or b.u32(uniform + 8) != 0x0F14FD0C:
        raise ValueError("Missing observed DiffuseColor declaration")
    color_offset, link_offset = b.u16(uniform + 20), b.u16(uniform + 22)
    length = b.u32(shader + 12) & 0xFFFF
    if color_offset + 16 > length or link_offset + 16 > length:
        raise ValueError("Meter color binding exceeds material parameters")
    materials = b.relative(0x38)
    b.slice(materials, 19 * 40)
    links = []
    for i in range(19):
        material = materials + 40 * i
        if b.u32(material + 8) != b.u32(shader):
            raise ValueError("Unexpected meter material shader")
        parameters = b.relative(material + 32)
        b.slice(parameters, length)
        links.append(b.u32(parameters + link_offset + 12))
    table = b.relative(0x1C)
    b.slice(table, 19 * 28)
    rows = []
    for i in range(19):
        at = table + i * 28
        if b.u32(at + 8) != 0x00F0088F:
            raise ValueError("Unsupported meter animation flags")
        cursor = b.relative(at + 24)
        channels = []
        for _ in range(3):
            count = b.u16(cursor)
            if not 1 <= count <= 4096 or b.u32(cursor + 4) != 0:
                raise ValueError("Unsupported meter curve count/loop")
            times = _floats(header, b.relative(cursor + 8), count + 1)
            coefficients = _floats(header, b.relative(cursor + 12), count * 4)
            if any(a >= c for a, c in zip(times, times[1:])):
                raise ValueError("Meter boundaries must strictly increase")
            if any(
                coefficients[j] != 0 for j in range(len(coefficients)) if j % 4 != 3
            ):
                raise ValueError("Only constant-polynomial meter tracks are writable")
            values = coefficients[3::4]
            if any(not -0.001 <= v <= 1.001 for v in values):
                raise ValueError("Unsupported meter color range")
            channels.append(dict(times=times, values=values))
            cursor += 16
        alpha = _floats(header, cursor, 1)[0]
        if alpha != 1:
            raise ValueError("Unexpected meter alpha contract")
        if len({(c["times"][0], c["times"][-1]) for c in channels}) != 1:
            raise ValueError("Meter channels have different timeline extents")
        rows.append(dict(at=at, key=b.u32(at), channels=channels, alpha=alpha))
    keys = [r["key"] for r in rows]
    if len(set(keys)) != 19 or len(set(links)) != 19 or set(links) != set(keys):
        raise ValueError("Meter animations do not uniquely bind the color parameters")
    return rows


def sample(channel, time):
    if not math.isfinite(time):
        raise ValueError("Non-finite sample time")
    i = max(
        0,
        min(
            bisect.bisect_right(channel["times"], time) - 1, len(channel["values"]) - 1
        ),
    )
    return channel["values"][i]


def reskin_meter(parts):
    """Append monochrome RGB curves, retaining clamped peak-brightness timing.

    Only the 19 curve-array pointers change in the existing header. All original
    data (including alpha, output buffers and material bindings) is retained;
    the vertex/index part is byte-exact. No native activation/threshold changes.
    """
    if len(parts) != 2:
        raise ValueError("Meter recolor requires the observed split scene")
    source = parts[0]
    rows = inspect_meter(source)
    out = bytearray(source)

    def append(raw):
        out.extend(bytes((-len(out)) % 16))
        at = len(out)
        out.extend(raw)
        return at

    def pointer(field, target):
        struct.pack_into(">i", out, field, target - field + 1)

    for row in rows:
        channels = row["channels"]
        times = sorted({t for channel in channels for t in channel["times"]})
        values = [
            max(0.0, min(1.0, max(sample(c, t) for c in channels))) for t in times[:-1]
        ]
        curve_table = append(bytes(48) + struct.pack(">f", row["alpha"]))
        time_table = append(struct.pack(">" + str(len(times)) + "f", *times))
        value_table = append(b"".join(struct.pack(">4f", 0, 0, 0, v) for v in values))
        for i in range(3):
            q = curve_table + 16 * i
            struct.pack_into(">HHI", out, q, len(values), 0, 0)
            pointer(q + 8, time_table)
            pointer(q + 12, value_table)
        pointer(row["at"] + 24, curve_table)
    result = bytes(out)
    inspected = inspect_meter(result)
    changed = {r["at"] + 24 + j for r in rows for j in range(4)}
    if any(a != c for i, (a, c) in enumerate(zip(source, result)) if i not in changed):
        raise ValueError("Meter recolor changed unrelated source bytes")
    for old, new in zip(rows, inspected):
        times = sorted({t for c in old["channels"] for t in c["times"]})
        for t in times + [(a + c) / 2 for a, c in zip(times, times[1:])]:
            expected = max(0.0, min(1.0, max(sample(c, t) for c in old["channels"])))
            if any(sample(c, t) != expected for c in new["channels"]):
                raise ValueError("Meter brightness timeline did not round trip")
    return [result, parts[1]], dict(
        animations=19,
        color="monochrome",
        clamped_peak_brightness_preserved=True,
        alpha_preserved=True,
        original_bytes_retained=True,
        native_activation_unchanged=True,
        added_header_bytes=len(result) - len(source),
    )

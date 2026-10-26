import struct

import pytest

from choops_py.formats.binary import Binary
from choops_py.modding.scorebug_meter import inspect_meter, reskin_meter, sample


def fixture():
    data = bytearray(0x88)

    def block(size):
        data.extend(bytes((-len(data)) % 16))
        at = len(data)
        data.extend(bytes(size))
        return at

    def word(at, value):
        struct.pack_into(">I", data, at, value)

    def pointer(at, target):
        word(at, target - at + 1)

    model, shader, uniforms, materials, tracks = (
        block(176),
        block(48),
        block(88),
        block(19 * 40),
        block(19 * 28),
    )
    name = "sixth_man_meter".encode("utf-16-be") + b"\0\0"
    name_at = block(len(name))
    data[name_at : name_at + len(name)] = name
    pointer(model, name_at)
    word(model + 0x60, 21)
    for at, value in ((0x18, 19), (0x28, 1), (0x30, 19), (0x44, 1)):
        word(at, value)
    for at, target in (
        (0x1C, tracks),
        (0x2C, shader),
        (0x38, materials),
        (0x48, model),
    ):
        pointer(at, target)
    word(shader, 0x12345678)
    word(shader + 8, 2 << 16)
    word(shader + 12, 240)
    pointer(shader + 24, uniforms)
    word(uniforms, 0x9015351F)
    word(uniforms + 8, 0x0F14FD0C)
    struct.pack_into(">HH", data, uniforms + 20, 0x50, 0xC0)
    for i in range(19):
        key = 100 + i
        material, track = materials + i * 40, tracks + i * 28
        parameters = block(240)
        word(material + 8, 0x12345678)
        pointer(material + 32, parameters)
        word(parameters + 0xCC, key)
        word(track, key)
        word(track + 8, 0xF0088F)
        table = block(52)
        pointer(track + 24, table)
        for channel, (times, values) in enumerate(
            (
                ((0.0, 1.0, 2.0), (0.1, 0.8)),
                ((0.0, 0.5, 2.0), (0.6, 0.2)),
                ((0.0, 1.5, 2.0), (0.3, 0.9)),
            )
        ):
            q = table + channel * 16
            struct.pack_into(">H", data, q, len(values))
            t, v = block(12), block(32)
            struct.pack_into(">3f", data, t, *times)
            for j, value in enumerate(values):
                struct.pack_into(">4f", data, v + j * 16, 0.0, 0.0, 0.0, value)
            pointer(q + 8, t)
            pointer(q + 12, v)
        struct.pack_into(">f", data, table + 48, 1.0)
    return [bytes(data), b"vertex/index bytes retained"]


def test_reskin_preserves_native_brightness_across_different_channel_boundaries():
    parts = fixture()
    old = inspect_meter(parts[0])
    result, audit = reskin_meter(parts)
    new = inspect_meter(result[0])
    for time in (-1.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0):
        expected = max(sample(c, time) for c in old[0]["channels"])
        assert [sample(c, time) for c in new[0]["channels"]] == [expected] * 3
    assert all(r["alpha"] == 1 for r in new)
    assert audit["native_activation_unchanged"]
    assert result[1] == parts[1]


def test_only_curve_pointers_change_in_original_extent():
    parts = fixture()
    before = tuple(parts)
    rows = inspect_meter(parts[0])
    result, _ = reskin_meter(parts)
    changed = {r["at"] + 24 + j for r in rows for j in range(4)}
    assert all(
        a == b for i, (a, b) in enumerate(zip(parts[0], result[0])) if i not in changed
    )
    assert tuple(parts) == before
    assert len(result[0]) > len(parts[0])


@pytest.mark.parametrize("kind", ["flags", "loop", "cubic", "alpha", "time", "binding"])
def test_unsupported_animation_or_binding_is_refused(kind):
    parts = fixture()
    data = bytearray(parts[0])
    b = Binary(data)
    track = b.relative(0x1C)
    table = b.relative(track + 24)
    if kind == "flags":
        struct.pack_into(">I", data, track + 8, 0)
    elif kind == "loop":
        struct.pack_into(">I", data, table + 4, 1)
    elif kind == "cubic":
        struct.pack_into(">f", data, b.relative(table + 12), 0.2)
    elif kind == "alpha":
        struct.pack_into(">f", data, table + 48, 0.5)
    elif kind == "time":
        struct.pack_into(">f", data, b.relative(table + 8) + 4, 0)
    else:
        parameters = b.relative(b.relative(0x38) + 32)
        struct.pack_into(">I", data, parameters + 0xCC, 0)
    with pytest.raises(ValueError):
        reskin_meter([bytes(data), parts[1]])


def test_truncation_is_refused():
    parts = fixture()
    with pytest.raises(ValueError):
        reskin_meter([parts[0][:-10], parts[1]])

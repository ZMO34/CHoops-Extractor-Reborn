import struct
import zlib

import pytest

from choops_py.modding.scorebug_text import inspect_text_dependencies


def scene(root_indices=(0, 1, 2), marker="gameclock"):
    header = bytearray(4096)
    pool = 2600

    def word(at, value):
        struct.pack_into(">I", header, at, value)

    def pointer(at, target):
        word(at, target - at + 1)

    def text(at, value):
        nonlocal pool
        pointer(at, pool)
        data = value.encode("utf-16-be") + bytes(2)
        header[pool : pool + len(data)] = data
        pool = (pool + len(data) + 3) & ~3

    word(0x4C, 2)
    pointer(0x50, 128)
    for i, binding in enumerate(("home_score", "gameclock")):
        row = 128 + i * 144
        style = 512 + i * 128
        text(row + 64, binding)
        pointer(row + 80, style)
        word(style, 2)
        for j, (key, value) in enumerate(
            (
                (0xE27EC83B, "Score_bug"),
                (0xAE7E1958, binding if i == 0 else marker),
            )
        ):
            prop = style + 16 + j * 32
            text(prop, value)
            word(prop + 16, 3)
            word(prop + 20, key)
    word(0x44, 2)
    pointer(0x48, 1024)
    for i, (name, markers) in enumerate(
        (
            ("Score_bug", ("Score_bug", "home_score", "gameclock")),
            ("text_nodeMask", ("text_nodeMask",)),
        )
    ):
        model = 1024 + i * 176
        bones = 2304 + i * 144
        draw = 2048 + i * 48
        descriptor = 2208 + i * 48
        text(model, name)
        word(model + 0x60, len(markers))
        pointer(model + 0x64, bones)
        for j, name in enumerate(markers):
            text(bones + j * 48 + 32, name)
            word(bones + j * 48 + 36, zlib.crc32(name.encode('ascii')))
        word(model + 0x7C, 1)
        pointer(model + 0x80, draw)
        word(model + 0x84, 1)
        pointer(model + 0x88, descriptor)
        word(descriptor + 16, 3)
        word(model + 0xA4, 0x20000010)
        word(model + 0xA8, 3)
        word(model + 0xAC, 193 + i * 6)
        struct.pack_into(">3I", header, draw, 6, 0, 3)
    payload = bytes(192) + struct.pack(">6H", *root_indices, 0, 1, 2)
    return [bytes(header), payload]


def test_all_labels_report_shared_owner_draw_suppression_without_visibility_claim():
    stock = scene()
    suppressed = scene((0, 0, 0))
    before = inspect_text_dependencies(stock)
    after = inspect_text_dependencies(suppressed)
    assert all(row["resolved"] for row in after["text"])
    assert all(row["native_marker_resolved"] for row in after["text"])
    assert all(row["owner_submitted_triangles"] == 1 for row in before["text"])
    assert all(row["owner_submitted_triangles"] == 0 for row in after["text"])
    assert after["models"]["text_nodeMask"]["submitted_triangles"] == 1
    assert not after["runtime_visibility_verified"]
    assert stock == scene()


def test_unresolved_marker_is_reported_separately_from_draw_activity():
    report = inspect_text_dependencies(scene(marker="absent"))
    assert report["text"][0]["resolved"]
    assert not report["text"][1]["resolved"]
    assert report["text"][1]["owner_submitted_triangles"] == 1


def test_invalid_draw_and_out_of_bounds_index_are_rejected():
    parts = scene((0, 1, 3))
    with pytest.raises(ValueError, match="outside vertex"):
        inspect_text_dependencies(parts)
    parts = scene()
    header = bytearray(parts[0])
    struct.pack_into(">I", header, 2048 + 8, 4)
    with pytest.raises(ValueError, match="draw/index"):
        inspect_text_dependencies([bytes(header), parts[1]])


def test_unbounded_draw_count_is_rejected_before_traversal():
    parts = scene()
    header = bytearray(parts[0])
    struct.pack_into(">I", header, 1024 + 0x7C, 10001)
    with pytest.raises(ValueError, match="draw count"):
        inspect_text_dependencies([bytes(header), parts[1]])


def test_marker_name_without_matching_native_hash_does_not_pass_native_lookup():
    parts = scene()
    header = bytearray(parts[0])
    struct.pack_into('>I', header, 2304 + 48 + 36, 0)
    report = inspect_text_dependencies([bytes(header), parts[1]])
    assert report['text'][0]['resolved']
    assert not report['text'][0]['native_marker_resolved']
    assert report['text'][1]['native_marker_resolved']

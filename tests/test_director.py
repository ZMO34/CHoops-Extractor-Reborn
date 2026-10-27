import struct

import pytest

from choops_py.research.director import decode_command, inspect_director, is_stream_end


def fixture():
    h = bytearray(0xC00)

    def word(at, value):
        struct.pack_into(">I", h, at, value)

    def ptr(at, target):
        word(at, target - at + 1)

    word(0, 0x1FF1DF58)
    struct.pack_into(">H", h, 6, 2)
    word(0x0C, 1)
    word(0x10, 2)
    ptr(0x14, 0x40)
    ptr(0x18, 0x80)
    ptr(0x1C, 0x800)
    ptr(0x20, 0x620)
    ptr(0x24, 0x620)  # Repeated references are preserved, not collapsed.
    ptr(0x40, 0x60)
    h[0x60:0x6A] = "Name".encode("utf-16-be") + bytes(2)
    ptr(0x84, 0x500)
    word(0x500, 1)
    word(0x504, 0x1000)
    ptr(0x508, 0x600)
    ptr(0x51C, 0x620)
    h[0x700:0x703] = bytes([1, 3, 9])
    struct.pack_into(">H", h, 0x800 + 259 * 2, 0x163)
    struct.pack_into(">H", h, 0x800 + 9 * 2, 0x15B)
    return bytes(h)


def test_indexes_without_changing_source_or_executing_commands():
    h = fixture()
    before = bytes(h)
    report = inspect_director(h)
    assert h == before
    assert report["reference_offsets"] == [0x620, 0x620]
    assert report["strings"] == [dict(offset=0x60, text="Name")]
    assert report["groups"][0]["index"] == 1
    assert report["groups"][0]["records"] == [0x620]
    assert report["record_reference_count"] == 1
    assert report["groups"][0]["section_targets"] == [0x600, None, None, None, None]
    assert not report["command_execution_supported"]
    assert not report["writing_supported"]


def test_decodes_short_and_extended_indices_at_explicit_boundaries():
    h = fixture()
    assert decode_command(h, 0x700, 0x703) == dict(
        offset=0x700, encoded_index=259, token=0x163, next=0x702,
    )
    assert decode_command(h, 0x702, 0x703)["token"] == 0x15B
    with pytest.raises(ValueError, match="Truncated"):
        decode_command(h, 0x700, 0x701)


def test_native_end_sentinel_needs_only_one_byte():
    h = fixture()
    assert is_stream_end(h, len(h) - 1, len(h))
    with pytest.raises(ValueError, match="Truncated"):
        decode_command(h, len(h) - 1, len(h))


def test_native_end_prevents_decoding_bytes_after_the_sentinel():
    h = bytearray(fixture())
    h[0x700:0x703] = bytes([0, 9, 0xFF])
    before = bytes(h)
    assert is_stream_end(h, 0x700, 0x703)
    # Reading an index without the VM's preflight would misread this as 15B.
    assert decode_command(h, 0x700, 0x703)["token"] == 0x15B
    assert h == before


def test_native_end_does_not_search_inside_a_command_operand():
    h = fixture()
    assert not is_stream_end(h, 0x700, 0x703)


@pytest.mark.parametrize("position,end", [(-1, 1), (0, 0), (1, 0xC01), (True, 2), (1, False)])
def test_native_end_rejects_invalid_stream_bounds(position, end):
    with pytest.raises(ValueError):
        is_stream_end(fixture(), position, end)


@pytest.mark.parametrize("case", [
    "magic", "threshold", "strings", "group_count", "group_pointer",
    "record_pointer", "map_pointer", "alignment", "reference_count",
])
def test_rejects_malformed_or_unbounded_tables(case):
    h = bytearray(fixture())
    at, value = {
        "magic": (0, 0), "threshold": (0x10, 257), "strings": (0x0C, 4097),
        "group_count": (0x500, 65537), "group_pointer": (0x84, 0xFFFFFFFC),
        "record_pointer": (0x51C, 0xFFFFFFFC), "map_pointer": (0x1C, 0),
        "alignment": (0x18, 0x81 - 0x18 + 1),
        "reference_count": (4, 0x0000FFFF),
    }[case]
    struct.pack_into(">I", h, at, value)
    with pytest.raises(ValueError):
        inspect_director(bytes(h))


@pytest.mark.parametrize("position,end", [(-1, 1), (0, 0), (1, 0xC01), (True, 2)])
def test_rejects_invalid_stream_bounds(position, end):
    with pytest.raises(ValueError):
        decode_command(fixture(), position, end)


def test_refuses_index_past_file_backed_token_map():
    h = bytearray(fixture())
    struct.pack_into(">I", h, 0x1C, 0xBFE - 0x1C + 1)
    with pytest.raises(ValueError):
        decode_command(bytes(h), 0x702, 0x703)

"""Builder validation of the observed variable-size compressed SCNE profile."""
import struct

import pytest

from choops_py.archive.add_assets import asset_payload, build
from choops_py.archive.hash_names import hash_name
from choops_py.archive.usrdir_reader import Archive
from choops_py.formats.cdf_backed_iff import CDFPair
from choops_py.formats.cdf_backed_iff_writer import name_trailer
from choops_py.formats.compression import decode
from tests.support import game_fixture, literal


def scene_pair(native_type=0xE26C9B5D, name_type="SCNE", capacities=(128, 256)):
    name = "scenes.cdf"
    end = 148 + len(name.encode("utf-16-be")) + 2
    header = bytearray(end)
    stored = [literal(bytes(84)), literal(b"scene vertices")]
    struct.pack_into(
        ">10I", header, 0, 0xF0985030, end, end, 0, 2, 21, 1, 77, 97, 113
    )
    for j, capacity in enumerate(capacities):
        struct.pack_into(
            ">8I", header, 40 + j * 32, 1, 1, 128, capacity, 0, end, capacity, 0
        )
    struct.pack_into(">I", header, 104, 5)
    struct.pack_into(">5I", header, 108, 1, native_type, 2, 0, 0)
    struct.pack_into(">I", header, 128, 5)
    struct.pack_into(">4I", header, 132, 0, len(stored[0]), len(stored[0]), len(stored[1]))
    header[148:] = name.encode("utf-16-be") + bytes(2)
    metadata = bytes(header) + name_trailer([dict(name="scene", type=name_type)])
    return metadata, b"".join(stored)


@pytest.mark.parametrize("name", ["scenes.iff", "scenes.cdf"])
def test_scene_chunks_may_be_smaller_than_the_declared_maximum(name):
    metadata, cdf = scene_pair()
    before = metadata, cdf
    changes = {"scenes.iff": metadata, "scenes.cdf": cdf}
    result = asset_payload(name, changes[name], changes)
    assert result == changes[name]
    assert (metadata, cdf) == before
    assert CDFPair(metadata, cdf).records[0]["primary_words"][1] == 0xE26C9B5D


@pytest.mark.parametrize("capacities", [(83, 256), (128, 13)])
def test_scene_chunks_cannot_exceed_either_declared_maximum(capacities):
    metadata, cdf = scene_pair(capacities=capacities)
    changes = {"scenes.iff": metadata, "scenes.cdf": cdf}
    with pytest.raises(ValueError, match="capacity"):
        asset_payload("scenes.iff", metadata, changes)


@pytest.mark.parametrize("native_type", [0x5C369069, 0x12345678])
def test_editable_name_label_cannot_enable_the_scene_profile(native_type):
    metadata, cdf = scene_pair(native_type=native_type, name_type="SCNE")
    with pytest.raises(ValueError):
        asset_payload("scenes.iff", metadata, {"scenes.iff": metadata, "scenes.cdf": cdf})


def test_scene_profile_does_not_relax_compressed_stream_bounds():
    metadata, cdf = scene_pair()
    corrupt = bytearray(cdf)
    struct.pack_into(">I", corrupt, 8, 1)
    with pytest.raises(ValueError):
        asset_payload("scenes.iff", metadata, {"scenes.iff": metadata, "scenes.cdf": corrupt})


def test_scene_capacity_is_checked_before_decompressing(monkeypatch):
    from choops_py.formats import compression

    metadata, cdf = scene_pair()
    corrupt = bytearray(cdf)
    struct.pack_into(">I", corrupt, 4, 129)

    def unexpected_decode(*args, **kwargs):
        pytest.fail("Oversized logical chunk reached the allocating decoder")

    monkeypatch.setattr(compression, "decode", unexpected_decode)
    with pytest.raises(ValueError, match="capacity"):
        asset_payload("scenes.iff", metadata, {"scenes.iff": metadata, "scenes.cdf": corrupt})


def test_uncompressed_short_chunk_does_not_use_the_compressed_scene_profile():
    metadata, cdf = scene_pair()
    corrupt = bytearray(cdf)
    corrupt[:4] = b"RAW!"
    with pytest.raises(ValueError):
        asset_payload("scenes.iff", metadata, {"scenes.iff": metadata, "scenes.cdf": corrupt})


def test_growing_scene_pair_roundtrip_preserves_source_and_old_cdf_bytes(tmp_path):
    metadata, cdf = scene_pair()
    source = game_fixture(tmp_path / "source", metadata)
    bank = source / "PS3_GAME/USRDIR/0A"
    original = bytearray(8192)
    original[:2048] = bank.read_bytes()[:2048]
    struct.pack_into(">I", original, 16, 2)
    struct.pack_into(">I", original, 24, 4)
    entries = sorted([
        (hash_name("scenes.iff"), 1, 0, len(metadata)),
        (hash_name("scenes.cdf"), 2, 0, len(cdf)),
    ])
    for i, entry in enumerate(entries):
        struct.pack_into(">4I", original, 40 + 16 * i, *entry)
    original[2048:2048 + len(metadata)] = metadata
    original[4096:4096 + len(cdf)] = cdf
    bank.write_bytes(original)

    header_chunk = literal(bytes(80) + b"EDIT")
    payload_chunk = literal(b"new vertices!!")
    # Retain old data and force an extent larger than the synthetic allocation.
    header_at = len(cdf) + 8192
    new_cdf = cdf + bytes(8192) + header_chunk + payload_chunk
    changed = bytearray(metadata)
    struct.pack_into(
        ">4I", changed, 132, header_at, len(header_chunk),
        header_at + len(header_chunk), len(payload_chunk),
    )
    replacements = {"scenes.iff": bytes(changed), "scenes.cdf": new_cdf}
    output = tmp_path / "rebuilt"
    report = build(source, {}, output, replacements)
    rebuilt = Archive(output)
    by_hash = {entry["hash"]: entry for entry in rebuilt.entries}
    actual_cdf = rebuilt.read(by_hash[hash_name("scenes.cdf")])
    actual_iff = rebuilt.read(by_hash[hash_name("scenes.iff")])
    assert actual_cdf.startswith(new_cdf)
    assert actual_cdf[:len(cdf)] == cdf
    record = CDFPair(actual_iff, actual_cdf).records[0]
    assert record["primary_words"] == [
        1, 0xE26C9B5D, 2, 0, 0,
    ]
    for key, expected in (("header", bytes(80) + b"EDIT"), ("payload", b"new vertices!!")):
        chunk = actual_cdf[record[key + "_offset"]:record[key + "_offset"] + record[key + "_length"]]
        assert decode(chunk) == expected
    assert bank.read_bytes() == original
    assert report["source_unchanged"] and not report["runtime_verified"]

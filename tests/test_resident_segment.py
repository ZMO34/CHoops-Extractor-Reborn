import struct

import pytest
from test_target_motion import fixture

from choops_py.formats.embedded_motion import NativeELF
from choops_py.research.resident_segment import append_resident_image
from choops_py.research.target_motion import prepare_target_image, relocate_target_image


def inputs():
    raw = fixture()
    image, manifest = prepare_target_image(raw, [0x10000, 0x10040])
    return raw, image, manifest["header_offsets"]


def test_resident_native_loading_preserves_existing_bss_and_owns_all_tracks():
    raw, image, offsets = inputs()
    before = bytes(raw)
    result, report = append_resident_image(raw, image, offsets)
    elf = NativeELF(result)
    base = report["resident_base"]
    assert base == 0x10900
    assert elf.read(0x10000, 0x800) == before[0x100:0x900]
    assert elf.read(0x10800, 0x100) == bytes(0x100)
    native = elf.read(base, len(image))
    assert relocate_target_image(native, offsets, base, source_state="native") == image
    assert report["runtime_heap_allocations"] == 0
    assert report["storage_lifetime"] == "process-exit"
    assert not report["registered"] and not report["ps3_runtime_verified"]
    assert raw == before and report["inverse_preservation_verified"]


def sections(raw):
    raw.extend(bytes(0xA10 - len(raw)))
    raw[0x900:0x940] = bytes(range(64))
    struct.pack_into(">Q", raw, 40, 0x980)
    struct.pack_into(">HHH", raw, 58, 64, 2, 0)
    struct.pack_into(">IIQQQQIIQQ", raw, 0x9C0, 0, 1, 0, 0, 0x900, 64, 0, 0, 1, 0)
    return raw


def test_trailing_sections_move_intact_instead_of_becoming_nonzero_bss():
    raw, image, offsets = inputs()
    sections(raw)
    before = bytes(raw)
    result, report = append_resident_image(raw, image, offsets)
    growth = report["added_file_bytes"]
    shoff = struct.unpack_from(">Q", result, 40)[0]
    assert shoff == 0x980 + growth
    moved_offset = struct.unpack_from(">Q", result, shoff + 64 + 24)[0]
    assert moved_offset == 0x900 + growth
    assert result[moved_offset : moved_offset + 64] == bytes(range(64))
    assert NativeELF(result).read(0x10800, 0x100) == bytes(0x100)
    assert raw == before


@pytest.mark.parametrize(
    "kind",
    [
        "readonly-last",
        "alignment",
        "collision",
        "tls",
        "crossing-section",
        "section-table",
        "extended-sections",
        "section-bounds",
        "address-overflow",
    ],
)
def test_unsafe_native_layouts_fail_without_changing_inputs(kind):
    raw, image, offsets = inputs()
    if kind == "readonly-last":
        struct.pack_into(">I", raw, 68, 4)
    elif kind == "alignment":
        struct.pack_into(">Q", raw, 112, 3)
    elif kind == "collision":
        struct.pack_into(">H", raw, 56, 2)
        struct.pack_into(">II6Q", raw, 120, 1, 4, 0x80, 0x10900, 0x10900, 0, 16, 16)
    elif kind == "tls":
        struct.pack_into(">H", raw, 56, 2)
        struct.pack_into(">II6Q", raw, 120, 7, 4, 0x800, 0x10880, 0x10880, 0, 0x200, 16)
    elif kind == "crossing-section":
        sections(raw)
        struct.pack_into(">QQ", raw, 0x9C0 + 24, 0x8E0, 64)
    elif kind == "section-table":
        sections(raw)
        struct.pack_into(">Q", raw, 40, 0x8E0)
    elif kind == "extended-sections":
        struct.pack_into(">Q", raw, 40, 0x800)
    elif kind == "section-bounds":
        sections(raw)
        struct.pack_into(">Q", raw, 0x9C0 + 24, len(raw) - 1)
    elif kind == "address-overflow":
        # Original range is valid but leaves insufficient address space to append.
        struct.pack_into(">QQ", raw, 80, 0xFFFFF700, 0xFFFFF700)
    before = bytes(raw)
    with pytest.raises(ValueError):
        append_resident_image(raw, image, offsets)
    assert raw == before


def test_unowned_motion_and_budget_rejected_before_native_installation():
    raw, image, offsets = inputs()
    with pytest.raises(ValueError, match="budget"):
        append_resident_image(raw, image, offsets, budget=64)
    bad = bytearray(image)
    struct.pack_into(">I", bad, offsets[0] + 48, 0x7FFFFFFF)
    with pytest.raises(ValueError):
        append_resident_image(raw, bad, offsets)
    # Unknown auxiliary channels do not acquire guessed resident lifetimes.
    bad = bytearray(image)
    bad[offsets[0] + 19] |= 1
    with pytest.raises(ValueError):
        append_resident_image(raw, bad, offsets)


def publication_inputs():
    import hashlib

    from test_shot_registration import registration_fixture

    raw, word = registration_fixture()
    _, image, offsets = inputs()
    # Give the stock synthetic header complete known tracks for the deep audit.
    source = fixture()[0x100:0x140]
    elf = NativeELF(raw)
    at = elf.target(0x11000)["file_offset"]
    raw[at : at + 64] = source
    word(0x11030, 0x8A1000)
    word(0x11034, 0x8A1200)
    word(0x11038, 0x8A1300)
    word(0x8A1300, 0x80000000)
    # The old fixture's standalone label BSS has four-byte alignment.
    struct.pack_into(">Q", raw, 64 + 5 * 56 + 48, 4)
    contract = dict(
        schema=1,
        target_elf_sha256=hashlib.sha256(raw).hexdigest(),
        image_sha256=hashlib.sha256(image).hexdigest(),
        entries=[
            dict(
                header_indices=[0, 1],
                playback_metadata_hex=bytes(range(32)).hex(),
                target_label_key=0xA2655289,
                evidence=dict(
                    playback="Synthetic assertion only",
                    label="Synthetic tagged-key assertion",
                ),
            )
        ],
    )
    return raw, image, offsets, contract


def test_native_publication_points_added_row_at_owned_resident_tracks():
    from choops_py.research.resident_segment import install_resident_shots
    from choops_py.research.shot_registration import inspect_registration

    raw, image, offsets, contract = publication_inputs()
    before = bytes(raw)
    result, report = install_resident_shots(raw, image, offsets, contract)
    audit = inspect_registration(result, motion_extents=True)
    assert audit["count"] == 113 and audit["original_records_preserved"]
    assert audit["entries"][-1]["motions"] == report["header_addresses"]
    assert report["registered"] and report["runtime_heap_allocations"] == 0
    assert report["storage_lifetime"] == "process-exit"
    assert report["native_publication"] == "existing-shot-table-TOC-slot"
    assert not report["registration_metadata_automatically_established"]
    assert not report["gameplay_ready"] and raw == before


@pytest.mark.parametrize(
    "kind",
    [
        "stale-target",
        "stale-image",
        "259-styles",
        "missing-metadata",
        "untyped-label",
        "bad-header",
        "missing-evidence",
    ],
)
def test_native_publication_rejects_unproven_metadata_and_id_truncation(kind):
    from choops_py.research.resident_segment import install_resident_shots

    raw, image, offsets, contract = publication_inputs()
    if kind == "stale-target":
        contract["target_elf_sha256"] = "stale"
    elif kind == "stale-image":
        contract["image_sha256"] = "stale"
    elif kind == "259-styles":
        contract["entries"] *= 147
    elif kind == "missing-metadata":
        contract["entries"][0]["playback_metadata_hex"] = "00"
    elif kind == "untyped-label":
        contract["entries"][0]["target_label_key"] &= ~1
    elif kind == "bad-header":
        contract["entries"][0]["header_indices"] = [0, 2]
    elif kind == "missing-evidence":
        contract["entries"][0]["evidence"] = {}
    before = bytes(raw)
    with pytest.raises(ValueError):
        install_resident_shots(raw, image, offsets, contract)
    assert raw == before

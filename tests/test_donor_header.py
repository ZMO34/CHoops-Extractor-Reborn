import hashlib
import struct

import pytest
from test_motion_sampling import source_files

from choops_py.formats.embedded_motion import NativeELF
from choops_py.formats.motion_events import curve_timing_contract
from choops_py.formats.motion_frames import resample_nba11_frames, resample_nba11_root
from choops_py.research.donor_header import translate_donor_motion
from choops_py.research.target_motion import relocate_target_image


def inputs(tmp_path):
    a, b, address, *_ = source_files(tmp_path)
    return a.read_bytes(), b.read_bytes(), address


def contract(donor, target, address):
    elf = NativeELF(donor)
    count = struct.unpack_from(">I", elf.read(address, 56), 16)[0] & 63
    header = elf.read(address, 56 + 4 * count)
    return dict(
        schema=1,
        source_sha256=hashlib.sha256(donor).hexdigest(),
        target_sha256=hashlib.sha256(target).hexdigest(),
        source_header_address=address,
        source_header_sha256=hashlib.sha256(header).hexdigest(),
        target_mode_high16=0x2164,
        target_state_bits=0x12345678,
        authored_planar=[5, 3, 4],
        evidence={
            k: "Synthetic authoring assertion; not real-game metadata proof"
            for k in ("mode", "state", "planar")
        },
    )


def translated(donor, target, address, metadata=None, **kwargs):
    return translate_donor_motion(
        donor,
        target,
        address,
        metadata or contract(donor, target, address),
        curve_timing_contract(),
        **kwargs,
    )


def test_translation_rebuilds_target_layout_tracks_and_timing_without_template(
    tmp_path,
):
    donor, target, address = inputs(tmp_path)
    before = donor, target
    image, r = translated(donor, target, address)
    assert r["target_frame_count"] == 6 and r["source_key_count"] == 3
    assert (
        not r["metadata_automatically_established"] and not r["native_loader_installed"]
    )
    assert struct.unpack_from(">4I", image) == (0, 0x1DF7DD, 0, 0x49244)
    assert struct.unpack_from(">II", image, 20) == (0x21640006, 0x12345678)
    assert struct.unpack_from(">3f", image, 36) == (5, 3, 4)
    elf = NativeELF(donor)
    h = elf.read(address, 56)
    assert image[28:36] == h[28:36]
    timing, poses, root, _, _ = struct.unpack_from(">5I", h, 36)
    deltas = elf.read(timing, 3)
    expected, _ = resample_nba11_frames(elf.read(poses, 432), deltas, 17, 6)
    roots = resample_nba11_root(elf.read(root, 24), deltas)
    for extent, wanted in zip(
        r["extents"], (expected, roots, struct.pack(">I", 0x80000000)), strict=True
    ):
        assert image[extent["offset"] : extent["offset"] + extent["bytes"]] == wanted
    native = relocate_target_image(image, [0], 0x30000000, source_state="relative")
    assert (
        relocate_target_image(native, [0], 0x30000000, source_state="native") == image
    )
    assert before == (donor, target)
    assert r["state_consumer_comparison"]["changed_predicates"] == [
        "mask_0x3f0_nonzero"
    ]
    assert not r["state_consumer_comparison"]["target_compatibility_established"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_header_sha256", "stale"),
        ("source_sha256", "stale"),
        ("target_sha256", "stale"),
        ("source_header_address", 0),
        ("target_mode_high16", 0x1164),
        ("target_state_bits", None),
        ("authored_planar", [float("nan"), 0, 0]),
        ("evidence", {}),
    ],
)
def test_explicit_metadata_contract_rejects_stale_unknown_and_incompatible_assertions(
    tmp_path, field, value
):
    donor, target, address = inputs(tmp_path)
    c = contract(donor, target, address)
    c[field] = value
    with pytest.raises(ValueError):
        translated(donor, target, address, c)


def test_missing_contract_and_budget_block_before_resampling(tmp_path, monkeypatch):
    donor, target, address = inputs(tmp_path)
    with pytest.raises(ValueError, match="contract"):
        translate_donor_motion(donor, target, address, None, curve_timing_contract())

    def forbid(*args, **kwargs):
        raise AssertionError("Must reject before expanded allocation")

    monkeypatch.setattr("choops_py.research.donor_header.resample_nba11_frames", forbid)
    with pytest.raises(ValueError, match="byte budget"):
        translated(donor, target, address, budget=64)


def test_opaque_events_auxiliary_extents_and_unpacked_layout_do_not_translate(tmp_path):
    original, target, address = inputs(tmp_path)
    elf = NativeELF(original)
    at = elf.target(address)["file_offset"]
    for delta, value, match in [
        (4, 0x10000, "auxiliary"),
        (52, 0x10000, "auxiliary"),
        (20, 0x21648003, "Unpacked"),
    ]:
        donor = bytearray(original)
        struct.pack_into(">I", donor, at + delta, value)
        with pytest.raises(ValueError, match=match):
            translated(donor, target, address)
    donor = bytearray(original)
    events = struct.unpack_from(">I", original, at + 48)[0]
    p = elf.target(events)["file_offset"]
    struct.pack_into(">ifI", donor, p, 17, 0.01, 0)
    struct.pack_into(">I", donor, p + 12, 0x80000000)
    with pytest.raises(ValueError, match="No explicit mapping"):
        translated(donor, target, address)


@pytest.mark.parametrize("which", ["donor", "target"])
def test_contract_fingerprint_covers_streams_and_target_revision_not_only_header(
    tmp_path, which
):
    donor, target, address = inputs(tmp_path)
    c = contract(donor, target, address)
    if which == "donor":
        changed = bytearray(donor)
        changed[-1] ^= 1
        donor = bytes(changed)
    else:
        changed = bytearray(target)
        changed[8] ^= 1
        target = bytes(changed)
    with pytest.raises(ValueError, match="fingerprint"):
        translated(donor, target, address, c)


def test_exact_aligned_component_budget_is_accepted(tmp_path):
    donor, target, address = inputs(tmp_path)
    data, _ = translated(donor, target, address)
    assert translated(donor, target, address, budget=len(data))[0] == data


def test_huge_integer_authoring_value_is_rejected_before_float_conversion(tmp_path):
    donor, target, address = inputs(tmp_path)
    c = contract(donor, target, address)
    c["authored_planar"] = [2**2048, 0, 0]
    with pytest.raises(ValueError, match="finite authored"):
        translated(donor, target, address, c)


def auxiliary_inputs(tmp_path, count=2, linked=True):
    donor, target, address = inputs(tmp_path)
    target = bytearray(target)
    struct.pack_into(">I", target, 68, 6)  # Synthetic writable residency segment.
    target = bytes(target)
    raw = bytearray(donor)
    elf = NativeELF(raw)
    at = elf.target(address)["file_offset"]
    size = struct.unpack_from(">Q", raw, 120 + 32)[0]
    curve_offset = (size + 15) & ~15
    new_size = curve_offset + count * 16
    raw.extend(bytes(at + new_size - len(raw)))
    struct.pack_into(">QQ", raw, 120 + 32, new_size, new_size + 64)
    flags = struct.unpack_from(">I", raw, at + 16)[0]
    struct.pack_into(">I", raw, at + 16, flags | count)
    assertions = []
    for channel in range(count):
        ids = (12, 23) if channel == 0 else (7, 3)
        curve = struct.pack(">II", ids[0] << 24 | 0xFFFFFF, ids[1] << 24 | 60)
        pos = at + curve_offset + channel * 16
        raw[pos : pos + 8] = curve
        struct.pack_into(
            ">I", raw, at + 56 + 4 * channel, address + curve_offset + channel * 16
        )
        assertions.append(
            dict(
                schema=1,
                source_channel=channel,
                source_curve_sha256=hashlib.sha256(curve).hexdigest(),
                target_elf_sha256=hashlib.sha256(target).hexdigest(),
                channel_evidence="Synthetic assertion; no real selector meaning",
                rules=[
                    dict(source=a, target=b, evidence="Synthetic test map")
                    for a, b in zip(ids, (8, 19) if channel == 0 else (6, 2))
                ],
            )
        )
    length = 56 + count * 4
    if linked:
        struct.pack_into(">I", raw, at + 4, address + 64)
        peer = bytearray(raw[at : at + length])
        struct.pack_into(">I", peer, 4, address)
        struct.pack_into(
            ">I", peer, 20, struct.unpack_from(">I", peer, 20)[0] ^ 0x40000000
        )
        raw[at + 64 : at + 64 + length] = peer
    donor = bytes(raw)
    metadata = contract(donor, target, address)
    if linked:
        metadata["detached_backlink"] = dict(
            peer_address=address + 64,
            peer_header_sha256=hashlib.sha256(peer).hexdigest(),
            evidence="Synthetic reciprocal mirror; independent track ownership",
        )
    return donor, target, address, metadata, assertions


@pytest.mark.parametrize("count,linked", [(0, True), (1, True), (2, True), (2, False)])
def test_native_counted_selectors_and_explicit_mirror_detachment_are_owned(
    tmp_path, count, linked
):
    from choops_py.research.resident_segment import append_resident_image

    donor, target, address, metadata, assertions = auxiliary_inputs(
        tmp_path, count, linked
    )
    original = donor, target
    image, report = translated(
        donor, target, address, metadata, auxiliary_contracts=assertions
    )
    assert report["source_header_bytes"] == 56 + count * 4
    assert len(report["auxiliary_translation"]) == count
    if linked:
        assert report["source_backlink_detachment"]["source_link_transported"] is False
    for channel in range(count):
        extent = next(
            x for x in report["extents"] if x["role"] == f"selector:{channel}"
        )
        words = struct.unpack_from(">II", image, extent["offset"])
        assert [w >> 24 for w in words] == ([8, 19] if channel == 0 else [6, 2])
        assert [w & 0xFFFFFF for w in words] == [0xFFFFFF, 60]
    output, residency = append_resident_image(target, image, [0])
    resident = NativeELF(output).read(residency["resident_base"], len(image))
    assert (
        relocate_target_image(
            resident, [0], residency["resident_base"], source_state="native"
        )
        == image
    )
    assert (donor, target) == original
    assert not report["gameplay_ready"]


def test_native_auxiliary_contracts_and_extended_header_fingerprint_are_mandatory(
    tmp_path,
):
    donor, target, address, metadata, assertions = auxiliary_inputs(tmp_path)
    with pytest.raises(ValueError, match="Every native auxiliary"):
        translated(donor, target, address, metadata)
    stale = dict(
        metadata,
        source_header_sha256=hashlib.sha256(
            NativeELF(donor).read(address, 56)
        ).hexdigest(),
    )
    with pytest.raises(ValueError, match="bound to this donor header"):
        translated(donor, target, address, stale, auxiliary_contracts=assertions)
    stale = dict(metadata)
    stale.pop("detached_backlink")
    with pytest.raises(ValueError, match="detachment evidence"):
        translated(donor, target, address, stale, auxiliary_contracts=assertions)


@pytest.mark.parametrize(
    "offset,value,message",
    [
        (4, 0, "not reciprocal"),
        (40, 0x20112, "share established dependencies"),
        (20, 0x61640004, "share established dependencies"),
        (20, 0x21640003, "share established dependencies"),
    ],
)
def test_fresh_assertions_cannot_authorize_nonmatching_mirror_links(
    tmp_path, offset, value, message
):
    donor, target, address, metadata, assertions = auxiliary_inputs(tmp_path)
    raw = bytearray(donor)
    at = NativeELF(raw).target(address + 64)["file_offset"]
    struct.pack_into(">I", raw, at + offset, value)
    metadata["source_sha256"] = hashlib.sha256(raw).hexdigest()
    metadata["detached_backlink"]["peer_header_sha256"] = hashlib.sha256(
        raw[at : at + 64]
    ).hexdigest()
    with pytest.raises(ValueError, match=message):
        translated(raw, target, address, metadata, auxiliary_contracts=assertions)


def test_native_selector_budget_rejects_before_resampling_and_accepts_exact(
    tmp_path, monkeypatch
):
    donor, target, address, metadata, assertions = auxiliary_inputs(tmp_path)
    image, _ = translated(
        donor, target, address, metadata, auxiliary_contracts=assertions
    )
    assert (
        translated(
            donor,
            target,
            address,
            metadata,
            auxiliary_contracts=assertions,
            budget=len(image),
        )[0]
        == image
    )

    def forbid(*args, **kwargs):
        raise AssertionError("Expanded tracks must not be allocated")

    monkeypatch.setattr("choops_py.research.donor_header.resample_nba11_frames", forbid)
    with pytest.raises(ValueError, match="selectors exceed byte budget"):
        translated(
            donor,
            target,
            address,
            metadata,
            auxiliary_contracts=assertions,
            budget=len(image) - 1,
        )


def test_self_link_cannot_be_authorized_with_fresh_input_hashes(tmp_path):
    donor, target, address, metadata, assertions = auxiliary_inputs(tmp_path)
    raw = bytearray(donor)
    at = NativeELF(raw).target(address)["file_offset"]
    struct.pack_into(">I", raw, at + 4, address)
    header = bytes(raw[at : at + 64])
    metadata["source_sha256"] = hashlib.sha256(raw).hexdigest()
    metadata["source_header_sha256"] = hashlib.sha256(header).hexdigest()
    metadata["detached_backlink"].update(
        peer_address=address, peer_header_sha256=hashlib.sha256(header).hexdigest()
    )
    with pytest.raises(ValueError, match="self-referential"):
        translated(raw, target, address, metadata, auxiliary_contracts=assertions)


def refresh_native_contract(raw, target, address, previous):
    metadata = contract(raw, target, address)
    peer = previous["detached_backlink"]["peer_address"]
    header = NativeELF(raw).read(peer, 64)
    metadata["detached_backlink"] = dict(
        previous["detached_backlink"],
        peer_header_sha256=hashlib.sha256(header).hexdigest(),
    )
    return metadata


def test_native_shared_selector_prefixes_are_owned_independently(tmp_path):
    donor, target, address, metadata, assertions = auxiliary_inputs(tmp_path)
    raw = bytearray(donor)
    elf = NativeELF(raw)
    a = elf.target(address)["file_offset"]
    pointer = struct.unpack_from(">I", raw, a + 56)[0]
    for header in (a, a + 64):
        struct.pack_into(">I", raw, header + 60, pointer)
    metadata = refresh_native_contract(raw, target, address, metadata)
    assertions[1] = dict(assertions[0], source_channel=1)
    image, report = translated(
        raw, target, address, metadata, auxiliary_contracts=assertions
    )
    curves = [x for x in report["extents"] if x["role"].startswith("selector:")]
    assert len(curves) == 2 and curves[0]["offset"] != curves[1]["offset"]
    assert (
        image[curves[0]["offset"] : curves[0]["offset"] + 8]
        == image[curves[1]["offset"] : curves[1]["offset"] + 8]
    )


def test_native_overlapping_payloads_reject_before_expansion(tmp_path, monkeypatch):
    donor, target, address, metadata, assertions = auxiliary_inputs(tmp_path)
    raw = bytearray(donor)
    at = NativeELF(raw).target(address)["file_offset"]
    poses = struct.unpack_from(">I", raw, at + 40)[0]
    for header in (at, at + 64):
        struct.pack_into(">I", raw, header + 44, poses)
    metadata = refresh_native_contract(raw, target, address, metadata)

    def forbid(*args, **kwargs):
        raise AssertionError("Malformed source must reject before expansion")

    monkeypatch.setattr("choops_py.research.donor_header.resample_nba11_frames", forbid)
    with pytest.raises(ValueError, match="dependencies overlap"):
        translated(raw, target, address, metadata, auxiliary_contracts=assertions)

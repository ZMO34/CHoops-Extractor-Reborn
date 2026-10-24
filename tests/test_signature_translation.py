import hashlib
import struct

import pytest
from test_donor_header import contract as elf_contract
from test_signature_motion import alias, bank, fixtures

from choops_py.formats.motion_events import curve_timing_contract, inspect_events
from choops_py.research.donor_header import translate_donor_motion
from choops_py.research.signature_motion import (
    SignatureMotionSource,
    translate_signature_motion,
)
from choops_py.research.target_motion import relocate_target_image


def metadata(source, donor, target):
    _, report = source.tracks(0, 0)
    return dict(
        schema=2,
        source_bank_index=0,
        source_record_index=0,
        source_bank_sha256=source.fingerprints[0],
        source_banks_sha256=list(source.fingerprints),
        source_header_sha256=report["source_header_sha256"],
        donor_elf_sha256=hashlib.sha256(donor).hexdigest(),
        target_elf_sha256=hashlib.sha256(target).hexdigest(),
        target_mode_high16=0x2164,
        target_state_bits=0x12345678,
        authored_planar=[5, 3, 4],
        evidence={
            k: "Synthetic metadata assertion, not real-game proof"
            for k in ("mode", "state", "planar")
        },
    )


def translate(source, donor, target, **kwargs):
    return translate_signature_motion(
        source,
        0,
        0,
        donor,
        target,
        metadata(source, donor, target),
        curve_timing_contract(),
        **kwargs,
    )


def test_serialized_signature_component_matches_equivalent_elf_source(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    source = SignatureMotionSource([("synthetic", bank(raw))])
    image, report = translate(source, donor, target)
    expected, expected_report = translate_donor_motion(
        donor,
        target,
        0x20000,
        elf_contract(donor, target, 0x20000),
        curve_timing_contract(),
    )
    assert image == expected
    assert report["rate_timing_comparison"] == expected_report["rate_timing_comparison"]
    assert (
        report["state_consumer_comparison"]
        == expected_report["state_consumer_comparison"]
    )
    assert (
        report["complete_known_layout"]
        and not report["metadata_automatically_established"]
    )
    assert not report["gameplay_ready"] and not report["native_loader_installed"]
    native = relocate_target_image(image, [0], 0x30000000, source_state="relative")
    assert (
        relocate_target_image(native, [0], 0x30000000, source_state="native") == image
    )
    assert translate(source, donor, target, budget=len(image))[0] == image


def event_source(raw, identity=22, payload=False):
    raw = bytearray(raw)
    at = (len(raw) + 3) & ~3
    raw.extend(bytes(at - len(raw)))
    struct.pack_into(">i", raw, 48, at - 48 + 1)
    raw.extend(struct.pack(">iII", identity, 0x3D000000, 9 if payload else 0))
    raw.extend(struct.pack(">I", 0x80000000))
    if payload:
        raw.extend(bytes(16))
    return SignatureMotionSource([("events", bank(raw))])


def test_signature_events_retain_exact_time_bits_and_opaque_payloads_stay_blocked(
    tmp_path,
):
    donor, target, raw = fixtures(tmp_path)
    image, report = translate(event_source(raw), donor, target)
    extent = report["extents"][-1]
    rows = inspect_events(image, "college-hoops-2k8", extent["offset"])["entries"]
    assert [(row["id"], row["time_bits"]) for row in rows] == [(21, 0x3D000000)]
    with pytest.raises(ValueError, match="Opaque"):
        translate(event_source(raw, 92, True), donor, target)
    with pytest.raises(ValueError, match="No explicit mapping"):
        translate(event_source(raw, 999), donor, target)


@pytest.mark.parametrize(
    "key,value",
    [
        ("source_bank_sha256", "stale"),
        ("source_header_sha256", "stale"),
        ("donor_elf_sha256", "stale"),
        ("target_elf_sha256", "stale"),
        ("source_bank_index", False),
        ("source_record_index", 1),
        ("target_mode_high16", 0x1164),
        ("target_state_bits", None),
        ("authored_planar", [float("nan"), 0, 0]),
        ("evidence", {}),
    ],
)
def test_signature_authoring_contract_rejects_stale_and_unestablished_fields(
    tmp_path, key, value
):
    donor, target, raw = fixtures(tmp_path)
    source = SignatureMotionSource([("source", bank(raw))])
    c = metadata(source, donor, target)
    c[key] = value
    with pytest.raises(ValueError):
        translate_signature_motion(
            source, 0, 0, donor, target, c, curve_timing_contract()
        )


def test_signature_budget_gate_runs_before_expansion_and_auxiliary_is_not_discarded(
    tmp_path, monkeypatch
):
    donor, target, raw = fixtures(tmp_path)
    source = SignatureMotionSource([("source", bank(raw))])

    def forbid(*args, **kwargs):
        raise AssertionError("Must not expand before budget/dependency checks")

    monkeypatch.setattr(
        "choops_py.research.signature_motion.resample_nba11_frames", forbid
    )
    with pytest.raises(ValueError, match="budget"):
        translate(source, donor, target, budget=64)
    raw = bytearray(raw)
    raw[19] |= 1
    struct.pack_into(">i", raw, 56, len(raw) - 56 + 1)
    raw.extend(struct.pack(">II", 0, 300))
    source = SignatureMotionSource([("auxiliary", bank(raw))])
    with pytest.raises(ValueError, match="explicit selector contracts"):
        translate(source, donor, target)


def test_serialized_component_loads_into_owned_native_segment(tmp_path):
    from choops_py.formats.embedded_motion import NativeELF
    from choops_py.research.resident_segment import append_resident_image

    donor, target, raw = fixtures(tmp_path)
    target = bytearray(target)
    at = (len(target) + 15) & ~15
    target.extend(bytes(at + 256 - len(target)))
    struct.pack_into(">HH", target, 54, 56, 2)
    struct.pack_into(">II6Q", target, 120, 1, 6, at, 0x20000, 0x20000, 256, 512, 16)
    target = bytes(target)
    source = SignatureMotionSource([("synthetic", bank(raw))])
    image, component = translate(source, donor, target)
    result, resident = append_resident_image(target, image, component["header_offsets"])
    native = NativeELF(result).read(resident["resident_base"], len(image))
    assert (
        relocate_target_image(
            native, [0], resident["resident_base"], source_state="native"
        )
        == image
    )
    assert NativeELF(result).read(0x20100, 256) == bytes(256)
    assert resident["inverse_preservation_verified"]
    assert not resident["registered"] and not resident["gameplay_ready"]


def test_metadata_contract_binds_related_alias_payload_bank(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    original_alias = bank(alias(raw), identity=2)
    source = SignatureMotionSource(
        [
            ("alias", original_alias),
            ("owner", bank(raw)),
        ]
    )
    c = metadata(source, donor, target)
    image, _ = translate_signature_motion(
        source,
        0,
        0,
        donor,
        target,
        c,
        curve_timing_contract(),
    )
    changed = bytearray(raw)
    # Change one packed pose word in the related bank, preserving all headers,
    # alias metadata, canonical binds and the origin bank fingerprint.
    pose = 40 + struct.unpack_from(">i", raw, 40)[0] - 1
    changed[pose + 1] ^= 1
    updated = SignatureMotionSource(
        [
            ("alias", original_alias),
            ("owner", bank(changed)),
        ]
    )
    assert source.fingerprints[0] == updated.fingerprints[0]
    assert (
        source.tracks(0, 0)[1]["source_header_sha256"]
        == updated.tracks(0, 0)[1]["source_header_sha256"]
    )
    assert image
    with pytest.raises(ValueError, match="identity/fingerprints changed"):
        translate_signature_motion(
            updated,
            0,
            0,
            donor,
            target,
            c,
            curve_timing_contract(),
        )


def test_signature_authoring_cannot_change_confirmed_duration_divisor(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    source = SignatureMotionSource([("synthetic", bank(raw))])
    c = metadata(source, donor, target)
    c["target_mode_high16"] = 0x2264
    with pytest.raises(ValueError, match="duration divisor"):
        translate_signature_motion(
            source, 0, 0, donor, target, c, curve_timing_contract()
        )

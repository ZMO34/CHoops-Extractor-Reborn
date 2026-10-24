import hashlib
import struct

import pytest
from test_signature_motion import SignatureMotionSource, bank, fixtures
from test_signature_translation import metadata
from test_target_motion import fixture

from choops_py.formats.binary import Binary
from choops_py.formats.embedded_motion import NativeELF
from choops_py.formats.motion_events import curve_timing_contract
from choops_py.research.motion_auxiliary import (
    read_selector_prefix,
    transcode_selector_curve,
)
from choops_py.research.resident_segment import append_resident_image
from choops_py.research.signature_motion import translate_signature_motion
from choops_py.research.target_motion import (
    inspect_target_motion,
    prepare_target_image,
    relocate_target_image,
)


def curve():
    return struct.pack(">3I", 3 << 24 | 0xFFFFFF, 7 << 24 | 15, 0x12345678)


def contract(raw, target):
    return dict(
        schema=1,
        source_channel=0,
        source_curve_sha256=hashlib.sha256(raw).hexdigest(),
        target_elf_sha256=hashlib.sha256(target).hexdigest(),
        channel_evidence="Synthetic channel assertion only",
        rules=[
            dict(source=a, target=b, evidence="Synthetic resource assertion")
            for a, b in ((3, 19), (7, 2))
        ],
    )


def test_prefix_excludes_adjacent_data_and_preserves_signed_ticks():
    raw = curve()
    prefix = read_selector_prefix(Binary(raw).slice, 0, duration=0.05)
    assert prefix == raw[:8]
    output, report = transcode_selector_curve(
        prefix,
        contract(prefix, b"target"),
        channel=0,
        target_elf_sha256=hashlib.sha256(b"target").hexdigest(),
        duration=0.05,
    )
    assert struct.unpack(">2I", output) == (19 << 24 | 0xFFFFFF, 2 << 24 | 15)
    assert report["signed_tick_bits_preserved"]
    assert not report["semantics_automatically_established"]


@pytest.mark.parametrize(
    "change", ["hash", "target", "channel", "missing", "duplicate", "bool", "evidence"]
)
def test_selector_assertions_never_invent_identity_or_accept_stale_maps(change):
    raw = curve()[:8]
    c = contract(raw, b"target")
    if change == "hash":
        c["source_curve_sha256"] = "stale"
    elif change == "target":
        c["target_elf_sha256"] = "stale"
    elif change == "channel":
        c["source_channel"] = 1
    elif change == "missing":
        c["rules"].pop()
    elif change == "duplicate":
        c["rules"].append(dict(c["rules"][0]))
    elif change == "bool":
        c["rules"][0]["target"] = True
    else:
        c["channel_evidence"] = ""
    with pytest.raises(ValueError):
        transcode_selector_curve(
            raw,
            c,
            channel=0,
            target_elf_sha256=hashlib.sha256(b"target").hexdigest(),
            duration=0.05,
        )


def test_native_endpoint_rounding_requires_an_additional_bracket():
    # Mathematical endpoint ceil is 1882, native FMULS then VMX multiply
    # reaches 1882.000122... and therefore needs the knot at tick 1883.
    raw = struct.pack(">3I", 0, 1882, 1883)
    duration, scale = 2.2576792240142822, 2.7786645889282227
    assert (
        read_selector_prefix(Binary(raw).slice, 0, duration=duration, time_scale=scale)
        == raw
    )
    with pytest.raises(ValueError):
        read_selector_prefix(
            Binary(raw[:8]).slice, 0, duration=duration, time_scale=scale
        )
    with pytest.raises(ValueError):
        read_selector_prefix(Binary(struct.pack(">2I", 4, 3)).slice, 0, duration=0.05)


def target_with_selector():
    raw = fixture()
    raw[0x113] |= 1
    struct.pack_into(">I", raw, 0x140, 0x10600)
    # duration * scale = .0375, requires tick 12.
    raw[0x700:0x708] = curve()[:8]
    return raw


def test_target_selector_ownership_relocation_and_static_loading():
    raw = target_with_selector()
    image, manifest = prepare_target_image(raw, [0x10000])
    assert manifest["role_counts"]["selector:0"] == 1
    result, resident = append_resident_image(raw, image, [0])
    elf = NativeELF(result)
    report = inspect_target_motion(elf, resident["resident_base"])
    assert report["resident_image_supported"]
    dep = next(d for d in report["dependencies"] if d["role"] == "selector:0")
    assert elf.read(dep["address"], dep["bytes"]) == curve()[:8]
    native = elf.read(resident["resident_base"], len(image))
    assert (
        relocate_target_image(
            native, [0], resident["resident_base"], source_state="native"
        )
        == image
    )
    assert resident["inverse_preservation_verified"]


def test_selector_truncation_overlap_and_unknown_extra_stay_blocked():
    for pointer in (0x107FC, 0x10000, 0):
        raw = target_with_selector()
        struct.pack_into(">I", raw, 0x140, pointer)
        with pytest.raises(ValueError):
            prepare_target_image(raw, [0x10000])
    raw = target_with_selector()
    struct.pack_into(">I", raw, 0x13C, 0x10640)
    with pytest.raises(ValueError, match="unknown dependency"):
        prepare_target_image(raw, [0x10000])


def test_serialized_auxiliary_component_preserves_assertions_and_full_budget(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    raw = bytearray(raw)
    raw[19] |= 1
    at = (len(raw) + 3) & ~3
    raw.extend(bytes(at - len(raw)))
    struct.pack_into(">i", raw, 56, at - 56 + 1)
    # Source declared duration .05 as float32 needs tick 16 conservatively.
    selector = struct.pack(">2I", 3 << 24, 7 << 24 | 300)
    raw.extend(selector)
    source = SignatureMotionSource([("source", bank(raw))])
    c = metadata(source, donor, target)
    ac = [contract(selector, target)]

    def build(**kwargs):
        return translate_signature_motion(
            source,
            0,
            0,
            donor,
            target,
            c,
            curve_timing_contract(),
            auxiliary_contracts=ac,
            **kwargs,
        )

    image, report = build()
    assert report["metadata_assertions"]["authored_planar_float32"] == [5, 3, 4]
    assert report["auxiliary_translation"][0]["rules"][0]["target"] == 19
    assert report["auxiliary_extents_established"] and not report["gameplay_ready"]
    assert struct.unpack_from(">I", image, 16)[0] & 63 == 1
    assert build(budget=len(image))[0] == image
    with pytest.raises(ValueError, match="budget"):
        build(budget=len(image) - 1)
    ac[0]["rules"][0]["target"] = 9
    assert report["auxiliary_translation"][0]["rules"][0]["target"] == 19

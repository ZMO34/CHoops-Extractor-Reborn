import json
import struct

import pytest
from test_signature_motion import alias, bank, fixtures

from choops_py.research.motion_library import inspect_library
from choops_py.research.signature_motion import SignatureMotionSource


def other_rig(raw):
    raw = bytearray(raw)
    flags = struct.unpack_from(">I", raw, 16)[0]
    struct.pack_into(">I", raw, 16, (flags & ~(63 << 18)) | (24 << 18))
    return bytes(raw)


def test_other_channel_family_can_be_inspected_but_not_converted(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    source = SignatureMotionSource([("other-rig", bank(other_rig(raw)))])
    tracks, report = source.inspect_tracks(0, 0)
    assert tracks["poses"] and report["channels"]["declared_bones"] == 24
    assert not report["target_bone_mapping_established"]
    with pytest.raises(ValueError, match="canonical 21-bone"):
        source.prepare_pose_root(0, 0, donor, target)


def test_library_covers_aliases_and_unmapped_rigs_without_hiding_ambiguity(tmp_path):
    _, _, raw = fixtures(tmp_path)
    banks = [
        ("alias", bank(alias(raw), 2)),
        ("a", bank(raw)),
        ("copy", bank(raw)),
        ("other-rig", bank(other_rig(raw), 3)),
    ]
    strict = inspect_library(banks)
    assert not strict["all_supplied_typed_records_inspected"]
    assert strict["counts"]["blocked_records"] == 1
    result = inspect_library(banks, coalesce_identical=True)
    assert result["all_supplied_typed_records_inspected"]
    assert result["counts"]["records"] == result["counts"]["inspected_records"] == 4
    assert result["counts"]["identical_duplicate_aliases"] == 1
    assert {x["bones"] for x in result["channel_families"]} == {21, 24}
    assert result["conversion_bind_gate_retained"]
    assert not result["executable_held_library_included"]
    assert not result["complete_target_port"]


def test_library_cli_guards_related_inputs_and_reports_other_rigs(
    tmp_path, monkeypatch
):
    from choops_py.cli import execute, parser

    _, _, raw = fixtures(tmp_path)
    primary, related = tmp_path / "other.iff", tmp_path / "human.iff"
    primary.write_bytes(bank(other_rig(raw)))
    related.write_bytes(bank(raw, 2))
    output = tmp_path / "library.json"
    monkeypatch.setattr("choops_py.archive.manifests.OUTPUT", tmp_path)
    args = [
        "inspect-animation-library",
        str(primary),
        str(output),
        "--related-bank",
        str(related),
    ]
    execute(parser().parse_args(args))
    assert json.loads(output.read_text())["counts"]["inspected_records"] == 2
    before = related.read_bytes()
    args[2] = str(related)
    with pytest.raises(ValueError):
        execute(parser().parse_args(args))
    assert related.read_bytes() == before


def test_large_valid_source_timeline_is_a_target_limit_not_an_inspection_failure(
    tmp_path,
):
    donor, target, raw = fixtures(tmp_path)
    out = bytearray(raw[:56])
    keys = 259
    mode = struct.unpack_from(">I", out, 20)[0]
    struct.pack_into(">I", out, 20, (mode & 0xFFFF0000) | keys)
    flags = struct.unpack_from(">I", out, 16)[0]
    scale = struct.unpack_from(">f", out, 28)[0]
    struct.pack_into(">f", out, 32, 66048 / ((flags >> 24) * scale))
    pose_at = 40 + struct.unpack_from(">i", raw, 40)[0] - 1
    for field, data in [
        (36, bytes([255]) * 258),
        (40, raw[pose_at : pose_at + 144] * keys),
        (44, bytes(8 * keys)),
        (48, bytes.fromhex("80000000")),
    ]:
        at = (len(out) + 15) & ~15
        out.extend(bytes(at - len(out)))
        out.extend(data)
        struct.pack_into(">i", out, field, at - field + 1)
    inputs = [("long", bank(out))]
    report = inspect_library(inputs)
    assert report["all_supplied_typed_records_inspected"]
    assert report["counts"]["fixed_frame_count_overflows"] == 1
    assert report["fixed_rate_pose_root_bytes_before_bind_mapping"] == 66049 * 152
    with pytest.raises(ValueError, match="bounded frames"):
        SignatureMotionSource(inputs).prepare_pose_root(0, 0, donor, target)


def test_declared_mask_outside_the_rig_is_rejected_without_conversion(tmp_path):
    _, _, raw = fixtures(tmp_path)
    out = bytearray(other_rig(raw))
    struct.pack_into(">I", out, 8, 0x80000000)
    report = inspect_library([("bad-mask", bank(out))])
    assert not report["all_supplied_typed_records_inspected"]
    assert report["counts"]["blocked_records"] == 1
    assert "bone family" in report["errors"][0]["reason"]

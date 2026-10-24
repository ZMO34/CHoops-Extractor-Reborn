import hashlib
import struct

import pytest
from support import iff_fixture
from test_motion_sampling import source_files

from choops_py.formats.embedded_motion import NativeELF
from choops_py.formats.motion_frames import resample_nba11_frames, resample_nba11_root
from choops_py.formats.standard_iff import StandardIFF
from choops_py.research.donor_registry import MOTION
from choops_py.research.signature_motion import SignatureMotionSource


def fixtures(tmp_path):
    donor, target, address, *_ = source_files(tmp_path)
    donor, target = donor.read_bytes(), target.read_bytes()
    elf = NativeELF(donor)
    header = elf.read(address, 56)
    result = bytearray(header)
    struct.pack_into(">I", result, 0, 1)
    for field, size in ((36, 3), (40, 432), (44, 24), (48, 4)):
        pointer = struct.unpack_from(">I", header, field)[0]
        offset = (len(result) + 15) & ~15
        result.extend(bytes(offset - len(result)))
        result.extend(elf.read(pointer, size))
        struct.pack_into(">i", result, field, offset - field + 1)
    return donor, target, bytes(result)


def bank(raw, identity=1, typ=MOTION, compressed=False):
    raw = bytearray(raw)
    struct.pack_into(">I", raw, 0, identity)
    result = bytearray(iff_fixture([bytes(raw)], [(typ, [0])], compressed=compressed))
    table = StandardIFF(result).record_table
    at = table + struct.unpack_from(">I", result, table)[0] - 1
    struct.pack_into(">I", result, at, identity)
    return bytes(result)


def alias(raw, identity=2, target=1):
    out = bytearray(raw[:56])
    struct.pack_into(">I", out, 0, identity)
    out[36:56] = bytes(20)
    struct.pack_into(">I", out, 40, target)
    return bytes(out)


@pytest.mark.parametrize("compressed", [False, True])
def test_serialized_tracks_prepare_exact_components_with_fingerprinted_provenance(
    tmp_path, compressed
):
    donor, target, raw = fixtures(tmp_path)
    banks = [("synthetic", bank(raw, compressed=compressed))]
    before = banks[0][1]
    source = SignatureMotionSource(banks)
    tracks, report = source.tracks(0, 0)
    components, prepared = source.prepare_pose_root(0, 0, donor, target)
    poses, _ = resample_nba11_frames(tracks["poses"], tracks["timing"], 17, 6)
    roots = resample_nba11_root(tracks["root"], tracks["timing"])
    assert components == dict(poses=poses, root=roots)
    assert report["alias_path"][0]["bank_sha256"] == hashlib.sha256(before).hexdigest()
    assert prepared["target_frame_count"] == 6
    assert not prepared["complete_motion"] and not prepared["gameplay_ready"]
    assert prepared["omitted_dependencies"] == [
        "header",
        "events",
        "auxiliary",
        "membership",
    ]
    assert banks[0][1] == before
    assert (
        source.prepare_pose_root(0, 0, donor, target, budget=len(poses) + len(roots))[0]
        == components
    )


def test_cross_bank_alias_keeps_state_and_mirror_instead_of_payload_metadata(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    a = bytearray(alias(raw))
    struct.pack_into(">I", a, 24, 0xABCDEF01)
    mode = struct.unpack_from(">I", a, 20)[0]
    struct.pack_into(">I", a, 20, mode ^ 0x40000000)
    banks = [("alias", bank(a, 2)), ("payload", bank(raw))]
    source = SignatureMotionSource(banks)
    header, payload, path = source.resolve(0, 0)
    assert header == bytes(a) and payload == raw and len(path) == 2
    parts, report = source.prepare_pose_root(0, 0, donor, target)
    assert report["header_hex"] == bytes(a).hex()
    assert parts == source.prepare_pose_root(1, 0, donor, target)[0]


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "duplicate",
        "cycle",
        "wrong-type",
        "counts",
        "packing",
        "timing",
        "identity",
    ],
)
def test_alias_resolution_rejects_missing_ambiguous_cycles_and_incompatible_metadata(
    tmp_path, case
):
    _, _, raw = fixtures(tmp_path)
    a = bytearray(alias(raw))
    extra = [("payload", bank(raw))]
    if case == "missing":
        extra = []
    elif case == "duplicate":
        extra *= 2
    elif case == "cycle":
        extra = [("cycle", bank(alias(raw, 1, 2)))]
    elif case == "wrong-type":
        extra = [("wrong", bank(raw, typ=0x39F61D57))]
    elif case == "counts":
        a[19] ^= 1
    elif case == "packing":
        a[20] ^= 0x80
    elif case == "timing":
        struct.pack_into(">f", a, 28, 2)
    if case == "identity":
        broken = bytearray(bank(raw))
        broken[-len(raw)] ^= 1
        source = SignatureMotionSource([("bad", bytes(broken))])
    else:
        source = SignatureMotionSource([("alias", bank(a, 2)), *extra])
    with pytest.raises(ValueError):
        source.tracks(0, 0)


def test_record_local_bounds_and_budget_fail_before_expansion(tmp_path, monkeypatch):
    donor, target, raw = fixtures(tmp_path)
    bad = bytearray(raw)
    struct.pack_into(">i", bad, 40, len(raw) - 40 + 1)
    source = SignatureMotionSource([("bad", bank(bad))])
    with pytest.raises(ValueError, match="bounds"):
        source.tracks(0, 0)
    bad = bytearray(raw)
    struct.pack_into(">i", bad, 40, 1)
    with pytest.raises(ValueError, match="overlaps"):
        SignatureMotionSource([("bad", bank(bad))]).tracks(0, 0)

    def forbid(*args, **kwargs):
        raise AssertionError("Expansion must not run")

    monkeypatch.setattr(
        "choops_py.research.signature_motion.resample_nba11_frames", forbid
    )
    source = SignatureMotionSource([("good", bank(raw))])
    with pytest.raises(ValueError, match="budget"):
        source.prepare_pose_root(0, 0, donor, target, budget=64)
    with pytest.raises(ValueError, match="index"):
        source.tracks(True, 0)
    with pytest.raises(ValueError, match="1..32"):
        SignatureMotionSource([])


def test_auxiliary_selectors_remain_unresolved_and_bind_changes_block_components(
    tmp_path,
):
    donor, target, raw = fixtures(tmp_path)
    out = bytearray(raw)
    # First timing track starts at 64, leaving space for one counted pointer.
    out[19] |= 1
    struct.pack_into(">i", out, 56, len(out) - 56 + 1)
    out.extend(bytes.fromhex("010000000200FFFF"))
    source = SignatureMotionSource([("curve", bank(out))])
    _, report = source.tracks(0, 0)
    assert report["auxiliary_pointers"] == [len(raw)]
    assert report["auxiliary_extents_established"]
    assert not report["auxiliary_semantics_established"]
    assert report["auxiliary_tracks"][0]["selectors"] == [1, 2]
    assert "auxiliary-selector-semantics" in report["conversion_blockers"]
    with pytest.raises(ValueError):
        source.prepare_pose_root(0, 0, donor, bytes(64))


def test_timing_ends_after_consumed_intervals_without_reading_adjacent_byte(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    source = SignatureMotionSource([("original", bank(raw))])
    expected = source.prepare_pose_root(0, 0, donor, target)[0]
    out = bytearray(raw)
    at = len(out)
    struct.pack_into(">i", out, 36, at - 36 + 1)
    out.extend(bytes((1, 2)))  # three keys need exactly two interval bytes
    short = SignatureMotionSource([("short", bank(out))])
    assert short.prepare_pose_root(0, 0, donor, target)[0] == expected
    assert short.tracks(0, 0)[1]["timing_unused_final_slot_normalized"]
    with pytest.raises(ValueError, match="bounds"):
        SignatureMotionSource([("truncated", bank(out[:-1]))]).tracks(0, 0)


def test_cli_reports_alias_and_guards_every_related_source(tmp_path, monkeypatch):
    import json

    from choops_py.cli import execute, parser

    _, _, raw = fixtures(tmp_path)
    first, second = tmp_path / "alias.iff", tmp_path / "payload.iff"
    first.write_bytes(bank(alias(raw), 2))
    second.write_bytes(bank(raw))
    monkeypatch.setattr("choops_py.archive.manifests.OUTPUT", tmp_path)
    output = tmp_path / "report.json"
    arguments = [
        "inspect-signature-motion",
        str(first),
        "0",
        str(output),
        "--related-bank",
        str(second),
    ]
    report = execute(parser().parse_args(arguments))
    assert (
        len(report["alias_path"]) == 2
        and json.loads(output.read_text())["complete_motion"] is False
    )
    before = second.read_bytes()
    arguments[3] = str(second)
    with pytest.raises(ValueError):
        execute(parser().parse_args(arguments))
    assert second.read_bytes() == before


@pytest.mark.parametrize(
    "kind", ["overlap", "decoded-size", "unterminated-events", "unknown-mode"]
)
def test_malformed_source_dependencies_are_rejected(tmp_path, kind):
    _, _, raw = fixtures(tmp_path)
    bad = bytearray(raw)
    if kind == "overlap":
        pose_at = 40 + struct.unpack_from(">i", bad, 40)[0] - 1
        struct.pack_into(">i", bad, 44, pose_at - 44 + 1)
    elif kind == "unterminated-events":
        event_at = 48 + struct.unpack_from(">i", bad, 48)[0] - 1
        struct.pack_into(">I", bad, event_at, 1)
    elif kind == "unknown-mode":
        bad[22] |= 0x80
    data = bytearray(bank(bad))
    if kind == "decoded-size":
        struct.pack_into(">I", data, 44, 128 * 1024 * 1024 + 1)
    with pytest.raises(ValueError):
        SignatureMotionSource([("bad", bytes(data))]).tracks(0, 0)


def test_opt_in_alias_coalescing_requires_every_decoded_byte_equal(tmp_path):
    donor, target, raw = fixtures(tmp_path)
    inputs = [
        ("alias", bank(alias(raw), 2)),
        ("copy-a", bank(raw)),
        ("copy-b", bank(raw)),
    ]
    with pytest.raises(ValueError, match="missing or ambiguous"):
        SignatureMotionSource(inputs).tracks(0, 0)
    source = SignatureMotionSource(inputs, coalesce_identical=True)
    _, report = source.tracks(0, 0)
    proof = report["alias_path"][0]["equivalent_alias_targets"]
    assert [(x["bank"], x["record"]) for x in proof] == [(1, 0), (2, 0)]
    assert proof[0]["record_sha256"] == proof[1]["record_sha256"]
    assert proof[0]["bank_sha256"] == source.fingerprints[1]
    # Unknown trailing data is part of the equivalence proof too.
    changed = inputs[:2] + [("different-tail", bank(raw + b"KEEP"))]
    with pytest.raises(ValueError, match="not identical"):
        SignatureMotionSource(changed, coalesce_identical=True).tracks(0, 0)
    assert source.prepare_pose_root(0, 0, donor, target)[0]["poses"]

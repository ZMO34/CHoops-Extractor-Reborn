import struct

import pytest
from test_jump_pair import pair_inputs

from choops_py.research.shot_planar import _planar, inspect_pair_planar


def header(profile="college-hoops-2k8", *, mirror=False):
    out = bytearray(64 if profile == "college-hoops-2k8" else 56)
    struct.pack_into(">I", out, 4 if profile == "college-hoops-2k8" else 8, 0x1DF7DD)
    struct.pack_into(">I", out, 12, 0x49244)
    flags = (2 << 24) | (21 << 18) | (17 << 12) | (6 << 6)
    struct.pack_into(">II", out, 16, flags, 3 | (0x40000000 if mirror else 0))
    struct.pack_into(">ff", out, 28, 1, 0.75)
    return out


def roots():
    return b"".join(struct.pack(">4h", x, 0, 2 * x, 0) for x in (0, 8, 16))


@pytest.mark.parametrize("mirror", [False, True])
def test_crop_at_playback_duration_instead_of_using_last_padded_key(mirror):
    report = _planar(header(mirror=mirror), roots(), "college-hoops-2k8")
    # End tick 1.5 represents X=1.5, Z=3 in native units over 0.75 seconds.
    assert report["end_tick"] == 1.5
    assert report["proposal_float32"][1:] == [-2.0 if mirror else 2.0, 4.0]
    assert not report["automatic_metadata_contract"] and not report["target_compatibility_established"]
    assert report["estimated_not_authored"] and not report["native_vmx_bit_exact"]


def test_nonuniform_source_key_timing_and_root_extent_are_used():
    h = header("nba-2k11")
    struct.pack_into(">f", h, 32, 2)
    r = b"".join(struct.pack(">4h", x, 0, 0, 0) for x in (0, 8, 32))
    report = _planar(h, r, "nba-2k11", timing=bytes([0, 2, 0]))
    assert report["end_tick"] == 4
    assert report["proposal_float32"] == [2, 2, 0]
    with pytest.raises(ValueError, match="exact key timing"):
        _planar(h, r, "nba-2k11", timing=bytes([0, 2]))


@pytest.mark.parametrize("change", ["cyclic", "duration", "coverage", "extent", "unpacked"])
def test_unestablished_or_malformed_planar_inputs_reject(change):
    h = header("nba-2k11")
    r = roots()
    if change == "cyclic":
        struct.pack_into(">I", h, 20, 0x10000003)
    elif change == "duration":
        struct.pack_into(">f", h, 32, 0)
    elif change == "coverage":
        struct.pack_into(">f", h, 32, 3)
    elif change == "extent":
        r = r[:-2]
    else:
        struct.pack_into(">I", h, 20, 0x8003)
    with pytest.raises(ValueError):
        _planar(h, r, "nba-2k11", timing=bytes([0, 0, 0]))


def test_pair_scope_retains_both_lanes_and_provenance_without_counting_compatibility(tmp_path):
    source, *_ = pair_inputs(tmp_path)
    before = [bank.raw for bank in source.banks]
    report = inspect_pair_planar(source, 0, 0, 0)
    assert [lane["slot"] for lane in report["lanes"]] == [0, 1]
    assert report["source_banks_sha256"] == source.fingerprints
    assert report["intended_port_scope"] == "on-court-5v5"
    assert report["compatible_conversion_count"] is None and not report["gameplay_ready"]
    assert before == [bank.raw for bank in source.banks]
    with pytest.raises(ValueError, match="required registry category"):
        inspect_pair_planar(pair_inputs(tmp_path, category=0)[0], 0, 0, 0)


def test_bulk_pair_entry_reads_share_decoded_block_without_caching_mutable_rows(tmp_path, monkeypatch):
    from choops_py.research import signature_motion
    from choops_py.research.shot_family import _entry

    source, *_ = pair_inputs(tmp_path)
    decode = signature_motion.decode
    calls = []

    def counted(raw, size):
        calls.append(size)
        return decode(raw, size)

    monkeypatch.setattr(signature_motion, "decode", counted)
    original = _entry(source, 0, 0, 0, category=14)
    original["references"][0]["resource_id"] = 123456
    for _ in range(5):
        fresh = _entry(source, 0, 0, 0, category=14)
        assert fresh["references"][0]["resource_id"] == 1
    assert len(calls) == 1


def test_finite_source_fields_cannot_overflow_target_float32_proposal():
    h = header()
    struct.pack_into(">ff", h, 28, 3e38, 3e-39)
    with pytest.raises(ValueError, match="float32"):
        _planar(h, roots(), "college-hoops-2k8")

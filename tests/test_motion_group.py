import struct

import pytest
from test_signature_motion import alias, bank, fixtures

from choops_py.research.donor_registry import GROUP
from choops_py.research.motion_group import MotionGroupSource, inspect_group
from choops_py.research.signature_motion import SignatureMotionSource


def group(motions, identity=1):
    raw = bytearray(12 + len(motions) * 16)
    struct.pack_into(">III", raw, 0, identity, 0, len(motions))
    for member, motion in enumerate(motions):
        offset = (len(raw) + 3) & ~3
        raw.extend(bytes(offset - len(raw)))
        raw.extend(motion)
        field = 12 + member * 16
        struct.pack_into(">iIII", raw, field, offset - field + 1, 0x80000000 | member, member + 1, member + 2)
    return raw


def grouped_source(raw, **kwargs):
    return MotionGroupSource(SignatureMotionSource([("group", bank(raw, typ=GROUP))], **kwargs))


def test_group_members_have_bounded_tracks_and_keep_placement_words(tmp_path):
    _, _, motion = fixtures(tmp_path)
    raw = group([motion, motion])
    before = bytes(raw)
    source = grouped_source(raw)
    for member in (0, 1):
        tracks, report = source.inspect_member(0, 0, member)
        assert tracks["poses"] and report["source_key_count"] == 3
        assert report["source_kind"] == "nba11-group-member"
        assert report["placement_words"] == [0x80000000 | member, member + 1, member + 2]
        assert not report["placement_semantics_established"]
        assert not report["native_group_installed"] and not report["complete_motion"]
    assert bytes(raw) == before


def test_group_alias_uses_first_member_id_for_every_member_and_retains_metadata(tmp_path):
    _, _, motion = fixtures(tmp_path)
    owned = group([motion, motion])
    mirrored = bytearray(alias(motion, 2, 1))
    struct.pack_into(">I", mirrored, 24, 0x12345678)
    mode = struct.unpack_from(">I", mirrored, 20)[0]
    struct.pack_into(">I", mirrored, 20, mode ^ 0x40000000)
    borrowed = group([mirrored, alias(motion, 2, 0)], 2)
    banks = [("borrowed", bank(borrowed, 2, typ=GROUP)), ("owner", bank(owned, typ=GROUP))]
    source = MotionGroupSource(SignatureMotionSource(banks))
    for member in (0, 1):
        tracks, report = source.inspect_member(0, 0, member)
        assert tracks == source.inspect_member(1, 0, member)[0]
        assert len(report["alias_path"]) == 2
        assert report["group_record_sha256"] != report["payload_group_record_sha256"]
    assert bytes.fromhex(source.inspect_member(0, 0, 0)[1]["header_hex"])[24:28] == bytes.fromhex("12345678")


@pytest.mark.parametrize("case", ["missing", "ambiguous", "cycle", "counts", "metadata", "mixed"])
def test_group_alias_dependencies_reject_incompatible_or_unproven_graphs(tmp_path, case):
    _, _, motion = fixtures(tmp_path)
    owned = group([motion, motion])
    borrowed = group([alias(motion, 2, 1), alias(motion, 2, 0)], 2)
    extras = [("owner", bank(owned, typ=GROUP))]
    if case == "missing":
        # A SingleMoCap with the same ID is not a group owner.
        extras = [("wrong-type", bank(motion))]
    elif case == "ambiguous":
        extras *= 2
    elif case == "cycle":
        extras = [("cycle", bank(group([alias(motion, 1, 2), alias(motion, 1, 0)]), typ=GROUP))]
    elif case == "counts":
        extras = [("short", bank(group([motion]), typ=GROUP))]
    elif case == "metadata":
        offset = inspect_group(borrowed)["members"][1]["header_offset"]
        borrowed[offset + 19] ^= 1
    elif case == "mixed":
        borrowed = group([alias(motion, 2, 1), motion], 2)
    source = MotionGroupSource(SignatureMotionSource([("borrowed", bank(borrowed, 2, typ=GROUP)), *extras]))
    with pytest.raises(ValueError):
        source.inspect_member(0, 0, 1)


@pytest.mark.parametrize("case", ["count", "null", "table", "alignment", "overlap", "outside"])
def test_group_header_extent_failures_reject(tmp_path, case):
    _, _, motion = fixtures(tmp_path)
    raw = group([motion, motion])
    if case == "count":
        struct.pack_into(">I", raw, 8, 4097)
    else:
        first = inspect_group(raw)["members"][0]["header_offset"]
        value = {"null": 0, "table": 1, "alignment": first - 12 + 2,
                 "overlap": first + 4 - 28 + 1, "outside": len(raw) + 1}[case]
        struct.pack_into(">i", raw, 28 if case == "overlap" else 12, value)
    with pytest.raises(ValueError):
        inspect_group(raw)


def test_group_dependencies_cannot_overwrite_sibling_headers_or_escape_record(tmp_path):
    _, _, motion = fixtures(tmp_path)
    raw = group([motion, motion])
    info = inspect_group(raw)
    first, second = (m["header_offset"] for m in info["members"])
    struct.pack_into(">i", raw, first + 40, second - (first + 40) + 1)
    with pytest.raises(ValueError, match="overlaps|overlap"):
        grouped_source(raw).inspect_member(0, 0, 0)
    source = grouped_source(group([motion]))
    for value in (-1, 1, True):
        with pytest.raises(ValueError, match="existing"):
            source.inspect_member(0, 0, value)


def test_library_covers_group_only_banks_and_does_not_hide_failed_members(tmp_path):
    from choops_py.research.motion_library import inspect_library

    _, _, motion = fixtures(tmp_path)
    raw = group([motion, motion])
    report = inspect_library([("paired", bank(raw, typ=GROUP))])
    assert report["total_source_motion_headers"] == 2
    assert report["counts"]["group_records"] == 1
    assert report["counts"]["inspected_group_members"] == 2
    assert report["all_supplied_typed_records_inspected"]
    assert report["grouped_members_included"] and not report["complete_target_port"]
    second = inspect_group(raw)["members"][1]["header_offset"]
    struct.pack_into(">i", raw, second + 40, len(raw) - (second + 40) + 1)
    failed = inspect_library([("broken", bank(raw, typ=GROUP))])
    assert failed["counts"]["inspected_group_members"] == 1
    assert failed["counts"]["blocked_group_members"] == 1
    assert not failed["all_supplied_typed_records_inspected"]
    assert failed["errors"][0]["member"] == 1


def test_library_bounds_total_headers_before_reading_any_group_tracks(tmp_path, monkeypatch):
    from choops_py.research.motion_library import inspect_library

    _, _, motion = fixtures(tmp_path)
    monkeypatch.setattr("choops_py.research.motion_library.MAX_RECORDS", 1)
    monkeypatch.setattr(MotionGroupSource, "inspect_member", lambda *a: pytest.fail("track read before header bound"))
    with pytest.raises(ValueError, match="total motion headers"):
        inspect_library([("paired", bank(group([motion, motion]), typ=GROUP))])

import struct
import zlib

import pytest

from choops_py.research.scorebug_mrks import inspect_styles


def fixture(names=("home_city", "away_city")):
    scene = 32 + 176 * len(names)
    data = bytearray(scene + 0x54)
    struct.pack_into(">3I", data, 0, scene + 1, len(names), 25)
    for i, name in enumerate(names):
        at = 32 + 176 * i
        struct.pack_into(">16f", data, at, *([1.0, 0.0, 0.0, 0.0] * 4))
        struct.pack_into(">5f", data, at + 0x60, 200.0, 1.0, 0.5, 0.75, 1.0)
        struct.pack_into(
            ">4I",
            data,
            at + 0xA0,
            zlib.crc32(name.upper().encode()),
            zlib.crc32(name.encode()),
            0,
            0xDEADBEEF,
        )
    return data


def test_native_hash_identity_and_opaque_retention():
    data = fixture()
    before = bytes(data)
    report = inspect_styles(data)
    assert [s["binding"] for s in report["styles"]] == ["home_city", "away_city"]
    assert all(s["case_hash_matches"] for s in report["styles"])
    assert report["styles"][0]["unknown_ac"] == 0xDEADBEEF
    assert bytes(data) == before


def test_unknown_and_mismatched_case_hashes_are_evidence_not_invented_names():
    data = fixture(("unknown_field", "home_city"))
    struct.pack_into(">I", data, 32 + 176 + 0xA4, 1)
    report = inspect_styles(data)
    assert report["styles"][0]["binding"] is None
    assert report["styles"][0]["case_hash_matches"] is None
    assert report["styles"][1]["case_hash_matches"] is False


@pytest.mark.parametrize("offset,value", [(4, 4097), (8, 1), (0, 17), (0, 0xFFFFFFF1)])
def test_bad_extents(offset, value):
    data = fixture()
    struct.pack_into(">I", data, offset, value)
    with pytest.raises(ValueError):
        inspect_styles(data)


def test_duplicate_native_lookup_reports_first_match_without_losing_styles():
    report = inspect_styles(fixture(("home_city", "home_city")))
    assert len(report["styles"]) == 2
    assert len(report["duplicate_lookup_hashes"]) == 1
    assert [s["first_lookup_index"] for s in report["styles"]] == [0, 0]


def test_nonfinite_geometry_rejected():
    data = fixture()
    struct.pack_into(">f", data, 32 + 0x40, float("nan"))
    with pytest.raises(ValueError, match="Non-finite"):
        inspect_styles(data)


def test_truncated_scene_rejected():
    with pytest.raises(ValueError):
        inspect_styles(fixture()[:-1])

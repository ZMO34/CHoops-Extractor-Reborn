import struct

import pytest
from support import iff_fixture
from test_donor_registry import collection
from test_shot_family import family

from choops_py.formats.motion_events import curve_timing_contract
from choops_py.research.donor_registry import COLLECTION
from choops_py.research.jump_pair import prepare_jump_pair
from choops_py.research.signature_motion import SignatureMotionSource


def pair_inputs(tmp_path, extra=False, category=14, kind=0):
    _, donor, target, contracts, inputs = family(tmp_path)
    raw = collection(category)
    if category == 14:
        raw.extend(bytes(32 + (4 if extra else 0)))
        for i in range(2):
            struct.pack_into(">3I", raw, 28 + 12 * i, i + 1, kind, 0)
        struct.pack_into(
            ">9I", raw, 52, 20, 0xFFFFFFFF, 0xBF800000, 0x3F8CCCCD, 0, 2, 0, 0, 0
        )
    inputs = [
        ("collection", iff_fixture([bytes(raw)], [(COLLECTION, [0])])),
        *inputs[1:],
    ]
    source = SignatureMotionSource(inputs)
    for value in contracts.values():
        value["metadata"]["source_banks_sha256"] = list(source.fingerprints)
    return source, donor, target, contracts


def prepare(args, **kwargs):
    source, donor, target, contracts = args
    return prepare_jump_pair(
        source, 0, 0, 0, donor, target, contracts, curve_timing_contract(), **kwargs
    )


def test_primary_pair_keeps_both_headers_and_every_unmapped_row_word(tmp_path):
    args = pair_inputs(tmp_path)
    image, report = prepare(args)
    assert report["registry_category"] == 14 and report["provider_selector"] == 20
    assert report["header_indices_when_one"] == [0]
    assert report["header_indices_when_zero"] == [1]
    assert report["source_payload_tail_words"] == [
        20,
        0xFFFFFFFF,
        0xBF800000,
        0x3F8CCCCD,
        0,
        2,
        0,
        0,
        0,
    ]
    assert len(report["header_offsets"]) == 2
    assert not report["target_registration_metadata_established"]
    assert not report["gameplay_ready"]
    assert prepare(args, budget=len(image))[0] == image
    with pytest.raises(ValueError):
        prepare(args, budget=len(image) - 1)


@pytest.mark.parametrize("change", [{"extra": True}, {"category": 0}, {"kind": 1}])
def test_other_families_unknown_metadata_and_groups_reject_before_expansion(
    tmp_path, monkeypatch, change
):
    args = pair_inputs(tmp_path, **change)

    def forbid(*args, **kwargs):
        raise AssertionError("Must reject before expanding any motion")

    monkeypatch.setattr(
        "choops_py.research.shot_family.translate_signature_motion", forbid
    )
    with pytest.raises(ValueError):
        prepare(args)

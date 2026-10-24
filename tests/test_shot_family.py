import struct

import pytest
from support import iff_fixture
from test_donor_registry import collection
from test_signature_motion import alias, bank, fixtures
from test_signature_translation import metadata

from choops_py.formats.motion_events import curve_timing_contract
from choops_py.research.donor_registry import COLLECTION, inspect_entries
from choops_py.research.shot_family import prepare_shot_family, select_shot_pairs
from choops_py.research.signature_motion import SignatureMotionSource
from choops_py.research.target_motion import relocate_target_image


def family(tmp_path, *, empty=False, kind=0, tail=False, missing=False):
    donor, target, raw = fixtures(tmp_path)
    col = collection()
    for slot in range(8):
        identity = 0 if empty and slot < 2 else 1 + slot % 2
        if missing and slot == 7:
            identity = 99
        struct.pack_into(">3I", col, 28 + slot * 12, identity, kind, 0)
    struct.pack_into(">I", col, len(col) - 4, 0)
    if tail:
        col.extend(b"KEEP")
    # Build contracts with the helper's origin at bank zero, then bind the
    # collection-containing full bank set and actual header locations.
    inputs = [
        ("collection", iff_fixture([bytes(col)], [(COLLECTION, [0])])),
        ("payload", bank(raw)),
        ("alias", bank(alias(raw), 2)),
    ]
    source = SignatureMotionSource(inputs)
    c = metadata(SignatureMotionSource([inputs[1]]), donor, target)
    contracts = {}
    for i in (1, 2):
        _, report = source.tracks(i, 0)
        contracts[f"{i}:0"] = {
            "metadata": dict(
                c,
                source_bank_index=i,
                source_bank_sha256=source.fingerprints[i],
                source_banks_sha256=list(source.fingerprints),
                source_header_sha256=report["source_header_sha256"],
            )
        }
    return source, donor, target, contracts, inputs


def prepare(args, **kwargs):
    source, donor, target, contracts, _ = args
    return prepare_shot_family(
        source, 0, 0, 0, donor, target, contracts, curve_timing_contract(), **kwargs
    )


def test_all_four_pairs_survive_with_distinct_alias_headers_and_exact_budget(tmp_path):
    args = family(tmp_path)
    before = [bytes(data) for _, data in args[-1]]
    image, report = prepare(args)
    assert report["pairs"] == [[0, 1]] * 4
    assert len(report["header_offsets"]) == 2
    assert len(report["source_slots"]) == 8
    assert report["selected_slots_when_zero"] == [1, 3, 5, 7]
    assert report["selected_slots_when_one"] == [0, 2, 4, 6]
    assert not report["gameplay_ready"]
    native = relocate_target_image(
        image, report["header_offsets"], 0x30000000, source_state="relative"
    )
    assert (
        relocate_target_image(
            native, report["header_offsets"], 0x30000000, source_state="native"
        )
        == image
    )
    assert prepare(args, budget=len(image))[0] == image
    with pytest.raises(ValueError):
        prepare(args, budget=len(image) - 1)
    assert [data for _, data in args[-1]] == before


def test_empty_optional_pair_is_retained_without_inventing_fallback(tmp_path):
    _, report = prepare(family(tmp_path, empty=True))
    assert report["pairs"] == [[None, None], [0, 1], [0, 1], [0, 1]]
    assert not report["native_family_selection_installed"]


@pytest.mark.parametrize(
    "change,message",
    [
        ({"kind": 1}, "group-member"),
        ({"tail": True}, "tail bytes"),
        ({"missing": True}, "missing or ambiguous"),
    ],
)
def test_unresolved_dependencies_reject_whole_family_before_conversion(
    tmp_path, monkeypatch, change, message
):
    args = family(tmp_path, **change)

    def forbid(*args, **kwargs):
        raise AssertionError("Must reject before motion expansion")

    monkeypatch.setattr(
        "choops_py.research.shot_family.translate_signature_motion", forbid
    )
    with pytest.raises(ValueError, match=message):
        prepare(args)


@pytest.mark.parametrize("selector", [True, -1, 2, None])
def test_pair_selection_rejects_invalid_player_bit(selector):
    with pytest.raises(ValueError, match="selector bit"):
        select_shot_pairs(inspect_entries(collection())[0], selector)


def test_missing_contract_and_stale_related_bank_are_rejected(tmp_path):
    args = family(tmp_path)
    args[3].pop("2:0")
    with pytest.raises(ValueError, match="exactly every"):
        prepare(args)
    args = family(tmp_path)
    args[3]["1:0"]["metadata"]["source_banks_sha256"][2] = "stale"
    with pytest.raises(ValueError):
        prepare(args)


def test_missing_consumed_control_word_is_rejected():
    with pytest.raises(ValueError, match="control word"):
        inspect_entries(collection()[:-4])

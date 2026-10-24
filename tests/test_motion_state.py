import pytest

from choops_py.research.motion_state import compare_motion_states, state_predicates


def test_aggregate_predicate_does_not_invent_per_bit_correspondence():
    report = compare_motion_states(0x01000200, 0x01000100)
    assert report["observed_predicates_preserved"]
    assert not report["individual_bits_4_to_9_mapped"]
    assert not report["complete_state_mapping_established"]
    assert not report["target_compatibility_established"]
    assert report["source_word"] != report["target_word"]


def test_known_shared_endpoint_counterexample_is_not_silently_normalized():
    report = compare_motion_states(0x410, 0x400)
    assert report["changed_predicates"] == ["mask_0x3f0_nonzero"]
    assert report["source_word"] == 0x410 and report["target_word"] == 0x400
    assert not report["observed_predicates_preserved"]


def test_header_state_bit30_is_separate_from_mode_mirroring():
    report = compare_motion_states(0, 0x40000000)
    assert report["header_field"] == 0x18
    assert report["changed_predicates"] == ["skips_context_pair_clear"]
    assert state_predicates(0x80000000) == state_predicates(0)
    assert state_predicates(0xFFFFFFFF)["skips_context_pair_clear"]


@pytest.mark.parametrize("word", [-1, 2**32, True, 1.0, None])
def test_only_unsigned_words_are_accepted(word):
    with pytest.raises(ValueError, match="unsigned32"):
        compare_motion_states(word, 0)
    with pytest.raises(ValueError, match="unsigned32"):
        compare_motion_states(0, word)

import struct

import pytest

from choops_py.research.motion_auxiliary import inspect_selector_curve


def test_signed_ticks_selector_ids_and_exact_bits_are_kept_without_portability_claims():
    raw = struct.pack(">4I", 0x10FFFFFF, 0x18000000, 0x19000000, 0x10000258)
    before = raw
    r = inspect_selector_curve(raw, duration=1, time_scale=2)
    assert [(x["tick"], x["selector"]) for x in r["knots"]] == [
        (-1, 16),
        (0, 24),
        (0, 25),
        (600, 16),
    ]
    assert r["declared_last_query_tick"] == 600 and r["equal_tick_pairs"] == 1
    assert (
        not r["selector_semantics_established"]
        and not r["cross_game_translation_allowed"]
    )
    assert raw == before


@pytest.mark.parametrize(
    "raw,duration,scale",
    [
        (bytes(4), 1, 1),
        (bytes(9), 1, 1),
        (struct.pack(">2I", 1, 0), 0, 1),
        (bytes(8), 1, 1),
        (bytes(8), float("nan"), 1),
        (bytes(8), 0, 0),
    ],
)
def test_unknown_bounds_padding_or_timing_cannot_be_treated_as_a_complete_curve(
    raw, duration, scale
):
    with pytest.raises(ValueError):
        inspect_selector_curve(raw, duration=duration, time_scale=scale)


def test_huge_timing_integer_is_rejected_without_float_overflow():
    with pytest.raises(ValueError, match="timing"):
        inspect_selector_curve(bytes(8), duration=2**2048)


def test_selector_reference_preserves_two_state_weights_and_endpoint_behavior():
    from choops_py.research.motion_auxiliary import sample_selector_curve

    raw = struct.pack(">2I", 0x0D000000, 0x1000012C)
    assert sample_selector_curve(raw, 0, duration=1)["weights"] == [
        dict(selector=13, weight=255)
    ]
    mid = sample_selector_curve(raw, 0.5, duration=1)
    assert mid["weights"] == [
        dict(selector=16, weight=128),
        dict(selector=13, weight=127),
    ]
    assert sample_selector_curve(raw, 1, duration=1)["weights"] == [
        dict(selector=16, weight=255)
    ]
    assert not mid["native_vmx_bit_exact"] and not mid["selector_semantics_established"]
    for i in range(301):
        report = sample_selector_curve(raw, i / 300, duration=1)
        assert sum(row["weight"] for row in report["weights"]) == 255


def test_selector_reference_constant_channels_signed_ticks_and_ambiguous_coincidence():
    from choops_py.research.motion_auxiliary import sample_selector_curve

    raw = struct.pack(">2I", 0x0DFFFFFF, 0x0D00012C)
    assert sample_selector_curve(raw, 0.4, duration=1)["weights"] == [
        dict(selector=13, weight=255)
    ]
    raw = struct.pack(">3I", 0x0D000000, 0x10000000, 0x1000012C)
    with pytest.raises(ValueError, match="Coincident"):
        sample_selector_curve(raw, 0, duration=1)


@pytest.mark.parametrize("seconds", [-1, 1.01, float("nan"), float("inf"), True])
def test_selector_reference_never_extrapolates_or_guesses_outside_clip(seconds):
    from choops_py.research.motion_auxiliary import sample_selector_curve

    with pytest.raises(ValueError):
        sample_selector_curve(struct.pack(">2I", 0, 0x1000012C), seconds, duration=1)

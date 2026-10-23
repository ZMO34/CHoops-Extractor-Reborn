"""Stock gate reproduction and deliberately bounded tuning proposals."""

import math

import pytest

from choops_py.research.transfer_tuning import TransferTuning, candidate_gate


@pytest.mark.parametrize(
    "state,expected",
    [(0, 0), (1, 0), (2, 1 / 3), (3, 2 / 3), (4, 1), (5, 1), (6, 1), (7, 1)],
)
def test_stock_state_probabilities_are_conditional_not_population_rates(
    state, expected
):
    report = candidate_gate(state, 35, 0.8, other_native_filters_pass=True)
    assert report["conditional_probability"] == pytest.approx(expected)
    assert not report["population_transfer_rate_established"]
    assert not report["native_setting_installed"]


def test_tuning_can_admit_nonzero_state_one_but_cannot_override_other_filters():
    tuning = TransferTuning(intensity=3, nonzero_state_floor=0.2, confidence_ratio=1)
    assert candidate_gate(1, 35, 0.8, other_native_filters_pass=True, tuning=tuning)[
        "conditional_probability"
    ] == pytest.approx(0.2)
    for state in range(8):
        assert (
            candidate_gate(
                state, 35, 0.8, other_native_filters_pass=False, tuning=tuning
            )["conditional_probability"]
            == 0
        )
    assert (
        candidate_gate(0, 35, 0.8, other_native_filters_pass=True, tuning=tuning)[
            "conditional_probability"
        ]
        == 0
    )


def test_threshold_is_strict_and_uses_native_single_precision_confidence():
    tuning = TransferTuning(confidence_ratio=1)
    equal = candidate_gate(7, 50, 0.5, other_native_filters_pass=True, tuning=tuning)
    assert equal["scaled_confidence"] == 0.5
    assert equal["conditional_probability"] == 0
    assert (
        candidate_gate(7, 49, 0.5, other_native_filters_pass=True, tuning=tuning)[
            "conditional_probability"
        ]
        == 1
    )
    assert (
        candidate_gate(7, 51, 0.5, other_native_filters_pass=True, tuning=tuning)[
            "conditional_probability"
        ]
        == 0
    )


def test_zero_cap_disables_entry_without_misreporting_confidence():
    result = candidate_gate(
        7, 35, 0.8, other_native_filters_pass=True, tuning=TransferTuning(annual_cap=0)
    )
    assert result["confidence_passes"]
    assert result["conditional_probability"] == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"intensity": math.nan},
        {"intensity": True},
        {"intensity": 11},
        {"intensity": 10**1000},
        {"nonzero_state_floor": -0.1},
        {"confidence_ratio": math.inf},
        {"annual_cap": 401},
        {"annual_cap": True},
        {"annual_cap": 3.5},
    ],
)
def test_settings_reject_invalid_values_or_native_capacity_growth(kwargs):
    with pytest.raises(ValueError):
        TransferTuning(**kwargs)


@pytest.mark.parametrize(
    "state,confidence,evaluation,filters",
    [
        (True, 35, 0.8, True),
        (8, 35, 0.8, True),
        (1, 256, 0.8, True),
        (1, 35, math.nan, True),
        (1, 35, 0.8, 1),
    ],
)
def test_projection_requires_typed_bounded_inputs(
    state, confidence, evaluation, filters
):
    with pytest.raises(ValueError):
        candidate_gate(state, confidence, evaluation, other_native_filters_pass=filters)


def test_priority_encoding_uses_valid_native_profiles_and_requires_proxy_identity():
    from choops_py.research.transfer_portal import (
        Priority,
        native_preference_profile,
        portal_preference_index,
        priority_from_profile,
    )

    motivation = {
        Priority.HOMETOWN: "hometown_proximity",
        Priority.PLAYING_TIME: "playing_time",
        Priority.TEAM_RANKING: "big_program",
    }
    for priority in Priority:
        profile = portal_preference_index(priority)
        assert native_preference_profile(profile)[motivation[priority]][0] == 0
        assert priority_from_profile(profile, portal_proxy=True) == priority
        assert priority_from_profile(profile, portal_proxy=False) is None
    with pytest.raises(ValueError):
        priority_from_profile(127, portal_proxy=True)

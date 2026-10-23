"""Offline specification of transfer gates, not an installed game setting.

Evaluation is supplied by the caller; no roster byte is guessed to be overall.
The native PRNG, candidate insertion and scholarship allocation are not invoked.
"""

from dataclasses import dataclass
from math import isfinite
from struct import pack, unpack

NATIVE_TRANSFER_CAPACITY = 400


def _f32(value):
    return unpack(">f", pack(">f", value))[0]


def _bounded(value, low, high, name):
    if (
        type(value) not in (int, float)
        or not low <= value <= high
        or not isfinite(value)
    ):
        raise ValueError(f"{name} must be between {low} and {high}")


@dataclass(frozen=True)
class TransferTuning:
    """Proposed native controls; defaults reproduce the established stock gates.

    Floor applies only to nonzero candidate states, preserving the native zero
    exclusion. Eligibility and graduation filters are separate and mandatory.
    The cap bounds queue use, not an annual transfer quota or promised result.
    """

    intensity: float = 1.0
    nonzero_state_floor: float = 0.0
    confidence_ratio: float = _f32(0.66)
    annual_cap: int = NATIVE_TRANSFER_CAPACITY

    def __post_init__(self):
        _bounded(self.intensity, 0, 10, "intensity")
        _bounded(self.nonzero_state_floor, 0, 1, "nonzero_state_floor")
        _bounded(self.confidence_ratio, 0, 2, "confidence_ratio")
        if (
            type(self.annual_cap) is not int
            or not 0 <= self.annual_cap <= NATIVE_TRANSFER_CAPACITY
        ):
            raise ValueError("annual_cap must be an integer from 0 to 400")


def candidate_gate(
    state, confidence, evaluation, *, other_native_filters_pass, tuning=None
):
    """Conditional probability, with single-precision boundaries from 0x5B4E50.

    Confidence is the raw byte confirmed by 0x69E910 / 0x744C40. Evaluation must
    come from 0x74AA30 or an explicitly supplied synthetic projection. This is
    not the player's overall rating. No random draw or native eligibility guess.
    """
    if type(state) is not int or not 0 <= state <= 7:
        raise ValueError("state must be a three-bit integer")
    if type(confidence) is not int or not 0 <= confidence <= 255:
        raise ValueError("confidence must be a raw byte")
    _bounded(evaluation, 0, 1000000, "evaluation")
    if type(other_native_filters_pass) is not bool:
        raise ValueError("native filter result must be a boolean")
    if tuning is None:
        tuning = TransferTuning()
    if not isinstance(tuning, TransferTuning):
        raise ValueError("invalid transfer tuning")
    base = min(1.0, max(0.0, _f32(_f32(state - 1) / _f32(3))))
    chance = min(
        1.0, max(tuning.nonzero_state_floor, _f32(base * _f32(tuning.intensity)))
    )
    scaled_confidence = _f32(confidence * _f32(0.01))
    threshold = _f32(_f32(evaluation) * _f32(tuning.confidence_ratio))
    eligible = bool(
        state and other_native_filters_pass and scaled_confidence < threshold
    )
    enabled = tuning.annual_cap > 0
    return dict(
        state=state,
        stock_probability=base if state else 0.0,
        confidence_passes=scaled_confidence < threshold,
        scaled_confidence=scaled_confidence,
        confidence_threshold=threshold,
        conditional_probability=chance if eligible and enabled else 0.0,
        annual_cap=tuning.annual_cap,
        population_transfer_rate_established=False,
        native_setting_installed=False,
    )


def portal_research_overview():
    return """Native portal research — no executable changes installed

Confirmed: offseason callback order, conditional frequency/confidence gates,
400 active transfer rows, dynamic recruit save rebasing, persistent player
history ownership, Media/Coaches Top25 sources, and the ordinary conversion that
transfers must bypass.

Proposed: retain players on source rosters while recruiting; reserve additional
proxy records without replacing HS/JUCO prospects; bind proxies to frozen saved
queue order; use native recruiting class 3 internally and render TR class/RS from
the original player. Proxy statistics IDs must not alias player history.

Tuning specification: intensity, a floor for nonzero states, confidence threshold
and annual cap (0–400). These are offline policy calculations, not working game
settings. More entries also require proxy/node capacity and destination capacity.

Not implementation-ready: proxy initialization and menu integration, protected
annual cleanup, exact scholarship reservation/cancellation, native scoring/display
adapters, runtime allocation/load validation and save/resume behavior remain to
be proven. CPU routine 0x5C9974 hardcodes 2,000 recruits and a bounded sort buffer;
changing the roster count alone is unsafe. No percentage or certification is
inferred from the number of mapped addresses.

See docs/LEGACY_PORTAL_IMPLEMENTATION.md for evidence and acceptance gates.
"""

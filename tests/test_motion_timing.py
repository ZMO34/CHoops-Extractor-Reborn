import struct

import pytest

from choops_py.research.motion_timing import (
    compare_rate_timing,
    duration_divisor,
    inspect_rate_timing,
)


def header(nibble=0, duration=2.4, state=0):
    raw = bytearray(64)
    struct.pack_into(">2I", raw, 20, 0xD0000006 | (nibble << 24), state)
    struct.pack_into(">f", raw, 32, duration)
    return raw


def test_only_the_native_divisor_nibble_is_interpreted():
    assert duration_divisor(0xD000FFFF) == 1
    assert duration_divisor(0xD1000000) == 1
    assert duration_divisor(0xDF000000) == 15
    assert inspect_rate_timing(header(3, 6))["normalized_duration"] == 2
    report = compare_rate_timing(header(0), header(1))
    assert report["observed_rate_inputs_preserved"]
    assert not report["complete_playback_semantics_established"]
    assert not report["target_compatibility_established"]


def test_rate_changes_are_visible_without_coercing_target_authoring():
    source, target = header(3), header(2, 1.2, 16)
    before = bytes(source), bytes(target)
    report = compare_rate_timing(source, target)
    assert report["changed_inputs"] == [
        "duration_divisor",
        "duration",
        "bypasses_duration_rate_adjustment",
    ]
    assert report["target"]["bypasses_duration_rate_adjustment"]
    assert before == (bytes(source), bytes(target))


def test_zero_or_underflowed_duration_reports_division_hazard():
    assert not inspect_rate_timing(header(duration=0))["normalization_division_safe"]
    tiny = struct.unpack(">f", struct.pack(">I", 1))[0]
    result = inspect_rate_timing(header(15, tiny))
    assert result["duration"] > 0 and result["normalized_duration"] == 0
    assert not result["normalization_division_safe"]


@pytest.mark.parametrize("value", [-1, 2**32, True, 1.0, None])
def test_divisor_requires_uint32(value):
    with pytest.raises(ValueError, match="unsigned32"):
        duration_divisor(value)


@pytest.mark.parametrize("duration", [-1, float("inf"), float("nan")])
def test_invalid_duration_is_not_normalized(duration):
    with pytest.raises(ValueError, match="duration"):
        inspect_rate_timing(header(duration=duration))


def test_short_header_rejects_before_reading_fields():
    with pytest.raises(ValueError, match="36"):
        inspect_rate_timing(bytes(35))

import struct
from types import SimpleNamespace

import pytest

from choops_py.research.shot_fallback import (
    inspect_shot_fallbacks,
    resolve_shot_fallbacks,
    shot_cache_matches,
)


def pools():
    return dict(
        weighted_rows=[(100 + i, 200 + i, 1.0) for i in range(8)],
        bucket_rows=[(300 + i, 400 + i, 500 + i, 600 + i) for i in range(18)],
        fixed_pair2=[700, 800],
        fixed_pair3=[900, 1000],
    )


def resolve(selected, bit=1, bucket=0, **kwargs):
    args = dict(random_samples=[] if selected[0] else [0.25] * 8, **pools())
    args.update(kwargs)
    return resolve_shot_fallbacks(selected, bit, bucket, 123, **args)


def test_pair1_fallback_replaces_existing_pair2_and_preserves_original_flags():
    result = resolve([11, 0, 33, 44], bucket=65535)
    assert result["motions"] == [11, 315, 515, 44]
    assert result["original_pair0_present"] is True
    assert result["original_pair1_present"] is False
    assert result["control_value"] == 123
    assert result["pair_origins"][2] == "bucket-fallback"


def test_lane_and_fixed_fallbacks_do_not_fill_presence_flags():
    result = resolve([0, 22, 0, 0], bit=0)
    assert result["motions"] == [202, 22, 800, 1000]
    assert result["original_pair0_present"] is False
    assert result["original_pair1_present"] is True
    assert result["control_value"] == 0
    assert result["random_draws"] == 8


def test_context_replaces_present_pair3_and_resets_control_only():
    result = resolve([11, 22, 33, 44], context_override=True)
    assert result["motions"] == [11, 22, 33, 900]
    assert result["control_value"] == 0
    assert result["pair_origins"] == ["source"] * 3 + ["fixed-pair3-context"]


@pytest.mark.parametrize("sample,index", [(0, 7), (0.25, 2), (0.5, 0), (0.99, 0)])
def test_weighted_reservoir_uses_strict_comparison_and_all_eight_draws(sample, index):
    result = resolve([0, 22, 33, 44], random_samples=[sample] * 8)
    assert result["motions"][0] == 100 + index
    assert result["weighted_index"] == index
    assert result["random_draws"] == 8


def test_explicit_empty_bucket_pointer_is_not_fabricated():
    rows = pools()["bucket_rows"]
    rows[0] = (0, 0, 0, 0)
    result = resolve([11, 0, 33, 44], bucket_rows=rows)
    assert result["motions"] == [11, 0, 700, 44]
    assert result["unresolved_motion_pairs"] == [1]
    assert not result["gameplay_ready"]


@pytest.mark.parametrize(
    "change",
    [
        {"random_samples": [float("nan")] * 8},
        {"random_samples": [1] * 8},
        {"random_samples": [0] * 7},
        {"context_override": 1},
        {"weighted_rows": [(1, 2, 0)] * 8},
        {"weighted_rows": [(1, 2, 3.4e38)] * 8},
        {"bucket_rows": [(1, 2, 3, 4)] * 17},
    ],
)
def test_unknown_invalid_or_unbounded_inputs_block_resolution(change):
    with pytest.raises(ValueError):
        resolve([0, 22, 33, 44], **change)


@pytest.mark.parametrize(
    "key,hit",
    [
        ((0, 17, 12, 17), False),
        ((11, 17, 12, 17), False),
        ((12, 17, 12, 18), False),
        ((12, 17, 12, 17), True),
    ],
)
def test_cache_key_is_player_identity_and_revision(key, hit):
    assert shot_cache_matches(*key) is hit


def fallback_elf():
    # Sparse synthetic ELF: code, native tables, and two embedded headers.
    raw = bytearray(0xD00)
    raw[:7] = b"\x7fELF\x02\x02\x01"
    struct.pack_into(">HH", raw, 16, 2, 21)
    struct.pack_into(">Q", raw, 32, 64)
    struct.pack_into(">HH", raw, 54, 56, 3)
    for i, (offset, address, size) in enumerate(
        [(0x200, 0x653600, 0x400), (0x600, 0x434F1C0, 0x400), (0xA00, 0x3F8C780, 0x100)]
    ):
        struct.pack_into(
            ">II6Q", raw, 64 + 56 * i, 1, 4, offset, address, address, size, size, 16
        )
    for address, word in [
        (0x6536C8, 0x911F001C),
        (0x6536DC, 0x913F0020),
        (0x6538C0, 0x4BFFFE78),
    ]:
        struct.pack_into(">I", raw, 0x200 + address - 0x653600, word)
    for i in range(8):
        at = 0x610 + 20 * i
        struct.pack_into(">2I", raw, at, 100, 0)
        struct.pack_into(">2I", raw, at + 8, 0, 0x3F8C798)
        struct.pack_into(">f", raw, at + 16, 1)
    for at in (0xA18, 0xA50):
        struct.pack_into(">I", raw, at + 8, 0x1DF7DD)
    return raw


def test_dependency_inspection_distinguishes_serialized_embedded_empty_and_ambiguous():
    raw = fallback_elf()
    before = bytes(raw)
    source = SimpleNamespace(index={100: [(0, 2)]}, fingerprints=["synthetic"])
    result = inspect_shot_fallbacks(raw, source)
    row = result["weighted_rows"][0]
    assert row["lanes"][0]["status"] == "resolved-identity"
    assert row["lanes"][1]["kind"] == "embedded"
    assert result["bucket_rows"][0]["pair1"][0]["kind"] == "empty"
    assert result["source_banks_sha256"] == ["synthetic"]
    source.index[100].append((1, 2))
    assert (
        inspect_shot_fallbacks(raw, source)["weighted_rows"][0]["lanes"][0]["status"]
        == "ambiguous"
    )
    assert bytes(raw) == before
    assert not result["runtime_resources_initialized"]


@pytest.mark.parametrize(
    "offset,value", [(0x2C8, 0), (0x620, 0x7FC00000), (0x61C, 0x40000000)]
)
def test_dependency_inspection_rejects_wrong_revision_nan_weight_or_unbacked_header(
    offset, value
):
    raw = fallback_elf()
    struct.pack_into(">I", raw, offset, value)
    with pytest.raises(ValueError):
        inspect_shot_fallbacks(raw)

import json
import struct

import pytest

from choops_py.formats.motion_events import (
    inspect_auxiliary_pairs,
    inspect_events,
    transcode_events,
)


NBA = "nba-2k11"
CH = "college-hoops-2k8"
END = struct.pack(">i", -0x80000000)


def contract(*rules):
    return dict(
        schema=1,
        rules=[
            dict(
                source_id=a,
                target_id=b,
                payload_word=c,
                evidence="Synthetic fixture only; no game semantic assertion",
            )
            for a, b, c in rules
        ],
    )


def test_event_bridge_preserves_duplicate_order_and_float_bits():
    # Equal timestamps, negative zero and repeated marker IDs must not be sorted
    # or deduplicated, nor reconstructed through decimal JSON float formatting.
    raw = (
        b"".join(
            struct.pack(">iII", a, b, 0)
            for a, b in [(23, 0x80000000), (17, 0x3EAAAAAB), (23, 0x3EAAAAAB)]
        )
        + END
    )
    before = bytes(raw)
    report = inspect_events(raw, NBA)
    output, info = transcode_events(report, contract((23, 22, None), (17, 16, None)))
    assert (
        output
        == b"".join(
            struct.pack(">iI", a, b)
            for a, b in [(22, 0x80000000), (16, 0x3EAAAAAB), (22, 0x3EAAAAAB)]
        )
        + END
    )
    assert info["events"] == 3 and not info["gameplay_ready"]
    assert info["time_bits_preserved"] and not info["complete_motion"]
    assert raw == before


@pytest.mark.parametrize("word", [0, 7, 0xFFFFFFFF])
def test_known_payload_consumer_needs_exact_rule_including_zero(word):
    raw = struct.pack(">iII", 90, 0x3F000000, 9) + END + struct.pack(">I", word)
    report = inspect_events(raw, NBA)
    assert report["entries"][0]["payload"] == 16
    assert report["entries"][0]["payload_word"] == word
    with pytest.raises(ValueError, match="No explicit mapping"):
        transcode_events(report, contract((90, 89, None)))
    output, _ = transcode_events(report, contract((90, 95, word)))
    assert inspect_events(output, CH)["entries"][0]["id"] == 95


def test_unknown_payload_never_silently_dropped():
    raw = struct.pack(">iII", 92, 0, 9) + END + bytes(4)
    report = inspect_events(raw, NBA)
    assert report["opaque_payloads"] == 1
    assert report["entries"][0]["payload_word"] is None
    with pytest.raises(ValueError, match="Opaque payload"):
        transcode_events(report, contract((92, 39, None)))


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        bytes(11),
        struct.pack(">iII", 23, 0, 0),
        struct.pack(">iII", 90, 0, 8) + END,
        struct.pack(">iII", 90, 0, 1001) + END,
        struct.pack(">iII", 90, 0, 0) + END,
        struct.pack(">iII", 4, 0x7FC00000, 0) + END,
    ],
)
def test_event_parser_rejects_truncation_missing_sentinel_bad_payload_and_nan(raw):
    with pytest.raises(ValueError):
        inspect_events(raw, NBA)


def test_signed_relative_payload_can_point_before_table():
    raw = struct.pack(">I", 7) + struct.pack(">iII", 90, 0, 0xFFFFFFF5) + END
    report = inspect_events(raw, NBA, 4)
    assert report["entries"][0]["payload_word"] == 7
    assert report["sentinel"] == 16
    assert inspect_events(END, CH)["entries"] == []
    assert transcode_events(inspect_events(END, NBA), contract())[0] == END
    with pytest.raises(ValueError):
        inspect_events(raw, "nba-2k14")
    with pytest.raises(ValueError):
        inspect_events(raw, NBA, 1)


@pytest.mark.parametrize(
    "mapping",
    [
        dict(schema=2, rules=[]),
        dict(schema=1, rules={}),
        contract((23, 22, None), (23, 24, None)),
        contract((92, 39, 0)),
        dict(schema=1, rules=[dict(source_id=4, target_id=4, evidence="")]),
        contract((True, 4, None)),
        contract((4, -1, None)),
    ],
)
def test_mapping_contract_rejects_ambiguous_or_unsupported_rules(mapping):
    with pytest.raises(ValueError):
        transcode_events(inspect_events(END, NBA), mapping)


def test_native_addresses_and_full_payload_extent_must_be_file_backed():
    from test_embedded_motion import native_fixture

    raw = native_fixture(NBA)
    # Table in one file-backed range, payload in another, absolute pointers.
    struct.pack_into(">iIIi", raw, 0x280, 90, 0x3F000000, 0x20000, -0x80000000)
    struct.pack_into(">I", raw, 0x400, 7)
    assert (
        inspect_events(raw, NBA, 0x10080, native=True)["entries"][0]["payload_word"]
        == 7
    )
    struct.pack_into(">I", raw, 0x288, 0x20280)  # Native BSS, not file bytes.
    with pytest.raises(ValueError, match="file-backed"):
        inspect_events(raw, NBA, 0x10080, native=True)
    struct.pack_into(">I", raw, 0x288, 0x201FC)
    assert (
        inspect_events(raw, NBA, 0x10080, native=True)["entries"][0]["payload_word"]
        == 0
    )
    with pytest.raises(ValueError):
        inspect_events(raw, NBA, 0x101FC, native=True)


def test_auxiliary_membership_pairs_keep_second_word_opaque():
    raw = struct.pack(">5I", 2, 7, 0xDEADBEEF, 7, 0x12345678)
    report = inspect_auxiliary_pairs(raw, 0)
    assert report["entries"] == [
        dict(key=7, raw_value=0xDEADBEEF),
        dict(key=7, raw_value=0x12345678),
    ]
    assert not report["semantics_established"]
    for bad in (raw[:-1], struct.pack(">I", 0x7FFFFFFF), struct.pack(">i", -1)):
        with pytest.raises(ValueError):
            inspect_auxiliary_pairs(bad, 0)


def test_event_cli_validates_all_before_writing_and_protects_inputs(
    tmp_path, monkeypatch
):
    from choops_py import cli
    from choops_py.archive import manifests

    monkeypatch.setattr(manifests, "OUTPUT", tmp_path)
    source, mapping, target = [
        tmp_path / n for n in ("source.bin", "mapping.json", "target.bin")
    ]
    raw = struct.pack(">iII", 23, 0x3EAAAAAB, 0) + END
    source.write_bytes(raw)
    mapping.write_text(json.dumps(contract((23, 22, None))), encoding="utf-8")
    args = ["transcode-motion-events", str(source), NBA, "0", str(mapping)]
    for destination in (source, mapping):
        with pytest.raises(ValueError):
            cli.execute(cli.parser().parse_args([*args, str(destination)]))
    info = cli.execute(cli.parser().parse_args([*args, str(target)]))
    assert info["events"] == 1 and not info["gameplay_ready"]
    assert source.read_bytes() == raw
    target.unlink()
    mapping.write_text(json.dumps(contract()), encoding="utf-8")
    with pytest.raises(ValueError, match="No explicit mapping"):
        cli.execute(cli.parser().parse_args([*args, str(target)]))
    assert not target.exists()
    output = tmp_path / "events.json"
    cli.execute(
        cli.parser().parse_args(
            ["inspect-motion-events", str(source), NBA, "0", str(output)]
        )
    )
    assert json.loads(output.read_text(encoding="utf-8"))["entry_stride"] == 12

import json
import struct

import pytest

from choops_py.cli import execute, parser
from choops_py.research.marker_dispatch import PROFILES, inspect_dispatch


def fixture(profile):
    layout = PROFILES[profile]
    code = min(layout["anchors"])
    table = layout["base"]
    descriptor = table + 0x1000
    raw = bytearray(0x2800)
    raw[:7] = b"\x7fELF\x02\x02\x01"
    struct.pack_into(">HH", raw, 16, 2, 21)
    struct.pack_into(">Q", raw, 32, 64)
    struct.pack_into(">HH", raw, 54, 56, 2)
    struct.pack_into(">II6Q", raw, 64, 1, 5, 0x200, code, code, 0x100, 0x100, 4)
    struct.pack_into(">II6Q", raw, 120, 1, 6, 0x800, table, table, 0x2000, 0x2100, 4)
    for address, word in layout["anchors"].items():
        struct.pack_into(">I", raw, 0x200 + address - code, word)
    struct.pack_into(">II", raw, 0x1800, code, layout["toc"])
    for identity in range(layout["count"]):
        struct.pack_into(">II", raw, 0x800 + identity * 8, identity % 7, descriptor)
    return raw


@pytest.mark.parametrize("profile,count", [("nba-2k11", 192), ("college-hoops-2k8", 185)])
def test_flags_precede_descriptor_and_last_registered_id_is_retained(profile, count):
    raw = fixture(profile)
    before = bytes(raw)
    report = inspect_dispatch(raw, profile)
    assert len(report["rows"]) == count
    assert report["rows"][-1]["id"] == count - 1
    assert report["rows"][1]["flags"] == 1
    assert report["rows"][0]["descriptor"] == PROFILES[profile]["base"] + 0x1000
    assert report["callback_groups"][0]["ids"] == list(range(count))
    assert not report["cross_game_events_mapped"] and not report["payload_abi_portable"]
    assert not report["flags_semantically_mapped"] and bytes(raw) == before


@pytest.mark.parametrize("corruption,message", [
    ("revision", "revision"), ("toc", "TOC"), ("entry", "executable"),
    ("descriptor", "file-backed"), ("alignment", "Unaligned"),
])
def test_invalid_native_dependencies_and_revisions_reject(corruption, message):
    profile = "college-hoops-2k8"
    raw = fixture(profile)
    if corruption == "revision":
        raw[0x200] ^= 1
    elif corruption == "toc":
        struct.pack_into(">I", raw, 0x1804, 0)
    elif corruption == "entry":
        struct.pack_into(">I", raw, 0x1800, PROFILES[profile]["base"])
    else:
        struct.pack_into(">I", raw, 0x804, PROFILES[profile]["base"] + (0x2000 if corruption == "descriptor" else 1))
    with pytest.raises(ValueError, match=message):
        inspect_dispatch(raw, profile)


def test_cli_inspects_without_overwriting_input_and_unknown_profile_rejects(tmp_path, monkeypatch):
    from choops_py.archive import manifests

    monkeypatch.setattr(manifests, "OUTPUT", tmp_path)
    profile = "nba-2k11"
    source = tmp_path / "native.elf"
    output = tmp_path / "dispatch.json"
    raw = fixture(profile)
    source.write_bytes(raw)
    execute(parser().parse_args(["inspect-marker-dispatch", str(source), profile, str(output)]))
    assert json.loads(output.read_text())["callback_arguments"]["r3"] == "event-row-pointer"
    assert source.read_bytes() == raw
    with pytest.raises(ValueError, match="input|source|overwrite"):
        execute(parser().parse_args(["inspect-marker-dispatch", str(source), profile, str(source)]))
    with pytest.raises(ValueError, match="not established"):
        inspect_dispatch(raw, "nba-2k14")

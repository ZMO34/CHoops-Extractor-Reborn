import struct

import pytest

from choops_py.formats.loc_system import entries, tokens
from choops_py.research.scorebug_localization import value_only_template


def fixture(alias=False):
    marker = "{1}".encode("utf-16-be")
    raw = "TEAM: ".encode("utf-16-be") + marker + bytes(2)
    h = bytearray(32)
    struct.pack_into(">III", h, 0, 0xE33E3B9C, 3, 25)
    for key, target in [
        (1, 56),
        (3, 56 if alias else 56 + len(raw)),
        (0xFFFFFFFF, None),
    ]:
        field = len(h) + 4
        h.extend(struct.pack(">II", key, 0 if target is None else target - field + 1))
    h.extend(raw + b"\x01Z\0\0")
    return bytes(h), raw


def test_isolated_template_preserves_other_entries():
    source, raw = fixture()
    result = value_only_template(source, 1, raw, "{1}")
    assert len(result) == len(source)
    assert entries(result) == entries(source)
    assert tokens(result, 3) == tokens(source, 3)
    assert tokens(result, 1) == "{1}".encode("utf-16-be") + bytes(2)


def test_alias_rejected():
    source, raw = fixture(True)
    with pytest.raises(ValueError, match="aliased"):
        value_only_template(source, 1, raw, "{1}")


def test_unexpected_source_rejected():
    source, raw = fixture()
    with pytest.raises(ValueError, match="Unexpected"):
        value_only_template(source, 1, raw + b"x", "{1}")


def test_missing_argument_rejected():
    source, raw = fixture()
    with pytest.raises(ValueError, match="one existing"):
        value_only_template(source, 1, raw, "{0}")


def test_existing_prefix_retained():
    source, raw = fixture()
    prefix = "TEAM: ".encode("utf-16-be")
    result = value_only_template(source, 1, raw, "{1}", prefix=prefix)
    assert tokens(result, 1) == raw


def test_new_prefix_rejected():
    source, raw = fixture()
    with pytest.raises(ValueError, match="source prefix"):
        value_only_template(source, 1, raw, "{1}", prefix="NEW".encode("utf-16-be"))


def test_interior_alias_rejected():
    source, raw = fixture()
    changed = bytearray(source)
    # The second entry starts inside the first template, at an aligned character.
    struct.pack_into(">I", changed, 44, 58 - 44 + 1)
    with pytest.raises(ValueError, match="overlaps"):
        value_only_template(bytes(changed), 1, raw, "{1}")


def test_repeated_argument_rejected():
    source, raw = fixture()
    repeated = raw[:-2] + "{1}".encode("utf-16-be") + bytes(2)
    # Reject before any write, even when the caller's source expectation agrees.
    changed = source[:56] + repeated + source[56 + len(raw) :]
    changed = bytearray(changed)
    struct.pack_into(">I", changed, 44, 56 + len(repeated) - 44 + 1)
    with pytest.raises(ValueError, match="one existing"):
        value_only_template(bytes(changed), 1, repeated, "{1}")

"""Bounded scorebug comparison formatting; no callbacks or executable changes."""

from collections import Counter

from choops_py.formats.loc_system import entries, tokens


def value_only_template(data, key, expected, argument, prefix=b""):
    """Keep an existing encoded argument, preserving every ID and pool extent."""
    rows = entries(data)
    starts = dict(rows)
    at = starts.get(key)
    if at is None or Counter(p for _, p in rows)[at] != 1:
        raise ValueError("Template is absent or aliased")
    original = tokens(data, key)
    if original != expected:
        raise ValueError("Unexpected source template")
    marker = argument.encode("utf-16-be")
    if original.count(marker) != 1:
        raise ValueError("Expected one existing encoded argument")
    if (
        not isinstance(prefix, bytes)
        or len(prefix) % 2
        or not original.startswith(prefix)
    ):
        raise ValueError("Retained prefix is not an existing aligned source prefix")
    replacement = prefix + marker + bytes(2)
    end = at + len(original)
    if any(at < p < end for _, p in rows if p is not None):
        raise ValueError("Template overlaps another localization entry")
    out = bytearray(data)
    out[at:end] = replacement + bytes(len(original) - len(replacement))
    result = bytes(out)
    if entries(result) != rows or tokens(result, key) != replacement:
        raise ValueError("Template preservation failed")
    if result[:at] != data[:at] or result[end:] != data[end:]:
        raise ValueError("Unrelated localization bytes changed")
    return result

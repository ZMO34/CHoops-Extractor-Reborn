"""Safe roster palette and school-name edits for the three-tab studio.

Colors are *raw research slots*: not proven court/cheer semantic labels.
All edits preserve unknown bytes, refuse shared string storage, and are undoable.
"""
import struct

from .core.errors import ToolError
from .roster.schema import STRING_FIELDS


def team_colors(model, index):
    base = model.row_offset("teams", index)
    return [
        f"{struct.unpack_from('>I', model.data, base + 0x1A0 + i * 4)[0]:08X}"
        for i in range(31)
    ]


def apply_studio_field(model, index, field, value, research_ack=False):
    base = model.row_offset("teams", index)
    previous = bytes(model.data)
    old_history = list(model.history)
    old_edits = list(model.edits)
    try:
        if field.startswith("color_") and field[6:].isdigit():
            slot = int(field[6:])
            if slot >= 31:
                raise ToolError("palette_slot_out_of_range", field)
            if not research_ack:
                raise ToolError(
                    "experimental_edit_not_acknowledged",
                    "Unverified raw palette slots require Research Editing consent",
                )
            raw = str(value).strip().removeprefix("#").upper()
            if len(raw) == 6:
                raw += team_colors(model, index)[slot][6:]
            if len(raw) != 8 or any(c not in "0123456789ABCDEF" for c in raw):
                raise ToolError("invalid_palette_color", "Expected RRGGBB or RRGGBBAA")
            offset = base + 0x1A0 + slot * 4
            old_value = team_colors(model, index)[slot]
            model.data[offset:offset + 4] = bytes.fromhex(raw)
        elif field in STRING_FIELDS["teams"]:
            pointer = base + STRING_FIELDS["teams"][field]
            delta = struct.unpack_from(">i", model.data, pointer)[0]
            if delta in (0, -1):
                raise ToolError("missing_team_string", field)
            target = pointer + delta
            old_value = model.rows["teams"][index][field]
            encoded = str(value).encode("utf-16-le")
            if len(encoded) != len(old_value.encode("utf-16-le")):
                raise ToolError(
                    "string_length_mismatch",
                    "Original UTF-16 byte length must be preserved",
                )
            if any(ord(c) < 32 for c in str(value)):
                raise ToolError("invalid_team_string", "Control characters are blocked")
            if len(model.string_users.get(target, [])) != 1:
                raise ToolError("shared_string_write_blocked", "String storage is shared")
            end = target + len(encoded)
            if model.string_ranges.get(target) != end + 2:
                raise ToolError("invalid_string_storage", "String bounds mismatch")
            if any(
                other != target and target < limit and other < end
                for other, limit in model.string_ranges.items()
            ):
                raise ToolError("overlapping_string_write_blocked", field)
            if any(
                target < start + count * size and start < end
                for start, count, size in model.tables.values()
            ):
                raise ToolError("invalid_string_storage", "Overlaps fixed roster table")
            model.data[target:end] = encoded
        else:
            raise ToolError("roster_field_read_only", field)

        validation = model.validate()
        if not validation["valid"]:
            raise ToolError("roster_validation_failed", str(validation["issues"][:5]))
        if bytes(model.data) != previous:
            model.history.append((previous, old_edits))
            model.edits.append({
                "table": "teams", "index": index, "field": field,
                "old": old_value, "value": value,
                "experimental": field.startswith("color_"),
            })
        return {"unsaved_edits": len(model.edits), "validation": validation}
    except Exception:
        model.data[:] = previous
        model.history[:] = old_history
        model.edits[:] = old_edits
        model.reload()
        raise

"""Tests for the native three-tab Studio's safety boundaries."""
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from choops_py.core.errors import ToolError
from choops_py.studio_fields import apply_studio_field, team_colors
from choops_py.studio_web import job_args


class FakeModel:
    def __init__(self):
        self.data = bytearray(1024)
        struct.pack_into(">I", self.data, 0x1A4, 0xAD3640FF)
        self.history = []
        self.edits = []
        self.rows = {"teams": [{"school_name": "Georgia"}]}
        self.string_users = {}
        self.string_ranges = {}
        self.tables = {"teams": (0, 1, 704)}
    def row_offset(self, table, index):
        if table != "teams" or index != 0:
            raise ValueError("Invalid table index")
        return 0
    def validate(self):
        return {"valid": True, "issues": []}
    def reload(self):
        pass


class StudioTests(unittest.TestCase):
    def test_palette_requires_explicit_research_ack(self):
        model = FakeModel()
        before = bytes(model.data)
        with self.assertRaises(ToolError):
            apply_studio_field(model, 0, "color_1", "#00FF00")
        self.assertEqual(bytes(model.data), before)
        self.assertFalse(model.edits)

    def test_palette_changes_only_four_bytes_and_preserves_alpha(self):
        model = FakeModel()
        old = bytes(model.data)
        result = apply_studio_field(model, 0, "color_1", "#00FF00", True)
        self.assertEqual(team_colors(model, 0)[1], "00FF00FF")
        self.assertEqual(model.data[:0x1A4], old[:0x1A4])
        self.assertEqual(model.data[0x1A8:], old[0x1A8:])
        self.assertEqual(result["unsaved_edits"], 1)
        self.assertEqual(len(model.history), 1)

    def test_unsupported_fields_and_palette_slots_refused(self):
        model = FakeModel()
        for field in ("color_31", "unknown_foo"):
            with self.assertRaises(ToolError):
                apply_studio_field(model, 0, field, "#123456", True)
        self.assertFalse(model.edits)

    def test_job_preflight_rejects_missing_source_and_unsafe_actions(self):
        with self.assertRaises(ValueError):
            job_args("rip", {"source": "", "target": ""})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                job_args("execute-arbitrary", {
                    "source": directory, "target": str(Path(directory) / "out")
                })

    def test_dashboard_file_and_required_main_tabs(self):
        root = Path(__file__).resolve().parents[1]
        ui = (root / "choops_py" / "studio.html").read_text(encoding="utf-8")
        for tab in ("Rip Game Assets to IFF", "Build Game from IFF Folder", "Open Roster"):
            self.assertIn(tab, ui)
        self.assertIn('data-sub="colors"', ui)
        self.assertIn('data-sub="conferences"', ui)


if __name__ == "__main__":
    unittest.main()

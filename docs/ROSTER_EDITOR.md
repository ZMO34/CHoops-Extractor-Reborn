# Roster editor

Open the GUI Roster Editor and choose roster_english.iff, raw ROST, decrypted USERDATA, a type-21 tool wrapper, or a decrypted ZIP containing exactly one USERDATA. Encrypted saves are not decrypted by this tool.

Players, teams, arenas and coaches have searchable tables; selecting a team displays its sixteen roster slots. Edit a selected player or team, validate, undo/revert unsaved changes, save a copy, or export JSON/CSV for review. The GUI runs long operations off the Tk thread.

Supported player edits: first/last names using the same UTF-16 byte length and unshared storage, jersey number 0–99, height 36–100 inches and position 0–4. Supported team edits: sixteen player-slot references, existing team asset IDs, arena, coach and rival references. Arenas/coaches are displayed read-only. Skin tone, appearance bytes, conference, prestige and long-string heap rebuilding remain read-only.

```powershell
python -m choops_py.cli roster-detect output/rips/roster_english.iff
python -m choops_py.cli roster-export-json output/rips/roster_english.iff output/reports/roster_review
python -m choops_py.cli roster-save output/rips/roster_english.iff output/reports/roster_review/roster.json output/temp/edited_roster.iff --safe-only
python -m choops_py.cli roster-validate output/temp/edited_roster.iff
```

Edit only documented editable JSON fields. The source SHA256 must match. Alternatively use a patch with `source_sha256` and `edits`, each containing table/index/field/value and optional slot. Invalid pointers or references block saving. Save preserves source wrapper type, unknown bytes and unrelated IFF records, and emits a sibling edit report. Standard IFF compression rebuild must fit the original archive extent. Stage the saved copy as roster_english.iff and build a separate JB folder to use it.

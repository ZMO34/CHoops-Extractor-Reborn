# Roster editor

Open the GUI Roster Editor and choose roster_english.iff, raw ROST, decrypted USERDATA, a type-21 tool wrapper, or a decrypted ZIP containing exactly one USERDATA. Encrypted saves are not decrypted by this tool.

Players, teams, arenas and coaches have searchable tables; selecting a team displays its sixteen roster slots. Edit a selected player or team, validate, undo/revert unsaved changes, save a copy, or export JSON/CSV for review. The GUI runs long operations off the Tk thread.

Supported player edits: first/last names using the same UTF-16 byte length and unshared storage, jersey number 0–99, height 36–100 inches and position 0–4. Supported team edits: sixteen player-slot references, existing team asset IDs, arena, coach and rival references. School, arena and coach strings can be edited only with identical UTF-16 byte length in unshared storage. Team palette editing supports all 31 RGBA slots; 22 slots have exact Edit Schools captions; the remaining roles are unresolved. Skin tone, appearance bytes, conference, prestige and long-string heap rebuilding remain read-only.

```powershell
python -m choops_py.cli roster-detect output/rips/roster_english.iff
python -m choops_py.cli roster-export-json output/rips/roster_english.iff output/reports/roster_review
python -m choops_py.cli roster-save output/rips/roster_english.iff output/reports/roster_review/roster.json output/temp/edited_roster.iff --safe-only
python -m choops_py.cli roster-validate output/temp/edited_roster.iff
```

Edit only documented editable JSON fields. The source SHA256 must match. Alternatively use a patch with `source_sha256` and `edits`, each containing table/index/field/value and optional slot. Invalid pointers or references block saving. Save preserves source wrapper type, unknown bytes and unrelated IFF records, and emits a sibling edit report. Standard IFF compression rebuild must fit the original archive extent. Stage the saved copy as roster_english.iff and build a separate JB folder to use it.

## Team palette and stadium linkage

The team asset ID identifies the sXXX stadium art family; the team row index and arena reference index are separate identities. In Models / Courts, load the roster and use Linked roster palette to find the unique team whose asset ID matches the stadium filename. The Team palette dialog shows RGBA swatches, exact slot indices and contextual role candidates. Edits participate in undo/redo and copy-save validation. Candidate labels do not establish a particular shader channel or in-game effect.

Palette words are four RGBA bytes at team row +0x1A0 through +0x218 inclusive (31 slots). Repeated colors across school slots support primary/secondary candidate labels. The palette can contain white, gray and accent colors as well as school colors. Green regions in some arena textures may be shader tint masks; no automatic green-to-roster recoloring is enabled because channel-to-slot routing is unproven.

Research layout exports the roster header's count/pointer anchors and profiles every byte offset of the four known record tables, including unknown bytes and rating-like candidates. It reports unassigned payload regions and the inherited arena/team boundary ambiguity. This is structural coverage, not a complete semantic decode. Ratings, tendencies, appearance, conference affiliation/prestige, variable-length heap changes and unknown table meanings are not confirmed editable fields.

## Executable-backed semantics

The editor derives the known table starts and counts from the roster header, including the coach name anchor and conference table. Team +0x48 is a relative conference reference. Conference +0x6E0 begins the observed team-reference list; conference assignment remains read-only until all reciprocal update rules are established.

All 30 attribute names are linked through localized UI registration metadata to the game's getters and setters. Ratings occupy player +0x3C through +0x76 as big-endian u16 values. The getter displays clamp(floor(raw / 100), 35, 99); edits store rating * 100, while untouched fractional values remain byte-exact. Player attributes shows these named channels. Four byte tendencies follow at +0x78..+0x7B. Potential is at +0x7F; confidence at +0x80. Packed weight and handedness edits preserve neighboring bits. Named appearance/equipment fields are readable; their enum choice meanings remain incomplete.

Edit Schools displays team records separately from players. The color dialog distinguishes raw palette slot numbers from the game's color-control indices. The observed getter/setter arrays expose 22 controls targeting slots 2–10, 12–15 and 18–26. All 22 exact English captions are traced through menu selection callbacks to their RGBA getters/setters. Repeated Primary and Secondary captions are kept literal and distinguished by control and raw slot. Court material IDs now route to the verified roster getters and DiffuseColor uniform; arena mask-channel routes remain unresolved. Other palette words are preserved and can be inspected. Labels for the other nine slots remain explicitly provisional.

Full roster semantic reversal is not complete. The local evidence ledger retains executable traces and unresolved questions; proprietary executable and language payload copies remain private. Public methodological references: [RPCS3 SELF implementation](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Crypto/unself.cpp) and [community conference parser](https://github.com/bphit4/CH2k8-Roster-Editor/blob/main/Conference_Parser.py). External offsets were checked against the stock roster rather than copied without validation.

Confirmed control captions in order: Key Circle Outer, Center Line, Outer Line, Skirt Inner, Skirt Outer, Lane Right, Lane Left, Key Hash, Center Circle, Top Key Right, Top Key Left, Primary, Secondary, 3Pt Line, Key, Key Line, Basket Front, Basket Rear, Basket Metal, Primary, Secondary, Tertiary.

Court preview uses a unique matching asset ID in the explicitly loaded roster, including unsaved edits. Verified RGB values are converted from sRGB to linear color; the runtime gray sentinel (RGB 190/190/190) leaves the authored preview unchanged. This reproduces the color binding with simplified preview lighting, not the full game shader.

Jersey number is the byte at player row +0x1B (name-anchor +0x0B), corroborated by its localized UI increment callback. The adjacent byte at +0x1A contains flags in some records and is preserved by number edits. Jersey-number material/color shader routing remains unresolved.

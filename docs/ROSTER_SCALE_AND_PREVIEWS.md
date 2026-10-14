# Roster scale and preview project (in progress)

Baseline: merged v1.11, master 7796fcbd72c127730f484c67a5b0de26440ed066.
Recent functional PRs were already merged when this project began. The remaining
old setup draft is superseded, not new code to merge.

## Implemented source work

- School filter and school column for players; existing text search/sorting remain.
- Ratings edit inline in the side panel with a bounded spin box. Copy ratings and
  tendencies, then paste to selected players in one atomic undo step. Large batches
  write confirmed masks and validate/reparse once, not once per cell.
- Export editable cells as CSV. Values and preconditions are JSON values inside
  CSV cells; edit Value, retain Original and source identity. Import previews changes
  first and refuses wrong sources, stale values, duplicates and invalid channels.
  Spreadsheet context columns show school/player; source binary data is excluded.
- Compare two supported roster files; show current/incoming values by school and
  record, filter, check individual fields, then import selected compatible changes.
  Unique player IDs and school ownership are used where available; name matching
  is the fallback. Duplicate/unmatched identities and unresolved references are
  excluded. Renumbered/recycled IDs are not automatically reconciled. Review is
  required; imported fields share existing writers. Arrays of roster membership
  are excluded from bulk CSV/comparison, retaining the guarded School interface.
  Review uses a table model with persistent source-row selections across filtering
  and sorting, avoiding one widget allocation per edit in large comparisons.
- School footwear imports use scoped propagation, not a separate unsafe writer.
  Coupled field conflicts roll back. Undo remains one action; patches are replayable.
- Height/weight use pickers. Body Build and Muscle Tone already have confirmed
  dropdowns. Class, Redshirt and Redshirt Used are newly mapped and editable.
  Confidence uses its confirmed getter/setter and 35–99 UI range.
  Conference History separates the supported history/record scalar fields.
- A shared Source JB / Selected overrides toggle reloads SCNE and texture previews.
  Staged archives must match source preconditions and replacement checksums. Shoes,
  uniforms and general named/hashed archives use the same overlay. Standalone assets
  with no corresponding JB identity retain their standalone source; no counterpart
  is invented. No game folder is built for previewing.
- Loaded roster palettes update confirmed court bindings; manual school association
  handles shared stadium families. Arena mask routing remains unconfirmed.
- Explorer categories support shoes, uniforms, cloth geometry, stadiums, logos,
  players, audio, menus and rosters; category and roster-reference columns sort and
  search. Unknown identities retain hashes and evidence-labelled internal names.
  The known hi_shoe1 container gains a verified internal-record display label.
- Content-addressed DDS/GTF conversion and base-layout normalization caching checks
  input, layout, converter source and Pillow version, validates stored checksums,
  and limits the cache to 512 MiB. Changed/corrupt entries regenerate. The GUI build
  summary lists replacements, resized images, reuse and compatibility problems;
  machine staging metadata remains available to the build validator.

## Text growth and actual text-entry evidence

Strings no longer require the original encoded length or unique shared storage.
Copy-on-write appends a terminated UTF-16LE entry and updates only the selected
signed-relative pointer. Original strings, aliases, table positions and unknown
bytes remain intact. USERDATA length prefixes, type-21 wrappers, decrypted ZIP
members and sole-ROST/single-block IFF lengths rebuild and reparse. Unsupported
multi-block IFF growth is explicitly refused. These are structural checks, not a
claim of gameplay validation. No original roster or executable is overwritten.

Read-only EBOOT callbacks establish **game editor input capacities**, excluding
the terminator: player first/last 16 (0x693F98/0x691ACC, buffer 0x11); School Name
16 (0x6D17F8); Abbreviation 4 (0x6D18FC, buffer 5); Stadium Name 15 (0x6D1A00,
buffer 0x10); Nickname 16 (0x6D1AF4); Student Section 32 (0x6D1CFC, buffer 0x21).
Only the first/last-name mapping is currently enforced as a ROST input cap.
School/arena callbacks operate on temporary C++ strings; exact correspondence to
each serialized ROST text field still needs proof, so those values are not blindly
applied to the roster fields. The text-buffer constructor is 0x7C708C through 0x1E3224; keyboard initialization
0x1D8AAC uses that buffer descriptor. These are not claims that the renderer cannot
display longer authored vanilla strings. Existing longer values are preserved.

Conference and other unmapped text fields have **no invented field-specific cap**;
the UI identifies their engine limit as unresolved. Payload/relative-pointer size
guards still apply. The old arbitrary 256-character parser ceiling is removed.
Do not describe those unresolved limits as fully reverse-engineered.

## New eligibility evidence

Class display 0x68F4D0 dispatches through 0x49DBD4 to 0x1C0054. Initializer
0x1C7248 writes the table: 0–3 HS Freshman/Sophomore/Junior/Senior, 4–7 college
Freshman/Sophomore/Junior/Senior, 8 Graduate. Menu setters establish writable
0–7; Graduate is preserved, not newly assigned. Storage: row +0x94, bits 28–31.

Redshirt display 0x691D7C and controls 0x68F594/0x68F5F0 use row +0x94 bits
26–27. Constructor option table gives None/Normal/Transfer/Medical. A nonzero
selection clears Redshirt Used at row +0x9C bit 30. Used controls
0x68F64C/0x68F518 toggle that bit; setting it clears active Redshirt. Scholarship
bit 31 and weight bits 11–19 remain untouched. Tests cover these coupled effects.

Runtime number formatter 0x4E7C8C treats 100 as **00**; this sentinel exists in
stock data and now displays/edits as 00. NAME/numbers contains ten big-endian
(atlas x, glyph width) u16 pairs. The formatter aligns glyph widths to four pixels
and centers copies into a generated jersey-number texture. Exact references:
atlas 0x4E80EC, generated resource 0x4E8144,
player-number call 0x4E81C0–0x4E81D0. Geometry placement and shader color consumers
are still being traced; authored glyph rendering is not yet exposed as completed.

Further read-only tracing found global.iff's 256×128 jersey-number templates
(the runtime identifier is `jerseynum00` through `jerseynum23`) and its UnAD
`unidata` record. Function 0x4DCD5C uses +0x1C/+0x20 as number centre and
+0x24/+0x28 as number width/height, setting semantic hash 0x1B951FD0 to
(1/width, 1/height, 0.5-centreX/width, 0.5-centreY/height).
The number texture binds `NumberMap` (CRC32 0x7FF175D8) at 0x4E0C80/0x4E3174.
The program still needs the vertex UV and fragment mask/colour route; do not
substitute guessed placement. Embedded `PS_Jersey` Cg program headers were located
for continued read-only RSX analysis using published instruction definitions:
https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/RSX/Program/RSXFragmentProgram.h.

Confidence callbacks 0x69E910/0x69E924 read/write anchor +0x70, row +0x80.
Constructor metadata exposes bounds 35 and 99; source values outside those bounds
are preserved until explicitly edited. Jump-shot getter/setter +0x83 and its 0–111
range were also located; exact option captions remain unimplemented.

Read-only jersey colour tracing: 0x4DC8A0 binds semantic hashes 0x72251300
(`CustomJerseyColor`) and 0xDC165DB5 (`CustomPipingColor`). Its normal team
object path reads anchor +0x170/+0x174, corresponding to palette slots 0/1 with
the confirmed +0x30 team-anchor bias. It unpacks RGB through a lookup table and
normalizes the low byte separately; do not assume the fragment channel masks.
A separate mode calls 0x532C64, which uses getters 0x763DB0/0x763E00 at anchor
+0x1A8/+0x1AC (slots 14/15) and can swap their order based on team selection.
Thus these shader constants reuse both equipment and school primary/secondary
colours in different runtime paths. The enabling mode and fragment routing still
need proof before automatic jersey recolouring is implemented.

## Outstanding work (do not claim complete)

Full roster semantic reverse engineering, independent secondary positions,
remaining school/coach/player records, complete per-field engine text limits,
arena channel-to-palette masks, jersey-number geometry/shading and full menu asset
subrecord links remain unfinished. No secondary position control appears in the
traced localized player bindings; the confirmed position is a whole byte at +0x3B.
Class/Redshirt findings do not justify guessing those other bits. Body shape and
muscle masks are already confirmed; no guessed body geometry is added.

Existing conference-parser reference:
https://github.com/bphit4/CH2k8-Roster-Editor/blob/main/Conference_Parser.py.
Executable evidence is retained privately, read-only; no proprietary bytes/assets
or workstation paths are distributed. NEVER launch RPCS3 or make testing JB copies.

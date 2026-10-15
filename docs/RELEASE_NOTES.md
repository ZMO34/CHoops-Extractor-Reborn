# v1.14.2 — Explorer overrides, references and cache fixes

- Select overrides folder… moved to Explorer; stale fallback badges fixed.
- Explorer follows the selected source and shows its replacement sizes/origins.
  Reference columns are wider, with full-text detail and tooltips. Result-display
  errors are reported safely instead of escaping Qt callbacks.
- Added SELUH/A/X/Y/Z menu ownership plus confirmed cloth, player footwear,
  stadium and paired-CDF references. Loaded roster IDs determine ownership.
- Removed the Dry run GUI button. Build JB copy still validates automatically.
- Retained both source indexes, separate reusable scratch files and a bounded
  64 MiB RGBA cache. Input changes invalidate snapshots; checksum guards remain.
- DDS is preferred within overrides; TXTR is fallback only if no matching DDS.
  SCNE replacements remain supported.
- CSVs whitelist game roster fields and exclude references/UI/research metadata.
  Source hash, identities and original values remain for safe edit import.

Includes v1.14.1 fixes. No input renaming, RPCS3, automatic/testing JB build,
EBOOT edits or alternate assets. Broader reverse-engineering remains ongoing.

# v1.14.2 — override list refresh

Fixes stale JB fallback badges when selecting a new overrides folder while the
override source is already selected. Lists refresh immediately; the active
preview reloads after preparation. The visible Mod workspace determines preview
loading, and the toolbar shows the loaded archive override count. Invalid
workspaces are labelled unavailable instead of misleading fallback badges.
Legacy nested DDS/SCNE names remain supported without bulk renaming.

# v1.14.1 — preview source and asset lists

Fixes NoneType.lower during S258 floor preview by skipping unnamed archive
entries safely. The top toolbar uses one Source JB / Selected overrides dropdown
for all preview categories. Models / Courts has Jerseys, Shoes and Stadiums /
Floors subtabs with pick-only lists and explicit Override / JB fallback labels.
Includes v1.14 functionality. No emulator or automatic JB build.

# v1.14 — direct previews and override selection

Select jerseys, shoes and stadium/floor packages directly from the loaded JB
folder in Models / Courts. No manual IFF opening is required. The source toggle
selects JB or prepared overrides for both mesh and textures. Jersey neck/build,
shorts cut and top/shorts choices remain available. Stadium modes include arena
and floor together, floor only and arena only.

Select overrides folder… replaces staging terminology in the GUI. Existing
workspaces are preserved and a new numbered workspace is selected automatically.
The builder and previews use the successful new selection.

Includes thin optional stock-S256 court alignment guides independent of floor
materials and palettes; correct UTF-16BE roster string fixup, shared descriptor
length protection and advisory keyboard warnings; exact conference-logo editor
routing and raw SingleMoCap inspection/export. Secondary positions are closed
by owner confirmation. Remaining unknown roster bits, smaller engine display
ceilings, reflection/fake-bump/AO and all dynamic runtime modes remain unresolved.
No alternate assets, EBOOT edits, RPCS3 or testing JB builds.

Windows: extract the entire CHoops-Studio-v1.14-windows-x64.zip and run
CHoops-Studio.exe. Keep _internal alongside it. No Python or external texture
converters are needed. Included audio helpers retain sources and licence notices.

# Release notes

## v1.11 — side-panel editing and uniform previews

All categories now use selected-record side tabs. Palette and shoe controls,
shoe previews and direct jersey preview move into appropriate panes. Player School
supports safe move/unassign and one-step undo. Corrected 18-slot roster capacity
and active row-zero handling. School brands apply to that school’s players only,
normalizing incompatible styles/colors atomically. Jersey top and shorts render
together with neck/build/cut/part dropdowns. Edit selected/Team palette/shoe toolbar
actions are removed without losing supported field editing. No assets added.

## v1.10 — roster usability and Windows release

Player table shows feet/inches and PG–C. Always-visible Player/Ratings/Scholarship
tabs replace properties/attributes buttons; scholarship editing preserves weight
and neighboring flags. Equipment uses actual names and styles. Schools replaces
duplicate Teams/Edit Schools views. Shoe/export actions are grouped. Realignment
remains; D1, new alternate/five-jersey/independent-asset actions are removed.
No alternate assets added. EBOOT and inputs remain read-only; no emulator/testing
JB. Full Windows packaging includes LGPL audio helpers, source and notices.

## v1.08 — experimental audio development bundle

Windows GUI plus a portable Python audio-workspace with setup, documented CLI
and open-source ATRAC3 encoder source. Audio runs from Python, not a new GUI tab.

- Catalog maps 23 licensed songs/64 fight songs and shared artist artwork.
- PCM16 WAV export, single/batch stream replacement preparation, known standalone
  AUDO export/replacement and jukebox cover export/replacement CLI commands.
- AUSB offsets/durations rebuilt with untouched-stream checks; source preserved.
- Unchanged WAVs skipped by checksum; invalid sample extents rejected; new
  filenames required. Known inline/split/wrapped AUDO supported. Loop writes blocked.
- Shared Codex prompt, current evidence docs, portable setup/verification, PR
  template and two-account collaboration/independent review protocol.
- Generic synthetic fixtures corrected; truncated texture normalization gets a
  clear error; typed service annotations repaired without behavior changes.

Audio GUI, title editing, full CDF growth and self-contained codec packaging are
unfinished. No EBOOT editing, RPCS3 or testing JB. Python codec/toolchain dependencies
are installed by setup, not distributed as codec DLLs. Encoder source is included
as a separate corresponding-source archive. See AUDIO_WORKFLOW.md/TEST_REPORT.md.

## v1.07 — community roster and shoes

Unchanged bad name characters no longer block unrelated ratings/shoes; invalid
pointers/new corruption remain fatal. Player/team shoe dialogs, save/ZIP wrapper
preservation, roster IFF export and 2D stored-depth compatibility. 135 targeted
checks plus private round trips; no gameplay verification.

## v1.06 — courts and sizing

Single-surface floor preparation with actual bump routing and automatic supported
non-stadium texture normalization. Crash-free court allocation remains unknown.

Prior details remain in Git/GitHub history. Legacy converters are private optional
reference tools, excluded from current packages.

Explorer/workspace update: Select overrides folder… now lives in Explorer,
with source-aware asset sizes and Override/JB labels. Dry run is removed from the
GUI; Build JB copy still performs automatic validation. Roster references cover
home/away/alternate selection menus (SELUA/H/X/Y/Z), gameplay uniform banks,
confirmed cloth geometry, player/team shoes, stadiums, paired CDF payloads and
conference/school logo banks. These links use the loaded roster. The wider
reference column, full-text panel and tooltips preserve long references.
Unsupported display metadata is reported without escaping the Qt result callback.

JB and override indexes remain available together. Source-specific scratch files
are reused while file fingerprints are unchanged; RGBA previews share a bounded
64 MiB content cache. Changed manifests invalidate override snapshots; changed
payloads still undergo source/checksum validation. DDS artwork skips the matching
raw TXTR replacement; TXTR remains the fallback only when no DDS is present.
SCNE replacements remain supported. CSVs use explicit binary-backed field
whitelists: asset references, preview labels, research fields and row offsets are
excluded, while source/stale-edit safety columns are retained.

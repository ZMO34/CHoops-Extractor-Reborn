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

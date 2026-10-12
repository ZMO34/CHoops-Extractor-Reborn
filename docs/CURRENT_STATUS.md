# Current project status

Updated 2026-10-11. Upstream: ZMO34/CHoops-Extractor-Reborn; base: master.
Baseline before this handoff: `e556e360d0091df0bb645da9eb1d279e9d8f9e3a`.
Last published Windows feature release at that baseline: **v1.07**, commit
`bf43d81b10ea2f16bab7df3e798edb64435ab6f4`.
Check GitHub and git history for newer commits/releases; these are provenance,
not a permanently current HEAD assertion.

## Implemented foundation

- Native Python/PySide6 desktop GUI; CLI and GUI share parsers and services.
- Split JB archive browsing, extraction and identity recovery; bounded IFF/CDF,
  H7A compression, tool wrappers, TXTR and SCNE handling.
- Built-in DDS/GTF conversion, recursive override discovery, DDS priority over
  raw TXTRs, replacement SCNE priority, dynamic supported stadium asset sizes.
- Base-layout normalization outside sNNN stadiums; preserve source dimensions,
  format, mip count, remapping and layout. Use vanilla source for vanilla sizes.
- Texture and geometry previews including arena, cloth and shoe selection;
  material texture routing, packed geometry, camera movement and RSX remapping.
  Basic previews do not reproduce every game shader. Artificial floor lift is
  not the solution and must not be reintroduced.
- Roster adapters, editable confirmed fields, ratings, undo/redo, RGB color dialog,
  packed Yes/No and L/R choices, player/team shoe editing and roster IFF export.
- Community ZIP/save wrappers are preserved. Existing unchanged malformed name
  characters are warnings; new corruption or invalid pointers still block writes.
- Explicit alternate-linking/asset-building operations, availability checkboxes,
  optional D1 conversion. No automatic conversion or profile unlock bypass.
- Manual JB staging/building, source hash preconditions and transactional writes.
  Having this feature does not authorize agents to create testing game builds.
- Reusable single-surface court preparation; actual bump semantic and DXT5nm
  routing; only extra **floor** draws disabled. Arena remains normally textured.

## Current audio project

`audio_tools/{codec,banks,workflow}.py`, `formats/audio.py`, and the thin native
ATRAC3 helper source provide an **experimental** backend. Mapping recovered 23
licensed tracks and 64 fight songs in cribmusic. Title/artist/artwork mappings are
data in soundtrack_names.json. WAV decode/re-encode passed a synthetic round trip.
Bank replacement updates AUSB offsets/durations and checks untouched streams.
Workflow and game archive replacement still need broader regression validation.

Experimental catalog/WAV/song/batch/AUDO/jukebox-art CLI commands are exposed;
unchanged manifest WAVs are skipped and sample bounds/export overwrite are checked.
The Audio workspace now uses the shared backend in the Qt studio, with distinct
Licensed Music and Fight Songs tabs, selected/section WAV export, WAV replacement
preparation and shared cover-art actions. The GUI update is under review on top
of the open audio-backend PR; self-contained codec packaging remains pending.

Song-title/artist editing stays read-only because archive-only routing is not
established, and EBOOT writing is prohibited. Unknown AUDO loops and general CDF
audio growth remain unsupported. Users stage outputs and build JB copies manually.
See AUDIO_RESEARCH.md and AUDIO_WORKFLOW.md.

## Priorities for the next instance

1. Continue independent validation of audio metadata identity, conversion limits,
   cancellation and no-overwrite handling. Keep uncertain name fields read-only.
2. Validate standalone/paired/inline AUDO handling and explicitly block unknown
   loop formats or unsupported CDF writes. Do not claim all formats writable.
3. Finish native decoder/encoder release integration with corresponding sources,
   license notices and independent packaged checks. No proprietary codec tools.
4. Continue remaining roster semantics, palettes, shaders and asset-linking
   investigation as separate documented PRs; do not distract from audio validation.

## Remaining uncertainty

- Six team palette words (16, 17, 27–30) have no verified role. 22 exact Edit Schools
  captions plus three additional runtime roles are known; older nine-caption
  requests must not be mistaken for the latest remaining count.
- Complete arena shader-mask routing and authored number/name atlas behavior.
- Alternate/profile unlock behavior and newly inserted asset consumption in game.
- Independent asset IDs/menu-logo handling for decloned classic/all-time teams.
- Commercial shoe style names and exact special-family UI caption.
- Crash-free court texture budget. 4096 is a dimension ceiling, not a tested safe
  allocation. Defaults: court 2048x1024 DXT5; normal 512x512 DXT5, full mips.
- Soundtrack title localization override route, AUDO loop semantics, CDF growth.

## Verification boundary

No emulator tests and no automatic testing JB builds are permitted. v1.07 had
135 targeted Python/Qt checks plus private roster save/reopen and archive checks.
The initial audio commit had syntax checks and 10 existing archive regressions.
The handoff/audio CLI update passed 240 portable tests, source smoke, scoped lint
and mypy. Native WAV re-encode/resample, AUSB preservation and AUDO/header checks
are covered. Read-only stock catalog returned 23 licensed/64 fight/159 total music
bank streams. No game replacement consumption validation. See TEST_REPORT.md for
exact commands; new commits require their own results rather than reused counts.

All game inputs, rosters, templates, private reverse-engineering helpers and raw
audio are local and absent from Git. A fresh PC must supply its own authorized
fixtures. Do not assume a generated court template or any old local build exists.

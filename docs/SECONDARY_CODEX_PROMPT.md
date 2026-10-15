# Master prompt for the secondary Codex instance

You are the secondary development instance for **CHoops Modding Studio**, the
Python/PySide6 PS3 College Hoops 2K8 tool. You run on a different PC, GitHub account
and user session from the primary instance. This document is your portable
startup context; you cannot see the primary session's memory or private files.

Use **https://github.com/ZMO34/CHoops-Extractor-Reborn**, with PR base **master**.
Do not target kima1810/CHoops-Extractor or another historical upstream. It is only
a reference. Authenticate as your own user. Fork the canonical repository if you
lack collaborator access; upstream PRs from your fork are the normal path.

Read AGENTS.md and the current GitHub master version of this prompt before work.
Fetch master and read open PRs/issues/review comments. The snapshot below records
the current foundation; code, tests, current docs and newer PR evidence may
supersede its dated observations. Treat research hypotheses as hypotheses.

## Your operating instructions

1. Choose one bounded task, announce its scope through an issue or draft PR,
   avoid overlapping ownership, and implement a complete reviewable update.
2. **Every update is pushed through a documented feature-branch PR to canonical
   master.** Fixes to the same update continue its PR; unrelated work gets a new
   PR. Do not push directly to master, merge yourself, or publish releases unless
   the repository owner explicitly authorizes it.
3. **Both Codex instances must maintain documentation on every update.** Update
   CURRENT_STATUS, affected format/project/user/CLI docs, TEST_REPORT and changelog
   where appropriate. Regenerate this single-file prompt with
   `python tools/dev/handoff.py`; CI checks it has not drifted.
4. Post handoff comments containing pushed SHA, exact tests/results, limitations,
   unresolved questions and next action. Read and answer review discussion before
   the next push. GitHub is the durable cross-PC communication channel. Never
   assume chat-memory synchronization or silently abandon a blocker.
5. **NEVER open RPCS3, automate it or run emulator/gameplay tests. NEVER create
   full automatic/testing JB folders.** Users build their JB manually. Use Python,
   synthetic fixtures, Qt/source/packaged startup and read-only private input
   inspection. Tiny synthetic archive fixtures are okay; copied game tests are not.
6. Keep JB source, overrides, rosters, templates and EBOOT immutable. EBOOT may be
   read for research but never patched. If jukebox name changes need executable
   edits, do not implement them. v1.10 removes D1/alternate/independent-asset public
   actions. Keep realignment, but do not restore those actions or add alternates
   without an explicit new owner request. Read PLAYER_QOL_RESEARCH.md.
7. Preserve unknown bits/bytes, IDs, record ordering, padding and unaffected
   streams. Reparse written output and compare untouched ranges. Reject ambiguous
   aliases, unknown pointers/layouts, unsafe outputs and invalid data explicitly.
   GUI/CLI share a backend; worker threads never manipulate Qt widgets.
8. No personal info, local paths, tokens, logs, game/music/art assets, proprietary
   converters or generated binaries in public Git. Do not delete old files unless
   their generated ownership/path is proven; never copy primary-PC cleanup targets.
9. Test your exact PR head. The primary instance independently reviews/bug-tests
   your PR in an isolated checkout, posts findings and retests fixes/new commits.
   Do not label your own tests as independent approval or claim game compatibility.

## First actions on your PC

Install Git and Python 3.12 x64 if absent. Clone your fork or canonical repository,
add the canonical upstream remote, then create a feature branch from current
master. Use your GitHub connector or GitHub CLI for PR operations; credentials
remain on your PC. Run:

```powershell
python tools/dev/setup.py
python tools/dev/setup.py --audio-encoder
python tools/dev/verify.py
```

Setup creates a local .venv and installs desktop/test/tooling dependencies. The
optional encoder step obtains pinned LGPL source and builds the helper with Zig.
No Sony codec executable is needed. Existing primary-PC binaries/private tools
are not assumed available. Linux tests need their Qt system runtime libraries.

For audio, first reproduce the backend tests and inspect open audio PRs. Then
finish a shared backend-driven Audio GUI with **separate Licensed Music and Fight
Songs sections**, WAV export/replacement and shared cover-art editing. Keep
title/artist edits disabled until a proven archive-only route exists. Be explicit
about unknown AUDO loops/CDF writes and packaged codec dependencies. Continue
remaining roster/palette/uniform/asset investigations as separate scoped PRs.

The rest of this document embeds the maintained project knowledge so a new
instance can start without the original conversation. Generated from the named
source docs; update those docs, then regenerate rather than editing this output.

---

Embedded source: docs/CURRENT_STATUS.md

# v1.15.4 — faster override-folder preparation

Override selection prepares independent archive groups in separate CPU worker
processes (up to six, capped by cores and available RAM). A memory-weighted queue
keeps heavy archives from overloading the system. Each archive has one writer;
DDS priority, SCNE replacement, cube handling and validation remain unchanged.
Progress shows completed archives and active workers. Cancellation or failure
stops workers before removing partial output; the previous workspace is retained.

Repeat selection reuses validated completed archives from the current prepared
workspace when inputs, source checksums and importer code match. Changed inputs
recompile only their archive; tampered cached output is rejected and regenerated.
Conversion-cache identity is computed once per process and directory pruning is
batched under a cross-process lock, with a final size-maintenance pass.

Measured on 14 supplied scene groups / 612 DDS inputs with warm conversion cache:
Final run: 24.838 s serial, 10.008 s with six workers (2.48x),
6.676 s unchanged repeat. An earlier run measured 3.08x; timings vary with cache
and machine load.
All resulting archive hashes matched. These are preparation-only measurements;
whole-folder timings also include discovery and compatibility checks and vary
with CPU, RAM, storage and cache state. No RPCS3 or automatic/testing JB build.

# v1.15.3 — frontend override import geometry fix

Fixed folder selection aborting with `frontend_sync.iff: Geometry overlaps a
texture image`. Menu SCNEs can store inline geometry in their header block and
textures in a separate block. Image packing now distinguishes inline vertex
stream flag 0x40000002 from GPU stream flag 0x40000003, and header-relative index
flag 0x10 from data-relative 0x20000010. Inline geometry/pointers remain unchanged;
GPU buffers retain relocation and byte-preservation checks. Real overlaps and
out-of-bounds or modified inline geometry still fail closed.

Read-only validation passed all 14 supplied non-stadium SCNE import groups.
The complete portable suite passed 524 tests.

A failed folder import is atomic: it preserves the previous prepared workspace.
That explains the old LSU preview after the failed reselection. Once import
finishes successfully, the live source index and current S258 overrides activate.
No source files, prepared snapshots, EBOOT or JB builds are modified by this fix.


Legacy flat DDS artwork targeting a base cubemap is handled only in recognized
legacy folder imports: it updates the first (+X) face, resampled to the original
format, dimensions and mip chain; the other five faces are retained from source.
The result remains a full cubemap and its descriptor is preserved. The GUI
compatibility summary identifies this operation. Modern manifest-based imports
and direct DDS imports still require matching complete cubemap inputs.

# v1.15.2 — current override files in previews

Folder-based previews now use current loose DDS, SCNE and archive inputs instead
of treating an earlier prepared build snapshot as the selected folder. Only the
requested archive is compiled for preview; unchanged inputs reuse a bounded
64 MiB compiled cache. File changes invalidate materialized and decoded previews.
Missing or incompatible live inputs raise an error rather than showing JB art.
The same source applies to Explorer, texture, jersey, shoe and stadium previews.

Select overrides folder once after upgrading to register live input locations.
Older workspaces and imported patches remain usable prepared snapshots and are
labelled accordingly. New or renamed files require selecting the folder again.
After editing inputs, preview again (or switch sources) to reload. Select the
folder again before building to prepare an updated build snapshot; previews do
not change prepared builds or any original input. JB fallback applies only where
no replacement exists. No emulator, testing JB or EBOOT changes.

# v1.15.1 — resizable full-width 3D preview


## Resizable 3D preview

Models / Courts reserves more height for the full-width preview. Drag the wide
divider above it up or down to enlarge or shrink it. Controls scroll independently
when space is reduced; the main application window can also be resized normally.
Fit camera frames the model after changing the available viewing area.
# v1.15 — Explorer overrides, references and cache fixes

Roster controls explicitly open external roster IFF or decrypted USERDATA/USRDATA
(and supported save ZIPs), load the source JB roster, or load a real override
roster replacement independently of the preview dropdown. Export offers roster
IFF and decrypted USERDATA. An external IFF supplies its own export template;
other inputs use the loaded JB or a chosen IFF template. Save copy preserves the
original wrapper, including other members of a loaded save ZIP. USERDATA export
does not create encryption, PARAM files, or a complete console save package.
All writers validate and reparse the result and protect the original input.

Release: https://github.com/ZMO34/CHoops-Extractor-Reborn/releases/tag/v1.15

Select overrides folder… is in Explorer. The stale-fallback bug is fixed, source
counts and source-aware asset rows are shown, and the visible workspace is used
consistently. Dry run is removed from the GUI; JB builds still validate first.
Confirmed roster ownership includes uniform selection menus, gameplay uniforms,
cloth meshes, player/team footwear, stadiums and paired logo banks. Wider
reference columns have full-text panels/tooltips. CSVs exclude UI/research
fields and retain source/identity/stale-edit safety columns.

Both JB and override indexes are retained. Separate validated scratch copies and
a bounded 64 MiB decoded image cache support switching sources. DDS takes
priority; raw TXTR is used only without a matching DDS. SCNE geometry remains
supported. No user filenames or artwork were changed: the supplied names already
resolved to 1,824 targets. Existing prepared data showed 354 stadium and 727
uniform overrides; no shoe packages were supplied. No RPCS3 or testing JB build.

# v1.14.1 preview source/list hotfix

Release: https://github.com/ZMO34/CHoops-Extractor-Reborn/releases/tag/v1.14.1

Top-toolbar Source JB / Selected overrides dropdown controls all previews.
Models / Courts offers Jerseys, Shoes and Stadiums / Floors subtabs with pick-only
lists, explicit Override / JB fallback labels and retained selections. Missing
archive/scene names are handled safely. Switching sources keeps the active page.
Read-only S258 preview succeeded with unchanged input. 494 portable tests and 22
native GUI/GL checks passed; Windows frozen startup/audio checks passed.
Broader roster/shader research remains incomplete as described below.

# v1.14 release preparation

Direct Models / Courts selectors now preview jerseys, shoes and stadium/floor
packages without first opening an IFF. Captured source/override selection applies
to SCNE and texture data. Jersey shape controls remain available; stadium modes
choose arena+floor, floor only or arena only. Integrates tested PR #14 updates
and the override-folder fix in PR #15; broad reverse-engineering remains ongoing.

# Override-folder selection fix

The GUI action is now Select overrides folder… . Existing mod directories no
longer cause Choose a new mod directory: selection prepares a fresh numbered
workspace, preserving old folders, and updates both build and preview paths
only after successful compatibility checks. Verification: 464 portable tests passed; 26 targeted override checks passed.
Separate PR from the ongoing roster
and shader research (#14); no emulator or automatic JB build.

# Current project status

## Active roster, floor-layer and animation continuation

v1.13 is published from master 9e18f32aed8d0e3f81c2cfb05e0346d8854320b9:
https://github.com/ZMO34/CHoops-Extractor-Reborn/releases/tag/v1.13.
Its Windows package passed Windows/Linux CI and local frozen startup/audio checks.

The next feature branch adds orange advisory keyboard-limit warnings, independent raised
alignment guides from fixed stock S256 court coordinates, safer conference index validation, exact conference-logo editor routing and
read-only motion-record discovery/export. Byte coverage now reports unresolved
bits within packed words. Conference +0x1A is a tournament index, not a logo ID;
its unsafe generic writer is protected. See CONFERENCE_ASSETS.md and
ANIMATION_RESEARCH.md. No secondary-position search: the owner closed that task.

Complete remaining byte semantics, universal engine text ceilings, reflection,
fake-bump/AO and all dynamic palette modes remain unestablished. This continuation
does not claim completion of those research goals or gameplay certification.
No RPCS3, EBOOT edits, added alternates or testing JB folders.

Continuation verification: 482 portable tests passed (9 offscreen GL skips,
2 deselected), 28 native Qt/OpenGL checks passed, plus hidden read-only S256 line
rendering. Compile, CLI/Qt startup, Ruff, mypy and handoff checks passed.


PR #13 combined roster/arena continuation: twelve additional appearance/tattoo/
signature fields with verified inclusive option bounds, all 112 jump-shot labels,
and authored arena vertex-colour/alpha, second-UV lightmaps, glow/flare masks.
461 portable tests passed (9 offscreen GL skips, 2 deselected); 144 native
checks passed. See ROSTER_SEMANTICS.md and ARENA_SHADER_MASKS.md. Complete
remaining roster bytes, per-field engine ceilings
and every runtime shader/palette mode remain unproved; no guessed edits are added.


Authored jersey lettering continuation (PR #13): front/back numbers 0–99/00,
roster-linked or preview-only number choices, and curved Reborn surname rendering
use actual indexed fonts/metrics and placement. Declared material DiffuseColor
and integer shader switches are fixed. Palette 16/17 runtime-copy roles are
confirmed. Full roster semantics and remaining arena mask routes
remain under research. No guessed writers, EBOOT edits, RPCS3 or testing JB.
Verification: 448 passed, 4 offscreen-OpenGL skips, 2 deselected; native hidden
OpenGL checks separately passed. Source startup, CLI, lint/type checks passed.
The PR #13 continuation was published in v1.13; the active next branch above is unreleased.


## Roster / preview continuation

v1.12 is published from merged PR #12. Continuation source fixes worker source
snapshots and named SCNE identity, comparison reference matching, school-filter
reset and menu-logo subrecord references. Confirmed Edit Schools text capacities
are mapped to roster fields, and the jump-shot animation ID is editable with
confirmed bounds. See ROSTER_SCALE_AND_PREVIEWS.md for evidence and unfinished
semantics. This continuation is not a published release.
Combined with merged PR #11: 341 tests passed, 2 deselected; source/Qt startup,
lint/type and documentation checks passed. No RPCS3, EBOOT edits or testing JB.
## Latest release and single-slice integration

v1.12 publishes merged PR #12 at master 4f0eec7f95f9d624ff0fe09b4aac489ba4cf058e.
Windows ZIP and SHA256SUMS: https://github.com/ZMO34/CHoops-Extractor-Reborn/releases/tag/v1.12.
Exact-head Windows/Linux CI and local packaged startup/audio checks passed.
PR #11 is integrated with that source and independently tested: 329 passed,
1 isolated native-audio skip, 2 deselected. Depth-one, non-cubemap 3D TXTRs
support 2D DDS replacement while retaining their original descriptor; deeper
volumes remain unsupported. See TEST_REPORT.md for exact review evidence.

## Active roster scale / preview project

The feature branch adds source-bound CSV editing, selective comparison, atomic
ratings paste, inline rating boxes, school filtering, Class/Redshirt controls,
growing UTF-16 text, shared source/override SCNE and texture previews, archive
categories/references and bounded conversion/normalization caching. This remains
a continuing research project; its implemented checkpoint is published in v1.12,
while full reverse engineering remains unfinished.
See ROSTER_SCALE_AND_PREVIEWS.md for exact behavior, evidence and remaining work.
Development verification on 2026-10-13: 326 tests passed, 2 deselected; source/Qt
startup, lint/type and generated handoff checks passed. No testing JB or gameplay.
Merged checkpoint: https://github.com/ZMO34/CHoops-Extractor-Reborn/pull/12.
Jersey colour constants now trace to slots 0/1 and a separate mode using 14/15;
fragment routing and mode selection remain unfinished.
Recent functional PRs were merged before work; baseline is v1.11/master
7796fcbd72c127730f484c67a5b0de26440ed066.

## v1.11 side-panel update

Every roster category has a right-side editor. School palettes, shoes and jersey
previews are in appropriate side tabs; Edit selected/Team palette/shoe toolbar
actions are removed. Player School supports guarded move/unassign; all 18 slots
and counts are handled, with active player row zero correctly represented.
School brand application updates that school’s players only in one undo step.
Jersey preview combines top/shorts and offers neck/build/cut dropdowns. No alternate
assets created. See ROSTER_SIDE_PANELS.md; it supersedes historical 16-slot claims.

## v1.10 roster usability update

Current public GUI combines Teams/Edit Schools as Schools, displays player height
in feet/inches and positions as PG–C, and keeps Player/Ratings/Scholarship details
beside the player table. Scholarship/Walk-on is writable through a verified flag,
preserving weight and unknown bits. Separate properties/attributes dialogs and
D1/alternate/independent-asset actions are removed from the release surface;
conference realignment remains. No alternate work is authorized in this update.
See PLAYER_QOL_RESEARCH.md; older feature descriptions below record historical
backend capabilities rather than removed public actions.

Updated 2026-10-13. Upstream: ZMO34/CHoops-Extractor-Reborn; base: master.
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
- DDS replacement accepts depth-one 3D TXTR descriptors as single-slice images,
  preserving their descriptor; deeper volumes remain read-only.
- Texture and geometry previews including arena, cloth and shoe selection;
  material texture routing, packed geometry, camera movement and RSX remapping.
  Basic previews do not reproduce every game shader. Artificial floor lift is
  not the solution and must not be reintroduced.
- Roster adapters, editable confirmed fields and conference history records,
  ratings, undo/redo, RGB color dialog,
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
preparation and shared cover-art actions. Independent review fixes scene/shoe
navigation to Models/Courts by name, removes a clean-clone test dependency on
proprietary converters, and makes batch WAV export transactional. See PR #5 for
integration/review status. The `codex/audio-codec-packaging` branch adds a
restricted LGPL FFmpeg CLI and the ATRAC3 encoder to the standalone Windows GUI,
with matching source archives and notices. Exact-head Windows CI built both
helpers, packaged the GUI, and passed the frozen synthetic WAV round trip on
`e149790005fdaeb14d0a1b79689d0a3de3b8f2da` (run 54). This is CI-verified branch
work, not yet a published release. Follow-up fixes the ATRAC helper's PCM input
ceiling to ±4.0, aligned with its internal 1/4 scaling, for over-range float WAVs.
Licensed Music and Fight Songs replacements are also trimmed or silence-padded
to the selected track's catalog sample length before archive rebuilding.

Song-title/artist editing stays read-only because archive-only routing is not
established, and EBOOT writing is prohibited. Unknown AUDO loops and general CDF
audio growth remain unsupported. Users stage outputs and build JB copies manually.
See AUDIO_RESEARCH.md and AUDIO_WORKFLOW.md.

## Priorities for the next instance

1. Review and publish the CI-verified LGPL-only Windows audio-helper package,
   including corresponding sources, notices and packaged WAV round trips.
2. Continue independent validation of audio metadata identity, conversion
   limits, cancellation and no-overwrite handling. Keep uncertain name fields
   read-only. Reject non-WAV replacement sources before codec conversion.
3. Validate standalone/paired/inline AUDO handling and explicitly block unknown
   loop formats or unsupported CDF writes. Do not claim all formats writable.
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
The LGPL-helper packaging branch passed the Windows build and packaged audio
round trip on `e149790005fdaeb14d0a1b79689d0a3de3b8f2da`; see TEST_REPORT.md.

All game inputs, rosters, templates, private reverse-engineering helpers and raw
audio are local and absent from Git. A fresh PC must supply its own authorized
fixtures. Do not assume a generated court template or any old local build exists.

Additional appearance/tattoo/post/free-throw fields and all 112 jump-shot captions are now supported; see ROSTER_SEMANTICS.md. Arena vertex-colour/alpha, lightmap, glow and flare routing is implemented; see ARENA_SHADER_MASKS.md for evidence and remaining runtime effects.

Text edits now grow beyond old allocations and keyboard entry capacities. The UI separates advisory game-keyboard sizes from unproved engine ceilings; structural pointer/UTF-16/adapter guards still apply.

ROST string fixup 77FB1C computes field + signed delta - 1; 7C5818
consumes big-endian wide characters. The previous shifted LE view only happened
to work for ASCII. Copy-on-write now preserves non-Latin text and aligned targets.
The shared formatter count is limited to 65,535 UTF-16 units; smaller display
ceilings remain unresolved. Qt's unrelated 32,767-character cap is removed.

Preview source/list hotfix: the top toolbar dropdown selects Source JB or Selected
overrides for every preview category. Models / Courts has Jerseys, Shoes and
Stadiums / Floors subtabs with pick-only asset lists, preventing typed unmatched
filenames. Override mode labels replaced assets and JB fallbacks explicitly.
Unnamed archive entries no longer break stock court-reference lookup.
v1.14 is published from 2158df982f43ba3dbb1e2df1cfcd2030fb0a25ea;
this follow-up targets the reported missing-name error and source-list UX.

Override-source refresh fix: selecting another overrides folder while Selected
overrides is already active now refreshes asset lists immediately and reloads
the active preview after preparation. Preview loading uses the visible Mod
workspace field, not an older cached path. The toolbar shows the loaded override
count; an unavailable workspace is not mislabelled as JB fallback. Existing
legacy DDS/SCNE folder names remain supported; no bulk rename is required.

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

---

Embedded source: docs/ROSTER_SCALE_AND_PREVIEWS.md

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
Copy-on-write appends a terminated UTF-16BE entry (stored delta includes +1) and updates only the selected
signed-relative pointer. Original strings, aliases, table positions and unknown
bytes remain intact. USERDATA length prefixes, type-21 wrappers, decrypted ZIP
members and sole-ROST/single-block IFF lengths rebuild and reparse. Unsupported
multi-block IFF growth is explicitly refused. These are structural checks, not a
claim of gameplay validation. No original roster or executable is overwritten.

Read-only EBOOT callbacks establish **game editor input capacities**, excluding
the terminator: player first/last 16 (0x693F98/0x691ACC, buffer 0x11); School Name
16 (0x6D17F8); Abbreviation 4 (0x6D18FC, buffer 5); Stadium Name 15 (0x6D1A00,
buffer 0x10); Nickname 16 (0x6D1AF4); Student Section 32 (0x6D1CFC, buffer 0x21).
The Edit Schools save path now connects those temporary strings to serialized
fields: 0x6D09FC–0x6D0E5C writes team anchor +0/+8 (short/school name), +4
(abbreviation), +0xC (plural mascot), +0x16C (event name) and +0x168 (student
section). The team anchor bias is +0x30. Keyboard capacities are advisory, not engine storage caps:
16/16/4/16/64/32 UTF-16 units. Stadium-name temporary string 0x3140(r2) loads
from arena anchor +0 at 0x6D605C, matching arena row +0x18; its entry cap is 15.
Text storage may grow beyond those keyboard capacities; unknown engine ceilings are not guessed. Singular mascot,
conference and coach names are not assigned guessed caps.
The text-buffer constructor is 0x7C708C through 0x1E3224; keyboard initialization
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

Confidence callbacks 0x69E910/0x69E924 read/write anchor +0x70, row +0x80.
Constructor metadata exposes bounds 35 and 99; source values outside those bounds
are preserved until explicitly edited. Jump-shot getter/setter +0x83 and its 0–111
range were also located. The side panel now edits that animation ID with a
bounded dropdown; exact localized animation captions remain unresolved.

Continuation fixes: preview workers receive a source snapshot without reading Qt
controls. Unique SCNE names survive archive record reordering; missing names are
refused. Duplicate rest-pose records retain their explicit index and are not
assigned invented identities. Comparison maps conference references by unique
conference identity and excludes unnamed records. New rosters reset school
filters/preview association to avoid carrying a previous roster's school index.
Explorer nested records expose exact `teamselectlogo.iff/logoNNN` school links;
stadium references follow the arena pointer/code rather than guessing from a
school's asset ID. Other menu-bank subrecord routes remain under research.

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

Full roster semantic reverse engineering,
remaining school/coach/player records, complete per-field engine text limits,
arena channel-to-palette masks, complete jersey lighting and full menu asset
subrecord links remain unfinished. No secondary position control appears in the
traced localized player bindings; the confirmed position is a whole byte at +0x3B.
Class/Redshirt findings do not justify guessing those other bits. Body shape and
muscle masks are already confirmed; no guessed body geometry is added.

Existing conference-parser reference:
https://github.com/bphit4/CH2k8-Roster-Editor/blob/main/Conference_Parser.py.
Executable evidence is retained privately, read-only; no proprietary bytes/assets
or workstation paths are distributed. NEVER launch RPCS3 or make testing JB copies.

## Authored jersey lettering (PR #13 continuation)

The Jersey side panel supports every preview number 0–99 and **00**. A selected
player can follow the roster number or use a preview-only number; neither preview
numbers nor the requested **Reborn** surname alter roster data. Source/override
selection applies to glyph artwork as well as cloth/texture records.

Font TXTRs jersey_numbers/names use indexed L8, remap 0x5500, and a 256-entry
ARGB palette after the four-byte-aligned mip payload. The remap forces GPU ones;
CPU path 0x7A87B4/0x79F33C uses the palette instead. Preview decoding preserves
that authored RGBA and rejects missing palettes rather than using a system font.
NAME/numbers holds ten BE (x,width) u16 pairs; aligned copies/advances reproduce
0x4E7C8C, including sentinel 100 -> 00. Global jerseynum00 supplies the template.
UnAD/unidata +1C..28 places front numbers and +2C..38 places back numbers;
**the latter is not a surname transform**. 0x4DCD5C sets their reciprocal-extent
UV transforms; NumberMap is CRC32 0x7FF175D8.

Surname consumer 0x4E7F0C calls 0x520898. 0x520740 maps apostrophe/hyphen to
indices 0/1 and A–Z/a–z to 2–27; spaces advance without copying. NAME/names
metrics and 0x5207B8/0x520898 supply aligned spacing and centering. Global
jerseyname00 supplies the template (stock 256×32). UnAD +08..18 supplies the
polar horizontal/vertical centre, radius, angular width and radial scale.
The preview renders Reborn with authored uppercase glyphs and curved placement.
GLSL atan/length evaluates the polar transform rather than reproducing the
game's half-precision atan approximation; full cloth/lighting is not simulated.
RSX instruction definitions used for read-only interpretation:
https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/RSX/Program/RSXFragmentProgram.h.

Explicit glUniform1i corrects Qt scalar overloads for sampler/bool uniforms;
rendered-pixel tests cover front/back numbers, names and palette switches.
Supported material DiffuseColor is read at the shader-declared CPU offset;
confirmed court palette edits replace it. Arena channels are not assigned
unproven palette roles. Edit Schools save 0x6D0CC0..0x6D0CD0 copies slots 14/15
to 16/17; these are labelled school primary/secondary runtime copies. Slots
27–30 remain unresolved, not writable guesses. Secondary positions are closed by owner confirmation.

Additional appearance/tattoo/post/free-throw fields and all 112 jump-shot captions are now supported; see ROSTER_SEMANTICS.md. Arena vertex-colour/alpha, lightmap, glow and flare routing is implemented; see ARENA_SHADER_MASKS.md for evidence and remaining runtime effects.

Keyboard limits no longer block external edits. Dynamic text uses copy-on-write UTF-16 storage, NUL/control-character checks, signed-relative-pointer bounds and the adapter’s 60 MiB safety guard. That guard is a tool limit, not a claimed engine maximum; gameplay compatibility of arbitrary long names remains unverified.

Secondary-position search is closed by owner confirmation; only the primary position is exposed. See CONFERENCE_ASSETS.md for current index/logo behavior and tournament-link protection.

CSV boundary: both editable and per-table exports whitelist actual roster fields. Asset references, UI/source badges, research notes and row offsets do not enter CSV data. Editable CSV retains source SHA, table/index/slot identity and original values for safe import.

---

Embedded source: docs/ROSTER_SEMANTICS.md

# Roster semantic evidence and supported edits

## Appearance and signature controls

Read-only executable registration metadata links localized captions, paired
getters/setters, maximum option indices and caption arrays. +0x34 is the maximum
**index**, not the number of entries: adjacent array addresses corroborate the
inclusive last option (Bald, Red, Beard Style 6, Sideburns 3, Tattoo 12, Strong,
Freethrow 23 and Bigs 19). Unknown source codes remain unchanged until edited.
No new assets or executable modifications are required.

| Field | Raw player offset | Bits | Writable options | Getter |
|---|---|---|---|---|
| Hairstyle | 0x8C u32 | 7..12 | 0..36 | 0x69ED94 |
| Hair colour | 0x90 u32 | 13..15 | 0..4 | 0x69EF54 |
| Beard | 0x90 u32 | 21..23 | 0..6 | 0x69EE94 |
| Sideburns | 0x90 u16 | 0..1 | 0..3 | 0x69EF14 |
| Left shoulder tattoo | 0x84 u32 | 17..20 | 0..12 | 0x69E9DC |
| Right shoulder tattoo | 0x84 u32 | 13..16 | 0..12 | 0x69EA1C |
| Left biceps tattoo | 0x84 u32 | 9..12 | 0..12 | 0x69EA5C |
| Right biceps tattoo | 0x84 u32 | 5..8 | 0..12 | 0x69EA9C |
| Left forearm tattoo | 0x84 u32 | 1..4 | 0..12 | 0x69EADC |
| Right forearm tattoo | 0x88 u32 | 28..31 | 0..12 | 0x69EB1C |
| Post animation | 0x84 u32 | 21..25 | 0..7 | 0x69E99C |
| Free-throw animation | 0x84 u32 | 26..31 | 0..21 | 0x69E960 |

Jump shots at 0x83 now use all 112 exact game labels (Generic, Athletic, Guards,
Bigs); writable IDs remain 0..111. Free-throw captions deliberately skip 16,
as the game's table does. Tattoos and signature animations share packed words;
mask-preservation/undo tests guard every neighbouring field. Existing body build,
muscle tone, complexion, equipment, scholarship, class and redshirt controls remain.
All new scalars automatically participate in source-bound CSV and selective
comparison through the shared backend. No personal input data is included.

## Position and text evidence boundary

0x69DAA8/0x69DABC read/write the complete position byte at raw +0x3B. Adjacent
+0x3C begins scaled shooting ratings, not a secondary position. The localized
player bindings contain one Position control. This establishes the supported
primary field. The owner confirmed that secondary positions do not exist; that
search is closed and no secondary-position writer is supplied.

Confirmed text-entry capacities and copy-on-write growth are described in
ROSTER_SCALE_AND_PREVIEWS.md. Entry-buffer capacities are not a universal renderer
ceiling. Fields without confirmed engine limits are not capped to the old string
allocation. Complete semantics for every remaining byte are not claimed.

Keyboard-entry limits are displayed as advisory values rather than enforced as engine ceilings. External text edits grow the string heap safely; the tool does not claim a universal game rendering limit.

## Shared formatter representation ceiling

Read-only tracing establishes an upper representation bound of **65,535 UTF-16
units**, excluding NUL, for the common text-argument descriptor. Conference name
formatter 0x73FF00 calls 0x49E1B4 → 0x1E1610 → 0x1E2634. The latter obtains a
unit count via 0x11DF0 → 0x7C5818 (lhz until NUL, pointer difference divided by
two) and stores it with `sth` at descriptor +0xA. Serializer 0x1E1C00/0x1E1C4C
retains that u16. A count of 65,536 wraps to zero rather than retaining the text.

The shared backend therefore blocks larger new text values, including CSV and
comparison edits, with no mutation. This bound is separate from the adapter's
file-size guard and each keyboard buffer. It does not prove that every menu can
display 65,535 units, or establish smaller field-specific/combined-name limits.
Qt's default QLineEdit limit of 32,767 is removed so it cannot silently truncate
text before backend validation. Existing unchanged source values stay preserved.

## Current conference and coverage continuation

See CONFERENCE_ASSETS.md for the exact conference-logo route and newly traced
tournament index. Research coverage records `known_bit_mask` and
`unresolved_bit_mask` for every row byte, including packed player properties and
shoes. Fully known bytes, partially known bytes and known bit counts are separate;
unknown bits remain protected. Structural pointer classification is not proof of
all history/legacy meaning. Roster text dialogs show a live orange border beyond
confirmed game keyboard limits, measured in UTF-16 units. The warning does not
truncate text or impose an invented engine limit.

---

Embedded source: docs/ARENA_SHADER_MASKS.md

# Arena shader colour and alpha routing

The stadium SCNE contains embedded Cg programs; it is unnecessary to modify EBOOT
or load a complete game to inspect these shader families. The sampled source
programs establish these operations (RGBA multiplication, not guessed school
colours):

| SCNE shader hash | Embedded fragment program | Static preview |
|---|---|---|
| 0x9BF5D4AE | BasePrelitPixelShader | Diffuse × vertex RGBA |
| 0x9BF5D4AE | BaseLightmapPixelShader | Diffuse × vertex RGBA × lightmap RGBA |
| 0xAD91D4DE | GlowSignsPixelShader | RGB = diffuse RGB × vertex RGB × (1 + diffuse alpha); alpha = vertex alpha |
| 0xB3DC3294 | LightFlarePixelShader | RGB = diffuse RGB × vertex RGB; alpha = diffuse alpha |

Float4 COLOR declarations (usage 3) are preserved including HDR values. The
second signed-normalized TEXCOORD channel (usage 9) supplies lightmap coordinates;
base UVs are not reused when the second declaration is present. For the verified
prelit family, sampler 0xAB0D0064 is a lightmap, **not a normal map**. Other shader
families do not acquire that role merely by having the same sampler hash.
Material CPU offsets still select DiffuseColor; confirmed court palette uniforms
continue to follow loaded roster/selected school state. Prelit materials do not
receive a second artificial directional-light multiplier.

Source/selected overrides supply SCNE and all sampled texture records through the
same snapshot. Single archives remain usable. Tests verify declared attribute
bounds and actual rendered lightmap/colour/alpha pixels. Hidden read-only S256
inspection rendered 119 supported parts and 180 lightmapped batches without
shader errors. No RPCS3 or testing JB was involved.

This is static preview support. Reflection/environment lighting, full fake-bump
lighting, screen-space AO, dynamic arena illumination, cloth and every runtime
palette mode are not reproduced. Palette slots 24–26 must not be assigned to
seating from colour similarity: Edit Schools also includes cheerleader colours.
Unproved channel-to-roster links remain unassigned. Complete GPU/game shader
emulation and full roster reverse engineering are not claimed.

## Floor alignment guides

The optional 3-point and out-of-bounds guides are for positioning one-texture
court artwork only. They copy the verified line draw coordinates from the fixed
stock S256 floor, raised by 1 game unit. Guide depth bias is ordered above the existing coplanar floor passes.
The guide shader is flat amber and
independent of roster palettes, floor layout, texture overrides and lighting.
The floor itself keeps every original draw and its confirmed material/palette
behavior. Toggling guides never removes actual court markings. No bounds-based
apron geometry is invented; without the stock reference guides are unavailable.
These controls change no SCNE, roster or build data and retain the camera.

Reference guide width uses the central 10% of the authored strip UV: U across both 3-point and boundary strips. This thins guides without moving their centerlines or modifying floor geometry.

---

Embedded source: docs/CONFERENCE_ASSETS.md

# Conference assignment, logos and tournament evidence

School → References → Conference shows the name and numeric index. Double-click
to choose an existing conference. This updates the school pointer, both member
arrays and their counts together, reparses and validates every reciprocal link,
and provides one undo step. Negative, out-of-range and Boolean indices are
rejected without changing bytes. Conference row ordering is preserved.

Conference → Logo → Edit / preview conference logo opens its exact
`teamselectlogo.iff` record in the texture editor. Use Import edited DDS to assign
different artwork, save a new paired bank, then stage that folder for your manual
JB build. The source/overrides preview selector controls the opened bank. This
changes artwork in the existing asset, without changing the conference identity
or adding executable/asset entries.

Read-only executable evidence: menu helper 0x6A0734 reads the selected conference
through 0x6A0668, adds 900 and calls the 0x4A1294 thunk to 0x7FD80. That formatter
uses `logo%3d` (TOC 0xA54AC8 − 0x6D28). 0x6E7120 repeats the same routing. Stock
records `logo900` through `logo938` corroborate the 39 conference indices. Higher
indices are not assigned speculative logo names. Explorer subrecord references
now include conference owners as well as schools.

Do not confuse this with conference raw +0x1A. Getter 0x73D808 resolves the
conference through 0x4A1FF4 → 0x1BD9E0 and loads that u16. Its consumers include
0x65A1E8 → 0x58F74C and 0x73D840 → 0x58C420, indexing a 97-entry tournament
table with stride 0xAC. The legacy `presentation_id` read key is retained for
compatibility, but its displayed label is corrected to Tournament index and
editing is protected until tournament backlinks have a validated writer.

These traces establish asset naming and structural assignment behavior. They do
not certify gameplay or establish full tournament/history semantics. No RPCS3,
EBOOT changes or automatic/testing JB folders are involved.

---

Embedded source: docs/ANIMATION_RESEARCH.md

# Motion-capture extraction research

Stock embedded NAME metadata identifies record hash 0x60900D71 as `SingleMoCap`.
Located banks include crowd, gumbel, kellogg, playercreate, gameintro_cameras,
gamedata and global. These are mixed banks: discovering clips does not mean every
record in the bank is an animation. Explorer adds an Animation banks category for
the confirmed focused banks; unknown filenames may retain researched internal
labels. The standard IFF type fallback now recognizes SingleMoCap even without
an appended NAME table.

Use these commands on an extracted standard IFF:

```powershell
python -m choops_py.cli inspect-animations bank.iff output/temp/motion_inspection
python -m choops_py.cli export-animations bank.iff output/rips/motion_records
```

Inspection reports clip identities and decoded block sizes. Export extracts only
SingleMoCap records, decompresses their containing blocks, and retains each
record's exact byte span. The manifest explicitly says skeletal tracks have not
been decoded. A record with conflicting hash and embedded type name is rejected.
Original inputs remain immutable; no animation writer or FBX/BVH conversion is
claimed.

Initial motion blocks contain a compact header followed by packed streams; two
examined gumbel clips had different lengths but a common header structure. Bone
identity, frame timing, quantization, channel tables and keyframe decoding remain
under investigation. Do not infer a frame rate from a plausible float alone.
Stadium CDAN records describe crowd placement candidates and are not relabeled
as skeletal clips. Further extraction is currently lossless raw-block extraction.

Further read-only inspection located 319 SingleMoCap records in the sampled
standard-bank inventory. Candidate count/duration header relationships differ
between presentation and crowd clips; mirrored entries can be only 64 bytes.
Therefore a guessed universal frame rate or stand-alone BVH decoder is not
exposed. Clip dependency/alias resolution must precede skeletal export.

---

Embedded source: docs/ROSTER_SIDE_PANELS.md

# Selected-record side panels (v1.11)

Select one row in Players, Schools, Arenas, Coaches, Conferences or Uniforms.
The right pane changes to that category. Double-click a writable detail; references
use named selectors and existing validated model writers. Read-only metadata
remains marked. The Edit selected, Team palette and separate shoe toolbar actions
are removed. Existing save, export, undo/redo and known field editing remain.

Schools have School, References, Players, Palette, Shoes and Jersey tabs. Palette
opens the RGB/alpha picker directly from its swatches. References include safe
reciprocal conference realignment. Players exposes all **18** roster slots, with
count updates and guarded transfer/reordering. Coaches/Arenas/Conferences expose
their supported strings/scalars; Conferences also lists member schools. Uniforms
expose their existing writable selectors/shapes and a jersey preview tab.

## Player school assignment

The player School tab shows current ownership and allows move/unassign. The game
uses a team player array at runtime anchor +0x3C and a count at +0x158, corresponding
to editor row +0x6C and +0x188. Removal routine 0x7644B8 walks that array; assignment
routine 0x764548 onward checks capacity, appends a player and increments the count.
The mapped file pointers use player row +0x11 and signed self-relative deltas.

The stock data confirms 18 contiguous pointer slots, including the previously
hidden final members of 17/18-player schools. All 443 stock arrays agree with
their counts. Player row zero is a real Charlotte member, not always an empty
sentinel: an active slot may name it, while row-zero references beyond the active
count are empty. The reader now makes that distinction.

Transfers update source/destination arrays and counts in one undoable transaction.
Player attributes and current footwear remain unchanged. Full destinations,
duplicate/shared player records, invalid pointers and inconsistent/unmapped counts
are blocked with no partial change. Roster-slot editing uses the same guarded
membership writer; choosing an existing teammate swaps positions, removing a
member compacts slots, and incoming players transfer safely. Legacy recruitment,
eligibility and scholarship limits are not reproduced; gameplay is unverified.

Whole-table JSON exports now contain 18 slots. Refresh older 16-slot exports before
applying them; guessing omitted players or silently deleting row zero is unsafe.
Individual edit patches remain supported through the guarded writer.

## Shoes

Player and School Shoes tabs contain brand/style/home/away controls and a direct
preview button. Player edits affect that player record. Applying school shoes
automatically applies its brand to **that school’s roster only**, as requested.
Compatible player styles/colors remain; incompatible values use the first valid
choice for the new brand. School style/color defaults do not overwrite compatible
individual artwork choices. Shared player records block scoped propagation.
The school/default/player updates form one undo step and preserve unrelated bits.

## Jersey preview

Player, School and Uniform side panes offer direct Jersey preview of linked,
existing artwork. Models/Courts then shows neck, jersey build, shorts cut and
Top + shorts / Top only / Shorts only dropdowns. Neck choices are U, V, V triangle,
Triangle and Wishbone; available cloth bodies/cuts are Thin, Regular and Fat.
Existing top/short meshes are combined in their original coordinates and their
texture roles are routed independently. No artificial repositioning is applied.
These dropdowns affect the preview, not saved roster shapes. Static cloth preview
does not reproduce skinning, cloth simulation, player body or runtime name/number
overlays. Opening another JB clears prior preview context. No assets are added.

Stock verification used read-only source inputs: row-zero transfer/undo, scoped
brand propagation/undo and actual combined jersey+shorts geometry. Synthetic
tests cover guarded writes, field editing, palettes, references and texture roles.
No RPCS3, EBOOT writes or automatic testing JB is involved.

---

Embedded source: docs/PLAYER_QOL_RESEARCH.md

# Player editing and scholarship evidence (v1.10)

The v1.10 editor shows player details without a separate properties/attributes
button. Player, Ratings and Scholarship tabs share the existing validated model,
undo/redo and save-copy/export services. Names retain equal encoded lengths.

Height stays an integer byte at player row +0x3A and sorts numerically; only its
presentation/input changes to feet/inches. Position stays the whole byte +0x3B,
using 0 PG, 1 SG, 2 SF, 3 PF, 4 C. Edit-player getter/setter 0x69DAA8/0x69DABC
read/write anchor +0x2B; the runtime getter 0x753104 reads the same byte. All 5,685
stock player values fall in that five-value set. It is a single confirmed position
field, not two packed primary/secondary nibbles. No independent secondary field
has been established; the editor does not expose a guessed second position.

## Scholarship / walk-on

The localized Scholarship control (English key 0x360FDA01) is registered in the
edit-player constructor at 0x6971FC, with callback 0x68FE40. That callback toggles
bit 31 of a big-endian word at player anchor +0x8C, equivalent to model row +0x9C.
The name formatter at 0x69F30C tests the same signed word. Its nonnegative branch
at 0x69F3E4 uses suffix key 0xDEBE7B99 (walk-on); the negative branch uses the empty
suffix key 0x3729608D. Thus **bit 1 = Scholarship; bit 0 = Walk-on**.

The stock roster contains 5,166 set flags and 519 clear flags. These counts are
cross-checks, not format requirements. The editor masks only 0x80000000 and preserves
weight (bits 11–19) and all neighboring data. Tests check exact payload changes,
undo/redo and visible selection continuity. Recruiting-menu eligibility callback
0x68F974 has roster/context restrictions; this offline editor changes roster data
and does not claim to reproduce those Legacy restrictions or validate gameplay.

## Equipment and readable values

One-bit data uses established captions: hand L/R, muscle tone Buff/Ripped, sock
colors Black/White. Equipment bands/pads are multi-valued, so treating all codes
as booleans would be incorrect. Localized option arrays supply None, White Pad,
Black Pad, team-color variants and other styles for the established packed getters.
Unconfirmed left-arm styles remain read-only and display None/Style rather than
an invented semantic label. Confidence, potential, ratings and tendencies remain
numeric quantities. Unknown source enum values are preserved unless edited.

## Scope removal

Schools combines the former Teams/Edit Schools views. Realignment remains a
reciprocal conference-membership action without a conversion checkbox. Player
properties/attributes buttons, D1 conversion, alternate availability/creation,
five-jersey builds and independent-asset buttons are absent. Public CLI commands
for new alternate/archive insertion are no longer registered. Lower-level research
code/history is retained; no alternate assets are created or added in this update.

Executable/stock inputs were inspected read-only and are not distributed. EBOOT
is not modified. No emulator or automatic testing JB is used for this release.

---

Embedded source: docs/COLLABORATION.md

# Two-PC Codex collaboration

Canonical repository: https://github.com/ZMO34/CHoops-Extractor-Reborn.
All PRs target **master in that repository**, even when development happens in
another account's fork. The original CHoops-Extractor repository is a research
reference, not this project's PR destination.

## Start and coordinate

Read AGENTS.md, CURRENT_STATUS.md, SECONDARY_CODEX_PROMPT.md and this document.
Fetch upstream master; read open PRs, review comments and relevant issues. A
feature branch owns one bounded task. Announce the scope in its issue or draft
PR, identify overlapping work, and resolve overlap before editing the same area.
Do not infer the other instance's state from a stale checkout. Sessions exchange
information through GitHub, not local memory, paths, or private chat tools.

If the second account has write permission, use an upstream feature branch.
Otherwise fork the repository using that account and keep these remotes:

```powershell
git clone https://github.com/YOUR_ACCOUNT/CHoops-Extractor-Reborn.git
cd CHoops-Extractor-Reborn
git remote add upstream https://github.com/ZMO34/CHoops-Extractor-Reborn.git
git fetch upstream
git switch -c codex/audio-gui upstream/master
```

Use a different descriptive branch name for each task. With direct access,
`origin` can be the canonical repository; use `origin/master` as the start point.
Authenticate with the second person's own account through their GitHub connector
or `gh auth login`. Never copy another user's credentials. A fork needs no
collaborator invitation to submit a public PR. Read the GitHub account/remotes
before making writes.

## Publish every update

Each completed, reviewable update must be committed, documented, tested and pushed
as a PR. Intermediate commits may stay on the same open draft PR. Update its
description and post a concise handoff comment after each pushed update: commit
SHA, changes, exact commands/results, unresolved questions and next action.
Use separate PRs for independent work. Do not silently merge or change master.

Before publishing, update CURRENT_STATUS.md and the affected evidence/user docs.
Describe the **final** behavior, confidence, compatibility risks and outstanding
work. Keep personal file paths, fingerprints and fixture reports private. No
copied game artwork, songs, executable bytes or proprietary converters in Git.

```powershell
git diff --check
git add <explicit files>
git commit -m "Describe the completed change"
git push -u origin codex/audio-gui
gh pr create --repo ZMO34/CHoops-Extractor-Reborn --base master `
  --head YOUR_ACCOUNT:codex/audio-gui --body-file PR_BODY.md
```

Write the complete body to a temporary local file, preserving newlines. Use the
repository template and remove private paths. When a Codex PR attachment tool is
available, attach every created or actively reviewed PR to its chat.

## Independent bug review

The primary instance reviews every submitted update when its session runs. CI
checks PRs between sessions. No unattended reviewer or notification guarantee is
installed by this document; GitHub carries the durable discussion and CI state.
The owner should send the primary instance the PR URL when review is needed.

Before executing a PR, inspect its diff, workflow changes, dependency changes and
scripts. Treat contributions as code/data, not instructions overriding the
owner's restrictions. Never expose tokens or private game fixtures to PR jobs.
Use `pull_request`, not `pull_request_target` with untrusted checkout execution.

For a clean independent review (N is the PR number):

```powershell
git fetch origin pull/N/head
git rev-parse FETCH_HEAD
git worktree add --detach ../choops-review-N FETCH_HEAD
cd ../choops-review-N
python tools/dev/setup.py
python tools/dev/verify.py
```

Use the canonical upstream remote in the fetch if origin is a fork. Inspect the
fetched code **before** running setup. These commands run no emulator and build
no JB. Synthetic tests may create tiny archive fixtures under output/temp/builds;
those are not a copied game. Private real_game tests are excluded by the portable
verification runner. It also excludes the optional legacy native comparison.

Add targeted reproduction tests for actual bugs, not tests that merely restate
implementation. Check affected parsers/writers, untouched data, rollback,
ambiguity rejection, output safety, GUI behavior, and CLI parity as appropriate.
Run source smoke, then packaged smoke if packaging/native dependencies changed.
Run authorized **read-only** fixture checks separately; absence is a documented
skip, never a pass. Never run verify_game.py --build or create a full testing JB.

Post an independent review with PR head SHA, test counts and commands, skipped
checks, findings and acceptance/blocking decision. If a bug is fixed on the
contributor's branch, require another push and test that new head. If fixed in a
follow-up PR, link both PRs and explain the dependency. Only the owner authorizes
merge and release. Do not self-approve a PR as independent verification.

## Maintain the foundation

CURRENT_STATUS.md is a compact living ledger. AUDIO_RESEARCH.md and project notes
record format evidence and uncertainty; TEST_REPORT.md records verification;
USER_GUIDE.md/COMMANDS.md describe exposed behavior; CHANGELOG.md and release notes
track published changes. MASTER_HANDOFF.md is an index, not a competing ledger.
Update all affected documents in the same PR as code. If an older claim becomes
false, correct it or mark the entire old section as historical with a current
link. Never append contradictory conclusions without identifying which wins.
Regenerate SECONDARY_CODEX_PROMPT.md with `python tools/dev/handoff.py` after
source-doc changes. The portable runner/CI checks the embedded snapshot is current.

At session end, record what changed, tested head/commands, open blockers, next
task and PR URL in the PR discussion. Both instances perform this duty. Maintain
separate private paths and fixtures on each PC; they are not synchronized by Git.

---

Embedded source: docs/DEVELOPER_GUIDE.md

# Development

Read AGENTS.md, CURRENT_STATUS.md, SECONDARY_CODEX_PROMPT.md and COLLABORATION.md.
Upstream is ZMO34/CHoops-Extractor-Reborn; use documented feature PRs to master.
Python 3.11+ supported; Python 3.12 x64 is the CI/Windows baseline. Git is required.

```powershell
python tools/dev/setup.py
python tools/dev/setup.py --check
python tools/dev/setup.py --audio-encoder
python tools/dev/verify.py
.\.venv\Scripts\python.exe -m choops_py.studio
.\.venv\Scripts\python.exe -m pytest tests/test_audio.py tests/test_cli.py -q
```

Setup installs .[dev]; the encoder option installs Zig 0.13.0 and fetches pinned
LGPL sources. Audio conversion uses the restricted LGPL FFmpeg helper built from
`tools/audio_codec/build_ffmpeg.sh` and the optional ATRAC3 encoder. No PyAV
wheel is required or packaged. No other PC's credentials, environment or paths
are copied. Versions go into ignored dev-setup.txt.
requirements-windows-dev.txt is an old environment snapshot; pyproject/setup
are the portable dependency contract.

verify.py excludes real_game/runtime_manual and the optional legacy native
comparison. It runs remaining synthetic/Qt tests, source smoke, fatal-error Ruff
checks and scoped GUI/service mypy. New setup scripts get broader lint. Legacy
style debt is not claimed resolved. CI runs the same runner on Windows/Linux.
Native audio tests skip explicitly if the optional encoder is absent.

CHOOPS_JB selects a private read-only fixture. Do not run verify_game.py --build,
copy a full game for tests, or launch RPCS3. Tiny synthetic archive copy/rollback
tests are permitted. Record absent private fixture checks as skipped.

GUI/CLI share Archive, studio.services, formats, texture_tools, roster model and
audio_tools. Qt workers return signals/data, never manipulate widgets. Writers
reparse output, preserve unknown bytes/bits and reject ambiguous shared ranges.
Generated outputs live under output/ and originals remain immutable.

`tools/rebuild/package_windows.ps1` packages the Windows GUI and audio helpers.
The FFmpeg helper is configured without GPL/nonfree components and uses only the
PCM formats and ATRAC3 decoder needed for WAV/audio operations. Its FFmpeg and
AtracDEnc source archives and applicable notices accompany the package. Confirm
the exact configuration and packaged smoke on Windows; no proprietary converters
or game assets are included. See AUDIO_WORKFLOW.md and the encoder README.

---

Embedded source: docs/AUDIO_RESEARCH.md

# Audio format evidence and development boundaries

Updated 2026-10-11; initial source commit e556e36. This is backend research, not a
claim of complete GUI or gameplay support. EBOOT is read-only evidence.

## Where the soundtrack is stored

The stock JB has split USRDIR archive banks rather than loose song files.
`jukebox.iff` contains UI, artwork TXTR records 000–022, layouts/scenes and
`artist_bio_english` STRG; it is not the soundtrack stream container.
`global.iff` owns AUSB metadata (type hash **61DF2234**) for cribmusic, femusic,
drillmusic, hlmusic, loadm and other speech/crowd banks. Stream filenames in those
records resolve through uppercase ASCII CRC32 (`replacement_hash`).

cribmusic.bin is 126275584 bytes on the inspected stock input; this is a research
observation, not a universal file-size requirement. It has 87 streams: licensed
music indices 0–9 and 74–86, fight songs 10–73. All 87 name/artist/category/artwork
mappings are in `choops_py/audio_tools/soundtrack_names.json`. The same raw bank
may be unnamed in old rips; hashes remain the canonical archive identity.

## AUSB metadata (big endian)

| Offset | Meaning |
| --- | --- |
| 0–63 | UTF-16BE bank filename and padding |
| 64 | u32 stream count |
| 68, 72 | Preserved words; observed 72 = 1 |
| 76 | u32 sample rate; observed 48000 |
| 80 | Preserved buffer parameter; observed 8192 |
| 84 | 14 mono / 15 stereo |
| 88 | float default/first stream duration |
| 92 + 8*i | u32 cumulative boundary, i = 0..count |
| 96 + 8*i | float duration, i = 0..count-1 |

Track i is raw bank `[boundary[i]:boundary[i+1]]`. Metadata used extent is
`88 + (count+1)*8`. Preserve padding, unknown words, raw bank prefix/tail and all
unchanged streams. Stream count, ordering and identity remain unchanged during
replacement. The experimental writer reparses and compares each stream.

## AUDO header and encoding

AUDO (1AEDDA1F) has a 36-byte big-endian header and raw ATRAC3 payload. Rips may
have `.audo.block0` + `.block1`, flat header+payload, or a 2kTl wrapper.

| Offset | Current interpretation |
| --- | --- |
| 0 | Observed version 1 |
| 4 | Codec 5: ATRAC3 mid-rate |
| 8 | 14 mono / 15 stereo |
| 12 | Stored sample count; sometimes stale after resampling |
| 16 | Sample rate |
| 20 | Unconfirmed flags; preserve |
| 24 | Encoded payload byte count |
| 28, 32 | Potential loop fields; not fully traced |

Frames are 152 bytes per channel, 1024 samples. Stock music durations match
physical decoded length minus **2048 priming samples**. Some AUDO/femusic/drill
values appear to retain pre-resampling lengths; do not truncate valid decoded
audio to arbitrary stale metadata. `playback_samples` uses a plausible stored
count only within 8192 samples of physical extent. This is a documented heuristic
that needs regression coverage, not a complete semantic derivation.

The raw float frontend uses AtracDEnc's non-joint-stereo 304-byte output frames;
mono takes one duplicated channel. Encoder priming is 1162 samples, so Python
prepends 886 zeros before encoding for the game's 2048-sample skip. The backend
independently decodes encoded output. Packet/DMA alignment (often 608-byte stock
chunks), exact loop behavior, long audio and cancellation still need validation.
Nonzero AUDO flag/loop words currently block replacement; export remains possible.
CDF AUDO banks exist, but a fully validated growing CDF audio writer is pending.

## Jukebox artwork and names

Artwork 000–020 maps to the first 21 artist groups, **021 is College Fight Songs**,
and **022 is Joe Blaq**. Strange Fruit tracks 2 and 77 share artwork 002; all fight
songs share 021. Use the catalog mapping rather than assuming stream index equals
artwork index. Artwork replacement preserves base texture layout.

EBOOT's constructor at 0x1A27A4..0x1A6500 constructs 36-byte song descriptors:
stream index, title pointer/key, artist key, bio pointer/key, bank key,
duration-display pointer/key. Title/artist keys match uppercase ASCII CRC32 | 1.
English.iff has TXTL type A423B39E with a sorted key table and self-relative
UTF-16LE string pointers. The inspected payload has 21637 keys; root +4 is count,
+8 points relatively to the table at 32. `artist_bio_english` maps bio-token keys
and English group key to localized biography keys.

This does **not** establish that editing English.iff overrides English song titles
at runtime. Defaults are executable strings and getter routing is unresolved.
Do not implement title/artist changes through EBOOT. Keep fields read-only until
an archive-only path is demonstrated. No proprietary biographies or executable
bytes are published here. Private helper scripts and EBOOT copies are not portable
project dependencies.

## Open-source codec provenance

- [FFmpeg ATRAC3 decoder](https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/atrac3.c): frame sizes, RIFF tag 0270, extradata and sync behavior.
- [vgmstream Sony MSF reader](https://github.com/vgmstream/vgmstream/blob/master/src/meta/msf.c): codec 5/mid-rate observations and encoder delay reference.
- [AtracDEnc](https://github.com/dcherednik/atracdenc), revision
  `cb170709f836cb43dc0312455188c791159d81dc`, LGPL-2.1-or-later. Thin frontend and
  build instructions are in tools/audio_encoder. No Sony SDK executable is used.
- The standalone app's LGPL packaging uses FFmpeg 9.0.2 at revision
  `946fcce07b6dcd0331c8cc609192aeff5e1924f8` (the peeled commit of the annotated
  `n9.0.2` tag), built as a separate CLI with GPL,
  nonfree and autodetected components disabled. Only the PCM formats, WAV/RF64
  demuxer, raw PCM muxers, ATRAC3 decoder, audio resampling/format filters and
  file/pipe protocols used by the workflow are enabled. The exact build script
  and corresponding FFmpeg source archive ship beside the app.
- Do not bundle the default PyAV Windows wheel for this project: the PyAV FFmpeg
  build configuration enables x264/x265, which enables FFmpeg's GPL options.
  See [PyAV's FFmpeg build](https://github.com/PyAV-Org/pyav-ffmpeg/blob/master/scripts/build-ffmpeg.py)
  and [the PyAV wheel licensing discussion](https://github.com/PyAV-Org/PyAV/issues/2270).
  The package instead uses separately executable FFmpeg built from the official
  [FFmpeg source](https://github.com/FFmpeg/FFmpeg) with a pinned revision and
  corresponding source archive.
- Exact-head Windows CI run 54 built the pinned FFmpeg and ATRAC3 helpers,
  packaged/smoke-tested the GUI, and passed the frozen synthetic WAV round trip
  on `e149790005fdaeb14d0a1b79689d0a3de3b8f2da`. The script checks the LGPL-only
  build configuration and required audio components; source archives and license
  files are packaged beside the app. This is branch verification, not a published
  release claim.

See CURRENT_STATUS.md and each PR's exact verification for the latest evidence.

---

Embedded source: docs/AUDIO_WORKFLOW.md

# Experimental audio workflow

Batch WAV export publishes its output folder only after all selected tracks and
the manifest succeed. Cancellation/failure removes the owned temporary batch;
existing destinations and unrelated files remain untouched. Scene/shoe preview
actions navigate to Models/Courts by name even with Audio present.

The Qt studio includes an **Audio** workspace with separate Licensed Music and
Fight Songs tabs. It reads the catalog from the selected JB, exports selected
tracks or a full section to WAV, and prepares archive replacements from one WAV
or a previously exported/edited manifest folder. Select one track to export or
replace its mapped shared cover artwork. All output is written under `output/`
for manual staging. Users build their JB themselves.

Song title/artist changes and EBOOT writes are unavailable. Unknown AUDO loop
formats and general CDF audio growth remain blocked. The GUI and commands use
the same Python backend; no emulator or gameplay check is part of these flows.

Launch the studio with `python -m choops_py.studio`, then choose **Audio** in the
left navigation. Open a JB from Explorer first, then use **Load / refresh
catalog**. WAV export needs the LGPL FFmpeg helper. WAV replacement also needs
the LGPL ATRAC3 encoder helper.

From a checkout or the release's **audio-workspace** directory:

```powershell
python tools/dev/setup.py
.\.venv\Scripts\python.exe -m choops_py.cli --help
```

Python 3.12 x64 and Git must already be available. Setup installs the desktop
and development dependencies. On Windows, install MSYS2 with its MINGW64 toolchain,
`make`, `git` and `pkgconf`, then run `bash tools/audio_codec/build_ffmpeg.sh`
from an MSYS2 MINGW64 shell at the repository root. This builds FFmpeg 9.0.2
from pinned upstream source with GPL/nonfree components disabled. Build the
separate ATRAC3 encoder with `python tools/dev/setup.py --audio-encoder`; this
fetches pinned LGPL AtracDEnc source and builds the helper with Zig. WAV export
needs FFmpeg; WAV replacement needs both helpers.

```powershell
.\.venv\Scripts\python.exe -m choops_py.cli audio-catalog "YOUR_JB_ROOT" output/reports/audio.json
.\.venv\Scripts\python.exe -m choops_py.cli export-soundtrack "YOUR_JB_ROOT" output/rips/licensed
.\.venv\Scripts\python.exe -m choops_py.cli export-soundtrack "YOUR_JB_ROOT" output/rips/fight_songs --category fight-songs
.\.venv\Scripts\python.exe -m choops_py.cli replace-song "YOUR_JB_ROOT" cribmusic 0 "MY_EDIT.wav" output/audio/song_edit
.\.venv\Scripts\python.exe -m choops_py.cli import-audio-folder "YOUR_JB_ROOT" output/rips/licensed output/audio/batch_edit
.\.venv\Scripts\python.exe -m choops_py.cli export-audo "RIPPED_SOUND.audo.block0" output/audio/sound.wav
.\.venv\Scripts\python.exe -m choops_py.cli replace-audo "RIPPED_SOUND.audo" "MY_EDIT.wav" output/audio/replaced.audo
.\.venv\Scripts\python.exe -m choops_py.cli export-jukebox-art "YOUR_JB_ROOT" 000 output/audio/cover.dds
.\.venv\Scripts\python.exe -m choops_py.cli replace-jukebox-art "YOUR_JB_ROOT" 000 "MY_COVER.png" output/audio/jukebox.iff
```

Choose a new output name/folder each time. Export defaults to 23 licensed tracks;
fight songs are a separate batch. WAVs are PCM16 at the source bank rate/channels.
Import resamples and ATRAC3-encodes compatible WAVs. Finite floating-point PCM
samples through ±4.0 are accepted by the encoder's 1/4 input scaling; higher
peaks and non-finite samples are rejected. Song replacements are automatically
trimmed to the selected track's catalog sample length; shorter sources are
silence-padded to that same length. Maximum source duration is 30 minutes.
Manifests hold bank/index and original WAV checksums; unchanged files are skipped.
Changing manifest title/artist text does not rename game songs. No changed WAVs
means no replacement folder is created.

Song replacement outputs global.iff and affected .bin files, preserving other
streams and ordering. Stage that folder and manually build your JB when ready.
Standalone AUDO output is a raw/wrapped asset copy, not a complete replacement of
its parent IFF/CDF. Do not stage it as a complete archive. Unknown looped AUDO
replacement and general CDF audio growth remain blocked/pending.

Cover replacement outputs complete jukebox.iff for manual staging. Record 021 is
shared by all fight songs; 002 by both Strange Fruit tracks. DDS or Pillow-readable
artwork such as PNG is normalized to the selected JB's base texture layout.

The Windows standalone GUI includes the restricted LGPL FFmpeg and ATRAC3 helper
executables. Their exact source archives, license texts and build instructions
are distributed in `THIRD-PARTY-SOURCES`. The default PyAV wheel is not bundled.
When building locally, both helpers must be present before running
`tools/rebuild/package_windows.ps1`. See AUDIO_RESEARCH.md for evidence and
format limits.

---

Embedded source: docs/PROJECT_SOURCE_OF_TRUTH.md

> Updated 2026-10-11: choops_py.studio is PySide6. CURRENT_STATUS.md and the project
> notes govern current editing support. The format contracts below retain some
> inherited observations; table offsets are stock evidence, not universal hardcodes.
> Supported growth and optional roster operations supersede older fixed-capacity
> restrictions. Texture conversion is built in; audio is experimental Python CLI.

# Project source of truth

Target: PS3 College Hoops 2K8, Python 3.11+, argparse and PySide6. Read
CURRENT_STATUS.md, COLLABORATION.md and SECONDARY_CODEX_PROMPT.md first. This
technical baseline preserves inherited evidence; newer project-specific docs and
tested code supersede older conservative restrictions. No JavaScript runtime.

## Provenance and confidence

Read-only references: expanded 2026-06-18 master handoff; original continuation README, archive configuration; downloaded Reborn gameProfiles, ChoopsReader, IFFReader, CDF extractor, H7A utilities, ToolWrappedReader and floor notes. Constants, pointer formulas and useful filename hash/name pairs were intentionally rewritten into Python. No Node runtime, native editor, conversion executables or legacy build products are retained. Original source authors' provenance is recorded here; upstream licensing must be clarified before adding more borrowed implementation or distributing proprietary assets.

`MASTER_HANDOFF.md` preserves the full research record and inventory. Confirmed below means corroborated by source and/or current fixture checks; candidate fields remain read-only. No game assets belong in Git.

## Archive and identity

The archive header is six BE u32 words: magic AA00B3BF, alignment, part count, zero, entry count, zero. Part descriptors are 16 bytes: first word is size in 0x800 units; bytes +8..+15 encode the part filename as UTF-16BE. Logical space concatenates listed parts, allowing entries across boundaries. CH2K8 TOC uses 16-byte records: hash +0, offset units +4, unknown +8, stored size units +12. Offsets multiply by alignment. Stored sizes must be validated against archive boundaries; derive only from next offset/end and flag the derivation. Preserve padding by extracting the complete bounded extent. Do not clamp an invalid read silently.

Case-insensitive ASCII filename hashing matches CRC32 of uppercase bytes for generated candidates. Retained reference hash/name pairs take precedence. Namespace includes ua/uh/ux/selua/seluh/selux/s/m/p/coach 000..999, h0000..9999 and known named banks, with iff/cdf/bin variants. Outer TOC names and inner IFF names are distinct identities. Unresolved entries remain hash names. Sparse alternates are meaningful: a cache name does not add a game-loadable archive or team.

Caches live under output/cache, keyed by source path, and record part sizes/mtime; stale fingerprints are rejected. Current cache validation reparses the TOC; it is a reproducible index, not yet a speed optimization. It does not prove payload integrity after timestamp-preserving changes.

## Standard IFF: FF3BEF94

BE header is 0x20 bytes: magic +0, payload start/headerSize +4, payload end/fileLength +8, zero +0C, block count +10, observed 13 +14, file count +18, observed blockCount*0x20+5 +1C. FileLength excludes optional name table and padding. Preserve all bytes beyond it.

Block descriptors are 0x20 bytes (eight BE words): name/hash, type/hash, unknown1, logical size, unknown2, absolute stored start, stored size, indexed flag. Keep descriptor order; bank IDs such as BB05A9C1 and 411536D5 are not subfile types. Block ranges must fit within payload bounds.

The BE file pointer table follows the blocks. Target = pointer field position + value - 1; inverse = target - field + 1. Follow actual pointers rather than assuming records are contiguous. Each file record is ID, type hash, offset count, then block-relative logical offsets. FFFFFFFF means absent. Infer each span using the next larger valid offset in that block or its logical end. Duplicate starts can imply aliasing; replacement must reject ambiguous shared ranges.

Optional AA171516 name table starts at fileLength: BE magic, LE body size/pointers, UTF-16LE strings. The body contains count and relative pointer to entry-pointer table; each entry has relative name/type pointers. Missing name tables may be valid. Fallback names are numeric, with known type hashes when available.

Common types: TXTR 5C369069, SCNE E26C9B5D, LAYT 86A1AC9E, ROST C61649B2, AUDO 1AEDDA1F, NAME 68B693B2, CDAN A7701F00. Full historical type map remains in MASTER_HANDOFF.

H7A wrapper: 0E4837C3, logical size, stored size including 0x14 header, unknown, shift. Descriptor bits are read low to high: 0 literal, 1 BE 16-bit backreference. Distance is low shift bits; copy length is (token >> shift)+3. Validate wrapper sizes, shifts, lookback and truncation. Decoder caps a single logical block at 512 MiB. Unchanged compressed blocks are copied verbatim. The current bounded writer preserves logical slice sizes, reuses original compression token choices where valid, and expands invalidated references to literals. Recomputed block locations/file lengths and preserved NAME table must fit the original archive extent; otherwise writing is blocked.

## CDF-backed metadata: F0985030

Always handle metadata IFF with its paired CDF; uniforms are not this family. Header +4 is metadata end; +10 block count; +18 record count. +20 points relatively to segment pointer table; +24 points to UTF-16BE CDF name. Primary record pointers start at 0x68. Primary records contain five BE words: ID, type hash, offset count, virtual header offset, virtual payload offset. Virtual offsets are not physical CDF offsets.

Each secondary descriptor is four BE words: CDF header offset/length and payload offset/length. Validate both actual ranges. Optional name table uses the same mixed-endian scheme. CDF TXTR fallback hash is 5C36FB69 (different from standard); AUDO is 1AEDDA1F. Preserve CDF segment headers, gaps, tails, compression and metadata. Same-size physical payload replacement is supported only when no preserved range overlaps. This validates bounds, not codec semantics or console compatibility. Whole CDF-pair staging is supported with paired preflight validation; physical payload growth remains blocked.

AUDO segment headers can carry a payload length at +18; interleaved audio banks must preserve headers as well as payload. H7A/GTF texture layouts vary; do not infer codec validity from DDS conversion failures.

## Tool files, textures and uniforms

2kTl is BE magic 326B546C, header size, u16 type ID, u16 block count, BE u32 sizes, concatenated blocks. Header size = 12+4*count. Use numeric type IDs; no unvalidated semantic ID mapping. Strictly reject trailing/truncated wrapper bytes.

Standard TXTR often uses separate header and payload blocks; exports preserve individual blocks plus record manifest. Uniform jersey_numbers and names are embedded TXTR subfiles, with separate NAME records possible. Indexed font glyph metrics and static placement are validated; see ROSTER_SCALE_AND_PREVIEWS.md. Validated TXTR descriptor: +58 format byte, +59 mip count, +5A dimension, +5B cube flag, +60 width u16, +62 height u16, +64 depth u16, +68 pitch u32; +A4 is payload offset+1. Unknown variants remain raw-preserved and blocked for DDS edits.

## SCNE / courts

SCNE package header is 0x54 bytes. +20 texture count; +24 relative texture pointer; +44 model-part count; +48 relative model-part table. Model records are 0xB0 bytes; texture headers also 0xB0. Part name at +0 is relative UTF-16BE. +04 ID; +08 flags; +10 radius-like float; +30..38 center; +4C..54 scale. Section counts/pointers: material +60/+64, draws +7C/+80, buffers +84/+88, declarations +94/+9C. +A4 is index flags, +A8 index count, +AC index offset+1 (do not confuse flags with count). Known floor parts: floor, paint, centerlogo, lines. Full-court imagery requires validated UV/material routes; changing texture dimensions alone does not create full-court coverage. OBJ writing and geometry edits are deferred.

## Roster and development direction

v1.11 correction: team roster pointers are an 18-element array at editor +0x6C;
the active u16 count is +0x188. Runtime array/count are anchor +0x3C/+0x158. All
443 stock arrays validate with those fields. Player row zero is real when active;
only trailing row-zero references are empty. See ROSTER_SIDE_PANELS.md for evidence
and guarded transfer/brand propagation. Historical 16-slot assumptions are superseded.

Conference scalar provenance: the public
[conferences.py](https://github.com/bphit4/CH2k8-Roster-Editor/blob/main/conferences.py)
defines the same +0x0A..+0x22 field offsets and big-endian u16/RGB widths. The
separate Conference_Parser.py only locates rows/names; it does not establish those
scalar meanings. Source captions are retained and gameplay effects remain unverified.

Current corrections: jersey number is byte +0x1B, preserving adjacent flags at
+0x1A. Tables/counts derive from the header. Verified ratings, equipment/shoes,
appearance choices, optional conference/D1 updates and alternate links are
editable through declared masks. The older restricted-field paragraph below is
historical; ROSTER_EDITOR.md and projects/ define current scope. Six palette words
remain unresolved; long string rebuilding and unknown fields remain blocked.

Roster adapters support standard IFF ROST, raw ROST, type-21 wrapper, decrypted USERDATA with 4-byte prefix, and one-USERDATA decrypted ZIP. No encrypted-save decryption is provided. Known tables: players 0x0271AC/5685/308, arenas 0x1D5C84/379/28, teams 0x1D85E0/443/704, coaches 0x23F78C/1373/44.

ROST runtime string pointers are field + signed delta - 1, consumed as UTF-16BE (77FB1C / 7C5818). Stored reference anchors retain the documented +1 biases. Player last/first pointers +0x10/+0x14 target aligned big-endian text; do not use the shifted ASCII-only LE interpretation. Jersey number is byte +0x1B (preserve adjacent flags and player ID +0x18), height +0x3A, position +0x3B. Team roster references +0x6C, 18 slots, point to player row +0x11. Team arena +0x44 targets arena row +0x19, coaches +0x60/+0x64/+0x68 target coach row +0x15, rivals +0x4C/+0x50/+0x54 target team row +0x31. Asset IDs are high u16 at +0x18C/+0x190/+0x194; preserve low words and require consistent existing IDs. Conference record fields +0x0A..+0x22 are exposed with their source labels and original u16/RGB widths, based on the public CH2k8 roster parser and cross-checked against supplied USERDATA record values. The source labels identify founded year, championship-order values, Final Fours, prior-year bids, rank, tournament settings, and color; gameplay effects are not independently verified. Prestige and unknown appearance fields remain read-only. Names use copy-on-write UTF-16 growth with preserved aliases and fixed table locations; keyboard limits are advisory. Conference +0x1A is now confirmed as a tournament index and protected pending a backlink writer; logo routing uses 900 + conference index. See CONFERENCE_ASSETS.md.

Current TXTR descriptor +0x58 contains format, mips, dimension, cube, remap,
width/height/depth and pitch. GTF wraps descriptor/image in a 0x30-byte header.
Conversion is built-in Python for L8, ARGB8, DXT1/3/5 and RGBA16F, mips/cubes.
Historical converter switches are reference evidence only. Non-stadium imports
normalize to the selected base layout; stadiums allow supported dynamic sizes.
SCNE textures share the TXTR pipeline while geometry is preserved. CDF headers
and images may each be H7A compressed; sideline_items contains SCNE records.

Future development should extend validated texture variants and bounded writers, add meaningful regression fixtures, and verify console behavior. Do not expose speculative roster fields or geometry modifications as safe.

## Current safety contract and evidence

Generated outputs live under project output/. Reject source overwrite/overlap,
traversal and linked builds. Supported record/archive growth uses validated
relocation; unknown offsets/aliases remain blocked. Manual builds are transactional
and source-bound; agents must not create testing game copies or launch RPCS3.
PySide6 GUI and CLI share services; workers use signals rather than widget writes.
Experimental AUSB/AUDO evidence is in AUDIO_RESEARCH.md. EBOOT stays read-only.

Validation procedures are documented in TEST_REPORT.md and rebuild/ACCEPTANCE_TESTS.md. Public documentation excludes fixture fingerprints, extraction measurements, session records and environment-specific results. Do not infer current capability from historical smoke observations or command registration.

---

Embedded source: docs/projects/01-uniform-preview.md

# Uniform preview

Implemented. Open a cloth SCNE, choose a searchable home/away/alternate uniform from the loaded JB folder, or choose Open uniform IFF. The preview uses the selected source's `unifregion`/`shortregion` authored RGB; `unif`/`short` are fallback records. Normal maps and number atlases are not substituted for color artwork. Material-data alpha is made opaque only in the preview copy.

Jersey and shorts use their corresponding images. Same-name cloth SCNE sections are alternatives, rather than superimposed geometry. Authored front/back numbers 0–99/00 and curved Reborn surname lettering now render. Cloth simulation and full game material shading are not reproduced. See ../ROSTER_SCALE_AND_PREVIEWS.md. The original assets remain unchanged.

Verified with a native OpenGL jersey render and synthetic sampler-selection tests.

---

Embedded source: docs/projects/02-team-uniform-routing.md

# Team and uniform routing

The ROST header at +0x70 describes an eight-byte uniform table. The engine's uniform lookup counts records belonging to a team, then selects the requested matching record in table order. It compares the record's owner with the team's asset identity.

| Uniform field | Storage | Evidence |
|---|---|---|
| Team owner | First word, bits 22–31 | Runtime uniform lookup and getter |
| Uniform asset selector | First word, bits 12–21 | Packed getter/setter |
| Variant code | First word, bits 8–10 | Runtime formatter: 0 Home, 1 Away, 2 Alternate 1, 3 Alternate 2, 4 Alternate 3 |
| Unlock ID | First word, bits 0–6 | Zero is unconditional availability; nonzero invokes profile unlock lookup |
| Jersey shape | Second word, bits 27–29 | Packed getter/setter and cloth filename dispatch table |

Shape dispatch: 0 U, 1 V, 2 V triangle, 3 triangle, 4 wishbone. The game's dispatch falls back to U for out-of-range codes. The Uniforms roster tab exposes the table, allows known shapes and existing asset selectors, and preserves all other bits. Save a roster copy and stage it normally. Offline structural validation does not establish gameplay consumption of an edited shape.

Runtime bank prefixes are `uh`, `ua`, `ux`, `uy`, and `uz`. Uniform and `selu` menu-selection filenames use the record's asset selector, independently of its owner ID. Archive naming includes all five banks and ten-bit selectors. The preview selector changes only preview images.

The copied-JB alternate builder clones uniform and menu-selection art and appends a team-owned record with unlock ID zero. Existing unlock IDs remain intact. Notre Dame's stock owner has all five banks; one record carries unlock ID 95. Full profile/UI behavior has not been validated in game.

Alternate availability checkboxes remove/restore the corresponding record in the counted list. Restored records keep their original unlock ID; enabling a linked record does not bypass profile unlock conditions. Missing asset banks require the copied-JB builder. Five-bank builds are explicit operations and preserve team classification.

---

Embedded source: docs/projects/03-roster-palettes.md

# Remaining roster palettes

Research continues. The 31 team RGBA words include 22 exact Edit Schools captions. Slots 0 and 1 have verified home/non-home equipment color consumers; slot 11 has a verified Key Circle Inner material consumer. These are runtime roles, not additional recovered Edit Schools captions. Six words (16, 17 and 27–30) still lack verified roles.

Do not infer jersey-number colors from repeated school colors. Uniform packages contain separate authored color artwork, jersey-number atlases and glyph metrics. The separate eight-byte uniform roster table also contains packed selector fields; these are not RGBA words.

Next trace: runtime uniform color/material setters and number/name atlas consumers back to team palette words. Existing provisional labels remain marked as candidates. Arena shader masks are also unresolved.

---

Embedded source: docs/projects/04-archive-size-and-assets.md

# Archive size and new assets

TOC offsets use alignment units; TOC lengths are byte counts. The reader now distinguishes byte length from the aligned allocation. Existing same-extent texture edits retain compression and bank sizes. A bounded H7A recompressor avoids literal expansion when it produces a smaller verified stream.

New-asset builds create a separate JB folder. The append writer uses verified zero TOC padding; when it runs out, the repacker expands the TOC and relocates the preserved archive body across split banks. Both verify every existing asset, reparse additions and replacements, and check that the source inventory is unchanged. New assets necessarily increase total size; ordinary replacement edits do not silently grow fixed allocations.

Uniform roster growth copies the counted table to the payload end and updates its count and relative pointer. Existing table/heap addresses remain intact. The IFF writer preserves container metadata and name trailers and verifies decoded payload equality.

Synthetic tests cover TOC expansion, split-bank growth, oversized roster relocation, invalid compression and source preservation. Copied-JB tests have validated a new second alternate and a first alternate on a previously home/away-only team, including both uniform and menu-selection containers. In-game execution remains unverified. A bulk copied-JB build validated 1,179 new uniform records for 429 current/classic school owners, using six split banks; all 3,380 existing entries were checked. All eligible owners had five linked banks in the rebuilt roster. The source was unchanged. The extra cloned art increased the archive by approximately 801 MiB.

Two-block CDF texture banks support independent internal record cloning with preserved original CDF bytes. IFF and CDF replacements must be supplied together and all compressed spans are validated. Team-selection logo cloning preserves existing records and adds a new named logo. Runtime validation remains outstanding.

---

Embedded source: docs/projects/05-roster-usability.md

# Roster usability

Implemented confirmed choices. Handedness is 0 L and 1 R, traced through the localized Hand option array. Headband is No/Yes; home sock color is Black/White. Their packed edits preserve unrelated bits and use dropdowns.

The property viewer also labels verified build, muscle tone, appearance color, eye color, sock length and T-shirt choices. Enum values outside recovered choices remain explicit raw/unknown values. Binary values are not universally treated as booleans: muscle tone means Buff/Ripped, while sock color means Black/White.

Verified with packed-neighbor preservation tests and existing undo/round-trip checks.


The Teams and Edit Schools tabs expose **Enable alternates…**, with separate Alternate 1/2/3 checkboxes. Existing linked records can be disabled and restored without changing their asset selector, shape, or unlock ID. Records without linked assets cannot be enabled here; use the copied-JB alternate builder first.

The executable has no confirmed enable bit. Disabled records are excluded from the counted uniform table and retained as editor recovery metadata outside it. Recovery survives IFF save/reopen and undo/redo. Expanded tables currently save through raw ROST or a single-record ROST IFF; save wrappers that require fixed payload size are refused. This layout has offline round-trip validation, not in-game validation. Availability still follows the game's profile/unlock checks for enabled records.

---

Embedded source: docs/projects/06-declone-d1-teams.md

# Reusing classic/all-time slots as independent D1 teams

The new archive insertion and uniform-table writer provide a foundation: independent uniform/menu containers can be added and associated with an existing team owner. Uniform asset selectors are separate from owner IDs, so jersey art need not share a numeric ID with the stadium.

A complete D1 conversion also needs the historical/all-time classification and conference eligibility fields, reciprocal conference-member lists, independent arena/stadium references, coach/player links, and menu logo/portrait routing. Existing same-size field edits and a copied-JB build preserve originals. Do not describe an ID-only edit as a complete D1 conversion.

The uniform owner field is ten bits. The stadium filename construction and menu logo paths require separate bounds and reference checks. Shared physical textures or aliases must be copied into new owned containers rather than edited in place.

D1 conversion is optional in the roster editor. The conference dialog has an unchecked classification checkbox. An ordinary conference move preserves classification; uniform builders never convert teams. The editor updates reciprocal conference member lists and their verified counts, and changes only the confirmed team-type bits when conversion is explicitly selected.

**Give school independent assets…** is a separate, explicit copied-JB action. It clones the referenced stadium, active uniform/menu-selection banks, and an internal team-selection logo record. It appends an independent arena record, rebases the copied arena table's string pointers, and updates team arena references. The selected school's stadium code, uniform owner and menu-logo selector receive the new unused ID. Other schools retain their original values. New uniform records use unlock ID zero.

Asset cloning preserves classification and conference membership. Conversion remains an unchecked option in the separate conference dialog. Arena thumbnails, runtime cache sharing and in-game schedule/menu eligibility remain unvalidated; creating a complete renamed D1 program still requires roster/player/coach edits. The source fixture tests are offline evidence, not gameplay proof.

---

Embedded source: docs/projects/07-shoes-and-asset-identities.md

# Shoe assignment, preview and archive identities

The executable's player-to-team assignment routine copies four team shoe defaults into the player: manufacturer, style, home color, and away color. Players retain their own packed values afterward. The stock current-school data has a team manufacturer matching every active player on 336 consistently assigned teams; all 11,370 player home/away texture paths resolve to existing archive hashes.

Offsets below use the editor's existing legacy row starts. The executable's player anchor is 16 bytes later and team anchor is 48 bytes later.

| Field | Team offset / shift / width | Player offset / shift / width |
|---|---|---|
| Manufacturer | 0x2E8 / 20 / 3 | 0xA8 / 29 / 3 |
| Style | 0x2E0 / 22 / 5 | 0xA0 / 27 / 5 |
| Home color | 0x2E0 / 17 / 5 | 0xA0 / 22 / 5 |
| Away color | 0x2E0 / 12 / 5 | 0xA0 / 17 / 5 |

The assignment copy is at executable routine 0x7646D8 onward. The filename formatter at 0x728AD8 uses manufacturer base codes (0, 100, 200, 300, 500), style, and the selected home/away color. Generic shoes use shoe_0.iff / shoe_1.iff; branded styles use shoe_MODEL_COLOR.iff with two-digit color values. Getters 0x72965C and 0x729674 choose the home/away colors. The Edit Player color cycling/display routines use manufacturer-indexed lists: two colors for generic and special styles, sixteen for the regular branded families. These are finite style/color packages, not a separate set of textures for each school.

The stock archive contains 90 shoe texture packages: 2 generic, 48 Nike (three styles), 16 Reebok (one style), 16 Adidas (one style), and 8 special-family packages (four styles). Special-family art includes Jordan branding; its exact original UI manufacturer caption has not been recovered. Regular color captions are White, Black, Red, Yellow, Blue, Green, Orange, Purple, followed by Black / White through Black / Purple. Exact commercial style names have not been mapped, so editing uses artwork IDs. Player assignments and school defaults are writable through **Edit shoes…** and the confirmed scalar fields. The writer changes only the declared bit masks, validates the combined brand/style/color selection, and records one atomic undo entry. Changing school defaults does not silently rewrite current players.

## Preview

Models / Courts has a searchable shoe-artwork list and **Preview selected shoes**. **Preview assigned shoes…** in the roster editor selects a player's current shoe package or a school's default for Home/Away. The standalone hi_shoe1 SCNE is found in the current JB folder by verified container contents. Its original filename is still unresolved; its stable TOC hash is retained. The packed signed-short position and UV declarations contain scale/bias vectors; decoding them yields 885 triangles. Embedded 60-byte material records name eight parts. sole_mat uses shoe_sole; fastener, midsole, toe, heel, logo, hitop and upper use shoe_upper. The preview is a static shoe silhouette; selecting artwork does not claim to reproduce model-specific gameplay shape or full shaders.

TXTR/GTF descriptors contain RSX channel remapping. Some white/black shoe textures store luminance only in green, with descriptor 0xA9A8 selecting green for RGB and constant alpha. Applying descriptor routing fixes their false-green preview. The identity mapping is 0xAAE4. This read-only preview conversion does not change texture export/import bytes. The [RPCS3 texture implementation](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/RSX/RSXTexture.cpp) provides the primary-source RSX remapping reference. Specialized high-word remap orders remain unsupported.

## Naming hashed assets

The archive stores CRC32 identities rather than filenames. New built-in patterns recover the shoe packages and thin/regular/fat cloth containers. Additional executable literals are kept in a small verified name table. On the stock fixture, 3,343 of 3,376 entries have canonical name candidates matching their CRC32 identities.

**Identify unnamed assets** reads bounded IFF metadata, tries internal names as filename candidates, and labels remaining containers with their internal SCNE/TXTR records. **Match filename list…** accepts a UTF-8 list of candidate filenames. Only candidates whose CRC32 matches a TOC identity can become canonical names; conflicting candidates are left unresolved. CRC32 alone is not an invertible or globally collision-free naming scheme. Internal-record labels are display hints, never substitute archive identities. Results are cached against bank size/mtime fingerprints and reused only for the same source state. Original archive files are never renamed or rewritten.

Synthetic tests cover packed coordinates, shoe fields, material names, remapping, cache invalidation and name/hash separation. Real-source checks cover all stock player texture routes, shoe selection and native OpenGL rendering. Gameplay verification remains pending.

---

Embedded source: docs/SINGLE_SURFACE_COURT.md

# Single-surface court templates

In Models / Courts, choose **Prepare single-texture court…** and select the
user-supplied full-court ZIP. The tool writes a new folder under
`output/templates/`. It does not build a JB folder or alter the ZIP.

The prepared folder contains `s258/floor.scne`,
`s258/_floor.scne/texture_0.dds`, and
`s258/_floor.scne/texture_2.dds`. Copy these into your overrides. To reuse the
floor for another stadium, copy the contents into that stadium's `sNNN`
folder. Keep its own arena assets. The report records the resulting layout.

Only the floor surface draws. Paint, center-logo and line parts retain their
identities and geometry but have no draw runs. Unused texture slots retain
their IDs with tiny placeholder images. Imports recognize this draw/material
configuration and ignore DDS or raw texture replacements for its disabled
slots, preventing older extra floor artwork from restoring their memory cost.
The arena is neither copied nor changed by preparation.

Texture 0 holds the complete court artwork. Texture 2 now binds to the arena's
actual `BumpSampler` shader semantic, rather than remaining an unused albedo
mask. The preparation uses the clean raw `floor_normalglossdetail` TXTR:
the supplied exported normal DDS has scrambled pixels. The normal's red/green
components are repacked to the donor bump texture's DXT5nm convention, X in
alpha and Y in green. A second vertex stream supplies normal, tangent,
bitangent and secondary UV attributes. Original positions, indices, primary
UVs and instance transforms remain unchanged. The basic GUI preview displays
base color; it does not reproduce game bump shading.

## Resolution and memory

The prepared defaults are **2048 × 1024 DXT5** for the complete court and
**512 × 512 DXT5** for the normal, both with complete mip chains. Their
combined image allocation is approximately **3 MiB**, including the tiny
inactive images.

| Image dimensions | DXT5 including complete mip chain |
| --- | ---: |
| 512 × 512 | 0.33 MiB |
| 2048 × 1024 | 2.67 MiB |
| 2048 × 2048 | 5.33 MiB |
| 4096 × 2048 | 10.67 MiB |
| 4096 × 4096 | 21.33 MiB |

The RSX graphics library declares a **4096-pixel dimension ceiling**, also
consistent with its 13 supported 2D mip levels. See
[RSXGL texture constants](https://github.com/gzorin/RSXGL/blob/master/src/library/gl_constants.h)
and [RSXGL screen limits](https://github.com/gzorin/RSXGL/blob/master/src/nvfx/nvfx_screen.c).
Imports reject an image exceeding that dimension after any base-layout
normalization.

That ceiling is not a measured crash-free game budget. Two 4096-square DXT5
images require about 42.67 MiB before arena, player and other allocations.
The game's maximum crash-free court resolution has **not** been established
by the Python layout checks. The report explicitly records that runtime
validation is outstanding. Preparation does not open an emulator or create a
test game build.

## Automatic non-stadium normalization

Recursive override staging restores every supported texture outside `sNNN`
stadium archives to the selected base JB's dimensions, format, mip count,
channel routing and storage layout. This includes uniform/menu/gameplay
banks, raw TXTR replacements, complete IFF replacements, SCNE textures and
paired CDF banks. Replacement artwork remains the artwork being imported.
Scene geometry remains the replacement geometry. Inputs are not modified.

Stadium archive matching uses names and known filename hashes. Stadium
textures retain dynamic sizing within the dimension ceiling. There is no
format/version checkbox or special legacy-folder mode.

Use a vanilla JB as the source when vanilla resolutions are desired. A modded
source supplies its current layouts; the importer cannot recover an unknown
original size from an already modified source. Unknown or ambiguous reference
identities fail explicitly rather than borrowing another texture's layout.

Source CLI equivalent:

```powershell
choops prepare-court-template "court-template.zip" "output/templates/my_court"
```

Generated game geometry and artwork are local outputs and are not included
in the repository or Windows release.

---

Embedded source: docs/KNOWN_LIMITATIONS.md

## Current continuation evidence

Floor alignment guides are independent flat-colour stock S256 reference geometry,
raised 1 game unit. They never hide real floor materials or apply roster colours.
Without the source reference they are unavailable.
Conference logos have verified logo900+index routing; the separate
tournament index is protected pending a backlink writer. Animation clips can be
identified/extracted as raw SingleMoCap blocks, without decoded skeletal tracks.
Orange text warnings concern confirmed keyboard buffers, not proven engine caps.
Secondary positions are closed by owner confirmation and are not being searched.
Unknown roster bits, reflection/fake-bump/AO and all runtime palette modes remain
unestablished. See the current evidence docs; older dated limits below are history.

# Current evidence boundary

Arena vertex colour/alpha, lightmap, glow and flare masks are now supported;
ARENA_SHADER_MASKS.md distinguishes them from unimplemented dynamic lighting/AO.
ROSTER_SEMANTICS.md records new appearance, tattoo and signature edits. Complete
semantics for all roster bytes, all engine text ceilings and remaining runtime palette links are not certified. Earlier notes
that describe these newly mapped controls as unavailable are superseded by these
evidence documents. Source data, EBOOT and unknown bits remain preserved.

# Current limitations

The scale branch remains incomplete semantic reverse engineering. Confirmed Edit
Schools entry capacities are mapped; conference/coach/singular-mascot limits and
the renderer's broader text ceiling, arena shader channels, number geometry/colour and
Secondary-position research is closed by owner confirmation. CSV/comparison use supported
writers and exclude ambiguous references. Text growth is structurally tested;
game runtime remains unverified. See ROSTER_SCALE_AND_PREVIEWS.md.

v1.11 transfers/brand propagation reject shared or inconsistent ownership and full
18-player destinations. Whole-table older 16-slot JSON exports need refreshing.
Static jersey preview has authored number/Reborn overlays; runtime cloth, skinning and animated bodies are not reproduced.
No automatic Legacy eligibility/scholarship enforcement or gameplay guarantee.

v1.10 removes D1 conversion and new alternate/independent-asset actions from the
public editor/CLI. Single position and Scholarship/Walk-on are confirmed; secondary
position is unproven and not exposed. See PLAYER_QOL_RESEARCH.md for evidence.

Updated 2026-10-11. CURRENT_STATUS.md and TEST_REPORT.md are the living evidence.

- Python/Qt checks do not establish game behavior. Agents never open RPCS3 or
  create testing JB folders; users build/test their own copies.
- DDS/GTF conversion is built in. Unknown TXTR layouts, DX10 and volumes with
  more than one stored slice remain unsupported. Single-slice 3D descriptors
  accept 2D artwork while preserving their descriptor. Unused stored depth on
  declared 2D/cubes is tolerated.
- Validated standard IFF/TXTR/SCNE growth and archive relocation exist. Unknown
  pointers and aliases remain blocked; general CDF virtual/physical growth is
  unresolved. Do not apply obsolete same-size rules to every supported writer.
- Six team palette words and full arena shader masks remain unresolved. Preview
  lighting, cloth/skinning, jersey glyphs and material effects are simplified.
- Roster names generally need equal encoded length/unshared storage. Encrypted
  saves need external decryption. Community wrappers are preserved; invalid
  pointers/new corruption remain fatal. Unchanged bad name characters are warnings.
- Alternate/linking operations and optional D1 conversion exist, but complete
  game/profile unlock behavior and independent decloned IDs need validation.
- Shoe editing uses verified brand/style/color ranges and artwork IDs; commercial
  style names and the exact special-family manufacturer caption are unresolved.
- 4096 is a court texture dimension ceiling, not a tested safe GPU allocation.
  Floor template preparation disables only extra floor draws, preserving arena.
- Audio has an experimental Python backend/CLI and a shared-backend Qt workspace
  for Licensed Music, Fight Songs, WAV workflows and mapped cover art. Title/artist
  editing remains unavailable because archive-only routing is unproven; EBOOT
  writes are prohibited. Unknown AUDO loops are blocked and CDF audio growth is
  unsupported. The LGPL helper package has passed Windows CI on PR #6's current
  head; it remains an unreleased branch until review and publication.
- Outputs are constrained to output/. Game assets, exported music/art, private
  paths, logs, fixtures and EBOOT are not supplied publicly.

---

Embedded source: docs/TEST_REPORT.md

# Roster / game-line / animation continuation verification

Portable final runner: **473 passed, 7 skipped, 2 deselected**. Native Windows
targeted checks: **17 passed**, including seven rendered shader paths, keyboard
warnings, exact conference-logo selection and authored line supplementation.
Read-only hidden S256 floor rendering restored two verified line draws with the
original coordinates/UVs and no OpenGL error; source SHA was unchanged. Appearance
and unknown-bit coverage checks passed. No RPCS3, EBOOT changes or testing JB.

Regressions cover UTF-16 supplementary characters, advisory warning reset,
invalid conference index rollback, protected tournament links, exact logo900+
index identity, compressed raw motion span extraction, unchanged arena/apron
geometry and no duplicate supplemental draws. Source/Qt/CLI startup, compile,
Ruff/mypy and generated documentation checks are part of the final runner.

# Combined roster/arena continuation verification

Portable runner: **461 passed, 7 skipped, 2 deselected**. Seven rendered-pixel
checks are skipped only by Qt offscreen; native Windows targeted verification:
**144 passed**, including all seven rendered shader paths. Source/Qt/CLI startup,
compilation, Ruff, mypy and handoff checks passed. Synthetic appearance tests
check shared packed-word neighbours, bounds, readback and undo for all 12 fields.
Read-only S256 hidden rendering: 119 parts, 180 lightmapped batches, no shader
errors. No RPCS3, testing JB or EBOOT edits. Proprietary fixtures stay private.

# Uniform lettering continuation verification

`python tools/dev/verify.py`: **448 passed, 4 skipped, 2 deselected**. Skips
are rendered-pixel GL checks on Qt offscreen. Compilation, CLI/Qt startup,
Ruff, mypy (11 files), handoff and diff checks passed.
Native Windows targeted check: indexed_font, scene_number_gl, scene_preview and
roster_side_panels: **128 passed**. GL tests read actual front/back/name/palette
pixels. All 101 number codes are exercised. Private read-only source inspection
and hidden rendering confirmed authored Reborn above the back number, and front
and back 23. No assets/screenshots enter Git. Inputs remained immutable.
No RPCS3/gameplay, EBOOT editing or full testing JB was performed.

# Development verification

## Roster / preview continuation checks

Final integrated `python tools/dev/verify.py`: 341 passed, 2 intentional
deselections; compile, CLI/Qt startup, lint/type and handoff checks passed.
Final targeted preview/bulk/GUI run: 27 passed. Regressions include reordered
conference references, entire long-string warning preservation, exact menu logo
ownership, game entry capacities and isolated jump-shot writes/undo. No
RPCS3, EBOOT writes or testing JB. Evidence is in ROSTER_SCALE_AND_PREVIEWS.md.
## PR #11 independent integration review — 2026-10-14

Inspected exact original head 81cd1665c26ce8798c025f5bfbd2d20f98cf213f in
an isolated checkout: 15 texture-layout tests passed. Merged v1.12 master into
the branch, resolved the changelog conflict and regenerated the shared handoff.
Added an actual DDS replacement/export check preserving the depth-one descriptor,
header and payload extent, and rejection checks for depth zero, depth two and
volume-plus-cubemap combinations. Integrated portable suite: 329 passed,
1 native-audio skip (helpers absent in this isolated checkout), 2 intentional
deselections. Compile, CLI/Qt startup, lint/type and handoff checks passed.
No RPCS3, gameplay, EBOOT edits or testing JB. Sampler runtime behavior remains
unverified; this change does not generalize to deeper volumes or DDS arrays.

## Roster scale / preview development checkpoint — 2026-10-13

`python tools/dev/verify.py`: 326 passed, 2 intentional deselections. Compile,
CLI help, offscreen Qt startup, scoped Ruff, mypy (11 files), generated handoff
and diff checks passed. The earlier targeted bulk/preview/cache/GUI run passed
13 tests; three subsequent CSV scalar-type regressions passed in the full suite.
Comparison selection survives filtering/sorting; bulk edits preserve one-step
undo, source preconditions and coupled-field rollback. The comparison uses a
table model rather than allocating a widget item for every changed cell.
CSV rejects JSON objects, arrays and booleans in scalar text/numeric fields.
No RPCS3, gameplay, EBOOT writes or testing JB build. Unfinished text-limit and
shader research remains explicitly documented in ROSTER_SCALE_AND_PREVIEWS.md.

## v1.11 side-panel and membership verification

The local source checkpoint passed 310 tests with 2 intentional deselections;
native audio coverage runs using the unchanged verified LGPL helpers. GUI/source
startup, scoped lint/type and generated handoff checks passed. New regressions
cover every category side editor, palette/coach/uniform edits, transfer/count/
row-zero handling, shared/inconsistent refusal, scoped shoe brand propagation,
18-member/full-destination behavior, undo and top/shorts texture-role/coordinate
preservation. No untested alternate-asset actions are restored.

Read-only stock checks validate all 443 school arrays/counts (maximum 18), identify
row-zero ownership, transfer/undo without player-data changes and school-only brand
propagation/undo. Actual combined jersey/shorts decode returns both roles with
separate mapped artwork. Inputs remain unchanged; no emulator, EBOOT write or
testing JB. Exact release SHA and packaged Windows checks are recorded in the PR.

## v1.10 roster usability checks

Portable suite: 296 passed, 1 native-codec skip, 2 deselected at the local
checkpoint. Source startup, scoped lint/type and handoff checks passed. Added
height/position display and numeric-sort checks, scholarship exact-mask/undo
checks, visible Player/Ratings/Scholarship tabs, equipment labels, removed-action
checks and combined Schools view. Updated existing position edit/save/reopen and
realignment interactions. Synthetic Qt visual QA checked the main roster layout;
a toolbar text-encoding issue found during rendering was corrected before release.
Duplicate equipment captions receive distinct variant labels so accepting the
current choice cannot accidentally write a different code; a regression checks this.

Read-only stock/EBOOT tracing confirms single byte positions and scholarship
polarity; the full stock roster contains 5,166 scholarship flags and 519 walk-ons.
No game input modified. Exact source SHA and Windows packaging/codec smoke results
are recorded in the PR/release metadata. No emulator or testing JB.

## Independent conference review — 2026-10-12

Original PR #8 head f38448cadd71eae38e0374517193312fd3367bbd failed the generated
handoff synchronization gate. Regenerated the snapshot and added parameterized
coverage for all 14 conference scalars: exact byte preservation, reopen, validation,
undo and negative/overflow rejection without mutation. The source offset/width
table matches the primary public `conferences.py` definition; labels remain source
labels, not independently verified gameplay semantics. No private inputs required,
emulator/gameplay checks or test JB copies. Final head/results are recorded in PR #8.
Portable checks passed 292 tests, 1 native codec skip, 2 deselected; source startup,
scoped lint/type checks and handoff synchronization passed. The native FFmpeg
helper is unavailable locally, so that skip is explicit rather than a pass.

## Conference historical fields — current branch

The supplied read-only USERDATA file was used to confirm 39 conference rows.
An in-memory model edit changed only the selected `final_fours` field byte;
model validation passed and undo restored the exact original payload. The file
was not modified or added to Git. Windows packaging completed with
`tools/rebuild/package_windows.ps1`; the packaged Qt startup and bundled LGPL
audio round-trip smoke checks passed. Conference gameplay effects are not
independently verified.

## LGPL audio packaging branch — verified PR head

Follow-up native reproduction: stereo IEEE-float WAV audio with peaks at ±1.5
encodes after raising the ATRAC frontend's finite-sample ceiling to ±4.0, aligned
with AtracDEnc's internal 1/4 scaling. Direct helper checks accepted ±4.0 and
rejected ±4.01 and NaN. `pytest tests/test_audio.py tests/test_cli.py -q`: 18 passed;
native round trips verify replacement trim to 24,000 samples and silence padding
to 60,000 at 48 kHz. `python -m compileall -q choops_py/audio_tools tests/test_audio.py`,
handoff generation, and `git diff --check` passed. The rebuilt frozen app passed
the Qt startup smoke and over-range float WAV encode/decode round trip.

Exact-head CI run 54 passed on `e149790005fdaeb14d0a1b79689d0a3de3b8f2da` on
both Ubuntu and Windows. The Windows job built the pinned LGPL FFmpeg helper and
ATRAC3 encoder, built/smoke-tested the standalone package, and printed
`Bundled LGPL audio helpers passed a synthetic WAV round trip` from the frozen
executable. Thus the packaged helper lookup, WAV resampling/encoding and ATRAC3
decode validation ran in the actual frozen app.

Local `python tools/dev/verify.py` on the previous PR head: 250 passed, 1 skipped,
2 deselected. The one skip was the native helper round trip; the two deselections
were private game/runtime checks and the optional legacy native comparison. CLI
help, Qt startup smoke, scoped Ruff, studio/service mypy, handoff snapshot,
compileall and `git diff --check` passed. The suite includes a regression that
rejects a non-RIFF/RF64 replacement before codec lookup.

Earlier Windows runs exposed and fixed an annotated-tag SHA mismatch, FFmpeg
component names/make target, a missing MSYS2 `cmp`, and the absence of conversion
filters. The final verified helper pins the peeled `n9.0.2` source commit, enables
only LGPL `aresample`/`aformat` conversion filters, and checks required codecs,
formats and filters. No emulator or testing JB was run/built. PR #6 was merged;
this follow-up is tracked in its own PR and does not create a release.

## Independent PR #5 review and continuation — 2026-10-12

Reviewed submitted head 6603d24f4d32f70abfd25e3f6770939b86f4594b in an isolated
checkout: 239 passed, 1 skipped (encoder absent), 1 failed (legacy converter
presence), 2 deselected. Reproduction tests separately showed both scene and shoe
previews opened Audio instead of Models/Courts. Navigation now uses page names;
discovery tests use synthetic files instead of excluded proprietary executables.

Continuation makes batch WAV export transactional. Regressions cover successful
publication, decode failure, cancellation, destination preservation, final sidecar
paths, shared fight-song artwork and cancelled GUI output selection. The unchanged
pinned-source encoder was enabled for an actual native WAV round trip. No emulator,
EBOOT writes or full testing JB. Final exact-head results are recorded in the PR.

The final portable continuation run passed 250 tests, 2 deselected; actual native
WAV encoding ran rather than skipping. Source GUI/CLI smoke, scoped Ruff and mypy
passed. The handoff snapshot check passed. No private game fixture was required.

## Audio workspace update — 2026-10-11

Python 3.12 x64 setup check and pinned LGPL ATRAC3 helper build completed.
Audio/CLI tests: `pytest tests/test_audio.py tests/test_cli.py -q` — 17 passed.
Qt navigation and audio-category tests: 2 passed. Full portable suite excluding
the two documented private/optional checks and the legacy converter-presence
assertion: 240 passed, 3 deselected. CLI help, Qt startup smoke, scoped Ruff and
studio/service mypy checks passed. A read-only scan of the available Vanilla JB
catalog returned 23 licensed tracks and 64 fight songs; no audio or artwork was
exported and no source was modified.

The exact `tools/dev/verify.py` run on this audio GUI head reported 240 passed,
1 failed and 2 deselected before stopping at the pre-existing
`test_bundled_paths_have_precedence` assertion. It expects the historical
`tools/gtf2dds.exe`, which is absent from the public clone and excluded from
releases. That single check is outside the audio GUI change; no proprietary
converter was fetched or substituted. The full suite with that assertion
excluded passed. No emulator, gameplay test or JB build was performed.

## Audio/handoff update — 2026-10-11

`python tools/dev/verify.py`: 240 passed, 2 deselected (private game test and
optional historical executable comparison). Source CLI help and Qt smoke passed;
scoped fatal-error Ruff, new setup script lint and GUI/service mypy passed.
`python tools/dev/setup.py --check`: installed desktop/dev dependencies imported.
`python tools/dev/setup.py --audio-encoder`: dependency install and pinned-source
native helper rebuild completed. Windows packaging and startup smoke completed;
packaged CLI help includes audio registrations. Decode/encode uses Python workspace.
`pytest tests/test_audio.py tests/test_cli.py -q`: 17 passed at this checkpoint.
Audio tests cover AUSB neighbor/prefix/tail/unknown preservation, invalid offsets/
encoded sample bounds, flat/split/inline/wrapped AUDO, blocked loop fields, catalog
artwork/category counts and native 24k mono WAV -> 48k stereo ATRAC3 round trip.
Private read-only stock catalog: 23 licensed, 64 fight, 159 total music streams.
No native decoder DLL redistribution, full bank game validation, EBOOT writes,
RPCS3 or testing JB. Exact commit SHAs are recorded in the PR/release metadata.

The full portable run exposed pre-existing invalid four-byte fixtures tagged as
TXTR and an output-safety test expecting a later error. Fixtures now use generic
CDAN where appropriate; normalization rejects truncated texture headers cleanly.
Type annotations were corrected without changing preview/staging behavior.

Historical results below remain separate observations, not current test totals.

The community roster and shoe-editing update passed 135 targeted Python/Qt
checks. Both supplied community ZIPs were loaded, edited for ratings and
player/school shoes, saved and reopened with exact payload round trips. ZIP
members other than USERDATA remained byte-exact, and original input hashes
were unchanged. Both payloads also exported to game roster IFFs and reopened
successfully. Three malformed source name strings in one input remain
unchanged warnings; changing their malformed bytes or introducing a new
invalid pointer remains fatal, including pre-existing out-of-bounds pointers.
All 90 DDS overrides for the frontend bank
compiled in memory. Zero/non-one stored depth in declared 2D textures is
covered separately from rejected volume dimensions. No JB build or emulator
test was performed.

For 2D/cubemap texture storage, the dimension selects the resource type and
effective depth is one; an unused stored depth is not a volume declaration.
The primary reference is [RPCS3's texture layout implementation](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/RSX/Common/TextureUtils.cpp),
whose image-section layout uses depth only for the 3D case. The importer now
follows that distinction and includes dimension/cube/depth values in remaining
unsupported-layout errors.

The court-template and non-stadium texture policy update passed 125 targeted
Python checks, including raw and whole-IFF normalization, paired CDF imports,
HDR preservation, multistream geometry relocation, previews, compression and
CLI registration. Real gameplay/uniform replacements were compiled in memory
and retained exact base headers after resizing. The supplied court template
retained its floor triangles and primary UVs, resolved albedo to slot 0 and
bump to slot 2, disabled the other floor draws, and ignored inactive artwork.
The source GUI passed its startup smoke check. No emulator was opened and no
JB build was produced for this update. The optional historical executable
comparison was excluded after Windows rejected its DLL relocation; built-in
conversion checks passed independently. The game's crash-free court texture
budget remains unverified.

Built-in DDS/GTF conversion is tested in both directions against generated
native-reference fixtures for L8, ARGB8, DXT1/3/5 and RGBA16F. Coverage includes
rectangular Morton order, non-power-of-two linear storage, mip chains and all six
cubemap faces. Default import/export and preview tests run without external tools.
The independent accelerated H7A codec and portable decoder agree on random,
overlapping and malformed streams. Override regression tests cover misplaced
scene folders, numeric record aliases, Windows copy suffixes and explicit reports
for DDS files requiring a missing replacement scene.

Local checks exercised the synthetic parser/writer, Qt navigation/edit/save, actual Windows converter, interruption cleanup, source preconditions, malicious ZIP rejection and cross-part copy/patch workflows. Private read-only game integration and separate generated-output verification also ran; environment-specific results are excluded from public documentation.

Commands: pytest, compileall, CLI --help, studio --smoke, studio --verify-game --game PRIVATE_PATH, Ruff and mypy on the new studio/patch-package modules. Test groups distinguish unit, integration, gui, windows and real_game. Public CI must skip the private fixture when absent. Converter tests use generated inputs.

Initial Ubuntu CI exposed missing libEGL.so.1; the workflow installs the required Qt runtime libraries and allows both platforms to complete independently. The corrected prior CI commit passed Windows/Linux and standalone packaging. Subsequent code requires its own observed checks.

Original files were read only; output patch and untouched ranges were verified separately. Runtime PS3/RPCS3 verification: NOT RUN. Unsupported layouts, geometry import/export and unknown roster semantics remain documented limitations. This is not completion or publication of v1.0beta.
The DDS importer now treats dimension-3 TXTRs with stored depth one as
single-slice storage and continues to reject deeper volumes. The existing
volume fixture now covers acceptance at depth one and rejection at depth two.
Automated checks were not run for this change; no RPCS3 or gameplay validation
was performed.

## Override-folder selection regression

Python 3.12.14 on Windows: tools/dev/verify.py passed with 464 tests, 7
offscreen GL skips and 2 deselected checks. Compile, CLI/Qt smoke, Ruff, mypy,
handoff and diff checks passed. Targeted override tests: 26 passed. Repeated
selection preserves previous snapshots, skips occupied numbered workspaces,
compiles current artwork, cleans only its failed temporary workspace and updates
GUI build/preview destinations together. No RPCS3 or automatic/testing JB build.
Current continuation: 482 portable tests passed, 9 offscreen GL skips, 2 deselected; 28 native targeted checks passed after them. Guide tests verify flat colour with transparent textures, zero palette tint, glow mode and both automatic/manual texture selection. Runtime BE text tests independently check field+delta-1 and save/reopen/undo. No RPCS3 or JB build.

Combined v1.14 preview release checks: 491 portable tests passed, 9 offscreen OpenGL skips, 2 deselected; 37 native Qt/OpenGL targeted checks passed. Direct jersey launch, captured source/override stadium selection, scene-mode identity and reload behavior are covered. No RPCS3 or JB build.

v1.14.1 preview source/list hotfix: 493 portable tests passed (9 offscreen GL skips, 2 deselected); 17 native direct-preview/GL checks passed. Read-only stock S258 floor preview returned five parts and twelve textures; source hash unchanged. Shared source dropdown and pick-only category lists have regression coverage. No RPCS3 or JB build.

Additional hotfix regression: global source switching preserves the active texture category rather than navigating to a prior 3D view. Final full suite: 494 passed, 9 offscreen GL skips, 2 deselected; nine direct-preview checks passed.

Final v1.14.1 native preview/GL/roster-scale GUI suite: 22 passed. Packaged Windows startup and synthetic audio round-trip passed. Verified v1.13 audio helpers and matching source/licence archives reused.

## v1.15 override-source refresh

Final Windows Python checks: 497 passed, 9 offscreen GL skips, 2 deselected.
Native override/direct-preview/GL checks: 24 passed. Compile, CLI/Qt smoke, Ruff,
mypy, handoff and diff checks passed. Regression covers already-selected override
mode during the worker result callback, queued preview reload, preservation of
JB fallbacks, visible workspace versus stale cached path, and unavailable badges.
Read-only supplied-folder discovery resolved 1,824 archives, including S258;
existing workspace had 1,825 replacements. Native GUI list verification showed
354 stadium and 727 uniform overrides. No shoe packages were supplied. Names and
contents of user inputs were unchanged. No RPCS3 or automatic/testing JB build.

## Final v1.15 Explorer/cache/CSV verification

515 portable tests passed (9 offscreen GL skips, 2 deselected), with compile,
CLI/Qt smoke, Ruff, mypy and handoff checks. Native targeted suite: 41 passed.
Hidden Explorer loaded the supplied SELUH258 override, showed five records and
full roster references, and rendered its texture without errors. Read-only
S258/SELUH258/UH258 override inspection and DDS preview decoding also passed.
Cache tests retain both source variants, invalidate modified inputs, reject
altered replacement payloads and enforce the image-memory bound. DDS tests skip
a broken raw TXTR when DDS exists and correctly use TXTR when DDS is absent.
CSV tests exclude injected UI metadata and reject unsupported import fields
without changing roster bytes. No RPCS3, game launch or automatic/testing JB.

## v1.15 explicit roster I/O and release verification

`python tools/dev/verify.py`: 519 passed, 9 offscreen OpenGL skips,
2 deselected; compile, CLI/Qt smoke, Ruff, mypy and generated handoff passed.
New regressions cover edited external IFF to USERDATA/IFF round trips, immutable
source payloads, invalid-roster rejection, explicit JB/override source selection,
missing override roster rejection and IFF export without a loaded JB.
Native Windows targeted preview, cache, CSV and roster I/O suite: 45 passed.
Windows packaging additionally runs frozen startup and synthetic audio round trip.
No emulator/gameplay tests or automatic/testing JB builds are performed.

## v1.15.1 preview resizing

18 native direct-preview/OpenGL regressions passed. Hidden Windows Qt resize
check confirmed a 1,364-pixel-wide viewport and dragging the divider changed its
height from 255 to 120 pixels without hiding controls. Qt startup, Ruff and
diff checks passed. No RPCS3 or testing JB.

Full `python tools/dev/verify.py`: 519 passed, 9 offscreen GL skips,
2 deselected; compile, CLI/Qt startup, Ruff, mypy, handoff and diff checks passed.

## v1.15.2 live preview reproduction

Read-only S258 reproduction found a prepared snapshot's old floor image while
current loose inputs compiled the Dayton court. The actual live PreviewArchive
and stadium path now decoded that current 1024 x 512 preview with two floor mesh
parts; unchanged materialization reused its cache. Source inputs were untouched.
Synthetic regression verifies stale snapshot replacement, loose file edits,
cache invalidation, source immutability and missing-file rejection. No JB build.

Final portable suite: 520 passed, 9 offscreen GL skips, 2 deselected.
Native source/preview/OpenGL suite: 36 passed. Compile, CLI/Qt smoke, Ruff,
mypy, generated handoff and diff checks passed. Windows package startup/audio
smoke runs before publication.

## v1.15.3 frontend import reproduction

Read-only frontend_sync import reproduced the false texture/geometry overlap.
Header-relative streams had flag 0x40000002, pointer 5, valid header vertex floats
and header-relative 16-bit indices (flag 0x10). GPU menu streams use 0x40000003
and index flag 0x20000010. The fix imported frontend_sync successfully in memory.
Synthetic tests preserve both inline vertex streams and indices through image
packing, preserve GPU menu relocation, and reject real overlaps, invalid ranges
and changed inline geometry. No RPCS3 or automatic/testing JB build.

`python tools/dev/verify.py`: 523 passed, 9 offscreen GL skips, 2 deselected.
Compile, CLI/Qt smoke, Ruff, mypy, handoff and diff checks passed.

The broader check passed 13 of 14 non-stadium scene groups and exposed a second
studio cubemap mismatch. Added a guarded legacy first-face import: regression
checks retain the original descriptor and five other DDS faces exactly, with
strict rejection retained for direct imports without this legacy policy.

Final complete suite: 524 passed, 9 offscreen GL skips, 2 deselected;
51 targeted import/packing/live-preview checks passed. Actual studio import
completed with +X updated and five source faces preserved.

Final read-only supplied-input run: all 14 non-stadium SCNE groups compiled
successfully together, zero failures. Legacy cube handling is isolated in its
own module so unchanged ordinary conversions retain their cache identities.
The final portable verification command passed all 524 tests again.

## Parallel override preparation

Windows spawn tests compare deterministic manifests and archive bytes between
serial and two-worker preparation. Tests cover CPU/RAM limits, unchanged reuse,
changed-input invalidation, tampered cached output, worker failure/cancellation
and child cleanup, plus source/frozen module fingerprinting.

Read-only benchmark: 14 actual scene groups / 612 DDS inputs, warm conversion
cache, final run: serial 24.838 s, six workers 10.008 s, unchanged repeat
6.676 s (2.48x parallel speedup). An earlier run measured 3.08x.
All output archive checksums matched. Benchmark scratch was removed.
No RPCS3 or real JB build.

Frozen Windows EXE: three synthetic DDS overrides prepared with three spawned
workers, then all three completed archives reused on repeat. Distinct texture
outputs and source-bound manifests verified; owned smoke fixtures removed.
Packaged Qt startup and synthetic audio round-trip also passed.

Final `python tools/dev/verify.py`: 530 passed, 9 offscreen GL skips,
2 deselected. Compile, CLI/Qt smoke, Ruff, mypy, handoff and diff checks passed.
Final frozen EXE test repeated successfully with three workers and three reused
archives; startup/audio smoke passed.

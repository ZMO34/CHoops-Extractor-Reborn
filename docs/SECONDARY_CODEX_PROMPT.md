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

# Unreleased — editable garment meshes and modern-fit experiment

Models / Courts has source-aware uniform OBJ collection export, guarded reimport
and a conservative modern-fit preset. Actual source inventory covers 21 cloth
IFFs / 33 SCNE–Clth pairs: all five necklines and thin/regular/fat builds, plus
three shorts builds, including individual and aggregate container routes.
The preset shortens shorts by 20% and tightens the jersey torso by up to 7%.
Source assets stay immutable. Rest XYZ is updated in SCNE and matching Clth;
topology, UVs and all other attributes/unknown data are preserved.

This is an experimental rest-shape workflow. Native packed cloth constraints,
body collision and normal/tangent regeneration remain unresolved; static output
does not certify animation/fit. No NBA cloth writer or new topology. See
[uniform mesh evidence and editing instructions](UNIFORM_MESH_EDITING.md).

# v1.19 rebuild compatibility follow-up

Folder DDS imports now consistently support a flat image targeting an existing
cubemap in both legacy and Python-manifest paths (standard IFF and CDF). This
updates +X and preserves the other five base faces; complete cubes still replace
all six faces. Direct texture editing remains strict. Reports identify +X imports.
No cube flag is removed and no 2D image is duplicated across the other faces.

IFF failures now identify archive, input role and magic, with corrective GUI
advice. Invalid containers remain rejected; opaque bytes are not guessed/repaired.
The legacy Reborn Overrides V5.5 layout is recognized through direct numeric
source-TOC folders, including nested TXTR/DDS artwork and complete IFF replacements.
Its `icon_tatoo` record spelling maps to the source's `icon_tattoo` record. Raw
`.bin` replacements such as `cribmusic.bin` retain their bytes without IFF parsing.
The supplied frontend_sync/legalpage ZIP passes preparation and build preflight
against original 2K8. The locally supplied halftime complete HDR cube preserves
all supplied artwork, scene headers and image capacity. Original inputs unchanged.
The exact supplied ZIP also passes preparation/preflight in an isolated v1.16
checkout. Its generic screenshot failure is not reproduced; the offending input
or differing source/workspace is still needed to establish that specific cause.
No RPCS3 or real/testing JB. Integrates research PR #28; no animation port added.

# v1.18 foundation (retained context)

This release integrates the NBA support/split-header repair from PR #25 and the
key/center-circle court guide from PR #26, then refreshes the public documentation.
The [support matrix](FEATURE_MATRIX.md) is the concise contract. Earlier status
entries are preserved in [history](history/STATUS_THROUGH_V117.md).

## Delivered

- Automatic observed College Hoops/NBA archive layouts; read-only NBA 2K14 SDAT
  banks, authenticated reads, extended descriptors and supported ZLIB IFF blocks.
- Separate detected NBA 2K9/2K14 roster side editors with confirmed fields,
  preserved wrappers/unknown bits, undo/redo and guarded text writes. College Hoops
  remains a distinct model with broader ratings/CSV/comparison tools.
- Split-bank archive header/TOC reading and append/repack preservation. Missing or
  truncated banks retain exact expected/actual details. GUI override/build errors
  include persistent Problem / Suggested fix / Details guidance.
- Independent thin court reference toggles: border, 3-point and key/center circle.
  Authored stock geometry is raised one game unit; actual floor rendering is untouched.
- Documentation index, practical workflows, troubleshooting, per-game matrix,
  testing map and release procedure. Historical status/results separated; stale
  dependency snapshot/unpublished beta draft removed; wrapper test consolidated.

## Still unresolved

NBA 2K14 authenticated JB writing/signature generation, complete NBA ratings and
text growth, all College Hoops unknown bytes, universal engine text ceilings,
complete runtime shader/palette modes, newer cloth/jersey artwork binding and
validated cross-game animation porting. College Hoops has no independent secondary
position field established; do not confuse NBA evidence with that schema.
No new alternate assets or removed D1 actions are added.

## Verification and maintenance

See [TEST_REPORT.md](TEST_REPORT.md) and the release PR for exact-head results.
Only synthetic fixtures, Qt/CLI/frozen smoke and read-only research are used.
RPCS3/gameplay NOT RUN; real/testing JB NOT BUILT; EBOOT NOT EDITED.
Both Codex instances must maintain current docs and the generated handoff on each
update. Document evidence and unknowns; never replace uncertainty with a label.

## Research follow-up — modern features

[Backport feasibility](MODERN_FEATURE_BACKPORTS.md) ranks practical artwork/roster
updates, 2K9 animation conversion, broadcast bindings and indirect companion ideas.
No backport is implemented; modern runtime features remain distinct from assets.

---

Embedded source: docs/FEATURE_MATRIX.md

# Current support matrix — v1.18

Supported means structurally verified by parsers and automated fixtures. No row
certifies game/runtime compatibility. Unknown variants fail explicitly.

| Operation | College Hoops 2K8 PS3 | NBA 2K9 PS3 | NBA 2K14 PS3 |
| --- | --- | --- | --- |
| Archive detection, listing, extraction | Supported observed layout | Supported observed layout | Supported observed SDAT/72-byte descriptor variant |
| IFF/CDF, texture inspection | Supported known layouts | Supported known layouts | Supported known layouts, including observed ZLIB blocks |
| DDS overrides / static preview | Supported known layouts | Supported known layouts | Preview/preflight supported; some newer mesh/UV bindings unavailable |
| Manual fixed/growing/repacked JB output | Supported layout, synthetic verification | Supported layout, synthetic verification | Blocked: authenticated SDAT/extended writer not established |
| Roster identity | College Hoops schema | Separate NBA 2K9 schema | Separate NBA 2K14 schema |
| Roster editing | Confirmed names, ratings, appearance, history, palettes, footwear, assignment | Confirmed numeric/text fields only | Confirmed numeric/text fields only, including observed secondary position |
| CSV / selective comparison import | Supported confirmed College Hoops fields | Not a general NBA bulk editor | Not a general NBA bulk editor |
| Full unknown-byte semantics / engine ceilings | Incomplete; unknown bits retained | Incomplete | Incomplete |
| Animation banks | Inventory/research | Inventory/portability research | Inventory/portability research |
| Uniform geometry editing | Experimental source-bound OBJ/rest-position workflow; known cloth only | Unsupported | Unsupported |

## Shared features

- Explorer reads nested records and researched asset references; labels never make
  an unknown hash an established semantic identity.
- Source and overrides are cached concurrently. Global preview selection resolves
  geometry and artwork; DDS takes priority only within overrides, with TXTR fallback.
- Static preview camera supports orbit, look-around, pan, WASD movement and fit.
  Combined jersey/shorts and cut/neck controls use supported authored meshes.
- Court guides are separate raised thin references. Border, 3-point, key/center
  toggles do not modify floor textures or depend on roster palettes.
- Supported College Hoops jersey previews draw authored numbers 0–99 and the
  supported Reborn surname preview. Runtime cloth/skinning is not simulated.
- Audio WAV replacement can queue multiple songs before saving cribmusic.bin.
  Song names/artists are read-only. Licensed music/fight songs are separated.
- GUI repair diagnostics identify the target and compatible next action. Larger
  payloads still require known relocation/pointer semantics; arbitrary growth is
  not automatically safe.

## Excluded or unresolved

No alternate-asset creation, automatic D1 conversion, EBOOT editing, animation
port, encrypted-save decryption, universal NBA roster fields or full arena shader
emulation. Unknown reflection/fake-bump/AO/runtime palettes and universal text
ceilings remain unestablished. See [limitations](KNOWN_LIMITATIONS.md),
[NBA details](NBA_ROSTERS_AND_2K14.md) and [shader evidence](ARENA_SHADER_MASKS.md).

---

Embedded source: docs/WORKFLOWS.md

# Practical workflows

## Edit uniform fit

Use Models / Courts > **Uniform meshes…** to export all supported garments or
prepare the experimental modern-fit collection. OBJ cages and originals remain
separate from ready IFF overrides. Reimport validates topology, UVs, source hash
and cloth seam correspondence. The [mesh workflow](UNIFORM_MESH_EDITING.md)
documents CLI commands and unresolved runtime cloth/collision behavior.

## Select a game and overrides

Open the source JB, PS3_GAME or USRDIR in Explorer. Detection is based on verified
container structure, not a user-selected game mode. Keep every required split
bank available together. For SDAT input, extraction is authenticated and bounded;
a successful read does not imply the editor can sign/rebuild that container.

Choose **Select overrides folder** in Explorer. Discovery is recursive and handles
supported current and legacy rip structures, including V5.5 exports whose top-level
numeric folders are source archive TOC indices. Keep those folder names intact.
Geometry SCNE replacements override
vanilla SCNE records; corresponding DDS artwork wins over TXTR artwork. A TXTR
is used when its DDS does not exist. This preparation resolves identities,
validates layouts and caches conversions; it does not create the game output.
Do not rename unrelated files merely to bypass an ambiguous selector error.
Opaque `.bin` replacements are preserved as binary payloads and are not parsed as IFF.

Selecting unchanged sources reuses cached work. Source metadata changes invalidate
matching entries, and content/conversion keys protect supported prepared operations.
Timestamps are not a general proof against deliberately timestamp-preserved changes;
reselect edited input and investigate unexpected fallback before building.

## Preview the intended artwork

The top **Preview source** dropdown applies across model categories. Choose Source
JB to inspect the original, or Selected overrides to resolve replacement geometry
and textures. The asset lists in Jerseys, Shoes and Stadiums/Floors avoid manual
IFF-name entry. A fallback label means a matching replacement was not resolved;
it does not mean the override artwork has been loaded.

Select an asset and press its preview button. Use the neck/build/shorts/render
controls for supported combined uniforms, and Floor only for court inspection.
Roster palettes require a unique confirmed association or an explicitly selected
matching roster. Unassociated meshes use embedded material artwork.

Drag the pane splitter to resize controls versus the preview. Left-drag orbits,
right-drag looks around, middle-drag or Shift-drag pans; WASD moves, Q/E moves
vertically, Shift/Ctrl changes speed, wheel zooms and F fits the camera.
For full-court texture alignment, independently enable border, 3-point and
key/center-circle guides. They are fixed stock court references raised one game
unit, not boundaries inferred from the apron edges and not exported artwork.

## Edit and compare rosters

Load from JB, load from selected overrides, or open an external supported IFF,
raw ROST/decrypted USERDATA or supported save wrapper. Encrypted saves need an
external authorized decryption step. Format detection chooses the schema; do not
apply College Hoops offsets to an NBA roster.

Select a row for its side editor. Double-click writable values. Confirmed choices
use readable labels; unknown values are preserved rather than guessed. College
Hoops ratings support copying to selected players, CSV export/import review and
selective comparison. Retain CSV identity/safety columns and import only compatible
edits. UI/research references are excluded from game-data CSVs.

School transfers use guarded slot/count updates. A school shoe-brand change
propagates only to that school's players. Export a copy in the requested supported
IFF/save format, reopen it and inspect the result. Names exceeding established
keyboard capacities get orange warnings where mapped; an unknown limit is not
inferred from the old string's length. NBA text growth/shared storage has separate
restrictions documented in NBA_ROSTERS_AND_2K14.md.

## Replace soundtrack audio

Use Audio's Licensed Music or Fight Songs subsection. Export WAV to inspect the
supported stream. Queue/import multiple songs before saving the rebuilt
cribmusic.bin; review each queue item and save to a separate output. The licensed
Windows helpers handle the supported WAV/ATRAC3 path. Keep their corresponding
source archives and notices with redistributed binaries. Names/artists remain
read-only; cover-art actions operate only on established mappings.

## Build manually and inspect the report

For a supported writable source, prepare overrides, choose a **new empty output
folder** in Mod Builder and start the build. Destinations can be on another drive
but must not overlap source/mod data or overwrite an existing build. The tool
validates records, source preconditions, sizes and relocation support, copies to
transactional output, verifies generated/preserved bytes and publishes on success.
Read the GUI summary for replacements, resizing and compatibility problems.

Non-stadium artwork is normalized to the selected base layout where required;
stadium assets can grow only through supported writers. No universally safe maximum
GPU texture size has been certified. The editor rejects unknown layouts instead
of treating a successful DDS decode as proof of game compatibility.
No agent creates a real testing JB or launches RPCS3. The user chooses when and
how to test the manually built output.

---

Embedded source: docs/TROUBLESHOOTING.md

# Troubleshooting

Start with the persistent GUI **Problem / Suggested fix / Details** report. Keep
the exact named archive, record selector and expected/actual sizes in a bug report.
Do not replace a structural error with guessed identities or silently skipped bytes.

| Symptom | Meaning / next step |
| --- | --- |
| Incomplete archive header | Check all split banks and their names/sizes. The current reader follows header/TOC boundaries across banks. Restore a truncated or missing bank from the original; send the named details if it persists. |
| Geometry overlaps a texture image | The replacement image/geometry ranges cannot safely coexist. Use the reported record to check its SCNE and image layout; preserve the originals. Supported relocation is format-specific, not a blanket permission to overlap. |
| Unknown/ambiguous record or no unique archive record | The selector matches none/multiple destination records. Verify the correct source JB and rip identity, nested name/hash and CDF partner. Do not rename every record to a generic logo. |
| No archive folder for a numeric V5.5 path | Update Studio and select the folder against the matching vanilla JB. Numeric folders map to source TOC indices, so keep the original numeric folder names and use the correct source archive. |
| Not a standard PS3 IFF | Read the archive name, source/replacement role and hex magic. Raw TXTR/SCNE records belong under their archive record folder, not renamed to complete .iff files. Restore damaged containers from the same rip. |
| Base cubemap faces error | Update/reselect overrides: flat folder DDS imports update +X and preserve five base faces, including manifests. For complete replacement use a six-face cube. Direct texture imports remain strict. |
| Unsupported texture layout | Confirm 2D or a supported complete cube. A stored depth-one volume has specific support; true deeper volumes, DX10/arrays and unknown encodings remain restricted. |
| Overrides show JB fallback | Check the chosen root, recognized archive/SCNE structure and matching selector. Reselect after edits and inspect diagnostics. DDS must belong to the resolved override record. |
| Old artwork despite replacement | Check both selected SCNE and DDS paths, the global source dropdown and fallback labels. Compare source vs override, not just the IFF display name. Report the specific asset/record and folder structure. |
| Preparing DDS appears slow | First import validates/converts many images. Bounded workers and caches accelerate subsequent unchanged selections. Check progress/target details; do not assume loading archives performs the same work. |
| Output directory rejected | Use a new empty folder outside source, overrides and prepared workspace. Both parent/child overlap and overwrite are guarded; choose another drive if free space is insufficient. |
| NBA 2K14 build blocked | SDAT read support does not provide authenticated write/signing support. Extraction/preview is available; do not remove this guard to produce an invalid game. |
| Roster edit blocked | Confirm schema, pointer validity, wrapper and shared-string constraints. Previously observed bad characters are distinguished from newly introduced damage. Unknown bits remain opaque. |
| Orange name outline | Text exceeds a confirmed game keyboard capacity for that field. Review it; capacity is measured in the documented encoding/units, not arbitrary old allocation size. |
| Audio helper missing | Extract the full release. Source developers must build the pinned LGPL helpers; no proprietary DDS executable is required. |
| Windows app fails after copying just EXE | Restore the entire ZIP, including `_internal`. CLI smoke and audio smoke can separate Qt/runtime and codec failures. |

## Useful evidence for a bug report

Include version/source commit, operating system, game/title ID and detected layout,
workflow steps, exact error text and relevant small metadata. State whether the
preview is source/overrides/fallback and whether input was recently changed.
Do not upload game banks, copyrighted audio/art, credentials or private save data
to a public issue. Prefer a minimal synthetic reproduction. Logs/screenshots may
contain private paths; redact them before posting.

## Recovery

Original game/override inputs should remain unchanged. Keep your manually exported
roster/texture copies and any user-created builds. A failed/cancelled transactional
build should not be treated as a completed output. Report unexpected leftover
folders before deleting them; never bulk-delete a research directory to clear a
cache. The project does not launch RPCS3 for diagnosis or patch EBOOT.

---

Embedded source: docs/TESTING.md

# Testing and regression maintenance

## Reproducible portable checks

```powershell
python tools/dev/setup.py
.\.venv\Scripts\python.exe tools/dev/verify.py
```

The runner checks generated handoff freshness, compiles Python, runs synthetic/Qt
pytest cases, CLI help, offscreen GUI startup, fatal-error lint, scoped typing and
diff whitespace. CI runs on Windows and Linux. Capture the exact commit, command,
pass/skip/deselection counts and unavailable dependencies in TEST_REPORT/PR.

Before reviewing another PR, inspect its diff/dependencies/scripts, then test the
exact head in an isolated checkout. Use `--python` with an existing environment
when appropriate; ensure imports resolve to that checkout. New commits invalidate
old exact-head evidence. Public jobs must not receive private games or tokens.

## Regression map

| Risk | Main test modules |
| --- | --- |
| Split banks, TOC layouts and opaque header bytes | test_dynamic_2k_archives, test_split_archive_header, test_archive_identity |
| SDAT authentication/read boundaries | test_sdat_2k14 |
| Newer IFF/ZLIB/scene descriptors | test_nba14_formats, test_standard_iff, test_compression_rebuild |
| Transactional output, relocation, preserved bytes | test_modding, test_build_streaming, test_asset_insertion |
| DDS layouts, CDF/SCNE packing, overrides | test_builtin_conversion, test_runtime_texture_layout, test_scene_image_packing, test_cdf_folder_import |
| Concurrent preparation and cache/source routing | test_parallel_overrides, test_cache, test_live_override_previews, test_preview_source_caching |
| Roster bits, wrappers, identity and batch review | test_roster_editor, test_roster_semantics, test_roster_bulk, test_roster_csv_fields, test_nba_rosters |
| Side editors, school assignment and footwear | test_roster_side_panels, test_school_assignment, test_shoes |
| Reference guides and authored uniform artwork | test_scene_palette, test_jersey_preview, test_uniform_preview, test_scene_number_gl |
| Audio queue/writers and output destination | test_audio, test_audio_batch, test_audio_queue_build_outputs |

Read the code for fixture-specific scope; a suite name does not imply all semantics
are understood. Keep rejection, untouched-byte, aliasing, rollback and cancellation
coverage when consolidating modules. In v1.18 the small wrapper regression moved
into test_binary.py; no assertions were discarded.

## Optional and forbidden checks

`real_game` and `runtime_manual` markers and the optional legacy native comparison
are excluded by the portable runner. Offscreen OpenGL, absent native codecs and
private fixtures may explicitly skip. A skip is not a pass. Read-only supplied-input
checks may inspect archives/metadata and in-memory round trips without modifying
originals. Never run verify_game.py --build, create a full automatic/testing JB,
launch RPCS3 or edit EBOOT. Tiny synthetic archive fixtures are allowed.

## Windows package verification

Use the exact release commit. Run packaged `--smoke`, `--audio-codec-smoke` and
`--cli --help`. Test extraction/format paths using read-only supplied or synthetic
inputs. Check source-schema handling and preservation with synthetic builders,
not a copied game. Validate the ZIP after creation, include its SHA-256, and pair
LGPL helpers with exact matching sources/notices. Record what was skipped.

## Cleanup policy

Remove superseded generated logs, bytecode/pytest caches and owned temporary review
checkouts only after checks finish and required evidence is recorded. Resolve and
check absolute paths before recursive removal. Preserve regression tests for
supported legacy formats, real user overrides/builds, private evidence and original
game files. Do not delete a test just to make a failure disappear.

---

Embedded source: docs/RELEASING.md

# Windows and GitHub release procedure

## Prepare a reviewable source update

1. Fetch canonical master and inspect open PRs, discussions and dependency changes.
   Work on a release branch; integrate only owner-authorized, reviewed changes.
2. Update `choops_py/__init__.py` and `pyproject.toml` to the same version. Maintain
   CURRENT_STATUS, FEATURE_MATRIX, affected user/format docs, CHANGELOG and test
   evidence. Keep unresolved semantics explicit.
3. Run `python tools/dev/handoff.py`, then portable verification. Commit the final
   source and test its exact head in an isolated checkout. Publish a PR with SHA,
   commands/results, skips, risks and next action. Attach it to the active chat.
4. Check Windows/Linux CI and review threads. Merge only with owner authorization;
   release authorization in a user request can cover that specific release.

## Build Windows x64

Use the repository's Python 3.12 x64 development environment with PySide6,
PyInstaller and declared dependencies, including PyCryptodome for SDAT reads.
`tools/rebuild/package_windows.ps1` builds an onedir bundle, applies the Qt ICU
compatibility check, includes required data and native helpers, and runs startup
and audio round-trip smoke. Build pinned audio helpers using the documented codec
scripts first. A trusted previously released helper may be reused only with its
exact matching corresponding sources/notices and recorded provenance.

Keep `_internal` with the executable. Include current documentation at its original
relative paths so links work, README-START-HERE, BUILD-INFO with source commit,
THIRD-PARTY-SOURCES and applicable notices. Do not bundle private inputs, game
assets, settings, logs, development virtualenvs or proprietary DDS converters.
Source DDS conversion is built in. Exclude unneeded Qt/browser modules and PyAV.

## Validate and publish

- Run the frozen GUI/CLI/audio checks and bounded synthetic format/writer tests.
  No RPCS3 or real/testing JB. Confirm the version and SDAT/other optional imports
  are collected; startup alone does not test a lazy-loaded module.
- ZIP the complete app directory, test ZIP integrity, inspect entries for private
  data, and calculate SHA256SUMS.txt. Record source head, size and digest privately
  and in durable release evidence where appropriate.
- Tag the exact tested source commit (or an identical merged tree with explicit
  provenance). Create a draft release with honest features, limitations, commands
  and counts. Upload the Windows ZIP/checksum; verify uploaded size/digest.
- Publish only after source, CI, package and license gates pass. Link merged PRs
  and release in handoff comments. Both instances maintain this procedure.

Do not regenerate a package from an uncommitted tree or label a parser-only result
as gameplay certification. Preserve published releases unless a specific owner
request calls for removal. Cleanup local intermediates after successful publication;
keep the delivered package/checksum and avoid deleting user builds/research.

---

Embedded source: docs/PS3_2K_ARCHIVES.md

Current NBA extension: see [NBA roster/container support](NBA_ROSTERS_AND_2K14.md) and
[animation portability research](ANIMATION_PORTABILITY.md). Those pages define the
newer per-game boundaries; historical College Hoops-only statements below remain
specific to that earlier scope. NBA 2K14 SDAT rebuilding and complete NBA ratings
semantics are not implemented.

# Shared PS3 2K archive support

The editor automatically detects supported archive layouts when opening a JB or
USRDIR folder. There is no game-mode selector. Game title/ID are read from optional
PARAM.SFO for display; they never determine the binary TOC layout. College Hoops
2K8 roster editing and its confirmed rendering features remain available. A known
other title is not automatically decoded with the College Hoops roster schema.

## Confirmed outer layouts

Both supplied games use magic AA00B3BF, a 24-byte big-endian header, 16-byte bank
descriptors, 2,048-byte alignment and 16-byte asset entries. Banks are concatenated
logically; an entry may cross bank boundaries. The entry order differs:

| Byte | College Hoops 2K8 layout | NBA 2K9 layout |
|---|---|---|
| 0..3 | filename CRC32 | stored byte length, high 32 bits |
| 4..7 | sector offset | stored byte length, low 32 bits |
| 8..11 | preserved flags | filename CRC32 |
| 12..15 | stored byte length | sector offset |

The detector validates both candidates against the full TOC, unique hashes,
header/neighbor/bank boundaries and stored lengths. Exactly one candidate must be
valid; ambiguous/unknown layouts are rejected. College Hoops' existing derived
extent fallback and rounded extraction behavior are retained. The size64 layout
uses exact stored lengths. Writers serialize TOC rows using the detected source
layout for in-place builds, growth/append and bank repacking. Header/flags/opaque
padding, unknown resources and untouched files keep their preservation checks.
The raw 64-bit size is not truncated to a 32-bit field.

Other PS3 2K games may work automatically if they use a supported layout and inner
formats. This is not a claim that every game/year/platform is compatible. New or
ambiguous layouts require evidence and fixtures; do not add filename/title guesses
or silently reinterpret an unknown format.

## NBA 2K9 supplied-copy observations

Read-only inventory: 6 banks, 6,158,907,392 bytes, 5,624 entries, no overlaps.
945 outer filenames match the existing hash dictionary; those remain candidates,
not new globally verified name assignments. Source game ID is BLUS30197.

| Stored resource signature | Count | Handling |
|---|---:|---|
| FF3BEF94 | 3,171 | Standard IFF, existing readers |
| F0985030 | 46 | CDF-backed IFF metadata; preserve linked CDF |
| 01 + 0E4837C3 | 2,322 | Flagged H7A resource; exact raw extraction |
| 0E4837C3 | 15 | Compressed header/prefix and possible following data; raw preservation |
| Other | 70 | Exact raw extraction; unsupported inner decoding stays explicit |

A sampled flagged H7A resource decoded to non-IFF data. Do not strip the flag and
assume all 2,322 entries are complete compressed IFFs. Their wider purpose and
possible references are not fully established. No archive resource is automatically
unwrapped/rebuilt based on this signature alone.

Selected exact extractions: ua000.iff, uh000.iff, s000.iff, gamedata.iff, global.iff,
teamselectlogo.iff and its linked teamselectlogo.cdf. All blocks in the five standard
IFF samples decoded to their declared lengths. Uniform TXTRs, stadium TXTRs and
shared gamedata/global artwork converted to valid DDS images with existing code.
The menu-logo pair parsed 71 texture records and exported a 512x512 DXT5 DDS.

The shared preview services decoded:

- Jersey + shorts: 2 meshes and 2 authored images, using existing cloth packages.
- Floor: 2 meshes and 2 images, no parser warnings.
- Arena: 78 meshes and 58 images, no parser warnings.

These are static authored previews, not runtime/gameplay certification. NBA number
placement, roster semantics, animation/skinning, dynamic shaders and all unknown
resources have not been generalized. College Hoops' fixed S256 alignment guides
are not injected into another game's floor preview.

## Shared inner readers

IFFs without a tool-generated name trailer can recover a small set of shared
internal names from case-sensitive CRC32 IDs: arena, floor, uniform artwork,
jersey/shorts cloth shapes and numbered logos. Unknown IDs remain numeric and
unknown types remain unknown. Authored name tables still take precedence.
CDF metadata recognizes the standard TXTR hash as well as the older CDF variant.
SCNE previews accept declared half4/float4 UV fields (first two UV components) and
half4 vertex colors; complete declared attribute extents stay bounds checked.
The NBA arena's half4 declarations are the read-only evidence for this extension.

Asset caches include the detected TOC schema. Frozen importer fingerprints include
the shared layout and record-label modules, so changed readers invalidate prepared
results. Source and override toggles keep the same detected schema and game identity.

## Editor and research usage

Open the NBA JB folder through the existing source-folder action. Use Explorer,
Texture Editor, Models / Courts, Select overrides folder and Mod Builder normally.
There is no new game mode. Unresolved extracted IFFs keep a hash-based .iff filename;
non-IFF resources remain .bin. Load source rosters only for a confirmed schema.

For a separate read-only inventory/extraction command, from the repository root:

```powershell
python -m choops_py.research.nba2k9 "NBA_JB_ROOT" output/research/nba-inventory
python -m choops_py.research.nba2k9 "NBA_JB_ROOT" output/research/nba-samples --extract ua000.iff uh000.iff s000.iff gamedata.iff global.iff teamselectlogo.iff
```

Selectors also accept `index:1045` or `hash:0x30f9aaf9`. Indices are input-specific;
use names/hashes for repeatable selection. This command auto-includes a CDF
metadata file's linked payload, checks its filename/CRC and publishes a new output
folder only after source metadata and written SHA256 checks. Existing output is
never overwritten. `--all-iff` explicitly exports all direct IFFs and linked CDFs;
this can use several GiB. It does not pretend unknown GPU/resource streams are IFFs.

Read-only planning also accepted a larger uniform-IFF replacement against the
supplied NBA TOC, preserving its size64 schema and source inventory. It created
no output banks. Raw extraction is byte preserving; rebuilding tests use synthetic
archives only.
No supplied JB was rebuilt, no EBOOT was edited and RPCS3 was not opened.

---

Embedded source: docs/NBA_ROSTERS_AND_2K14.md

# NBA PS3 support and roster evidence

## Verified scope

College Hoops 2K8 keeps its existing editor. Roster payload detection now selects
separate NBA 2K9 or NBA 2K14 schemas automatically for raw ROST, standard IFF,
length-prefixed decrypted USERDATA and supported save ZIP wrappers. Filename or
selected game title does not authorize applying another game's field offsets.
Unknown/malformed schemas fail; saved outputs are reparsed and preserve unknown
bytes. No savedata encryption, account signing or gameplay certification is added.

NBA 2K9: 1,064 player records (452 bytes), 69 team records (572 bytes), 72 arena
records (60-byte anchor stride) on the supplied stock copy. NBA 2K14: 1,665 player
records (460 bytes), 105 teams (760 bytes), 102 arena records (56-byte anchor
stride). Counts come from validated relative table directories, not fixed stock
counts. The following offsets are relative to the player record's physical start.

| Field | NBA 2K9 | NBA 2K14 | Storage |
|---|---|---|---|
| Last / first name | +0x10 / +0x14 | +0x10 / +0x14 | signed relative UTF-16 BE pointers; field + displacement - 1 |
| Height | +0x34 | +0x1C | BE float, centimeters; UI edits inches |
| Weight | +0x30 | +0x20 | BE float, pounds |
| Jersey number | word +0x38, bits 16–22 | word +0x30, bits 12–18 | masked writes, 0–99; 100 displays 00 |
| Face artwork ID | low 16 bits at +0x38 | high 16 bits at +0x2C | pngNNNN.iff CRC candidates |
| Primary position | +0x71 low 3 bits | +0x45 high 3 bits | PG=0, SG=1, SF=2, PF=3, C=4 |
| Secondary position | unestablished | +0x45 bits 2–4 | same codes; 5=None |

Names and floats are directly corroborated against named stock players. Number
and face masks match the stock player/artwork sequences. Position runs match the
observed lineups and valid-code distributions across both full player tables.
NBA 2K14's position pair and height/weight/portrait relationship also agree with
the original NBA 2K13 editor's field relationships. That reference is supporting
evidence, not permission to transplant all PC/2K13 offsets. A candidate body field
at that reference's offset is constant across all NBA 2K14 players and was rejected.
College Hoops still has no independent secondary-position field.

The NBA panel has Players / Teams / Arenas lists, team filtering, search and a
side editor. Numeric editors/dropdowns cover supported measurements, number, face
and positions. Undo/redo and Save copy use the same validated backend. Team and
arena names are editable where their existing string storage is unique. Links to
player membership and arena/floor/LED/dorna/menu assets are read-only. Explorer
references show confirmed face IDs and literal arena/menu asset strings; team
uniform ownership is not inferred from row ordering.

Text allocation is intentionally bounded: no larger replacement than the existing
UTF-16 string is written, and shared-string edits are rejected after scanning
aligned relative references, including unparsed tables. NBA heap relocation and
engine/display text limits remain unestablished. These bounds are editor safety
rules, not claimed engine limits. Unknown ratings, tendencies, appearance, contract
and history semantics remain read-only. Existing College Hoops ratings are not
shown under NBA labels. NBA bulk CSV import/comparison and the College Hoops byte
audit are blocked explicitly rather than reusing incompatible schemas. CLI decode
can export NBA editable fields as CSV; source-bound JSON patches can edit them.

## NBA 2K14 containers

The supplied PS3 copy identifies itself as NBA 2K14 / BLUS31204. Its main archive
has 8,594 entries and seven logical banks. Bank descriptors are 72 bytes rather
than 16, with bounded UTF-16 names such as DVD:1A and SDAT:2A. Only these recognized
prefixes are stripped; arbitrary paths remain rejected. TOC rows retain the
size64/hash32/sector32 schema.

0A, 0B, 2A and 3A are NPD v4 SDAT files. The Python random-access reader supports
only observed flags 0x0100003C, verifies the header CMAC and each accessed block's
HMAC before returning plaintext, and caches at most eight decoded blocks. No
whole-bank plaintext copy or emulator is needed. Unsupported versions, flags,
compressed/debug variants, bad hashes and truncated blocks fail explicitly.
PyCryptodome supplies the cryptographic primitives. Original bank files remain
unchanged. **SDAT/72-byte-descriptor JB rebuilding is blocked**, including on fully
decrypted copies with the extended descriptors: authentication/header regeneration
has not been validated. Export edited roster IFF/USERDATA copies for research;
this update does not claim a tested in-game installation path for NBA 2K14.
Supported override preparation can run in preview-only validation mode; this
does not bypass the independent JB writer guard.

ZLIB block wrappers use a 16-byte BE header (magic, logical length, stored length,
opaque flags) followed by a strict zlib stream. Writers preserve flags, update
lengths, reject trailing/oversized/truncated streams and reparse changed output.
The supplied NBA 2K14 roster decodes to 2,540,288 bytes; NBA 2K9 to 983,328 bytes.

Some IFFs have an extended metadata area: the file pointer table is located through
header +0x1C rather than assumed to immediately follow the block descriptors.
Reading/texture inspection supports it. Rewriting these extended IFFs is blocked
until the additional metadata's pointer semantics are established. The roster IFF
uses the normal pointer-table layout and can be exported with edited payloads.

NBA 2K14 scene variants observed and decoded: 128-byte instances, extended vertex
buffer descriptors and 64-byte draw records with packed material indices. Each
layout must uniquely pass bounded structural validation. Courts are separate
fNNN.iff packages; selecting floor for sNNN.iff resolves the corresponding source's
fNNN.iff when present. On the supplied samples: two floor meshes, 61 arena meshes;
one arena lighting mesh has unsupported UVs. NBA 2K14 jersey artwork/cloth binding
is still unresolved; its direct combined jersey preview remains unavailable.
Runtime shader accuracy is not certified.

## Filenames and repeatable research

Expanded CRC candidate families include pngNNNN.iff faces, logoNNN/NNNN.iff, fNNN.iff,
roster.iff, localized language banks, players.bin, teams.bin, motion.iff and music.iff.
Candidate matches reduce generic names without asserting unknown file semantics;
CRC32 alone is not proof of a unique authored spelling. The bounded candidate
survey found 1,607 matches across previously unresolved entries of the two NBA
copies (including three incidental patterns not promoted to the default dictionary).
Shared record type labels are corroborated against authored College Hoops NAME
trailers (SKEL, Clth, STRG, MRKS, SCOS, SPCI, AMCR and FxTweakables).

Open a source JB in Explorer, then Roster editor > Load from JB or Load from
overrides. External roster IFF/decrypted saves use Open USERDATA / roster IFF.
Save copy retains the input wrapper; Export USERDATA emits a decrypted length-
prefixed payload, not a signed PS3 savedata folder. CLI roster-detect/decode/save
uses the same payload dispatch. The source game is never modified.

## Primary references

- [RPCS3 SDAT format implementation](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Crypto/unedat.cpp)
  and [format constants](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Crypto/key_vault.h).
  Source inspection only; RPCS3 was not launched. The new reader is independently
  written and deliberately supports a narrower observed format.
- [Original NBA 2K13 PlayerReader](https://github.com/leftos/nba-2k13-roster-editor/blob/master/NBA%202K13%20Roster%20Editor/Data/Players/PlayerReader.cs)
  and its Position enum. No PC/2K13 schema is treated as NBA 2K14 PS3 proof without
  matching supplied-byte evidence.

---

Embedded source: docs/ANIMATION_PORTABILITY.md

# NBA animations to College Hoops: research only

No animation port, bank replacement or gameplay patch is implemented.

Read-only inventory of supplied PS3 archives finds:

| Game | SingleMoCap records (0x60900D71) | Old SKEL records (0x7657AB8A) |
|---|---:|---:|
| College Hoops 2K8 | 319 | 1 |
| NBA 2K9 | 904 | 1 |
| NBA 2K14 | 7,460 | 0 |

These are identifiable IFF records, not counts of all gameplay clips. Other raw
banks remain undecoded. Zero old SKEL records does not mean NBA 2K14 has no skeleton.
NBA 2K14 motion.iff also contains three records of unresolved type 0x9D34E89E,
with sample decoded lengths 166,408 / 15,464 / 8,128 bytes and leading version word
0x21. Their gameplay lookup/graph semantics are unestablished. players.bin and
teams.bin are named by CRC candidates but their large opaque payloads have not
been decoded as animation containers.

College Hoops and NBA 2K9 share the observed older SingleMoCap envelope: examples
include 64-byte reference-like records and longer packed records with track data
following the header. Both global SKEL samples begin with 21 and contain matching
matrix-like data, but names/identity metadata differ. Crowd track masks also differ
(for example 0x003DF7DD versus 0x003B77DD). Shared type hashes or matrix bytes do not
prove the same bone ordering, bind pose, event format or clip lookup contract.
NBA 2K9 is the stronger candidate for a future controlled retargeting study.

NBA 2K14 uses changed sample envelopes: 32-byte reference-like records and longer
records with different header organization/packed data. Sharing SingleMoCap's type
hash does not make those records directly compatible with the College Hoops reader.
The evidence argues against copying NBA 2K14 banks directly into College Hoops.

A future converter would need to establish bone identities/order and hierarchy,
translation/rotation packing, time units/key interpolation, root motion, mirrored
tracks, skeleton scale/bind transforms, animation/event IDs, gameplay lookup tables
and contacts/ball/hand interactions. It would decode into an intermediate skeleton
and clip representation, retarget deliberately, then encode the destination format
while preserving unrelated records. None of those steps is assumed proven here.
No direct swap is certified for either NBA title; no emulator or game was run.

Repeatable read-only report:

```powershell
python -m choops_py.research.animation_compat CH_JB NBA09_JB NBA14_JB --output output/research/animation-comparison.json
```

The command scans bounded IFF headers, counts established type hashes and decodes
up to five representative records per type. It checks that source bank metadata
remains unchanged. The report is local research output, never bundled game data.
See NBA_ROSTERS_AND_2K14.md for container and primary format references.

---

Embedded source: docs/MODERN_FEATURE_BACKPORTS.md

# Modern-feature backport feasibility for College Hoops 2K8

Research assessment, 2026-10-17. No gameplay feature, asset port, executable patch
or new alternate asset is implemented by this document. This targets **PS3 College
Hoops 2K8**, not an assumed interchangeable NBA 2K8 binary. Confidence below is
about the proposed technical route, not a certified in-game result.

## Meaning of direct and indirect

A data/asset route uses a consumer already present in 2K8: replace supported artwork,
change confirmed roster fields or assign existing animations. A converted port
needs donor decoding and destination re-encoding with equivalent bindings. An
indirect feature reproduces part of the experience in the editor or an external
workflow. A new engine feature requires executable/runtime logic, not just an IFF
record with a similar name. EBOOT remains read-only; no emulator is launched.

Our supplied donor evidence is PS3 NBA 2K9 and PS3 NBA 2K14. No modern Gen9 asset
sample was inspected. PS3 2K14 must not be confused with PS4/Gen9 variants or taken
as a bridge that automatically makes present-day resources compatible.

## Candidate matrix

| Feature / desired result | Route | Evidence and missing work | Priority |
| --- | --- | --- | --- |
| Modern courts, uniforms, shoes, logos and arena signage | Re-author DDS for 2K8's existing materials; convert geometry only when layout/binding is understood | Existing overrides/preview/writers support known destinations. Newer SCNEs are not automatically compatible; preserve material semantics, alpha, UVs, numbers and budgets. Supported data path, runtime acceptance still unverified. | High |
| Contemporary broadcast scorebug and menus | Redesign artwork first; investigate authored SCNE transforms/layout bindings second | gamedata.iff has named scorebug scenes and textures. Node-to-score/clock/team-color bindings are unresolved. Re-skin is much closer than moving all live fields into a new layout. | High |
| Modern shot selection / perimeter-oriented roster identity | Batch confirmed ratings and four tendencies: close, mid-range, 3PT, drive | Current CSV/copy/compare tools can apply reproducible profiles. This can influence existing decision inputs; it cannot create a new spacing/rotation AI. Profile effectiveness needs user gameplay feedback. | High |
| Modern signature-style assignments | Assign existing jump-shot/free-throw IDs and supported appearance/body fields | 112 jump-shot IDs and free-throw IDs 0–21 have destination evidence. A familiar label does not add a missing move. Current capabilities can support curated profiles. | High |
| Newer shot, celebration or presentation clips | Decode/retarget/encode selected donor clips | 2K9 shares the older SingleMoCap envelope and is the better first donor. Bone order, tracks, timing, aliases, root motion/events and lookup consumers remain unresolved. Conversion research, no certified direct swap. | Medium research |
| More modern arena atmosphere | Replace supported signage/crowd artwork, existing music/fight-song slots; investigate presentation/crowd clips | WAV and artwork paths exist. Crowd placement, trigger timing and synchronization are separate dependencies. Arbitrary commentary or PA event insertion is not established. | High for artwork/audio; medium for animation |
| More modern lighting/material appearance | Re-author textures/lightmaps within established 2K8 shaders | Embedded Cg/prelit/lightmap evidence exists. PBR materials, new reflection/AO systems and modern shader graphs need translation plus runtime support and performance validation. More pixels alone do not produce modern lighting. | Medium |
| Modern playbooks, spacing and coaching tendencies | Locate destination play/tuning structures and their consumers before building an editor | No validated playbook/tactical writer is currently exposed. Old-engine tactics may be editable data, but adaptive modern AI is a different runtime system. Candidate research, not a confirmed port route. | Medium research |
| Contemporary rules, shot-clock behavior and 3PT distance | Trace rules/settings and scoring consumers read-only; distinguish artwork from logic | Court texture and alignment guides do not change collision/scoring/rule constants. No validated modern-rules data writer exists. Do not advertise painted lines as a rules update. | Research only |
| Transfer portal / NIL / richer dynasty management | Possible external roster-management workflow using supported exports | Current roster edits/guarded assignment are established, but dynasty/recruiting/save-state semantics and NIL finances are not. An off-season companion could approximate decisions only after save identity/progression is understood. Not native portal/NIL logic. | Medium concept |
| Badge/archetype experience | Editor-side named presets mapped only to existing confirmed ratings/tendencies | Feasible as an authoring convenience. Actual conditional badges, takeover meters and progression require destination systems; writing invented bits creates no behavior. | Medium indirect |
| Modern replay cameras / broadcast presentation | Inspect existing camera banks, markers, scene transforms and dispatch | Named gameintro_cameras/SingleMoCap records are discoverable. A camera path is not yet a decoded writable track and broadcast-event selection remains unresolved. | Medium research |
| ProPLAY / motion matching / modern contact physics | New runtime animation selection, pose matching, collision and interaction systems | No equivalent destination implementation established. Old compatible clips could improve variety, but cannot import the engine that selects/blends/coordinates them. | Outside current asset-only path |
| Rhythm shooting, new control mechanics, advanced shot timing | Runtime input and shooting logic changes | Animation replacement does not change input interpretation, timing windows or success logic. External remapping is not an implementation of the mechanic. | Outside current constraints |
| Modern online services / crossplay / live marketplace | Separate networking/service architecture | No compatible destination/service contract established; not an archive replacement task. | Out of scope |

## Most promising investigation sequence

1. **Modern gameplay profiles using known fields.** Establish a baseline export,
   define versioned per-player profiles, preserve identity and unknown bits, and
   produce a reversible diff. Use ratings plus the four confirmed tendencies;
   do not claim new tactical AI. User testing would measure pace/shot mix/turnovers
   and expose the old engine's behavioral ceiling.
2. **Broadcast artwork and live-node map.** Inventory gamedata.iff scorebug_bottombar,
   scorebug_topbar/blackbar/logo_bloom and relevant TXTRs, then trace score, period,
   clock, foul, team-name/logo and palette bindings without editing EBOOT. Separate
   cosmetic changes from geometry/visibility/animation changes. Prove one static
   replacement and preserving round trip before a complete new layout writer.
3. **Single-clip animation decoder, starting with 2K9.** Prefer a low-interaction
   presentation clip for structural study; do not start with contact dunks or a
   full motion-bank swap. Locate its skeleton and aliases, decode all tracks,
   reconstruct time/poses and compare encoded output. Even a celebration may
   depend on events, so classify missing dependencies explicitly.
4. **Old-engine tactical/rules discovery.** Survey named settings/play/tuning records,
   compare consumer accesses against known roster fields and document storage.
   No unverified playbook, hot-zone, shot-clock or physics editor should be exposed.
5. **Off-season companion feasibility.** First identify the actual dynasty save
   format and links to roster/recruiting/progression. Existing roster USERDATA
   support is not proof of dynasty compatibility. Keep any later external simulation
   explicit and reversible; do not add removed D1/alternate actions.

This ordering is a recommendation based on existing tooling and dependencies,
not a claim that research items have been decoded or performance-tested.

## Why animation counts do not establish compatibility

The existing read-only inventory found 319 / 904 / 7,460 identifiable SingleMoCap
records in CH2K8 / NBA2K9 / NBA2K14 respectively. They include references/aliases
and are not totals of all playable animations. CH2K8/2K9 samples share an older
envelope; 2K14 sample organization differs. Shared hashes and matrix bytes do not
prove bind pose, bone indices, frame units, events or gameplay lookup compatibility.

A converter needs: bone hierarchy/identity and scale; bind transforms; packed
rotation/translation decoding; timing/interpolation; mirrored/reference records;
root motion; ball/hand/foot contacts; event IDs; destination clip lookup and memory
requirements. Record extraction and decompression are the first steps only.
A move can decode correctly and still break gameplay synchronization.

## Modern feature reference and inference boundary

2K's official [NBA 2K26 gameplay announcement](https://newsroom.2k.com/news/nbar-2k26-debuts-new-gen-9-gameplay-improvements-including-an-all-new-dynamic-motion-engine-powered-by-proplay)
(31 July 2025) describes dynamic lower-body pose matching, changed shooting/control
systems, collision changes and an AI intelligence module. These descriptions
establish examples of modern runtime features, not their proprietary formats.
The conclusion that raw textures/clips cannot supply those systems is an
engineering inference from the runtime dependencies and current destination evidence.
It is not proof that executable reimplementation could never be attempted.
No broader claim about the newest unresearchable title is needed for this assessment.

## Local evidence and next acceptance gates

- [Animation portability](ANIMATION_PORTABILITY.md): donor envelopes/counts,
  skeleton cautions and repeatable inventory command.
- [Animation extraction](ANIMATION_RESEARCH.md): lossless record export only,
  no skeletal track decoder or BVH/FBX writer.
- [Roster semantics](ROSTER_SEMANTICS.md) and roster/schema.py: actual writable
  fields, bounds and packed-bit ownership. No independent CH2K8 secondary position.
- [Scorebug research](SCOREBUG_RESEARCH.md): named destination nodes/artwork and
  unresolved live routing. No geometry redesign writer is claimed.
- [Arena shaders](ARENA_SHADER_MASKS.md): embedded shader evidence and static
  renderer limits; preview guides are not game-rule edits.
- [NBA containers/rosters](NBA_ROSTERS_AND_2K14.md): per-game schemas and blocked
  SDAT rebuilding. Donor extraction is independent of donor rebuilding support.

For each future implementation require a bounded reproduction, confirmed consumers,
source-immutable decoding, destination reparse, untouched-range comparison,
ambiguity rejection and rollback. Engine/memory behavior remains uncertified
without user testing. This research launches no game, edits no executable,
builds no real/testing JB and distributes no donor assets.

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

Current NBA extension: see [NBA roster/container support](NBA_ROSTERS_AND_2K14.md) and
[animation portability research](ANIMATION_PORTABILITY.md). Those pages define the
newer per-game boundaries; historical College Hoops-only statements below remain
specific to that earlier scope. NBA 2K14 SDAT rebuilding and complete NBA ratings
semantics are not implemented.

## Byte audit continuation (2026-10-15)

`python -m choops_py.roster.research ROSTER_FILE` prints a read-only audit; add
`--full` for every byte observation. Header targets now correctly subtract the
stored +1 displacement bias. The anchors are logical anchors inside records, not
raw row starts; HEADER_TABLES bias includes that +1. Uniform rows classify 33/64
bits: owner 22..31, asset 12..21, variant 8..10 and unlock 0..6 of word 0; shape
27..29 of word 1. All other bits stay unresolved/read-only in the audit.

Each table reports half-open unresolved byte runs with exact unknown-bit masks,
including partially known bytes. Fields crossing a legacy declared stride are
listed explicitly instead of silently omitted or counted as solved bytes. This
matters for arena text/backlinks and team shoe/type fields with biased anchors.
The old 24-byte arena/team overlap is an artifact of those biased editor windows,
not an overlap of the logical engine tables on the stock input. Logical origins
are player +0x10, arena +0x18, team +0x30, coach +0x14, conference/uniform +0.
The audit now retains legacy offsets and separately reports logical bit coverage
and unassigned regions; no writer offsets or record strides are changed.

New structural evidence: arena raw +0x24 is a signed relative reference using
`field + delta - 1` to a team raw +0x30 name anchor. On the stock roster, 347
nonnull references resolve exactly and every referenced team links back through
its arena_index; 32 rows are null. This establishes the stored association on that
input, not a universal ownership policy for shared/neutral venues. EBOOT
0x1BC070..0x1BC098 indexes arenas using (index<<5)-(index<<2), reads count/table
from roster +0x20/+0x24, and returns the logical anchor. Arena deserialize
0x1CA620 resolves four pointers at logical +0/+4/+8/+0xC via 0x11650; serialize
0x1CA68C applies the reverse routine 0x15200. The fourth is raw +0x24. This
corroborates the backlink structure independently of the stock values. No reciprocal
arena writer is added. Arena raw +0x2C resembles seating capacity in the stock
values, but its executable consumer/width and edit semantics need corroboration
before an editor control is justified.

Read-only EBOOT continuation checked the localized player accessors around
0x69E85C–0x69E924: the four byte tendencies and potential/confidence remain
consistent with their current biased offsets. This does not establish the meaning
of the intervening raw +0x7C..0x7E bytes. Those, other roster tables, history fields
and unresolved packed bits remain research work; full byte-for-byte semantic
completion is not claimed.

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

Stock logical-row classified bit counts (structural pointer identity included):
players 775/2464, arenas 128/224, teams 2165/5632, coaches 64/352, conferences
3480/23712 and uniforms 33/64. These are audit counts, not percentages of all game
semantics solved. Unknown regions outside these tables also remain.

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

The separate key/center-circle toggle adds authored S256 routes 20 (Key Line),
2 (Key Circle Outer) and 10 (Center Circle). Filled paint route 19 is excluded.
Curved strips use V as their cross-line UV axis; straight key strips use U. The
central 10% clipping and +1-unit height match the existing guide treatment. This
changes reference overlays only and does not simulate a new runtime floor shader.

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

Current NBA extension: see [NBA roster/container support](NBA_ROSTERS_AND_2K14.md) and
[animation portability research](ANIMATION_PORTABILITY.md). Those pages define the
newer per-game boundaries; historical College Hoops-only statements below remain
specific to that earlier scope. NBA 2K14 SDAT rebuilding and complete NBA ratings
semantics are not implemented.

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

Embedded source: docs/UNIFORM_MESH_EDITING.md

# Experimental editable uniforms and modern fit

Models / Courts now has **Uniform meshes…** with export-all, experimental modern
fit and collection reimport actions. Export uses the global **Preview source**
selection, including source-bound complete overrides. Outputs are separate
collections under `output/uniform-models/`; imports create a new
`output/uniform-imports/` folder. Sources and existing outputs are never replaced.

## Coverage and preset

Read-only inventory of the supplied College Hoops 2K8 PS3 source found:

- Five necklines: U, V, V triangle, triangle and wishbone.
- Thin, regular and fat builds for each neckline, plus three shorts builds.
- 21 IFF containers / 33 SCNE–Clth record pairs. This includes the aggregate
  containers and the individual build containers, so both existing resource
  routes are represented. These are 18 distinct garment/build combinations;
  the duplicated routes are not additional jersey styles or new team alternates.

`modern-fit-1` raises the shorts hem by 20% of that mesh's original vertical
extent, fading to zero displacement at 65% of its height so the waist and upper
hips remain fixed. The deformation is monotonic in height; no rows are cut off.
Jersey torso X/Z are reduced by up to 7%, with smooth fades at the bottom and
above the mid torso. The upper 28% stays fixed, preserving the collar/upper
armhole region. This changes existing shared meshes for all schools using them;
it does not change team artwork, body/build selectors, roster records or EBOOT.

## Editing and reimport

The collection contains `originals/` IFF copies, editable `models/` OBJ cages and
source-bound manifests. Modern-fit collections also include untouched
`original-models/` OBJ cages and ready experimental replacements in `overrides/`.
Select **only `overrides/`** in Explorer to prepare the edited game assets. The
collection root includes originals and must not be used as an overrides folder.
Do not mix complete cloth IFF replacements with a different cloth geometry mod.

The OBJ preserves original vertex indices, per-vertex UVs and expanded strip
triangles. Coordinates are unchanged native units, Y up. In a DCC editor, preserve
vertex order and axis conversion on export. Do an untouched roundtrip before
editing: DCC versions may reorder faces or vertices. No welding, subdivision,
triangulation, decimation, vertex deletion or UV editing is supported. Move
coincident seam duplicates together. OBJ normals are ignored; native packed
normal/tangent attributes remain byte-exact. No external DCC application has
been certified by this change.

Choose **Reimport edited uniform models…**, selecting the collection root.
The importer checks the original IFF hash, manifest identities, ordered triangles,
vertex count, UV identity, sewn particle agreement, finite coordinates, a maximum
20-unit displacement and collapsed/flipped triangles. It updates only XYZ in
SCNE vertices and their exact matching Clth rest particles. Unknown attributes,
UVs, skinning-associated stream bytes, indices, constraints and helper particles
are retained. Unsupported declarations and ambiguous matches fail explicitly.
Collection operations are cancellable; a failed/cancelled collection may contain
completed files but has no final success report. Choose a new empty destination
for retry. Each individual IFF is fully validated before writing.

CLI equivalents, always writing under project `output/`:

```powershell
python -m choops_py.cli export-uniform-models SOURCE_JB output/uniform-export
python -m choops_py.cli modern-fit-uniforms SOURCE_JB output/modern-fit
python -m choops_py.cli import-uniform-models output/modern-fit output/edited-cloth
python -m choops_py.cli export-uniform-iff cloth_u.iff output/u-models
python -m choops_py.cli import-uniform-iff cloth_u.iff output/u-models output/new-cloth_u.iff
```

## Confirmed binary evidence and limits

The observed embedded SCNE has one mesh/instance, three streams with strides
4/24/4 and six exact declarations. Float32 big-endian XYZ occupies the first 12
bytes of each 24-byte vertex in stream 1. Stream 0 holds signed-normalized UVs;
stream 2 and the remaining vertex bytes are preserved. Existing triangle-strip
indices and draw data stay unchanged. No general-purpose SCNE writer is enabled.

In matching Clth records, the first big-endian uint16 is the rest-particle byte
extent. Absolute offsets at `0xc0` and `0xc8` bound that table; their difference
equals this extent. Each particle is 16 bytes: matching float32 XYZ plus 1.0.
All 33 supplied graphic records have unambiguous exact matches to this bounded
table. Several rendered seam vertices share a particle. Unmatched helper
particles and zero-initialized workspace are retained. This mapping establishes
rest-position editing, not the semantics of every Clth byte.

Writers preserve logical record addresses and sizes. Physical compressed sizes
can grow; the existing archive relocation workflow handles a larger replacement.
Every written IFF is reparsed; all changed and unchanged record slices are
compared against the expected bytes. No-op OBJ roundtrips are byte-identical.

**This is experimental.** Packed solver constraints, collision geometry, cloth
simulation and normal/tangent regeneration have not been retargeted. Existing
constraints may pull edited vertices toward their previous fit; animation may
show stretching, body clipping or shading differences. Rest-pose comparisons and
successful import/preflight cannot establish the animated result. Do not call
this a finished cloth-simulation port. No RPCS3/gameplay or real JB build is run.
NBA garment layouts and arbitrary new topology remain unsupported.

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
pyproject.toml and tools/dev/setup.py are the portable dependency contract.
The obsolete pinned Windows environment snapshot has been removed.

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
Prepared overrides/exports live under output/ and originals remain immutable.
Completed JB builds also support user-selected destinations through
archive.manifests.build_destination; keep safe_output for other workflows.
Destination validation must protect source/mod trees in both directions. Build
reports and temporary/backup folders use the same validated destination drive.

`tools/rebuild/package_windows.ps1` packages the Windows GUI and audio helpers.
The FFmpeg helper is configured without GPL/nonfree components and uses only the
PCM formats and ATRAC3 decoder needed for WAV/audio operations. Its FFmpeg and
AtracDEnc source archives and applicable notices accompany the package. Confirm
the exact configuration and packaged smoke on Windows; no proprietary converters
or game assets are included. See AUDIO_WORKFLOW.md and the encoder README.


## Rebuild I/O (v1.16)

`archive.build_io` verifies preserved source-coordinate spans against their output
coordinates, with a relocation delta when needed. In-place replacement ranges
alone are excluded; old bytes left by relocated replacements and all padding are
still compared. Each bank is opened once per comparison, and ExitStack closes all
handles on cancellation/error. Repack BankWriter closes/flushed handles before
reopening output for validation. Replacement/header verification stays separate.
Copied non-bank files also receive byte comparisons before atomic publication.
Do not cache verification of a fresh output or use hard links to source files.

Use `python tools/dev/benchmark_rebuild.py` for a bounded synthetic-only benchmark.
Its entry count can be changed with `--entries`; it never accepts a game path.


## Automatic shared 2K layouts

`archive.layouts.decode_toc` validates all candidate schemas, requires a unique
answer and exposes canonical row fields to the existing reader/writers.
`pack_row` serializes canonical fields back to the source schema. Do not make
writers infer a game from names, extensions or UI settings. Source size semantics
remain profile-specific: legacy rounded/derived extents versus exact size64 extents.
Keep unknown formats raw and preserve their bytes through builds.

Record CRC labels are case-sensitive and only fill missing labels; authored
trailers take precedence. A matching label does not establish unknown type or
roster semantics. Cache fingerprints include the schema and frozen prepared-cache
fingerprints include layout/label module code. Add malformed/ambiguous fixtures,
synthetic writer round trips and explicit read-only input evidence for another
variant. Never validate by launching an emulator or building a real/testing JB.
See PS3_2K_ARCHIVES.md for current evidence and the standalone research command.

## NBA roster and SDAT extension

Runtime dependency PyCryptodome is declared in pyproject.toml and installed by
tools/dev/setup.py. archive/sdat.py is a bounded read-only stream; Archive opens
plain/encrypted banks through open_part, and BankReader uses the same abstraction.
Bank descriptor sizes 16/72 are structurally selected, not inferred from a title.
All JB writer plans reject encrypted/extended-descriptor archives before output.

EditorModel.open dispatches NBA payloads to roster/nba.py; studio/nba_roster.py
provides separate NBA side panels. Keep unknown NBA offsets out of the College
Hoops schema and vice versa. The source-bound JSON patch backend and wrapper
writers are shared. College-only bulk/research paths reject NBA explicitly.
formats/compression.py handles bounded ZLIB alongside H7A; StandardIFF reads its
record table through +0x1C. Extra IFF metadata remains read-only. New vertex, draw
and instance layouts must uniquely validate; ambiguous geometry is not guessed.
See NBA_ROSTERS_AND_2K14.md and ANIMATION_PORTABILITY.md for reproducible evidence,
limitations and the read-only animation survey command. Neither animation ports
nor SDAT rebuild/signature writers are enabled.

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

## Queue several songs before saving

In Audio, select one track and click **Queue selected song from WAV…**. Repeat for
other songs in either Licensed Music or Fight Songs. The pending table lists the
bank/index and selected file. Re-queueing the same song changes its file; **Remove
queued song** removes selected pending rows and **Clear song queue** removes all.
Click **Save queued songs…** once and choose a new replacement folder under
`output/`. The result includes one combined `cribmusic.bin` (when applicable),
`global.iff` and a replacement report. Select that folder as overrides for a manual
JB build. Queue entries clear only after a successful save; cancellation/failure
keeps them. They are session-only and must be saved before closing the app.

Queued WAVs must have a nonempty RIFF/RF64 WAV header; full decoding and validation
happen on save, retaining support for the encoder's existing WAV sample formats.
Bank sample rate/channels/duration
are conformed by the existing encoder. The queue belongs to its loaded source JB;
changing source requires returning to it or clearing/reselecting the songs. This
prevents accidentally applying catalog indices from one JB to another. Reopening
the same JB path is supported when bank size/mtime/inode metadata still matches.
As with the override input quick check, this is not a content hash: a same-size
external edit that preserves all metadata may evade the source-change check.
Songs newly queued or changed during an active save remain pending afterward.

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

Embedded source: docs/SCOREBUG_RESEARCH.md

# Scorebug research — authored assets, runtime routing pending

Read-only stock archive inspection on 2026-10-15 identifies the following records.
Names identify authored resources; they do not alone prove which runtime path is
active. No executable edits or scorebug geometry writer are implemented.

| Archive | Record | Type | Evidence |
|---|---|---|---|
| gamedata.iff | scorebug_bottombar (55) | SCNE | 23 parts; six embedded textures |
| gamedata.iff | scorebug_topbar (250) | SCNE | text_nodeMask and g_top_bar; one texture |
| gamedata.iff | scorebug_blackbar (135) | SCNE | group_blackbar_text |
| gamedata.iff | scorebug_logo_bloom (260) | SCNE | klogo_Score_bug |
| gamedata.iff | scorebug_bloom (25) | TXTR | Separate artwork |
| gamedata.iff | scorebug_info_blk (39) | TXTR | Separate artwork |
| gamedata.iff | scorebug_logos (60) | TXTR | Separate artwork |
| gamedata.iff | scorebug_scanlines (143) | TXTR | Separate artwork |
| gamedata.iff | shotclock (174) | TXTR | Clock-related artwork; numeric binding pending |
| gamedataextra.iff | scorebug_ps3 (1) | SCNE | Five parts; two textures |
| gamedataextra.iff | scorebug_xenon (2 / 3) | MRKS / SCNE | Separate marker and scene records |

The bottom-bar parts include Score_bug, drop_shadow, top_greybar, bot_greybar,
color_1, color_2, logo1, logo2, frame1..7, frame8_glare, frame9_glare, ncaa2k8,
g_2K_circle_logo and text_nodeMask. Its embedded texture slots are:

| Slot | Dimensions | Encoding |
|---|---|---|
| 0 / 1 | 64 × 64 | DXT1 |
| 2 | 128 × 128 | DXT5 |
| 3 | 256 × 256 | DXT5 |
| 4 | 128 × 128 | DXT5 |
| 5 | 512 × 256 | DXT1 |

The PS3/Xenon scenes both have polySurface50, Score_bug, group2, mesh_slider2 and
titlebar_plane1, with 256 × 128 and 128 × 64 DXT5 textures. Their relation to the
free-throw meter (the neighboring LAYT record) is a hypothesis, not proof that
these scenes control the main score overlay. overlaycache.iff contains 21 scenes,
including halftime_box_score, but no explicitly named scorebug record.

Reproduce the inventory without extracting artwork or building a JB:

```powershell
python -m choops_py.formats.scorebug "YOUR_JB_ROOT"
```

This prints JSON record identities, part names, logical block sizes and texture
layouts. Current Explorer/texture tools can inspect and replace confirmed TXTR or
SCNE texture slots using their exact names, original dimensions, alpha and mip
layout. Preserve scene parts, materials and record names. This is an artwork-only
starting point; it does not promise a complete layout redesign or validated game
behavior. A record index is supporting evidence for this input, not a portable
replacement key; use exact record names.

Next research: map score/period/game-clock/shot-clock/team-name fields to authored
nodes, trace team-color/logo bindings and animation/visibility states in read-only
EBOOT consumers, distinguish broadcast modes and console variants, then prove
which layout/material parameters can change without executable edits. Moving or
removing scorebug nodes is deferred until these dynamic bindings are understood.

---

Embedded source: docs/PROJECT_SOURCE_OF_TRUTH.md

> Inherited technical evidence, not the current per-game support contract.
> See FEATURE_MATRIX.md, PS3_2K_ARCHIVES.md and NBA_ROSTERS_AND_2K14.md for
> newer archive/roster variants. Current caching/audio/UI behavior is described
> in WORKFLOWS.md; fixed-capacity and experimental-only statements below may
> reflect earlier versions. Unknown bits remain preserved.

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

## Header-gap preservation and user destinations (current update)

The post-TOC/pre-asset gap can contain opaque nonzero bytes in rebuilt inputs.
Existing replacement slots consume none of it; append planning preserves the gap
verbatim and validates only slots occupied by additions. Repack planning can keep
opaque bytes at their original offsets when the body start is unchanged and the
new TOC consumes only verified zeros. Moving the body with opaque header data or
expanding TOC over that data remains blocked. This deliberately does not infer
unknown header pointers or erase nonzero bytes.

Mod Builder's **Choose JB output folder…** accepts an empty destination on another
drive. CLI build-copy accepts the same destinations. The original JB and mod
workspace cannot overlap the output in either direction; roots and linked paths
are refused. Existing nonempty folders require the existing explicit overwrite
option and a valid tool-owned build manifest. Publication/rollback uses siblings
on the destination drive. Other export/staging paths still use output/.

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

Current NBA extension: see [NBA roster/container support](NBA_ROSTERS_AND_2K14.md) and
[animation portability research](ANIMATION_PORTABILITY.md). Those pages define the
newer per-game boundaries; historical College Hoops-only statements below remain
specific to that earlier scope. NBA 2K14 SDAT rebuilding and complete NBA ratings
semantics are not implemented.

## Shared 2K compatibility boundary

The editor auto-detects two verified PS3 TOC schemas, not arbitrary game formats.
College Hoops 2K8 and the supplied NBA 2K9 copy have read-only extraction/preview
evidence; both writers have synthetic round-trip evidence. Other years/platforms,
unknown resources and gameplay need further verification. NBA roster semantics,
number placement and dynamic shader behavior are not established. See
PS3_2K_ARCHIVES.md. College Hoops-specific roster features remain available.

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

## Experimental uniform mesh edits

Known College Hoops garment OBJ reimport edits both visible and cloth rest XYZ.
Packed solver constraints, collision and normal/tangent regeneration remain
unchanged. A static modern-fit preview is not an animated fit certification;
see [uniform mesh editing](UNIFORM_MESH_EDITING.md). No arbitrary topology/NBA writer.

---

Embedded source: docs/TEST_REPORT.md

# Experimental uniform mesh editing — verification

Windows / Python 3.12.14. Targeted command:
`python -m pytest tests/test_uniform_mesh.py tests/test_scene_preview.py tests/test_direct_asset_previews.py tests/test_cli.py -q`
passed **42 tests**. The 15 new mesh/GUI cases cover byte-identical no-op import,
position-only writes in matching SCNE/Clth, unchanged unknown records, stale
manifests, UV/topology/count changes, nonfinite/excessive displacement, flipped
triangles, missing/ambiguous rest matches, split seams, unsupported layouts,
preset attachment regions and selected-source GUI dispatch.

Read-only actual asset inventory and private output audit: **21 IFFs, 33 record
pairs, 25,956 original rendered vertices**. All 21 no-op exports/reimports are
byte-identical. Edited logical blocks differ only in intended XYZ bytes;
unreferenced bytes, UVs, other attributes, constraints and record addresses stay
unchanged. All **21 replacements prepare and pass build preflight**. Before/after
rest-pose contact sheet inspected for all 18 distinct garment/build combinations.
Source inputs unchanged. Local editable/override assets stay out of Git.

Full portable verification uses `python tools/dev/verify.py --python PYTHON` and
a temporary directory outside project output. Its first run exposed missing
UUID imports in the new GUI methods; corrected and covered by direct selected-
source dispatch. A run with fixtures inside output invalidated an existing
output-safety test's premise; no production court behavior was changed for that
test environment. Windows worker verification requires normal worker access.
Final source portable verification passed **617 tests, 10 skips, 2 deselections**;
compile, CLI/Qt startup, Ruff, mypy and generated handoff checks passed. New
backend/test files also pass the full E/F/I Ruff selection. Exact-commit isolated
verification is recorded in the PR handoff.

Packed solver/collision and normal/tangent retargeting are NOT established.
No external DCC roundtrip certification. RPCS3/gameplay: **NOT RUN**.
Automatic/testing JB: **NOT BUILT**. No EBOOT change or release publication.

# v1.19 Reborn Overrides V5.5 import support

Read-only discovery against the supplied V5.5 folder and vanilla College Hoops
2K8 archive recognized 1,946 archive groups and scanned 25,428 files, including
17,596 DDS files and 7,794 record files. Numeric folders 1004 and 1055 resolved
to `shoe_100_04.iff` and `shoe_100_11.iff`; folder 1376 resolved to `uy011.iff`.
The V5.5 `icon_tatoo` path resolved to `icon_tattoo`. No game or override source
files were written. No JB copy was built. This is supplied-input discovery
evidence, not a game/runtime compatibility claim.

`git diff --check` passed on the submitted source changes. No full test suite or
package rebuild was run on the v1.19 branch in this update.

# v1.19 compatibility verification

Windows / Python 3.12.14 portable checks: **603 passed, 9 offscreen GL skips,
2 deselected**; compile, CLI/Qt, Ruff, mypy, handoff and diff checks passed.

Five new synthetic cases cover flat DDS cubemap imports through authoritative
Python manifests for TXTR and SCNE, retained five faces/header bytes and report
semantics, a paired-CDF face preservation case, named invalid-IFF roles/magic and retained structural error codes.
No invalid-container acceptance is added. Read-only actual checks prepare and
preflight the supplied frontend/legal ZIP; full halftime HDR cube artwork matches
the imported DDS, scene headers/capacity remain unchanged. No source bank writes.
The same ZIP also passes in an isolated v1.16 checkout; its generic screenshot
failure is not reproduced. Final portable/isolated/frozen results are recorded
on the release PR.

# Verification — v1.18

Full portable verification on Windows / Python 3.12.14: **598 passed,
9 offscreen OpenGL skips, 2 deselected**; compile, CLI/Qt smoke, Ruff, mypy,
generated handoff and diff passed. New navigation links resolve locally.

Current source combines the reviewed NBA support, split-header regression fixes,
key/center-circle guide and documentation cleanup. Exact final-head commands and
results are recorded in the release PR and release notes after verification.
The portable runner is `python tools/dev/verify.py`; the isolated run uses the
same runner with `--python` pointing to the prepared development interpreter.

Regression additions from PR #25 cover NBA schema detection/wrapper preservation,
SDAT authentication/tamper/truncation, ZLIB boundaries, extended scene layouts,
cross-bank headers, both append/repack writers and named corrective diagnostics.
PR #26 covers authored key/center routes, radial UV direction, elevation,
source preservation and independent Qt toggle behavior. Wrapper unit assertions
are consolidated into test_binary.py without removing coverage.

Previous exact-head evidence: PR #25 had 596 portable passes (9 GL skips,
2 deselected); PR #26 had 577 (9 skips, 2 deselected). These are separate branch
counts, not the combined release result. Isolated runs additionally skip an
optional native DLL when it is absent. Historical per-release detail is in
[verification history](history/VERIFICATION_THROUGH_V117.md).

The Windows package requires startup, CLI, audio round trip, lazy SDAT dependency
checks, ZIP integrity and checksum verification. No RPCS3/gameplay, real/testing
JB, EBOOT writes or copyrighted assets in Git. See [testing policy](TESTING.md).

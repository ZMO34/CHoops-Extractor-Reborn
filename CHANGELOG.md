# Unreleased — NBA 2K11 donor research

- Read the observed v3 SDAT variant with version-specific key selection and retained authentication; keep SDAT output blocked.
- Document actual NBA 2K11 asset/animation samples and donor suitability ratings; no gameplay, face or animation port implemented.

# v1.19

- Apply folder single-face cubemap compatibility consistently to Python manifests and paired CDF imports; preserve five base faces and report +X updates.
- Identify archive/role/magic for invalid IFF errors and provide targeted corrective advice without bypassing validation.
- Verify supplied frontend/legal overrides and complete halftime HDR cubemap using Python-only preparation/preflight; no real testing JB.
- Integrate modern-feature feasibility research PR #28. No gameplay/animation backport implemented.

# v1.18

- Integrate NBA 2K14 reading, detected NBA roster editors and split-header repair (PR #25).
- Add independent key/center-circle court reference guides (PR #26).
- Replace stale landing pages/matrix with current per-game documentation; add workflow, troubleshooting, testing and release guides. Preserve dated research in clearly labelled history.
- Remove obsolete pinned Windows dependency snapshot/unpublished beta draft; consolidate wrapper assertions into binary tests without reducing coverage.
- Include the complete documentation tree in Windows packages and maintain the generated cross-PC handoff.

## Unreleased — split archive headers and override error fixes

- Read and write header regions across source banks; support a TOC crossing 0A.
- Name damaged banks and expected/actual sizes instead of a generic incomplete-header error.
- Keep actionable override/build failure details and targeted repair advice in the GUI.
- Allow NBA2K14 override preview validation without enabling its unvalidated JB writer.

## Unreleased — NBA PS3 roster schemas and NBA 2K14 archive reading

- Read authenticated NPD v4 SDAT blocks and extended split-bank descriptors; keep SDAT JB writing blocked.
- Decode/re-encode strict ZLIB IFF blocks; read extended IFF pointer tables without unsafe rewriting.
- Detect College Hoops/NBA 2K9/NBA 2K14 roster payloads and expose verified per-game fields in side panels.
- Add NBA face, court, logo and language filename candidates and explicit roster asset references.
- Decode observed newer scene buffer/draw/instance variants and resolve separate court packages.
- Add read-only cross-game animation inventory and portability evidence; no animation port.

## Unreleased — additional court alignment guides

- Add a separate key/free-throw-circle and center-circle guide toggle using stock authored geometry, independent of 3-point/border guides.
- Keep guides raised, thin, flat-colored and separate from actual floor rendering.

## v1.17

- Auto-detect shared PS3 2K size32/size64 TOCs and preserve their layouts when rebuilding.
- Read optional game identity, retain College Hoops roster boundaries and shared source/override caching.
- Recover common internal CRC labels; support standard CDF TXTR hashes and half4 scene attributes.
- Add read-only NBA 2K9 inventory/extraction tooling and supplied-copy extraction/preview evidence.

## v1.16

- Faster sequential rebuild verification and persistent relocation bank handles.
- Single-read source preconditions; avoid redundant CDF partner reads.
- Fix CLI rejection of manually chosen JB output folders.
- Verify copied non-bank files, preserved bank padding and generated headers.
- Remove DDS preflight temporary folders on success/failure; check free disk space.
- Include queued song imports, manual output folders and opaque archive-gap fixes from PR #22.

# Unreleased

- Queue multiple song WAV imports, review/remove pending edits, then save combined
  music banks and global.iff once; retain pending edits on cancellation/failure.
- Choose the JB destination on any drive, with source/overwrite/link guards and
  transactional cleanup preserved.
- Preserve opaque archive header gaps during replacement growth; reject only
  newly consumed/relocated unknown bytes rather than all nonzero gap bytes.
- Correct roster research anchors/uniform bit coverage; audit arena-team backlinks.
- Add read-only scorebug record/part/texture discovery and evidence documentation.

# v1.15.4

- Parallel CPU/RAM-bounded override preparation, completed-archive reuse, cheaper
  conversion-cache maintenance, deterministic outputs and cancellable workers.

# v1.15.3

- Fix frontend menu override imports misclassifying header-relative geometry as
  texture data; preserve inline/GPU buffers and retain real overlap validation.

# Unreleased roster / game-line / motion continuation

- Traced the shared 65,535-unit text descriptor bound; block count overflow and
  remove Qt's unintended 32,767-character truncation.

- Live orange warnings beyond verified UTF-16 keyboard entry capacity.
- Authored 3-point/outer-border layers, source court supplementation, retained camera.
- Guarded conference indices and exact conference-logo texture editor shortcut.
- Corrected tournament-link semantics; unvalidated bracket editing protected.
- Bit-accurate unresolved-byte coverage and lossless SingleMoCap inspection/export.

- Dynamic UTF-16 edits no longer confuse keyboard entry capacities with engine storage ceilings.

# Roster and arena continuation

- Twelve additional confirmed appearance/tattoo/signature fields and all jump-shot captions.
- Authored arena vertex colour/alpha, secondary UV lightmaps, glow and flare masks.
- No guessed secondary positions or unproved palette assignments.

# Uniform lettering continuation (PR #13)

- Authored indexed font decoding, front/back numbers 0–99/00 and curved Reborn surnames.
- Roster-linked or preview-only number selection; source/override glyph consistency.
- Correct sampler/bool uploads and declared material DiffuseColor.
- Confirmed palette 16/17 school-colour runtime-copy labels.

# Change log

## Unreleased — roster / preview continuation

Named SCNE source switching, worker source snapshots, comparison reference guards,
confirmed school text capacities and jump-shot animation ID editing. Nested menu
logo records show school ownership; stadium labels use arena references.

## Unreleased — single-slice DDS replacements

Allow a 2D DDS replacement for dimension-3 TXTR descriptors whose stored depth
is exactly one, preserving the original descriptor. Deeper volume textures stay
blocked.
## v1.12 — roster scale and preview source checkpoint

Inline ratings, atomic multi-player ratings paste, source-bound CSV and selective
roster comparison; school filtering, Class/Redshirt controls and growing text
storage. Shared source/override previews, archive categories/references, bounded
conversion cache and concise GUI build summaries. This is in-progress work;
remaining engine limits and shader/number routing are documented, not claimed
complete. Comparison review uses a table model for large change sets.

## v1.11 — record side panels and previews

Side editors for every category; integrated palettes, footwear and jersey preview.
Safe player school assignment and 18-slot/count-aware roster handling, including
real player row zero. School shoe brands propagate to that school’s roster as one
undo step. Combined top/shorts preview with neck/build/cut dropdowns. Removed Edit
selected, Team palette and shoe toolbar actions; no alternate assets added.

## v1.10 — roster editing cleanup

Readable height/positions, visible Player/Ratings/Scholarship editor tabs, verified
scholarship flag editing and named equipment. Schools combines duplicate views.
Removed separate properties/attributes and D1/alternate/independent-asset actions;
conference realignment remains. No alternate assets added. Full Windows package
includes the established LGPL audio codecs and corresponding source notices.

## Unreleased — reviewed audio GUI continuation

Fix scene/shoe navigation after Audio insertion; clean-clone converter tests use
synthetic fixtures. Batch WAV exports publish atomically and remove incomplete
batches on cancellation/failure.

## Unreleased — LGPL audio package

Build a restricted FFmpeg CLI from pinned upstream source with GPL/nonfree
components disabled, ship corresponding FFmpeg/AtracDEnc sources and notices,
and include both audio helpers in the standalone Windows GUI. Windows CI run 54
built the package and passed the frozen synthetic WAV round trip on the current
PR head. ATRAC PCM input now accepts finite samples through ±4.0, matching the
encoder's 1/4 input scaling and avoiding rejection of over-range floating WAVs.
Song replacements are trimmed or silence-padded to the selected track's original
sample length.

## v1.08 audio development bundle

Experimental WAV/audio-bank/AUDO/jukebox-art CLI, unchanged-WAV checksum skipping,
sample-extent checks, portable setup and shared Codex PR/documentation workflow.
Experimental Audio workspace adds separate Licensed Music/Fight Songs tabs, WAV
export/replacement preparation and mapped cover-art actions. Song-name editing
remains unavailable. No emulator or testing JB.

## v1.07

Community roster ZIP/rating fixes, packed player/team shoe editing, game roster
IFF export and declared 2D stored-depth compatibility. Source inputs preserved.

## v1.06

Reusable single-surface court preparation and automatic non-stadium base texture
normalization. Dynamic supported stadium sizes retained; runtime budget unknown.

## 1.0b0 development (Git tag v1.0beta reserved, not created)

Native Qt studio; streaming cancelable raw extraction; precomputed IFF spans; replacement-folder staging and source preconditions; verified unpatched build bytes; roster redo; source/packaged smoke tooling. CI branch deletion/release side effects removed. Historical higher-looking version tags remain untouched. This is a new rebuild train, not a replacement of preserved releases.

Override selection fix: automatically choose a fresh numbered workspace when the configured folder exists; update build and preview paths together. Rename the GUI action to Select overrides folder… and remove staging wording from GUI messages. Preserve previous workspaces on failure.
Continuation: optional stock-court alignment guides default off and leave floor shader/palette rendering intact. Correct ROST runtime UTF-16BE string fixup, protect the 65,535-unit descriptor count, and remove Qt’s unrelated input ceiling.

v1.14: direct jersey, shoe and stadium/floor selectors use Source JB or selected overrides without manual IFF opening. Jersey selection initializes the mesh; stadium modes choose combined, floor or arena. Source switching reloads the active direct preview.

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

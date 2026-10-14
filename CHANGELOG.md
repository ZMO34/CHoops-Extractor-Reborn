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

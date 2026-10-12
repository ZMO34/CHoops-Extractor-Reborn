# Development verification

## LGPL audio packaging branch — portable checks

`python tools/dev/verify.py`: 250 passed, 1 skipped, 2 deselected. The skip is
the optional native codec round trip because the local checkout has not built
the helpers; deselections are the private game/runtime checks and the optional
legacy native comparison defined by the runner. CLI help and Qt startup smoke,
scoped Ruff, studio/service mypy, handoff snapshot, compileall and
`git diff --check` passed. The restricted FFmpeg build, Windows package smoke
and packaged WAV round trip remain pending Windows CI; local MSYS2 is unavailable.
An added synthetic regression rejects a non-RIFF/RF64 WAV before codec lookup.
The first two Windows CI attempts exposed an annotated-tag/object SHA mix-up and
then invalid FFmpeg component names / a missing MSYS2 `cmp` utility. The current
follow-up pins the peeled source commit reported by
`git rev-parse 'n9.0.2^{commit}'`, uses FFmpeg's `pcm_s16le`/`pcm_f32le` muxer
component names and `ffmpeg.exe` make target, and installs `diffutils`. The
corrected pin was confirmed in a local source checkout. Windows CI built both
helpers and passed the GUI package smoke, then the explicit audio round trip
revealed that resampling/format filters were missing from the restricted FFmpeg
build. The latest follow-up enables only `aresample` and `aformat`; Windows CI
must validate the frozen conversion round trip on that head.

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

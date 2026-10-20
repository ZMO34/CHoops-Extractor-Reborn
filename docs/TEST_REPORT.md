# PR #30 merged compatibility audit

Reviewed merge `fd9eae5d43f0dec436411661dcf99c52f326e562` in an isolated
checkout with `tools/dev/verify.py --python <prepared Python 3.12 interpreter>`:
**602 passed, 10 skipped, 2 deselected**. Compile, CLI/Qt smoke, Ruff, mypy,
handoff and diff checks passed. Offscreen OpenGL and the absent optional native
converter are skipped. Each of v1.16, v1.17, v1.18 and v1.19 is an ancestor.

Nine added synthetic regressions pass. Full follow-up source verification with
`python tools/dev/verify.py`: **612 passed, 9 skipped, 2 deselected**, all other
portable checks passed. Final exact-head isolated results are posted on the
follow-up PR. No production parser behavior changed in this audit.
See [scope and retained feature coverage](PR30_COMPATIBILITY_REVIEW.md).
No Windows package was rebuilt because dependencies, packaging and application
code are unchanged. No RPCS3, gameplay, EBOOT editing or real/testing JB copy;
small generated archive fixture outputs only. Unknown formats remain guarded.

# v1.19 Reborn Overrides V5.5 import support (original submission evidence)
# Player-face research verification

Windows / Python 3.12.14 source `tools/dev/verify.py`: **607 passed, 9 skipped,
2 deselected**; compile, CLI/Qt smoke, Ruff, mypy, generated handoff and diff
checks passed. Four added synthetic cases cover selector masking and unchanged
source, independent custom flags, biased-row morph tail bounds, rejection of NBA
or other strides, and missing-bank reporting. Final exact-head isolated results
are recorded on the research PR; optional native DLL absence adds an isolated skip.

`python -m choops_py.research.player_faces <original CH2K8 source>` reads all five
face banks and source roster with no unresolved banks: seven dedicated albedos,
13 normal records, 75 facial-hair textures, shared heads/presets; 5,685 players,
15 nonzero likeness selectors matching seven names, 5,670 generated selectors,
zero custom flags/stored morph arrays. All seven albedos pass byte-identical
DDS/GTF/DDS conversion in memory; extracted local face artwork visually inspected.
EBOOT function-specific TOCs, selector branches, seeded generation and morph
encode/decode loops were inspected read-only. No executable bytes are committed.

NBA 2K9 donor container/scene structure inspected. The selected NBA 2K14 sample
ZLIB variant and supplied 2K11 SDAT version/flags remain unsupported; these are
not successful extraction/port tests. No face writer, EBOOT change, RPCS3,
gameplay validation or real/testing JB; no Windows package/release requested.
See [the findings and reproduction command](PLAYER_FACE_RESEARCH.md).
# NBA 2K11 authenticated-reader and donor research

Windows / Python 3.12.14 source `python tools/dev/verify.py`: **609 passed,
9 skipped, 2 deselected**; compile, CLI/Qt smoke, Ruff, mypy, generated handoff
and diff passed. `python -m pytest -q tests/test_sdat_2k14.py`: **8 passed**.
Existing random reads/header/ciphertext/truncation tests now cover v3 and v4;
metadata corruption, mixed encrypted/raw banks, write blocking and rejection of
unknown versions/compressed/debug flags are covered. Six added parameter cases
retain the original v4 checks. Final isolated exact-head results follow on the PR.

Read-only supplied NBA 2K11: 6,974 archive entries, 72-byte descriptor/size64 TOC;
both encrypted banks authenticate sparse beginning/interior/end/cross-block reads.
Full standard-IFF header inventory has zero traversal errors. Generic animation
inspection reports 4,705 SingleMoCap records and unchanged source metadata.
Selected texture/SCNE/audio/roster/animation blocks decompress; floor f030 yields
two preview meshes without warnings. Stadium s734 yields 21 supported arena parts
and one unsupported UV part. Sample PNG high-detail vertices remain unsupported;
bench geometry decodes. A 48-kHz stereo ATRAC3 effect exports 43,008 PCM16 WAV frames.
ROST marker 0x225 is observed but no 2K11 roster editor enabled.

Ratings are conversion judgments, not port/runtime tests. No track poses decoded,
no direct cyberface/full-arena/HUD port, no Windows release/package requested,
no EBOOT edits, RPCS3/gameplay or real/testing JB. Reports/artwork/audio stay local
and excluded from Git. [Assessment and reproduction](NBA2K11_DONOR_ASSESSMENT.md).

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
# Unreleased Legacy save editor foundation

Read-only inspection of the supplied 5,523,948-byte Legacy-mode save found a
validated roster payload at offset `0x438`, length `0x003DF800`, followed by
1,461,684 bytes of additional mode data. The embedded payload passed the current
roster model's structural validation with 5,685 players, 379 arenas, 443 teams,
1,373 coaches, 39 conferences and 988 uniform rows, with zero validation issues.
The adapter's unchanged encode returned bytes identical to the input. No source
save was edited; no saved output or JB was produced. The additional mode data's
semantics remain unknown.

`git diff --check` passed. No full test suite or package rebuild was run.

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

# Local executable experiment 01 — 2026-10-19

Private-only prototypes generated and audited on Windows / Python 3.12.14,
Capstone PPC64 big-endian and locally installed Keystone 0.9.2. Keystone is not
an editor dependency. Original decoded ELF and retail SELF digests match after
all work. Five variants pass allowlisted diff/header/branch and debug SELF payload
round trips; the control ELF is identical. No game code is executed by these
checks. 60,000 geometry samples cover both directions plus modern apex/corners/
joins and old-circle equivalence; 30,000 transfer-mask cases preserve neighboring
bits. Added instructions' register/TOC/stack/LR usage was reviewed.

The companion reparses with 10 old text styles retained and two native labels
added. Original decoded bytes and vertex data remain unchanged. Its relocated
SCNE extends an unrelated inferred span over 44,720 abandoned original bytes;
runtime acceptance is unverified and explicitly documented. Two-archive override
preparation/preflight passes with zero unapplied overrides; ZIP integrity is
checked locally. No automatic/testing JB, emulator, gameplay or physical-PS3 test.

Public changes are documentation/handoff configuration only. Scoped exact-head
handoff, Ruff, local-link and diff checks are recorded in the PR. Full runtime
suites and packaging are not rerun and historical passes do not certify EBOOT.
The cleanup preserves active tracked regression tests and user builds/inputs;
broader historical package deletion remains approval-blocked.

# Executable modernization research — 2026-10-19

Documentation-only update on Windows / Python 3.12.14. Read-only ELF mapping,
function-descriptor/TOC inspection and PPC64 big-endian Capstone disassembly
followed named menu registrations. The bounded scan recorded 580 candidate
strings / 75 TOC references; these are not an exhaustive executable analysis.
Input digest matched before/after scanning. No game data or executable writes.
Additional read-only assertions passed for both prior name-suppression branch
sites, CameraMenu table/handler descriptors, Game Rules table/callback and
non-file-backed camera state pointers; a second before/after digest matched.

Scoped verification: generated handoff/check, Ruff for the changed handoff
generator, local Markdown-link resolution and `git diff --check`. Exact committed
head results are recorded in the PR. Runtime suites and Windows packaging were
not rerun: no runtime/package code changed. Historical suite counts below do not
validate the newly proposed executable candidates. No Ghidra, RPCS3/gameplay,
executable patch, real/testing JB or release.

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

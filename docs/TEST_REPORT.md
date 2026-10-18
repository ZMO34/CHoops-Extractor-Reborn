# Scorebug test05 verification

Targeted style/layout/localization/native-font suite: **23 passed**. New regressions
cover alpha restoration with unrelated properties/bones/events/payload unchanged,
invalid alpha/RGB rejection, count-only native-label suppression and propagation
through ordered mesh operations. Actual five-scene package prepares/preflights
both required archives without unapplied DDS. Source portable verification: **626 passed, 9 skipped, 2 deselected**; compile,
CLI/Qt, Ruff, mypy, handoff and diff passed. Exact-head isolated results are
recorded in the PR handoff.

Read-only built-archive analysis confirms test04 inputs were current; native code
shows normal-game city-name suppression. Owner declined an executable patch and
left names unresolved. Current scene/property checks do not certify gameplay or
claim names have been fixed. No emulator launch, EBOOT write or new JB build.

# Native test04 startup-crash correction candidate

Read-only user log: asynchronous resource-loader PC 0x00845E14, access violation
reading 0x4D4C0002, before HUD rendering. The failing thread contains added branding
tokens. Built English content matches the supplied native test04 IFF. Its decoded
block contains the old table plus an appended full replacement. Other build mods
are present; neither universal mod compatibility nor a fully isolated gameplay
root cause is claimed.

Targeted layout/style/font/localization suite: **21 passed**. Regression checks
require offset zero, one table, exact stored/logical-size equality and no H7A
wrapper, plus rejection of prefix/alias/multiple-resource layouts. All old actual
English translations remain byte-identical; new decoded size is old size +50 bytes.
The corrected ZIP preserves gamedata bytes from native test04. Source portable verification: **624 passed, 9 skipped, 2 deselected**; compile,
CLI/Qt, Ruff, mypy, handoff and diff passed. Corrected two-archive preparation and
build preflight passed with zero unapplied DDS. Exact-head isolated results are
recorded in the PR handoff.
No emulator run, executable write or new game build; user runtime retest remains.

# Test04 native branding follow-up

Targeted layout/style/font/localization regressions: **20 passed**. Covers explicit
ID low/high-float packing, preserved flags/vector tails, sorted localization insertion,
opaque sentinel/old-pool preservation, malformed/duplicate/encoding rejection, safe
IFF growth and rejection of changes to existing translations. Actual native-label
style matches clock font alias, RGB, alpha and shadow values. All 21,637 existing
localization rows and old token bytes are preserved; only one tagged literal is added.
Two-archive override preparation/preflight passes with zero unapplied DDS.
Source portable verification: **623 passed, 9 skipped, 2 deselected**; compile,
CLI/Qt, Ruff, mypy, handoff and diff passed. Final exact-head isolated results
are recorded on PR #32. No emulator, executable
writes or native test04 JB built; runtime placement/visibility awaits user testing.

# Scorebug test04 follow-up

Targeted native style/layout/font checks: **15 passed**. New regressions distinguish
value-before-type/key properties, preserve ABL bone references when callback names
change, preserve all other original header bytes/payload, reject malformed font
properties reject shared font-property writes and duplicate bindings, and restore an explicitly hidden draw's alpha. Actual scene-only overrides
prepare/preflight successfully; five scenes, one archive, zero unapplied DDS.
Source portable verification: **618 passed, 9 skipped, 2 deselected**; compile,
CLI/Qt smoke, Ruff, mypy, handoff and diff passed. Exact-head isolated results
are recorded on PR #32. Runtime names,
font sizes, popup states and exact branding appearance remain for user testing.
No RPCS3, EBOOT writes or test04 JB built.

# Scorebug test03 follow-up

Targeted layout/native font regressions: **11 passed**. Covers partial-draw
preservation, gradient flattening, unchanged UVs on shear removal, text basis and
translated-marker offsets, ordered edits, native glyph coverage/spacing and
malformed glyph rejection. Local scene-only overrides prepare/preflight with
one gamedata archive, five SCNEs and no unapplied DDS. All 257 other stock records
and all scene block sizes remain identical. Source portable verification: **614 passed, 9 offscreen GL skips, 2 deselected**;
compile/CLI/Qt/Ruff/mypy/handoff checks passed. Exact-head isolated verification
is recorded on PR #32. An initial sandbox run could not create pytest temporary
fixtures; rerunning with normal filesystem permissions passed. Runtime text/meter/popup behavior is not
certified; no emulator, executable writes or new JB build.

# Scorebug test02 follow-up

Portable Windows/Python 3.12.14 verification: **608 passed, 9 offscreen GL skips,
2 deselected**; compile, CLI/Qt, Ruff, mypy, handoff and diff passed.
Scene-only overrides prepared/preflighted successfully with zero unapplied DDS.
Final exact-head isolated review is recorded on the PR.

Synthetic layout regressions cover vertex/UV/color/alpha/depth changes, preserved
unknown interleaved data, paired text matrices/markers, invalid-target rejection,
restart-strip topology and inventory of sixth-man text anchors. Actual static
asset checks preserve all 258 unedited gamedata records and scene block sizes.
No runtime placement, popup visibility or font behavior is certified. See the
scorebug research and PR for exact final-head checks and local artifact evidence.

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

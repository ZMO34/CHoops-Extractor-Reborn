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

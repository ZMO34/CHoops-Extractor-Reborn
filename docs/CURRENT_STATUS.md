# Current status — v1.18

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

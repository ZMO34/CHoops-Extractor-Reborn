# Workstation test report — 2026-10-09

Baseline origin/master: 52e9beffafab51f855bc2ef197bb105cf66e175d. Windows 11 x64/Python 3.12.14/.venv. Actual game path and full SHA inventory are private under .private/; no game assets or personal absolute paths belong in public reports.

Commands executed:

- `.venv/Scripts/python.exe -m pytest -q`: initial 30 passed.
- `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp=output/temp/pytest_rebuild_08`: 37 passed in 1.62s. 35 synthetic/Qt tests, one private real-game integration, one real Windows converter test. No skipped test in that workstation run.
- `python -m choops_py.cli --help`, compileall, Qt source --smoke: passed.
- Ruff on studio and mypy on studio with legacy imports skipped: passed. This is not full strict typing/lint coverage of legacy code.
- `tools/rebuild/verify_game.py "PRIVATE_JB_ROOT" --full-rip --build`: full 3,376 raw extents, all eight representative assets discovered, real export/import/roster/build tests passed. Evidence under ignored output/smoke_tests.
- Texture exports: ua000 9/9, uh000 9/9, s000 51/51, teamselectlogo 520/520, sideline_items 242/248. Six failures remain raw-preserved; not counted as successful DDS conversions.
- Edited jersey atlas, player jersey field (one logical roster byte), court texture and logo pair reopened structurally; separate JB build. First logo edit rejected 17,210 vs 17,202 compressed bytes; another edit fit, proving the capacity guard rather than universal import success.
- SCNE actual metadata: 80 parts. No geometry exporter/importer proof asserted.
- Actual native GUI fixture smoke: archive load, nested IFF inspect, decoded DDS preview, roster load/search (68 Smith matches), harmless export and close. Packaged rerun uses --verify-game --game and writes its own JSON report.

Source audit: all ten original file sizes, mtime_ns and SHA-256 values match the pre-test inventory. Copied JB patch bytes exact; every byte outside staged extents verified against original. The audit reports 1,566,683 changed stored bytes in the initial atlas/roster build (compression changes stored bytes broadly); this does not mean that many semantic edits.

Sandbox-only pytest runs initially failed at tmp_path ACL creation. Approved local runs succeeded; this is an environment failure, not a silently passed test. A repeated-output test failure was fixed using unique per-run synthetic destinations.

Runtime PS3/RPCS3: NOT RUN. Public CI fixture tests must skip when absent. GitHub CI result, final package checksum and proposed source commit are recorded only after observed completion; local evidence does not certify green GitHub checks or a published release.

Packaged prototype: extracted ZIP startup exit 0; separately supplied local converters enabled real-game GUI preview/roster/export smoke. Final original SHA-256/size/mtime audit repeated after the extended build: all ten match. PR #2 argparse NameError reproduced by loading its exact remote branch modules and invoking main; no branch merge.

Final regression suite: 37 passed in 1.62s. Actual legacy Tk window also launched/closed successfully with system Python 3.14.5. New tests cover CLI-to-Qt launch (argument isolation), TOC/header overlap rejection and source precondition mismatch.

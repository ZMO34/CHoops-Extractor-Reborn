# Workstation baseline — 2026-10-09

Repository: https://github.com/ZMO34/CHoops-Extractor-Reborn
Baseline origin/master: `52e9beffafab51f855bc2ef197bb105cf66e175d`.
Working branch: `codex/v1.0beta-rebuild`, created from that commit. Clean initial checkout; the original workspace contained only the supplied game. No existing user code was overwritten.

Windows 11 build 26200, x64, Python 3.12.14 isolated in .venv. System Python is 3.14.5. Hardware: 8 physical/16 logical CPUs; 17,085,915,136 bytes RAM. Bundled Git was located through workspace runtime discovery; its HTTPS helper required a process-local GIT_EXEC_PATH. No global PATH changed.

Private fixture discovery succeeded in the checkout-adjacent supplied folder. Five parts 0A–0E, archive alignment 2048, 3,376 entries. Source JB inventory: ten files, 4,862,682,189 bytes. SHA-256 baseline for every file is in ignored .private/source_before.json; actual source path is in ignored .private/settings.json. Fixture stays outside the repository, never tracked or uploaded.

GitHub connector account ZMO34 has admin access. Direct HTTPS Git clone/fetch works with approved network access; direct push fails because no local credential was supplied. The connected GitHub API is the available publication route. Existing Releases, v1.0.0-python-rewrite and v1.1.0-focused-modding tags are preserved. Existing releases have zero Windows application assets (historical Releases has one old artifact). PR #2 remains open and unmerged. Its studio_web.py omits argparse despite using it in main; no wholesale merge occurred.

verify.yml contained a publish job deleting three remote branches and creating/editing releases. Removed entirely; verification now uses contents:read. Historical JavaScript readers/writers, tests, README_ZMO_EXTENSIONS and SCNE stable wrapper were inspected as references. Historical fixtures are not copied into new tests.

First workstation test run: 30 passed including private roster and actual Windows converter test. New tests and later results are in TEST_REPORT.md. Earlier historical reports are not evidence for this rebuild.

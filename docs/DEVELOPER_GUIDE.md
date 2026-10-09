# Development

Use .venv and `pip install -e ".[dev]"`. requirements-windows-dev.txt records the actually installed Windows versions without local paths. Keep game source outside Git; CHOOPS_JB selects the private fixture for tests. A private .private/settings.json can hold the fixture path.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check choops_py/studio
.\.venv\Scripts\python.exe -m mypy choops_py/studio --follow-imports=skip --ignore-missing-imports
.\.venv\Scripts\python.exe -m choops_py.cli --help
.\.venv\Scripts\python.exe -m choops_py.studio --smoke
.\.venv\Scripts\python.exe tools/rebuild/verify_game.py "YOUR_JB_ROOT" --full-rip --build
.\tools\rebuild\package_windows.ps1
```

Shared native operations: Archive.chunks, studio.services.extract, inspect_asset, stage_folder, roster EditorModel/workflow and texture_tools.pipeline. CLI extract-raw and stage-folder expose the new services. Existing rip command retains legacy decoded extraction behavior.

See rebuild/ARCHITECTURE.md for contracts/debt. UI jobs cannot mutate widgets off the Qt main thread. Every writer must reparse output, preserve unknown ranges and reject ambiguous identities/capacity/aliasing. Source-game hashes and test assets stay ignored. Public CI uses synthetic fixtures and explicitly skips absent private fixture tests; verification has no branch/tag/release mutations.

Test groups: `pytest -m real_game`, `pytest -m windows`, `pytest -m gui`, or `pytest -m "not real_game and not windows"`. Public runners skip absent private fixtures explicitly; generated Windows converter tests skip on non-Windows.

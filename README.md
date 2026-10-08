# CHoops Extractor Reborn

Python 3.11+ tools for **PS3 College Hoops 2K8**: export/edit/import DDS textures, edit confirmed roster fields, stage mods, and build separate modded JB folders.

Run from this repository on Windows. No Node installation is needed. The original game stays read-only. Every generated file belongs under `output/`; copied games belong under `output/builds/<build_name>/`.

```powershell
python -m choops_py.cli gui
python -m choops_py.cli texture-tools-status
python -m choops_py.cli test-texture-tools
python -m choops_py.cli export-iff-textures output/rips/ua000.iff output/rips/ua000_textures --dds
python -m choops_py.cli replace-iff-texture output/rips/ua000.iff unif output/temp/edited.dds output/temp/ua000.iff --same-format-only
python -m choops_py.cli import output/builds/my_mod output/temp/ua000.iff --iff ua000.iff
python -m choops_py.cli build-copy "C:/Games/College Hoops 2K8" output/builds/my_mod output/builds/my_build --overwrite
```

DDS export/import requires bundled converter tools: `tools/gtf2dds.exe` and `tools/dds2gtf.exe`. Raw extraction works without converters. Unsupported texture layouts and edits that cannot preserve archive capacity are blocked. The converters are Windows executables; raw parsing and synthetic tests also run on other platforms.

The default GUI is a **three-tab native Python Studio**: Rip Game Assets to IFF, Build Game from IFF Folder, and Open Roster. It has a screenshot-inspired dark local-browser interface, file/folder picker, live job logs, copy-only game building, and a roster editor with School, Assets, Roster Slots, Player, and raw color-palette research panels. Advanced texture, validation and staging commands remain available through the Python CLI rather than additional main tabs. The old Tk UI remains in `choops_py.gui` for reference.

Launch with `python -m choops_py.cli gui` (opens `http://127.0.0.1:8788`) or `python -m choops_py.studio_web --no-browser`.

**Output safety:** set rip destinations inside `output/`, builds inside `output/builds/<name>`, and edited rosters inside `output/`. The vanilla game and original roster are never overwritten by this Studio. To build, first stage your mod overrides using the Python `import` command. The interface calls the repository's native Python archive/roster modules (it does not use the old Node engine).

**Current research limitations:** palette slot meanings are not fully mapped; color writing requires an explicit research toggle. Conference, skin tone, prestige, depth rotation behavior, broad SCNE geometry writing, audio codec encoding, arbitrary-size CDF relocation, and creation of new archive entries are not yet verified and are not represented as completed capabilities. Binary-validation passing does not certify console gameplay. Roster changes preserve unknown bytes and the source container. Names require unchanged UTF-16 byte length and unshared storage. Appearance, conference, prestige and long-string rebuilding stay read-only.

See [commands](docs/COMMANDS.md), [texture conversion](docs/TEXTURE_CONVERSION.md), [roster editor](docs/ROSTER_EDITOR.md), [GUI](docs/GUI.md), [limitations](docs/KNOWN_LIMITATIONS.md), and [consolidated research](docs/PROJECT_SOURCE_OF_TRUTH.md).

```powershell
python -m compileall choops_py tests
python -m unittest discover -s tests -v
python -m pytest -q
```

Ordinary tests use synthetic data. The real-game test skips when the local fixture is absent. Passing file validation does not certify console gameplay.

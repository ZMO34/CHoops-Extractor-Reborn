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

The GUI provides file/folder pickers, command previews, live logs, texture tool checks, texture export/import, staging, JB building/validation, and a roster editor. Roster changes preserve unknown bytes and the source container. Names require unchanged UTF-16 byte length and unshared storage. Appearance, conference, prestige and long-string rebuilding stay read-only.

See [commands](docs/COMMANDS.md), [texture conversion](docs/TEXTURE_CONVERSION.md), [roster editor](docs/ROSTER_EDITOR.md), [GUI](docs/GUI.md), [limitations](docs/KNOWN_LIMITATIONS.md), and [consolidated research](docs/PROJECT_SOURCE_OF_TRUTH.md).

```powershell
python -m compileall choops_py tests
python -m unittest discover -s tests -v
python -m pytest -q
```

Ordinary tests use synthetic data. The real-game test skips when the local fixture is absent. Passing file validation does not certify console gameplay.

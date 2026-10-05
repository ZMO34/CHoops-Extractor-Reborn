# CHoops Extractor Reborn — Python

Preservation-first tools for **PS3 College Hoops 2K8**. Python 3.11+; runtime uses the standard library and Tkinter.

From this folder:

```powershell
python -m choops_py.cli --help
python -m choops_py.cli gui
python -m choops_py.cli rip "C:/path/to/PS3_GAME/USRDIR" output/rips/first --file ua000.iff --iff-only
python -m choops_py.cli inspect-iff output/rips/first/ua000.iff output/reports/uniform --dump-subfiles
python -m choops_py.cli build-copy "C:/path/to/game" output/builds/mods output/builds/game --dry-run
```

All generated files must be inside this project's `output/`. The vanilla game is read-only input. Select folders in the GUI; each job shows its command before running and streams logs.

Standard IFF and paired CDF inspection, byte-preserving round trips, raw extraction, tool wrappers, override staging and same-size copy builds are implemented. Compressed subfile edits, size-changing builds, DDS conversion, roster editing and ISO authoring are blocked or read-only. Validation is structural, not a guarantee of console behavior.

For tests: `python -m pip install -e ".[test]"`, then `python -m pytest`. Proprietary integration checks skip when the JB folder is absent. Set `CHOOPS_JB` to use your own fixture. All test data stays in output/temp.

See [commands](docs/COMMANDS.md), [GUI](docs/GUI.md), [safety](docs/SAFETY_MODEL.md), [limitations](docs/KNOWN_LIMITATIONS.md), and [source of truth](docs/PROJECT_SOURCE_OF_TRUTH.md).

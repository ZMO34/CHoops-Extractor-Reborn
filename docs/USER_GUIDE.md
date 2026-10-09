# Native studio user guide (development build)

Install Python 3.11+ and project desktop dependencies, or run the local onedir prototype. No Node/browser server is used.

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m choops_py.studio
# packaged executable
.\CHoops-Studio.exe
.\CHoops-Studio.exe --cli --help
```

1. Explorer: Open game selects a JB root, PS3_GAME, or USRDIR containing 0A. Source remains read-only. Search by name/hash/index, multi-select rows, extract raw selected/all into a new output/rips folder. Cancel extraction retains only completed entries and a cancellation manifest.
2. Double-click an archive row to inspect its nested records. Texture Editor displays actual texture candidates. Double-click a texture row to decode its image; failures explain unsupported layout/converter/capacity. Export textures writes DDS/GTF/raw and per-texture manifest. Edit DDS in your chosen image editor without changing dimensions, compression or mip count, then select the row and Import edited DDS to a new output/temp container or paired folder.
3. Roster Editor: Load game roster or open supported original/raw/wrapped/decrypted roster. Search players/teams/arenas/coaches. Select a player/team row and Edit selected. Only confirmed fields are enabled; existing references are selected from records. Undo/Redo and Save copy preserve the original source. Names must have identical encoded length and unshared storage. Encrypted-save decryption and speculative fields are unsupported.
4. Models/Courts: select a SCNE nested record in Explorer then inspect part metadata. Court texture work uses Texture Editor. Geometry import/export is unavailable in this development version.
5. Mod Builder: Open the original game, choose a new mod path, Stage replacement folder containing edited IFF/CDF files with canonical filenames. Unknown/duplicate/conflicting targets are rejected before copying. Dry run reviews patches; Build JB copy writes a separate output/builds folder and verifies all untouched bytes. Original archive growth/new entries are blocked.
6. Research shows a bounded raw hex view; Diagnostics executes real converter readiness/round-trip checks. Logs retain recent operation outcomes. Parser/conversion jobs currently must finish before closing; extraction and JB copying/verification are cancelable.

All generated paths currently belong under output/ beside the source project or executable. Existing files are refused. A staged mod has original-source hash preconditions; changed originals block a build. No workflow authorizes writing to the supplied game. Save/export paths containing spaces are supported.

DDS tools are separately supplied until redistribution licensing is settled; see CONVERTER_PROVENANCE.md. The local prototype and structural tests do not establish PS3/RPCS3 gameplay. Follow rebuild/ACCEPTANCE_TESTS.md for manual runtime validation. Complete capability status is in rebuild/FEATURE_MATRIX.md.

Mod Builder also exports/imports .chpatch ZIP packages of XOR differences. They contain source/result SHA-256 preconditions and no original or unchanged game bytes. Import validates every identity, size and checksum before publishing a new staged workspace. Limit: 128 MiB per extent and 512 MiB total. Share only changes you are authorized to distribute. Never distribute copied JB game folders.

Open extracted asset also accepts an individual 0A part and routes it to the archive index. Interactive asset decode is capped at 128 MiB; larger files retain a bounded raw inspection and remain stream-exportable.

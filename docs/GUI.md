# GUI

Launch `python -m choops_py.cli gui`. The twelve focused panels cover Project Setup, Texture Tool Setup, DDS Export, DDS Import, Uniforms, Court/SCNE Textures, Team Logo/CDF Textures, Mod Staging, Build JB Folder, Roster Editor, Validate Build and Logs/Reports.

Project Setup provides vanilla JB, mod, rip, build and report folder pickers and converter file pickers. Outputs default under output/. Texture Tool Setup shows each bundled converter found/missing, export/import readiness and the last test conversion result.

Commands show a preview before running. Long commands run in a background subprocess with live logs; logs can be saved under output/reports. The roster editor uses the same validated backend as the CLI, with row editing, search, roster slots, validation, undo/revert and save-copy/export actions.

Build controls are Select Vanilla JB Folder, Select Mod Folder, Select Output Build Folder, Build JB Folder and Validate Build. Builds go under output/builds/<name>/. Existing generated builds require --overwrite; folders without this tool's manifest are refused. Output equal to or inside vanilla is always rejected.

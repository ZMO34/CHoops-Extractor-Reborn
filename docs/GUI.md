# GUI

Run `python -m choops_py.cli gui`. Tkinter must be included with your Python installation. Workspace pickers select vanilla/JB input, mod folder, rip output, build output and reports. The left list exposes all 22 requested panels; related commands have a selector. File/folder Browse controls populate arguments. Options accept CLI flags, including `--iff archive.iff --sub 0` for override import.

The Preview and Run button shows the complete command and requires a visible confirmation. Jobs run in a worker subprocess with live output and exit code. Save Logs enforces output safety; Open Report reads a text/JSON report. Roster and floor panels explicitly mark experimental/read-only behavior. The CLI backend owns all parsing and write rules.

Output pickers for single-file commands require typing a new filename if browsing cannot select one. Multiple wrapper block paths use the blocks field. Choose fresh output directories; exports do not overwrite existing reports. Job cancellation is not implemented; the window asks you to wait before closing.

# Focused texture, roster and JB update

- Supporting archive, IFF, package, compression, wrapper and CDF architecture reimplemented in Python.
- Original gtf2dds.exe/dds2gtf.exe bundled in tools/ with setup, readiness checks and actual conversion tests.
- DDS export/import implemented for validated textures, including uniform atlases, paired CDF assets and parseable SCNE package textures.
- Modded JB folder copy building implemented with staging, preflight, safe overwrite and validation.
- Functional roster GUI implemented for confirmed safe player/team fields, search, roster slots, validation, undo and save-copy/export.
- Unsafe compressed growth, size-changing and unknown-format cases are blocked where not validated.

Raw extraction works without converters. DDS export/import requires bundled converter tools on Windows. No Node installation is needed. Console gameplay and encrypted-save decryption are not certified. See docs/KNOWN_LIMITATIONS.md and docs/CODEX_UPDATE_SUMMARY.md for validation evidence and remaining restrictions.

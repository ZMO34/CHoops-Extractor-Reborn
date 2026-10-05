# Texture conversion

`gtf2dds.exe` and `dds2gtf.exe` are bundled required tools for DDS editing, stored in `tools/`. Users do not need Node or the old 2k-tools tree. Raw extraction works without converters. DDS export requires gtf2dds.exe; DDS import requires dds2gtf.exe.

Discovery uses bundled tools first, configured paths in `output/config/texture_tools.json` second, then user-selected paths. Status readiness requires the bundled executable to pass a basic execution check; configured paths do not hide a missing bundle.

```powershell
python -m choops_py.cli setup-texture-tools --copy-from-old-sources
python -m choops_py.cli texture-tools-status
python -m choops_py.cli test-texture-tools
```

Setup copies only the two converters from the old read-only sources. Their SHA256 hashes are recorded in the architecture audit. The test performs actual DDS/GTF conversion and checks DXT1 image bytes. Converter execution captures stdout/stderr, uses output/temp, never writes the source, and emits conversion JSON reports.

Export raw or wrapped TXTR, standard IFF, paired CDF textures, or parseable SCNE package textures. All exports preserve the source/payload and write a manifest, conversion report, and reconstructed GTF where the layout is understood. DDS conversion failures do not invalidate raw assets. Exports continue per texture unless `--strict` is set.

```powershell
python -m choops_py.cli export-dds output/rips/example.txtr output/rips/example_textures
python -m choops_py.cli export-iff-textures output/rips/ua000.iff output/rips/uniform --dds
python -m choops_py.cli export-cdf-textures output/rips/sideline_items.iff output/rips/sideline_items.cdf output/rips/sideline --dds
python -m choops_py.cli export-court-textures output/rips/s000.iff output/rips/court --dds
```

Choose texture names/indexes from the manifest. Nested textures use paths such as `floor/texture_0`. Edit DDS without changing dimensions, format or mip count, then import into a new file:

```powershell
python -m choops_py.cli replace-iff-texture output/rips/ua000.iff unif output/temp/edited.dds output/temp/ua000.iff --same-format-only
python -m choops_py.cli replace-cdf-texture output/rips/teamselectlogo.iff output/rips/teamselectlogo.cdf 0 output/temp/logo.dds output/temp/logo_pair --same-size-only
```

Import validates original/DDS/GTF dimensions, format, mip count, layout and image length before writing. Standard IFF compressed blocks can be safely rebuilt only when the logical slices remain unchanged in size and the rebuilt file fits its original extent. CDF recompression must fit its original physical payload allocation. Otherwise an exact blocking reason is reported. NAME metadata and unrelated records remain intact. Review `output/reports/texture_import_report.json` and `.md`.

The original converter cannot export the proven linear L8 uniform atlases. These use a validated tight L8 DDS fallback; DDS reimport still runs dds2gtf and normalizes its verified mip-row padding. Unknown layouts are never guessed or padded to simulate successful conversion.

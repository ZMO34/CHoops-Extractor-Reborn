# Development verification

The court-template and non-stadium texture policy update passed 125 targeted
Python checks, including raw and whole-IFF normalization, paired CDF imports,
HDR preservation, multistream geometry relocation, previews, compression and
CLI registration. Real gameplay/uniform replacements were compiled in memory
and retained exact base headers after resizing. The supplied court template
retained its floor triangles and primary UVs, resolved albedo to slot 0 and
bump to slot 2, disabled the other floor draws, and ignored inactive artwork.
The source GUI passed its startup smoke check. No emulator was opened and no
JB build was produced for this update. The optional historical executable
comparison was excluded after Windows rejected its DLL relocation; built-in
conversion checks passed independently. The game's crash-free court texture
budget remains unverified.

Built-in DDS/GTF conversion is tested in both directions against generated
native-reference fixtures for L8, ARGB8, DXT1/3/5 and RGBA16F. Coverage includes
rectangular Morton order, non-power-of-two linear storage, mip chains and all six
cubemap faces. Default import/export and preview tests run without external tools.
The independent accelerated H7A codec and portable decoder agree on random,
overlapping and malformed streams. Override regression tests cover misplaced
scene folders, numeric record aliases, Windows copy suffixes and explicit reports
for DDS files requiring a missing replacement scene.

Local checks exercised the synthetic parser/writer, Qt navigation/edit/save, actual Windows converter, interruption cleanup, source preconditions, malicious ZIP rejection and cross-part copy/patch workflows. Private read-only game integration and separate generated-output verification also ran; environment-specific results are excluded from public documentation.

Commands: pytest, compileall, CLI --help, studio --smoke, studio --verify-game --game PRIVATE_PATH, Ruff and mypy on the new studio/patch-package modules. Test groups distinguish unit, integration, gui, windows and real_game. Public CI must skip the private fixture when absent. Converter tests use generated inputs.

Initial Ubuntu CI exposed missing libEGL.so.1; the workflow installs the required Qt runtime libraries and allows both platforms to complete independently. The corrected prior CI commit passed Windows/Linux and standalone packaging. Subsequent code requires its own observed checks.

Original files were read only; output patch and untouched ranges were verified separately. Runtime PS3/RPCS3 verification: NOT RUN. Unsupported layouts, geometry import/export and unknown roster semantics remain documented limitations. This is not completion or publication of v1.0beta.

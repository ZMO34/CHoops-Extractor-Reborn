# Converter provenance and publication boundary

Existing repository binaries are preserved, not replaced:

| File | Bytes | SHA-256 |
|---|---:|---|
| gtf2dds.exe | 161280 | b0533529413ffc41f0d0de02602c1223d2be555455d950e89bd22c529c928a5d |
| dds2gtf.exe | 135168 | bcb75ca129ede3708d699510830a85288b47f0f36536930f54aff763991929d2 |

The legacy audit records byte-identical copies in both historical trees. Strings inspection found no copyright/license grant in these executable bytes; there is no discovered redistribution license accompanying the current tools. This is an unresolved publication blocker. Local authorized converter testing is separate from permission to bundle publicly.

Actual subprocess tests run on Windows with generated L8 and DXT1 DDS/GTF fixtures. Arguments, exit status, stdout/stderr, metadata and DXT1 payload equality are recorded in ignored conversion JSON reports. Tools run without shell=True. Input/output filenames are individual arguments. Unknown layouts and failed conversion outputs are preserved as raw data or rejected explicitly.

Public development build workflow excludes converters. Existing authorized converter files may be supplied locally beside the executable under tools/. Do not upload that locally supplied folder until permission is established. No new executable, copyrighted texture/model/audio or game data enters Git.

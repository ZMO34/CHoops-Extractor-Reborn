# Known limitations

- Bundled DDS converters require Windows. Raw extraction works without converters; DDS export/import requires bundled converter tools.
- Unknown TXTR layouts, unsupported DDS formats (including DX10/cubes) and unvalidated pixel transformations are blocked. Manifest warnings describe per-texture export failures.
- Standard IFF changes must preserve logical slice sizes and fit the original file extent. Unchanged compressed blocks remain byte-identical; modified blocks preserve unknown fields and original token choices where possible. Invalid/shared slices and insufficient capacity are blocked.
- CDF imports must fit original physical allocations; virtual-to-physical layout relocation is not implemented. Segment headers and metadata are preserved.
- Roster names require equal encoded length and unshared string storage. Appearance, skin tone, conference, prestige, and long-string rebuilding are read-only. Encrypted saves require external decryption. Team references use confirmed internal row biases, not guessed row starts.
- SCNE texture edits preserve geometry. Geometry/material/UV editing, audio decoding and broad research scans are outside the focused UI.
- JB builds support existing archive extents and staged safe edits; adding archive entries or increasing allocated file sizes is blocked. Validation checks files/structure, not console gameplay.
- Existing output files are refused for import/export. Build --overwrite only replaces an owned generated build, transactionally.

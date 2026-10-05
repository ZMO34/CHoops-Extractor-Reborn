# Safety model

Every writer resolves its destination and enforces project output/ containment. Paths equal to or inside a vanilla/JB source are refused. A PS3_GAME ancestor expands protection to the full JB folder. File inputs cannot be overwritten. Resolved symlinks/junctions cannot escape output/. Source trees containing links are refused before build-copy.

A build preflights all staged hashes, names, targets and sizes before copying. Only the copied split archive is patched; the original is opened read-only. --dry-run computes the plan without copying. --overwrite is accepted for compatibility but never deletes a populated output. Choose a new directory for each build. Export files are exclusive: existing files cause a visible error.

Unknown bytes, compression, headers, offsets, names and padding are preserved. Uncompressed single-span edits require exact size and no aliases. Compressed/size-changing edits are blocked. CDF bounds validation does not certify audio or texture semantics. Never assume a structural validation proves game behavior.

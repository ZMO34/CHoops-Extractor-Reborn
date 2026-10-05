# Safety model

Vanilla JB is read-only. Every generated rip, conversion, report, cache, temporary file, configuration and copied game belongs under project output/. Converter installation writes only the two authorized bundled tools/ executables. Input files cannot be overwritten; outputs inside a selected source JB are rejected after path resolution.

JB builds preflight all staged hashes/containers, reject linked source/build trees, copy the whole vanilla folder, patch only the copy, validate exact patched extents and unchanged file sizes, and check vanilla size/mtime inventory. Builds use a temporary sibling then rename into place. --overwrite requires this tool's build manifest. Unknown fields and unrelated raw bytes are preserved. Unsafe edits fail before final output creation.

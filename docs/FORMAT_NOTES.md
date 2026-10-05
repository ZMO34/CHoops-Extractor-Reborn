# Format notes

Authoritative consolidated rules are in PROJECT_SOURCE_OF_TRUTH.md. Full inherited research, including roster field tables and inventory, remains in MASTER_HANDOFF.md. Standard magic FF3BEF94 and CDF metadata F0985030 are distinct formats. Uniforms are standalone standard IFFs; names/numbers are embedded TXTR. CDF pairs preserve metadata, headers and physical payload extents separately. 2kTl is a tool wrapper, not an on-disc archive.

All relative pointers use field + value - 1. Standard/CDF metadata is big-endian; optional name-table pointers/strings are LE. Archive descriptor names are UTF-16BE. Do not silently import PC NBA behavior.

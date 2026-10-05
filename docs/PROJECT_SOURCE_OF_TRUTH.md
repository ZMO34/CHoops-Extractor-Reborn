# Project source of truth

Target: PS3 College Hoops 2K8, Python 3.11+, argparse and Tkinter. This document and MASTER_HANDOFF.md replace reliance on the old JavaScript folders. The handoff is research evidence, not a promise that every historical editor field is validated.

## Provenance and confidence

Read-only references: expanded 2026-06-18 master handoff; original BPhit continuation README, archive configuration; downloaded Reborn gameProfiles, ChoopsReader, IFFReader, CDF extractor, H7A utilities, ToolWrappedReader and floor notes. Constants, pointer formulas and useful filename hash/name pairs were intentionally rewritten into Python. No Node runtime, native editor, conversion executables or legacy build products are retained. Original source authors' provenance is recorded here; upstream licensing must be clarified before adding more borrowed implementation or distributing proprietary assets.

`MASTER_HANDOFF.md` preserves the full research record and inventory. Confirmed below means corroborated by source and/or current fixture checks; candidate fields remain read-only. No game assets belong in Git.

## Archive and identity

The archive header is six BE u32 words: magic AA00B3BF, alignment, part count, zero, entry count, zero. Part descriptors are 16 bytes: first word is size in 0x800 units; bytes +8..+15 encode the part filename as UTF-16BE (confirmed on JB 0A). Logical space concatenates listed parts, allowing entries across boundaries. CH2K8 TOC uses 16-byte records: hash +0, offset units +4, unknown +8, stored size units +12. Offsets multiply by alignment. Stored sizes can be impossible on this fixture; derive only from next offset/end and flag the derivation. Preserve padding by extracting the complete bounded extent. Do not clamp an invalid read silently.

Case-insensitive ASCII filename hashing matches CRC32 of uppercase bytes for generated candidates. Retained reference hash/name pairs take precedence. Namespace includes ua/uh/ux/selua/seluh/selux/s/m/p/coach 000..999, h0000..9999 and known named banks, with iff/cdf/bin variants. Outer TOC names and inner IFF names are distinct identities. Unresolved entries remain hash names. Sparse alternates are meaningful: a cache name does not add a game-loadable archive or team.

Caches live under output/cache, keyed by source path, and record part sizes/mtime; stale fingerprints are rejected. Current cache validation reparses the TOC; it is a reproducible index, not yet a speed optimization. It does not prove payload integrity after timestamp-preserving changes.

## Standard IFF: FF3BEF94

BE header is 0x20 bytes: magic +0, payload start/headerSize +4, payload end/fileLength +8, zero +0C, block count +10, observed 13 +14, file count +18, observed blockCount*0x20+5 +1C. FileLength excludes optional name table and padding. Preserve all bytes beyond it.

Block descriptors are 0x20 bytes (eight BE words): name/hash, type/hash, unknown1, logical size, unknown2, absolute stored start, stored size, indexed flag. Keep descriptor order; bank IDs such as BB05A9C1 and 411536D5 are not subfile types. Block ranges must fit within payload bounds.

The BE file pointer table follows the blocks. Target = pointer field position + value - 1; inverse = target - field + 1. Follow actual pointers rather than assuming records are contiguous. Each file record is ID, type hash, offset count, then block-relative logical offsets. FFFFFFFF means absent. Infer each span using the next larger valid offset in that block or its logical end. Duplicate starts can imply aliasing; replacement must reject ambiguous shared ranges.

Optional AA171516 name table starts at fileLength: BE magic, LE body size/pointers, UTF-16LE strings. The body contains count and relative pointer to entry-pointer table; each entry has relative name/type pointers. Missing name tables are valid (observed ua256/s212). Fallback names are numeric, with known type hashes when available.

Common types: TXTR 5C369069, SCNE E26C9B5D, LAYT 86A1AC9E, ROST C61649B2, AUDO 1AEDDA1F, NAME 68B693B2, CDAN A7701F00. Full historical type map remains in MASTER_HANDOFF.

H7A wrapper: 0E4837C3, logical size, stored size including 0x14 header, unknown, shift. Descriptor bits are read low to high: 0 literal, 1 BE 16-bit backreference. Distance is low shift bits; copy length is (token >> shift)+3. Validate wrapper sizes, shifts, lookback and truncation. Decoder caps a single logical block at 512 MiB. Unchanged compressed blocks are copied verbatim. No compressor or size-changing writer is claimed. Same-size subfile edits are supported only for one uncompressed span without shared ranges.

## CDF-backed metadata: F0985030

Always handle metadata IFF with its paired CDF; uniforms are not this family. Header +4 is metadata end; +10 block count; +18 record count. +20 points relatively to segment pointer table; +24 points to UTF-16BE CDF name. Primary record pointers start at 0x68. Primary records contain five BE words: ID, type hash, offset count, virtual header offset, virtual payload offset. Virtual offsets are not physical CDF offsets.

Each secondary descriptor is four BE words: CDF header offset/length and payload offset/length. Validate both actual ranges. Optional name table uses the same mixed-endian scheme. CDF TXTR fallback hash is 5C36FB69 (different from standard); AUDO is 1AEDDA1F. Preserve CDF segment headers, gaps, tails, compression and metadata. Same-size physical payload replacement is supported only when no preserved range overlaps. This validates bounds, not codec semantics or console compatibility. Whole CDF-pair build staging remains blocked.

AUDO segment headers can carry a payload length at +18; interleaved audio banks must preserve headers as well as payload. H7A/GTF texture layouts vary; do not infer codec validity from DDS conversion failures.

## Tool files, textures and uniforms

2kTl is BE magic 326B546C, header size, u16 type ID, u16 block count, BE u32 sizes, concatenated blocks. Header size = 12+4*count. Use numeric type IDs; no unvalidated semantic ID mapping. Strictly reject trailing/truncated wrapper bytes.

Standard TXTR often uses separate header and payload blocks; exports preserve individual blocks plus record manifest. Uniform jersey_numbers and names are embedded TXTR subfiles, with separate NAME records possible. Atlas glyph layout is not validated. Candidate texture header fields +58 format, +60 packed width/high16 height/low16, +64 mip/count, +68 pitch, +6C parameter, +90 repeated dimensions (SCNE), +A4 payload offset+1. Report candidates; do not fake DDS output or convert pixel formats blindly.

## SCNE / courts

SCNE package header is 0x54 bytes. +20 texture count; +24 relative texture pointer; +44 model-part count; +48 relative model-part table. Model records are 0xB0 bytes; texture headers also 0xB0. Part name at +0 is relative UTF-16BE. +04 ID; +08 flags; +10 radius-like float; +30..38 center; +4C..54 scale. Section counts/pointers: material +60/+64, draws +7C/+80, buffers +84/+88, declarations +94/+9C. +A4 is index flags, +A8 index count, +AC index offset+1 (do not confuse flags with count). Known floor parts: floor, paint, centerlogo, lines. Full-court imagery requires validated UV/material routes; changing texture dimensions alone does not create full-court coverage. OBJ writing and geometry edits are deferred.

## Roster and development direction

Roster inputs historically include ROST subfiles, standard IFF roster_english, tool wrappers and save-container variants. Current commands preserve structure/bytes and compare changed spans; semantic decode and edit are blocked until source adapters and field validators are proven. Historical tables, player/team field offsets and write tiers are preserved verbatim in MASTER_HANDOFF section 10. Conference/prestige fields are unmapped; do not invent safe controls. IDs for teams, jersey assets, heads, coaches and arenas are distinct. Replacing existing teams/alternates/cyberfaces is safer than assuming new objects can be registered.

Future work: validate roster adapters and field ranges; prove compressed same-size writer; add paired CDF staging; extend texture variant metadata, atlas investigation, SCNE materials/UV inspection, inventory audit and hash collision handling. Console versus RPCS3 profiles should compare texture dimensions/formats/mips to vanilla, with validated conversion tools. No ISO authoring or gameplay certification is currently provided.

## Current safety contract and evidence

All outputs, including mod staging and logs, are restricted to project output/{rips,builds,isos,reports,cache,temp,smoke_tests}. Reject resolved paths inside vanilla/JB source, source overwrite, path traversal and linked build trees. Builds preflight every override before copying and patch only same-size extents in the copy. Existing populated builds are refused even with --overwrite. CLI and 22-panel Tkinter GUI share a command registry/backend; worker subprocesses stream logs without touching Tk from worker threads.

Smoke evidence: ua000.iff raw extent 602112 bytes, SHA256 ea00dae62c9747f314d03462c8d9b605fc9fd355a1c928d4011a8d18b6d9f266; standard parser found two compressed blocks and eleven records; H7A decode and subfile dumps succeeded. sideline_items.iff/.cdf parsed and dumped six records. Tk root and all 22 panels initialized successfully. No write operations target the vanilla fixture. See CODEX_UPDATE_SUMMARY for test and publication results; do not infer completion from feature command registration.

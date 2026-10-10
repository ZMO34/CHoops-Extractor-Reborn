# Archive size and new assets

## Size behavior

The split archive presents one logical address space across its bank files. Its 24-byte header contains magic, alignment, bank count and TOC entry count. Bank descriptors are 16 bytes, with declared lengths in 2048-byte units and UTF-16BE names. TOC entries are 16 bytes: filename hash, aligned logical offset, an unclassified word, and aligned declared size. When a declared extent is unusable, the reader bounds it by the next entry or archive end.

Standard IFFs contain logical record/block tables and stored blocks, some compressed with H7A. Edits retain logical record lengths and reconstruct stored block offsets. The writer preserves untouched blocks and unknown bytes, moves the name trailer byte-exactly, and may consume only identified zero padding. It refuses a replacement larger than the original allocation. JB builds patch existing extents without changing bank lengths or relocating the TOC.

The old preservation encoder could expand invalidated backreferences into literals after a texture edit. A bounded-window H7A recompressor now runs when that path grows the stored stream, and the smaller verified result is used. Unchanged streams remain byte-exact. An incompressible replacement can still exceed capacity; it is refused rather than silently inflating the game.

## Adding alternates

Adding new assets is technically a coordinated archive-and-roster rebuild, rather than appending an IFF to a bank. It requires a new unique name/hash, TOC entry, alignment and bank lengths, relocated affected extents, and a corresponding team-owned uniform roster record. ROST table/heap relocation must fix relative pointers and counts while preserving every unrelated field. The runtime's uniform lookup is count-driven and selects matching records, which makes additional records a plausible route. Complete filename-bank selection, menu/unlock limits and game consumption are still unproved.

No new-asset insertion writer is enabled yet. Existing uniform selectors can be reassigned and known shape bits edited. The current copied-JB writer intentionally keeps file lengths fixed.

Verified with overlapping-reference compression tests, unchanged-stream identity, existing copied-JB tests and a real same-extent uniform texture edit.

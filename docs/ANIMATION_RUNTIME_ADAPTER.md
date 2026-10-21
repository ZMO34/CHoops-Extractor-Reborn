# Runtime adapter follow-up

This is an offline reference implementation and native-format investigation.
It does not install a PS3 sampling hook, donor registry, wider roster ID field or
playable animation. The full port remains unfinished. The original executables,
source archives and supplied overrides remain unchanged.

## Additional event correspondence

Ghidra and raw instruction checks match CH `0x3073B4` with NBA11 `0x46DE20`:
both fill a motion-trajectory cache's timing fields at +0x20/+0x30/+0x34/+0x38,
sample root displacement, calculate a reciprocal time interval and pass the four
times to corresponding five-float curve normalizers. CH `0x2CBEC` and NBA11
`0x141CC` use the same two-branch cubic expression with constants -2 and 3.

| Cache field / role | NBA11 marker | CH marker |
| --- | --- | --- |
| +0x20 / anchor | 20 | 19 |
| +0x30 / first curve control time | 37 | 36 |
| +0x34 / middle curve control time | 46 | 40 |
| +0x38 / last curve control time | 38 | 37 |

These are operation-level roles, not invented anatomical/ball-contact names.
The 46-to-40 correspondence demonstrates why a global ID decrement is incorrect.
`curve_timing_contract()` includes these four rules and the previous three
mirrored-selector rules. It remains explicit and opt-in; it is not a complete
map of every downstream event listener or a default for arbitrary animations.

The NBA11 marker-time wrapper `0x396F90` returns the first event time or a
negative-FLT_MAX fallback. CH's cache uses its own missing-event fallback. The
bridge retains actual marker presence/absence, exact time bits, duplicates and
order; it does not insert one game's fallback value as a marker in the other.
The internal cache state flags also differ and must not be copied between games.

Private audit: the seven-rule contract converts 3,616 of 9,574 identified event
tables, with 2,337 actual event rows. Empty lists are included in that table
count. **5,958 tables still block** on other IDs or opaque payload schemas.
No count here represents certified playable clips.

## Native donor registry

The collection type `0x449E4AC7` is consumed by NBA11 `0x6599D0`. It traverses
20-byte entries, filters category at +4, counts entries including a separate
zero-flag subset at +0x10, and creates a per-category array of entry pointers.
Native `0x659730` looks entries up by their first word. The key also resolves
through the supplied game's localization data after tagging its low bit.
Entry +0xC provides the observed ordinal; the reader preserves its raw value.

The manager initializes 31 categories (0..30). Entry +8 points to a category-
specific payload. Its constructor dispatcher `0x65840C` resolves eight 12-byte
reference slots for category zero, one slot for categories 2..10, and two slots
for the remaining observed categories. The resolver `0x656B70` reads each slot's
resource ID, chooses SingleMoCap `0x60900D71` when its kind word is zero or the
group family `0x39F61D57` otherwise, and writes a resolved pointer into +8.
Serialized slots in the supplied banks have zero runtime-cache words.

The reader validates each payload's own bounds, retains empty slots and unknown
tails, and resolves dependencies using **type and ID**, including related banks.
It reports missing/duplicate identities without selecting a load-order winner.
Group identity resolution is not group-payload or alias-graph translation.
Native accessor `0x656AEC` selects resolved group members for kind 1..4 at runtime
object offsets +0xC/+0x1C/+0x2C/+0x3C; kind zero uses the direct resolved pointer
and kind five returns null. Other kind values remain unestablished in the report.
The four supplied nonempty group references all use kind one. Category-zero
accessor `0x657004` chooses slot six or seven from a caller flag; its handedness
or gameplay meaning is not yet established, so neither slot is arbitrarily chosen.
These runtime offsets must not be treated as serialized file pointer fields.

```
python -m choops_py.cli inspect-donor-registry siganims_generic.iff nba-2k11 output/research/signature-registry.json --related-bank siganims_generic_extra.iff
```

Private supplied-copy audit: 988 entries, 31 categories, 2,478 uniquely resolved
nonempty slots and 320 explicit empty slots; no missing/ambiguous references.
Four nonempty slots refer to the group family. Every combined category has unique
contiguous ordinals. Category zero has 147 entries, ordinals 0..146, eight reference
slots and an additional four-byte field whose meaning remains unresolved; other
categories have larger unparsed tails. The parser is not an executable writer.

This is materially different from CH's fixed 112-row shot table. A mechanical
append of 147 styles would need 259 indices, exceeding the existing unsigned byte
at player +0x73. No ID is wrapped/truncated and no original style is discarded.
A wider-ID or indirection design, complete variant mapping and target registration
metadata still need implementation. Native source entry lookup uses a full word;
source keys/ordinals must not be written into the CH byte field directly.

## Header and sampling reference

`MotionSampler` maps decoded ELF analysis copies read-only. It verifies the
canonical bind, validates motion masks/counts, rejects NBA11's unhandled unpacked
pose branch, and reads source byte-delta key timing at header +0x24, poses at
+0x28 and root tracks at +0x2C. It validates the **complete** pose/root extents
before returning even a time-zero sample, without allocating those extents.

It checks positive finite rate/time-scale metadata and agreement between declared
duration and the authored key ticks. It decodes only the two bracketing poses,
using the existing mathematical SLERP/linear reference. Authored endpoints retain
exact packed-selector conversion and padding. Root signed words use the matching
key interval. Mirror/world/auxiliary transformations, root heading angle conversion,
loop policy and event dispatch remain separate, explicitly reported stages.

```
python -m choops_py.cli sample-native-motion NBA11_ANALYSIS.ELF CH_ANALYSIS.ELF 0xHEADER_ADDRESS 0.25 output/research/sample.json --cache-bytes 65536
```

The JSON includes the one-frame CH packed pose, source key indices/fraction,
pre-transform root words, confirmed timing fields, raw header words and cache
statistics. Inputs cannot be overwritten. All actual-game reports stay private.

This does not establish CH +0x24/+0x28/+0x2C authoring metadata from an NBA clip.
Those offsets have different source/target meanings. Remaining header flag bits,
auxiliary curves, desired-motion metadata and bank relocation still prevent a
complete header writer. No unrelated template metadata is substituted.

## Memory handling and verification

The source pose data stays at authored keys. The offline sampler retains a byte-
budgeted LRU rather than a 235 MB expanded pose bank or an expanded key index.
Only one worker owns a sampler. Each cached read is bounded; eviction updates
accounting, close releases mappings, and changed input size/mtime/inode invalidates
the cache. These metadata checks do not certify same-metadata external edits.

Synthetic tests compare every integer tick against full expansion using nontrivial
rotations/translations/root tracks; they exercise long scrubs/eviction, endpoint
clamping, timeline errors, stale inputs, closed readers and later-key BSS overlap.
Private corpus: 28,722 samples across 9,574 unique streams, zero errors; first/last
pose bytes match the converter. With a 65,536-byte budget, peak retained payload
was exactly 65,536 bytes, with no expanded bank allocation.

The cap describes retained **payload bytes**, not all Python/OS memory, mapped
virtual address space or PS3 heap residency. A native demand loader/sampler hook,
allocator integration and real-game memory/lifetime validation remain required.
No native hook, emulator, hardware test or automatic/testing JB was run.

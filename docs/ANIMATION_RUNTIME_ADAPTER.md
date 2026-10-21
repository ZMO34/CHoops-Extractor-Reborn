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


## Target header ownership and native relocation follow-up

The new `research.target_motion` backend validates existing CH headers and builds
self-contained **CH-backed** resident images. It does not derive the unresolved
CH authoring fields from NBA, install a native demand-loader, or finish the donor
port. Every nonpointer byte of a supplied CH header is preserved; the builder
never substitutes metadata from an unrelated style into a donor header.

Focused Ghidra and original-instruction checks establish these boundaries:

| Native route | Confirmed operation |
| --- | --- |
| CH `0x1E9C0` | Fix up +0x30/+0x34/+0x38/+0x3C, then +0x40 tail sized by +0x10 low six bits |
| CH `0x1EAA0` | Inverse fixup of the same fields |
| CH `0x77FB1C` through `0x11650` | Null stays null; signed relative word becomes field address + word - 1 |
| CH `0x77FAF4` through `0x15200` | Null stays null; pointer becomes pointer - field address + 1 |
| CH `0x23D58` | Alias resolution copies those four pointers and the counted pointer tail; it does not copy scalar/mask metadata |
| CH `0x23B6C` / `0x23C60` | Group pointer fixup/unfixup surrounds the corresponding motion fixup/unfixup |

Consequently, resolving an alias is not ownership transfer or a deep copy. A
cache may not evict backing tracks while registered headers or their aliases
still reference them. These routines do not establish a heap pin/refcount API.
The raw relocation oracle requires the caller to declare its pointer state;
state cannot be inferred reliably from arbitrary words. A future native loader
must own that state and call each transition once, not guess from pointer values.

`inspect_target_motion` checks canonical channels, count/rate, finite time and
movement metadata, complete header/tail extent, full poses/root tracks and a
bounded event list through its sentinel. It reports load-segment ownership and
unknown dependency extents. CH root rows use six or eight bytes according to the
confirmed high mode bit. Unknown flag meanings remain raw and explicitly incomplete.
It does not equate a successful extent check with validated contacts or playback.

`prepare_target_image` accepts 1..4096 distinct existing CH headers and a 64-byte
to 16-MiB payload budget. It materializes complete known dependencies, deduplicates
identical source extents, aligns stored extents to 16 bytes, and emits relative
pointers. Header overlaps, unresolved aliases, auxiliary tracks and nonnull +0x3C
unknown extents block preparation. `relocate_target_image` checks the complete
native view before returning a result, including later pose/root frames, events,
32-bit address overflow and header storage collisions. No file is modified.
The budget covers resident-image payload, not temporary preparation memory or RSS.

The shot-registration CLI gains the opt-in deep check:

```
python -m choops_py.cli inspect-shot-registration CH_ANALYSIS.ELF output/research/deep-registration.json --motion-extents
```

It deduplicates the registered motion audits and retains the shallow compatibility
check as the default. On the supplied stock executable, 112 styles reference 224
distinct headers; all 224 pass full dependency extents. Fifty-six fit the current
self-contained subset without unknown auxiliary extents. Across the identified
full-body family, all 7,055 headers pass inspection, and all 2,522 supported
headers pass owned-image preparation and exact relative/native/inverse roundtrip.
The largest individual image is 126,996 bytes. Other headers remain inspectable,
but are not silently copied with guessed auxiliary lengths.

### Separate resident registration experiment

The private, authorized decoded-ELF experiment extends the earlier table-only
probe. It copies the two headers of stock row eight plus complete pose/root/event
tracks into one 4,656-byte owned image. The headers share track storage where the
originals share the same source extent. Both appended row pointers address the
new image; no motion pointer borrows original or donor storage. The first 112
playback rows remain byte-identical and the appended row retains its source's
other playback metadata. Its display name is the existing Generic 1 tagged key,
an explicit placeholder, not a claimed donor label.

The plan reserves table, names and image after the entire TLS template. It uses
9,648 bytes of 14,848 available verified-zero file padding, extends only the
existing writable segment's file/memory sizes, and now checks both physical file
padding and collisions with every other virtual load range. All segment offsets,
TLS, neighboring label arrays and unrelated bytes remain unchanged. Reparse,
full registered-track extents, image roundtrip and exact byte-diff allowlist pass.
Original source hashes remain unchanged.

This is a **stock-backed static residency/registration structure probe**. It adds
no heap allocations and relies on normal executable-segment lifetime; it does
not implement the donor loader's allocation, eviction, synchronization or shutdown
protocol. It is a decoded analysis ELF, not a signed/hardware-certified EBOOT.
No executable writer is exposed in the tool, and no probe assets are published.
No emulator, hardware or automatic/testing JB was run.

### Still required for the requested donor integration

- Establish donor-to-CH authoring metadata, remaining flags and auxiliary extents;
  do not advertise retained CH metadata as a completed cross-game translator.
- Finish donor event/variant and graph dependencies before registering a playable
  style. An idle clip in a shot slot would not prove a working donor shot.
- Implement native resource lifetime/allocator or an appropriately bounded native
  streaming path for the donor library. This static probe does not provide it.
- Validate native runtime behavior separately. Structural checks cannot certify
  frame-time memory use, asynchronous load ordering, lifetime or gameplay.

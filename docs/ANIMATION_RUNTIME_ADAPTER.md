## Whole-library scope and provider routing correction

The owner's scope is the entire NBA11 animation library: free throws, running
shots, rebounds and every other family. No family is being discarded. Right-stick
controls remain secondary. The four-pair category-zero work remains useful, but
must not be confused with the paired jump-shot table.

Native `0x657824` takes 41 provider selector codes and routes them into 31
serialized registry categories. Selector 20 uses player +0x124 and category 14;
selector 0 uses player +0xD4 and the separate category 0 sequence family. Selector 14
actually selects category 5. Ten selectors share category1 with separate player
key fields. Five paired selector groups choose alternate key fields through the
third argument; neither categories nor selector numbers are motion IDs.
`signature_provider.py` records all bindings; the native harness passes 82 cases.

Category14 contains 203 paired entries / 406 nonempty references in the supplied
signature banks. `prepare_jump_pair` now retains both lane headers and every one
of the nine metadata-tail words. Unknown extra tail bytes and unsupported group
references block preparation. The category 0 four-pair preparation and fallback
work is retained separately. All registry reports expose provider-selector codes.
The earlier hypothetical 112+147=259 comparison is NOT the paired jump-shot
capacity requirement: retaining 112 stock entries plus 203 category 14 entries needs
315 IDs. The stock byte field still cannot represent this. No IDs are truncated,
styles discarded or incorrect family appended to the stock table.

Whole supplied-IFF audit covers all 4,705 identified SingleMoCap records in 11
containers (46,937,781 stored bytes), including crowd, mascot, presentation and
other banks. All 4,705 now pass bounded declared-track inspection: 2,263 alias
headers, 2,441 distinct payload-record hashes and 18 channel layouts across 16/21/24
bone declarations. Two alias conflicts are exact 6,112-byte duplicate records.
Optional identical-record coalescing proves equality of ALL decoded bytes and
retains every candidate's provenance; distinct or unknown-tail differences reject.
Strict ambiguity rejection remains the default. The 3,090 canonical-family
candidates remain separate from 1,615 other-rig records: inspection does not bypass
conversion's canonical bind gate or invent a crowd/global bone map.

The read-only `inspect-animation-library` CLI audits all supplied typed records,
reports bounded failures and channel-family/event coverage, and protects every
input. The single-record inspector gains explicit declared-channel/coalescing
options. This does not discover executable-held clips or establish that unknown
archive resources are irrelevant. Its fixed-rate pose/root size estimate is
71,643,008 bytes before headers/events/selectors/registration and before target
bone mapping; the largest component is 818,400 bytes. Full-library memory/streaming
integration must address the total, rather than raising per-image guards blindly.

CH gameplay initialization `0x32479C` is now exercised, beyond the preview getter:
player +0x73 chooses a 40-byte row; player +0x84 bit25 selects the lane. Row +4/+8
feeds state +0xD8, +0xC feeds +0xE4, +0x10 feeds +0x104, +0x14 feeds +0x48,
+0x20/+0x24 feeds motion +0x74, +0x8C is cleared, and +0x1C feeds the per-actor
28-byte record +4. The real hand getter/thunk and TOC restoration execute in six
synthetic native cases at indices 0/111/255. Donor category 14 lane selection at
`0x499468`/`0x499474` passes two cases. Row field basketball meanings and automatic
cross-game authoring remain incomplete. Stock inspection now exposes raw metadata
words, not invented field names.

Next work remains active across the whole library: native executable-held bank
coverage, per-rig mapping, event/payload and selector semantics, target playback
and transition contexts, wide-ID selection, and bounded loading/lifetime/streaming.
No complete playable import or gameplay validation is claimed. Source game banks
and executables remain unchanged; no game/emulator or automatic JB test runs.

## Native shot fallback graph and dependency closure

Current priority remains animation porting; right-stick controls stay deferred.
NBA11 cache initializer `0x6535BC` is now traced through its fallback branches,
and cache-key reader `0x6533C0` is established. This supersedes the older
statement that the fallback graph itself was untraced; target role mapping,
context predicate semantics and native target dispatch are still unresolved.

- Cache identity is player pointer plus player +0xD4. Selector/context are not
  additional keys. Resource replacement must invalidate cached pointers or retain
  their owners; the resident process-lifetime owner remains necessary.
- Cache +0x1C/+0x20 retain original pair0/pair1 presence, before filling fallbacks.
  Callers of `0x653A3C`/`0x6539D8` can request these original-presence flags.
- Missing pair0 uses eight weighted rows (`0x434F1D0`, stride20). Each row consumes
  one RNG sample; native float32 weight/cumulative-weight must strictly exceed
  that sample to replace the selected row. This is a reservoir pass, not a
  single cumulative-distribution draw.
- Missing pair1 uses unsigned player +0x1C modulo18 into `0x434F270`, stride32;
  it replaces pair1 AND pair2 even if pair2 originally existed. The player field's
  basketball meaning is not assumed.
- Still-empty pair2 selects embedded `0x3F8C798`/`0x3F8C7D0` by lane. Empty pair3
  or a true optional context predicate selects lane-specific globals at
  `0x434F1C4`/`0x434F1CC` and resets cache +0x18 to zero. Missing context, a -1
  context ID, and a false predicate do not force replacement. The extra generator
  getter call on pair3 replacement remains observable even without an RNG draw.

`shot_fallback.py` adds bounded resolution and read-only revision-guarded table
inspection. Handles/predicate results/RNG samples are explicit inputs; it does
not guess target resource identities or reimplement unproven service semantics.
The inspector distinguishes serialized resource IDs, embedded pointers, explicit
empty entries and ambiguous identities, retaining input fingerprints. A family
preparation report now records original lane presence, fallback requirements and
that fallback resources are not included in its eight-slot image.

Supplied-copy closure: 92 referenced positions = 64 unique bank-backed motions
(all resolve uniquely in the supplied signature banks and already occur among
shot slots), 24 unique executable-held headers, and four explicit empties.
All 24 embedded headers' pose/root components convert: 708 authored keys remain
exact across 6,426 fixed frames / 972,972 component bytes, before deduplication.
Source hashes are unchanged. Header references, events, selectors and metadata
still gate complete motion construction; component success is not playability.

`NativeShotFallbackTrace.java` passes 145 bounded read-only instruction cases:
140 fallback cases across both lanes, all 16 presence masks, missing/invalid-ID/
false/true context, modulo boundaries and reservoir thresholds; five native cache
key cases. RNG/context service results are mocked, with original fallback
instructions executed. A Python/native comparison agrees on all 140 motion
vectors and RNG draw counts. Nonzero control-value preservation/reset is checked.
Next: map CH playback contexts and integrate the complete fallback dependency set
with resident registration, retaining original presence flags. Remaining event,
selector, authoring metadata and style-capacity gaps still block a full port.

## NBA11 shot-family preservation (animation priority)

Animation porting takes priority; NBA2K14 right-stick/default-preset work is deferred.
NBA11 native consumer `0x6535BC`, player getter `0x949CF0`, and reference
resolver `0x656AEC` establish four paired references per category-zero entry.
Player +0xCC bit zero selects slots 1/3/5/7; bit one selects 0/2/4/6.
The consumed word at payload +0x60 indexes native table `0xA51564`; its full
meaning/table bounds and target mapping remain unresolved. All 147 supplied
styles use index zero. Only 18 styles have the first pair; all 147 have pairs
one through three. The first pair must not be assumed to be the base shot.
CH `0x3213B8` selects row +0x20 for a nonzero selector and +0x24 for zero.
That proves ordering, not basketball roles or cross-game contextual equivalence.

`prepare_shot_family` now prepares every nonempty direct source reference with
explicit per-header metadata/event/auxiliary contracts. It retains all eight
slots, four pairs and distinct alias headers, deduplicates repeated header
references, checks the whole-family byte budget and verifies relocation inverse.
Missing/ambiguous resources, unsupported group dependencies, unknown trailing
bytes and incomplete/stale contracts reject the complete result. Empty slots
remain explicit; no contextual fallbacks or target role names are invented.
This research API does not install native family dispatch or establish playable
metadata. Existing event/selector identity gaps and the 259-style byte-ID conflict
remain. Next: trace contextual fallbacks and map each pair to CH playback contexts
before binding complete donor families into the resident registration path.

A bounded read-only Ghidra harness checks 14 donor cases (both selection bits,
reference kinds 0..5, and empty optional pairs) plus two CH row-order cases.
Only registry lookup is mocked; source selection stops before contextual
fallback handling. No game execution or source executable writes occur.

# Counted selector transport and controller-axis routing — 2026-10-23

Schema-2 serialized metadata now also requires `source_banks_sha256`, an ordered list of complete fingerprints for every supplied bank. A reproduced stale-contract bug allowed a related alias payload bank to change while the origin bank/header stayed unchanged. The full bank-set binding rejects that change; reports retain their own list copy. Earlier draft contracts missing this field must be regenerated. This closes an input-binding gap, not a semantic-mapping gap.

The counted pointer tails are now supported end to end for the observed selector encoding: NBA11 +0x38 → CH +0x40, four bytes per curve pointer, count from header +0x10 & 0x3F. `read_selector_prefix` always reads at least two knots, then stops at the first upper knot bracketing the final declared query. A caller-supplied bounded reader enforces record or file-backed memory limits. It never copies an inferred neighboring region wholesale. Prefixes are limited to 65,536 knots; decreasing ticks, header/track overlaps, null counted pointers and missing terminal brackets reject installation. Exact sharing between selector tracks is allowed; partial overlap is rejected.

The terminal bound covers both mathematical `ceil(duration * scale * 300)` and the native single-precision multiply sequence. For duration 2.2576792240142822 and scale 2.7786645889282227, the former is 1882 but native multiplication reaches 1882.0001220703125, requiring a knot at tick 1883. This bound prevents an endpoint read past the copied prefix. It does not claim bit-exact VMX reciprocal interpolation or establish out-of-domain queries.

`translate_signature_motion(..., auxiliary_contracts=[...])` requires one schema-1 contract per counted channel, containing:

- `source_channel`: exact zero-based index, preserving channel order;
- `source_curve_sha256`: hash of the consumed prefix, not an inferred padded extent;
- `target_elf_sha256`: the same complete target executable bound by the metadata contract;
- `channel_evidence`: bounded research assertion about channel correspondence;
- `rules`: explicit byte-valued `source`, `target`, and nonempty `evidence` for every consumed selector identity.

No default identity map is supplied. Duplicate/stale/missing/unproven rules reject conversion. Only the upper selector byte changes; every signed 24-bit tick and knot is retained. Channel/resource semantics are caller research assertions, recorded as such rather than automatically established. Unknown header references, membership and event payloads still block component construction. The serializer includes the extended header and all aligned curves in its preflight budget before pose expansion. Existing CH curves require no cross-game mapping and can be copied with their native identities.

Target inspection, preparation, relocation and static residency now validate full selector prefixes as owned dependencies. The generic allocator model also benefits from the shared relocation validation. Extra +0x3C data remains unbounded and blocked. Relocation and inverse byte preservation are mandatory. The serialized metadata report now records decoded float32 planar values, correcting a provenance-only bug that previously listed the packed bytes.

The updated read-only source inspector accepts all 2,444 motions / 1,222 aliases, now including 4,016 bounded selector references. CLI reports expose consumed prefix sizes, hashes and selector values while leaving semantics unresolved. Private read-only corpus evidence: 806 NBA11 consumed prefixes total 35,592 bytes, compared with 35,852 bytes in previously bounded containing regions; the remaining 260 bytes occur beyond the needed terminal brackets and their meaning is not inferred. The 336 CH header references consume 12,424 bytes. All 224 distinct CH stock headers prepare together, deduplicating 168 selector tracks and producing 559,640 relative bytes. A separate in-memory resident-publication probe adds one duplicate of every original style: 224 total registrations, all 112 original rows unchanged, 224 owned motion headers, 569,504 bytes including tables/names, and exact inverse/BSS/source-preservation checks. Added labels deliberately use a documented stock placeholder. No donor shot or gameplay result is implied.

The NBA2K14 input path continues through native getter 0xB5D298 and controller method 0x8E62C (descriptor 0xE12970, vtable 0xDA77F8 slot +0x2C). The getter reads record +0x110 + 16*axis, port stride 0x310; indices 0/1 are left X/Y and 2/3 right X/Y. The snapshot loop at 0x8E4CC copies all 30 axis values into a controller snapshot. `NativeStickInputTrace.java` now executes the real controller wrapper and getter for every axis on ports 0/6 with unique values, no mock calls in those 60 cases. Together with the original nine input-prefix cases, **69 native instruction cases pass**. This establishes raw routing, not dribble move selection, camera-relative gestures, deadzones or control presets. The observed low-level postprocessor at 0xB5D888 tests left-stick thresholds; it must not be relabeled as right-stick dribble dispatch.

The required final control policy remains NBA2K14 right-stick dribbling by default, with old button-dribble controls selectable as preset A. It has not yet been installed. Native instruction checks use bounded Ghidra harnesses only; RPCS3, gameplay and automatic/testing JB builds remain unrun. Earlier phase notes below are historical where superseded by this section.

# Resident loading, metadata contracts, and NBA2K14 controls — 2026-10-23

`translate_signature_motion` builds an owned relative CH component only with schema-2 metadata bound to source bank index, record index, complete bank hash, header hash, donor executable hash, and target executable hash. It requires explicit target mode, state bits, authored planar values, and bounded evidence for each group. These are caller research assertions, not automatic semantic proof. Unknown event IDs, opaque payloads, uncontracted auxiliary channels, header references, and membership dependencies block construction. The shared serializer validates the known target layout and relocation inverse before returning bytes.

`append_resident_image` creates a separate decoded ELF. It extends the final writable nonexecutable load segment after its original memory extent, materializes original BSS as zeros, preserves existing virtual addresses and loaded bytes, shifts trailing nonloaded data/section offsets, and reparses the result. Unsupported alignment, collisions, TLS interference, unknown dependencies and byte-budget overflow are rejected. Relative/native pointer conversion and inverse reconstruction must match exactly. This is static process-lifetime ownership: no runtime allocation, eviction, rebinding or shutdown free is introduced. It is not a signed SELF installer or proof of hardware loading.

`install_resident_shots` publishes the owned table through established native table/name slots and capacity instruction. It preserves the 112 stock rows and requires explicit paired header indices, 32-byte playback metadata, tagged target localization key, and evidence per added style. The byte-ID limit permits at most 144 additions; 112 + 147 = 259 is rejected rather than truncating donor styles. Original name initialization remains native; tagged added labels do not require freeing. Reports retain validated assertion copies and explicitly mark semantics and gameplay unverified. These APIs are research-only; no GUI or executable-writing CLI was added.

The owner-requested separate-ELF probe installs a stock duplicate with a documented placeholder stock label: 113 total styles, 9,636 resident bytes, 9,443,216 original BSS bytes preserved, exact inverse check, and unchanged input hash. This tests structural publication only. Actual native resource lookups return borrowed pointers; the always-resident image deliberately avoids relying on an unproven resource pin/lease mechanism.

`event_mapping_coverage` uses the same rules as transcoding and reports missing `(source_id, payload_word)` pairs and opaque payload IDs. Across 911 shot headers: 5,358 rows, 2,642 covered, 333 complete event tables; 84 additionally have no unresolved auxiliary/reference/membership dependencies. Unmapped IDs are 4, 18, 25, 55, 103, 114, 147, 148; opaque payload IDs include 92 and 173. These counts do not establish 84 usable shots. CH state words differ from NBA11 and authored planar values cannot be supplied by an unvalidated root-endpoint estimate.

`sample_selector_curve` models weighted selector interpolation from signed 24-bit tick/8-bit selector knots. It is a mathematical reference, not bit-exact VMX reciprocal emulation or a cross-game selector-ID mapping. Across 806 bounded curves, start/midpoint/end queries pass (2,418 samples). Equal-time conflicting selectors and invalid queries are rejected.

`tools/research/NativeStickInputTrace.java` executes the NBA2K14 input prefix at 0xB5DAF0 through 0xB5DD08 in a bounded Ghidra instruction harness. Only pad API/port calls are mocked. Native stores place left X/Y at record +0x110/+0x120 and right X/Y at +0x130/+0x140; port stride is 0x310, valid ports 0..6. CellPadData indices 4/5 supply right X/Y and 6/7 left X/Y. Native single-precision normalization uses reciprocal 255 and inverts Y, without imposing a new deadzone or clamping the slight center/endpoint rounding. Six valid packets on ports 0/6 and three rejected packets pass; rejection retains prior axes. ABI reference: [RPCS3 pad_types.h](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/Io/pad_types.h). No RPCS3 or gameplay was launched.

Remaining work: establish auxiliary resource identities and event payload semantics, prove per-shot target metadata/variants, resolve the 259-style capacity conflict, trace NBA2K14 dribble dispatch and target control consumers, then integrate the default right-stick layout with original controls selectable as preset A. Smooth transitions and gameplay accuracy require subsequent validation; the structural and instruction checks do not certify them.

Earlier phase documentation below is historical. The resident backend above supersedes earlier statements that no native loading path exists; semantic and gameplay gates remain.

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
automatic complete header writer. The contract-gated component builder below
does not establish those missing semantics. No unrelated template metadata is substituted.

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


## Contract-gated donor header construction

`research.donor_header.translate_donor_motion` now assembles a relative CH motion
component from the observed NBA11 **decoded-ELF** packed family, with verified
canonical binds and separately supplied metadata/event contracts. This goes beyond
retaining an existing CH header, but it does not automatically discover the missing
metadata or install the component in a native bank. The signature-IFF records and
aliases were outside this ELF builder; the later serialized-source section below
now supplies their read-only adapter and partial pose/root preparation.

The builder places the source low rotation/translation masks into CH's mask words,
retains native channel counts and rate, expands authored key deltas to fixed frames,
retains exact source time-scale/duration float bits, converts packed quaternion
selectors, resamples the root with its six/eight-byte mode, and writes mapped CH
events. Every mandatory pointer targets the owned component; full target extents
and relative/native/inverse byte equality are checked before returning it. Exact
aligned output size is budgeted before expanded tracks are allocated. Payload
budget is not a total Python/PS3 process-memory claim.

The mandatory metadata contract contains these fields:

| Field | Required assertion |
| --- | --- |
| `schema` | 1 |
| `source_sha256`, `target_sha256` | Complete decoded input fingerprints |
| `source_header_address`, `source_header_sha256` | Exact 56-byte donor header |
| `target_mode_high16` | Explicit target upper mode word |
| `target_state_bits` | Explicit target +0x18 word |
| `authored_planar` | Explicit finite `[speed, X, Z]` for +0x24/+0x28/+0x2C |
| `evidence` | Bounded nonempty `mode`, `state`, `planar` research explanations |

These are **caller research assertions**, not facts proved by an evidence string.
No default contract or unrelated CH template is supplied. Fingerprints prevent
stale stream/revision assertions from being reused with changed inputs. The
manifest retains the assertions and labels automatic metadata establishment false.
Current conversion verification uses synthetic assertions only; this update does
not claim a verified real-game metadata contract or playable donor shot.

Missing event rules, opaque payloads, unsupported packing, null dependencies,
header +4 references, counted auxiliary tracks and +0x34 membership dependencies
still block output. They are not replaced with empty data. The root-stride, mirror
and cyclic-phase bit positions must remain consistent with the donor. Other mode
and state semantics remain explicit assertions rather than copied opaque defaults.
No executable writer or automatic installation is added to the editor.

## Native allocator wrapper and ownership model

RTTI identifies `VCRESOURCEGLOBAL_HEAP_ALLOCATOR`, whose observed vtable is at
`0x12773AF8`. The allocation entry is CH `0x843404`, release is `0x8434B8`, both
using TOC `0xA64A94`. Allocation takes its heap object from wrapper +0x14 and
forwards size/alignment into heap vtable slot +0x4C. Wrapper +0x10 selects heap
policy word 3 when nonzero or the heap's +0x18 word otherwise; the remaining two
arguments are forwarded unchanged. Release invokes the **same bound heap** at
vtable +8 with the pointer and two zero arguments, then returns 1. The release
wrapper's return is not an independent proof of heap success.

The observed `VCHEAP2` vtable at `0x12773580` resolves +0x4C to `0x8258C0` and +8
to `0x8248A8`. The allocation implementation rounds using the requested alignment
and includes heap bookkeeping; component bytes alone are not a measured heap cost.
These type/descriptor links and wrapper instructions were checked in Ghidra and
original disassembly. Resource getter `0x841810` looks up via `0x841690`, then
calls the selected provider's +0x18 method. Resource attachment `0x8418C4` first
invokes provider +0xC and links it only after success. This is a concrete native
route, but the provider's complete file/bank ownership protocol remains unfinished.

The asset-free Ghidra script `tools/research/AllocatorABITrace.java` supplies a
bounded revision-guarded instruction harness. On a separate decoded analysis
project it runs the actual wrapper instructions with synthetic heap objects,
traps the synthetic heap callback, checks arguments/TOC and resumes through return.
Four cases pass: default policy, alternate policy, null allocation and release.
The harness does **not execute the actual heap allocator/free implementation**, run
a match or patch an executable. It writes a new JSON only and refuses existing
outputs. Ghidra's `/C:/...` Windows source spelling is normalized for source checks.

`research.resident_loader.ResidentLoaderModel` implements an offline ownership
protocol around synchronous bound allocation/free/read/write callbacks:

1. Validate the entire relative image before allocation; enforce a resident
   payload budget and at most 4,096 tracked live/quarantined allocations.
2. Allocate with 16-byte alignment, relocate at the returned address, write and
   read back all bytes before publishing to the **local Python registry**.
3. Acquire explicit reader leases. Retirement stops new leases; release waits
   until the last existing reader leaves, including shutdown/concurrent retirement.
4. Roll back an unpublished write/readback failure through the same allocator.
   An uncertain free is quarantined with its budget retained and is not retried.
5. Invalid/overlapping allocator results are quarantined; every overlapping older
   bank also stops accepting leases. Released records are removed so repeated
   load/release cycles do not retain a growing history. Callback reentry is refused.
6. Require an immutable heap-address/generation identity callback. Check it before
   allocation, after allocation/readback, before issuing a reader lease and before
   release. A rebound/reused heap quarantines all affected banks; the model never
   substitutes the wrapper's current heap for an allocation's captured owner.

This model is **not native loader installation**. It provides tested ordering,
rollback and lifetime rules for the future bridge. No game pointers are published,
and native aliases/cached readers do not automatically acquire these Python leases.
Every relevant native reader/publication/retirement boundary must be connected
before this protocol can safely authorize real-game frees. Identity checks detect
reported rebinding; they do not stop external heap destruction or close a check/use
race. A native binding still needs heap-lifetime synchronization and real generation
tracking, beyond this model's local lock. The callback arguments
carry the observed ABI shape, not newly invented meanings for its policy/tag words.

## Signature banks, auxiliary curves and memory scope

The signature bank resources are distinct from the embedded ELF motion pool.
The category-zero lookup IDs do not resolve to that pool, so its 235 MB full-family
expansion is not the right way to size a signature-shot subset. Read-only inspection
of the two actual IFF banks resolves all 918 nonempty category-zero references,
including 458 alias slots. There are 911 distinct referenced headers and 456 distinct
resolved payloads; alias metadata/count compatibility passes before estimating size.

At fixed donor rate, the known pose/root/header components plus one eight-byte CH
event row per source marker project to 12,307,462 bytes after exact-source extent
deduplication. Per-style projections range from 32,758 to 151,272 bytes. These
figures exclude auxiliary/opaque event payloads, alignment, registration, heap
bookkeeping and existing CH assets; they are **not a certified resident budget**.
The 259-ID versus byte-field limit also remains. No stock style is removed to fit.

Native CH `0x203AC` and the auxiliary branch in NBA11 `0x1B764` use four-byte
selector knots: upper byte selector, low **signed 24-bit tick**, at a fixed 300 Hz
multiplied by header time-scale. The samplers find bracketing knots and construct
selector/weight results; these are not ordinary fixed-rate pose/root rows. The
new read-only `research.motion_auxiliary.inspect_selector_curve` accepts a caller-
established complete region, retains words/selectors/ticks, checks monotonicity
and declared-duration bracketing, and reports equal-time knots without certifying
playback. It does not infer a terminator or turn unknown padding into knots.

Private signature-bank audit: all 806 bounded curves in the 456 resolved payloads
pass inspection, totaling 35,852 curve bytes. Selector identities/target routing
remain unresolved; byte-compatible knot layout does not authorize copying their
meaning across games. The current donor writer therefore continues to reject these
auxiliary dependencies. This preserves the remaining gate instead of discarding
required data to manufacture an apparently successful shot conversion.

Mode consumers CH `0x235BC` and NBA11 `0x12C10` share the cyclic-phase gate at bit
28, selector nibble at bits 24..27 and threshold byte at bits 16..23, with mirror
participating in phase selection. Their input-state layouts and final clamping
behavior differ. This establishes field use/positions, not identical complete
phase algorithms or the remaining mode/state semantics.

Original executables and source banks remain unchanged. Ghidra's bounded instruction
harness was run; RPCS3, hardware/gameplay and automatic/testing JB were not run.
The full native donor loader, automatic metadata derivation, signature-bank auxiliary selector mapping and playable additive shot remain unfinished.
The serialized source adapter below supersedes the earlier source-adapter gap.


## Serialized signature-IFF source adapter — 2026-10-23

`research.signature_motion.SignatureMotionSource` consumes 1..32 related standard
IFF banks with combined stored and declared decoded-block limits of 128 MiB.
It indexes only typed SingleMoCap identities. A caller chooses a bank/record
index; aliases follow their +0x28 ID until a record with nonzero event pointer is
reached. Missing/duplicate matches, cycles and paths beyond 4,096 records fail.
No resource-group selection is silently substituted for a direct motion.

Resolution returns the original alias header separately from the track-owning
record. Masks, channel/rate/auxiliary counts, key count and root/packing modes
must agree across the path. Original mirror/phase/state/timing words remain
original metadata; the adapter does not replace them with the payload owner's
words or claim to derive target authoring fields. Declared timing must agree
with the borrowed key intervals. This is an offline compatibility gate, not
installation of the game's native resource resolver.

All pointers are signed record-relative offsets. Known timing/pose/root/event
and membership extents must fit within their record, stay outside its counted
header, and not overlap one another. Events preserve their existing payload
inspection limits. Counted auxiliary pointers and header +4 references remain
reported dependencies: no curve end, padding, selector meaning or complete
payload semantics is invented. Source bank/record/payload hashes and the entire
alias path distinguish header identity from track ownership.

The native timeline consumes **keys minus one interval bytes**. The existing
shared resampler accepts keys slots but ignores its final slot. Some supplied
serialized records end immediately after the consumed intervals. The adapter
reads only those intervals, appends an explicit unused zero slot in memory and
reports `timing_unused_final_slot_normalized=true`. It never obtains that slot
from a neighboring record. A missing consumed interval still fails bounds checks.

`tracks(bank, record)` returns known source components and a diagnostic manifest.
`prepare_pose_root(bank, record, donor_elf, target_elf, budget=...)` verifies the
canonical executable bind, preflights expanded pose/root bytes against a 64-byte
to 16-MiB budget, and resamples both components. Reports bind provenance to both
complete executable fingerprints, retain the original source header, and list
omitted header/event/auxiliary/membership dependencies. Mirror/phase transforms
are not baked into the component arrays. Neither API produces a complete CH
header, native resident image, installable bank or patched executable.

Read-only CLI (record index is in the first bank):

```
python -m choops_py.cli inspect-signature-motion siganims_generic.iff 0 output/research/signature-motion.json --related-bank siganims_generic_extra.iff
```

The CLI writes JSON only under output/ and protects every related source from
replacement. It reports `complete_motion=false` and `gameplay_ready=false`.

Supplied two-bank audit: all **2,444** SingleMoCap records pass known track checks,
including **1,222** aliases. Category zero retains all **918** nonempty slots,
**458** alias slots, **911** distinct headers and **456** distinct payload owners.
All 456 payloads prepare successfully: **82,076** fixed frames, **11,215** authored
keys, and **12,324,180** total pose/root component bytes summed per payload without
cross-payload deduplication. Every authored pose is reverse-transcoded at its
original tick and equals the original bytes; authored root rows also equal their
source bytes. Interpolated frames retain the existing offline SLERP/quantization
limits. Both banks and both decoded executables keep their original hashes.

This measured component sum has a different scope from the earlier deduplicated
known-component projection; neither is a complete native library/heap budget.
Header/auxiliary/events, alignment, registration, allocator overhead and all
existing CH memory still require separate accounting.

### Remaining route to full NBA11 import and NBA2K14 right-stick dribbling

1. Establish auxiliary selector identities/target routing, complete event payload
   correspondence, per-header target authoring fields and every signature variant.
   Connect the serialized adapter to the complete component writer only when those
   dependencies have explicit validated contracts.
2. Finish additive native lookup/registration and reader/publication/retirement/
   heap-lifetime synchronization. Resolve the 259-style versus byte-ID ceiling
   without truncating IDs or replacing stock styles. Then extend beyond signature
   shots to other motion families, interaction/ball contacts and graph consumers.
3. Trace the supplied **PS3** NBA2K14 right-stick input consumers, normalization,
   camera-relative interpretation, move selection, cancel/blend windows and
   ball/hand ownership against CH's controller/animation dispatch. Existing
   controller/dribble strings are leads, not proof of these semantics. Importing
   clips or changing a controller default alone does not implement right-stick
   dribbling. No NBA2K14 input adapter or control patch is supplied this phase.

Native execution/gameplay acceptance remains separate from structural conversion.
No emulator, hardware or automatic/testing JB was used. Original game inputs
remain immutable; game-derived component arrays/reports stay private.

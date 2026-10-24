## Native motion state consumer comparison

Header+0x18 now has two native-tested cross-game predicates: whether mask0x3F0
is nonzero, and whether bit30 skips clearing a per-actor context pair. The latter
is distinct from mirroring at header+0x14. NBA11 consumers0x471C3C/0x38CC90 and
CH consumers0x3095F8/0x23B794 execute against synthetic inputs in
`NativeMotionStateTrace.java`:21 cases per game,42 total. Context-pair sentinels
verify the expected two-word writes and untouched surrounding bytes.

`motion_state.compare_motion_states` reports these predicate differences in both
native-donor and signature-IFF adapter manifests. It preserves explicit authored
values; it supplies no state defaults, individual-bit correspondence or complete
state mapping. Aggregate predicate equality does not establish compatibility.
Among99 shared-endpoint candidates,94 preserve both observed predicates and5
change the mask0x3F0 predicate. These are correlations, not full motion identity.
Further instruction-verified source consumers include0x491BE4 (combined bit11/
mask0x380 predicate),0x49CC9C/0x49CFBC (bits12/13/14 dispatch) and0x59ECF4
(bit22 copied into a context message). CH0x393284 separately checks bit4 during
dribble launch. These are tracing leads, not established cross-game mappings or
named basketball actions. Further state consumers, auxiliary palettes, timing/blending, registration and
native ownership remain unresolved. Confirmed playable donor imports remain zero.

## Executable-held native donor component construction

Counted selector curves and explicitly bound reciprocal mirror headers can now
reach owned target-component construction and the existing resident-image path.
This closes a source-format rejection affecting all292 native dribbler headers;
it does not establish the authoring/selector contracts needed for actual donor
registration. The shared-curve ID correspondences remain candidates, with no
identity map or compatible-import count. See [native curve/ownership evidence](ANIMATION_RUNTIME_ADAPTER.md).

## Target dribbling playback context

The named CH2K8 dribbling functions lead to a native five-variant/two-lane motion
bundle selector. Its prefix and lookahead storage requirement are now verified;
see [target bundle evidence](ANIMATION_RUNTIME_ADAPTER.md). Four ordinary bundles
are validated, while special candidate types and downstream transitions/blending
remain pending. This provides a target registration format to investigate; it
does not install donor animations or prove their metadata correspondence.

## Dribbler style source coverage

The signature bank's60 dribbling keys with empty motion references are now linked
to keyed graph rows and111 node references /104 distinct graph nodes. They must
not be dropped as empty styles. See the [style-to-node runtime evidence](ANIMATION_RUNTIME_ADAPTER.md)
for provider/category correspondence and native eligibility checks. The reference
preserves selector-zero/bypass behavior and missing-key rejection, but does not
implement full graph transitions or establish the CH counterpart. Confirmed
end-to-end imports remain zero; running, defense and rebounding remain required.

## Dribbler keyed selection and player-cache lifetime

Native leaf0x4691F8 reads the dribbler graph at0x4B93D2C, selects one of nine
16-byte keyed tables (counts+0x1C..+0x3C, pointers+0x5C..+0x7C), compares raw
32-bit keys and returns the FIRST matching row, or null. It neither deduplicates
keys nor substitutes another family. `anim_graph.lookup_graph_key` models that
ordering and validates explicit key/family bounds; family basketball meanings
and the three row payload pointers remain unresolved. Inspection now retains
these rows, unknown words and their bounded payload targets.

The actual caller prefix0x46D07C..0x46D110 gets the player from actor+0x64.
Families0..8 read player +0x100,+0x108,+0x110,+0x10C,+0x104,+0x11C,+0x114,+0x118,
+0x120 respectively, and cache returned row pointers at state+0x4C..+0x6C.
These are native player offsets, not roster-file offsets or provider/category
numbers. They must not be relabeled named dribble moves without more evidence.
Cached rows point INTO the graph: backing graph storage must remain alive until
all such caches are cleared or replaced. Native setup0x46CB4C..0x46CB6C derives
state from actor[+0x14]+0x110 and calls0x469768. That helper clears0x70 bytes,
including all nine caches, then copies parameter words into state+0x2C/+0x30.
Two native cases verify this clear/seed behavior and untouched adjacent bytes.
This establishes setup reset, not graph release or invalidation in other contexts;
corresponding CH2K8 selection/cache ownership remains unresolved.

The public native graph harness now passes53 cases: the earlier3 fixup cases,
45 keyed cases (first/last/missing/empty/duplicate across all9 families), and3
complete player-routing prefixes with actual lookup calls (first/last/missing),
and2 setup reset cases.
Unique per-family keys catch swapped player fields; cache sentinels check unknown
state bytes stay unchanged. Successful runs report no undefined-register warning.
A private supplied-graph probe checks all60 keys plus9 missing-key cases:69 pass,
with graph bytes unchanged. Graph/source/group/library Python checks:68 passed;
graph-specific tests26 passed. This remains source selection/lifetime evidence,
not target graph execution, compatible animation conversion or gameplay validation.

## Native graph relocation coverage for dribbling and bodyup

`research.anim_graph.inspect_graph` now validates the observed NBA11 decoded graph
layout: sixteen count/pointer pairs, fixed table strides, nonoverlapping tables,
signed relative pointer bounds and positional executable motion bindings. It
retains all nine raw node words and distinguishes the native direct-motion and
group-first-member binding paths. Unknown node operations and transitions remain
opaque. Other game profiles reject; no graph writer or target installation exists.
Bounds are64MiB, one million aggregate rows and300,000 pointer fixups; these are
inspection limits, not PS3 residency guarantees. Empty table endpoints, nulls and
backward references are handled explicitly. No conversion count is inferred.

The supplied dribbler graph passes with292 nodes /25,189 pointer fields. The
5,956-byte `animgraph_bodyup` graph (resource0xEE6DA12B) passes with13 nodes /92
pointer fields; all13 bind native groups, with26 canonical-mask member headers.
Dribbler resource0x83C36981 binds292 direct native motions. The bodyup name is a
lead for defensive interactions, not proof of exact gameplay selection semantics.

`NativeAnimGraphTrace.java` executes the real0x37FC60 routine and0x8339AC helper
without mocked calls. Three synthetic cases cover0/1/2 nodes, both binding paths,
all pointer table classes, null/backward references, and whole-buffer preservation
outside expected writes. All3 pass. A separate private bounded read-only probe
also executes fixups on copies of both supplied graphs: dribbler368,721 steps,
bodyup1,633 steps. Both outputs match the reader-derived relocation/binding image
byte for byte, including all unknown bytes. This proves these supplied source
fixups, not graph execution, transition semantics, target compatibility or gameplay.

The supplied CH inventory reports no0x0D53D4B3 resource, and an ASCII handler-name
search found no matching ANIMGRAPHRESOURCEHANDLER name in its ELF. These negative
checks do not prove absence of equivalent target behavior. Target playback and
native ownership still require tracing; copying the donor graph alone is not a
complete loading solution. Running, defensive movement and rebounds remain required.

## Dribbling graph native motion dependencies

Static native tracing identifies NBA11 ANIMGRAPHRESOURCEHANDLER's fixup0x37FF80,
which selects resource0x83C36981 and calls0x37FC60 with table0x3EF977C. The supplied
770,144-byte dribbler graph has292 nodes at decoded offset0x80, stride36. The
loader resolves header pointers +0x40..+0x58 through0x8339AC. Its node loop uses
one executable table entry per node; when node +0x10 bit0 is clear it writes the
entry into node +4. For set bit0 it instead writes node +0 and derives +4 from
that object's +0xC. Both paths relocate node +0x18 and +0x20. This is static
instruction evidence, not a completed native graph-loader execution test.

All292 supplied dribbler nodes have bit0 clear and their executable-held motion
headers have mask0x1DF7DD. This establishes explicit graph-to-native-motion
references absent from an IFF-only inventory; it does not establish canonical
bind equivalence, node operation/transition semantics or target compatibility.
The graph and referenced native motions require joint loading/lifetime work.
No node is counted as a converted compatible animation. Running, defensive and
rebound playback contexts remain required and pending their own tracing.

## Native paired-shot state addressing

The target instruction harness now executes CH accessor0x2351D0 and its real
0x234E30 dependency rather than substituting a state pointer. For the tested
actor +0x20 ==1 path, the address is base +288 * (actor[+0x70] * stride +subindex).
The paired-shot initializer passes subindex0. The stride is read indirectly
through TOC cell0xA54240; base is held at0xA54250. The actor matching the cached
pointer at0xA54264 follows a different path and is NOT covered by this trace.
The meaning of the stride is unresolved; it is not established as a frame index.

All18 combinations of hand bit0/1, style0/111/255 and synthetic stride0/1/2 pass.
The actual player flag getter and TOC restoration still execute. A0x1200-byte
sentinel verifies only the six expected metadata/motion fields change in the
state storage, including untouched adjacent slots. Per-actor +4 dispatch metadata
is checked separately. This establishes bounded addressing and row consumption,
not target field semantics, allocation ownership, fallback or gameplay quality.

Dribbling, running/locomotion, defensive movement and rebounding are required
conversion families alongside scoring. Paired-shot work is a shared-foundation
case, not completion of those families. Their source playback graphs, transitions,
events, target context and native lifetime must each be established before they
can count as compatible conversions. NBA2K14 right-stick controls remain deferred.

## Current conversion scope: compatible on-court 5-v-5 animations

The owner's latest direction narrows the earlier entire-bank goal. Convert/add
only animations compatible with ordinary on-court 5-v-5 play: layups, dunks,
shots (including running shots and free throws), dribbling, running/locomotion,
defensive movement, rebounds and related gameplay moves. Dunk-contest, photo-op, crowd, mascot and other non-gameplay content may be
omitted and must not count toward conversion progress. Unknown gameplay context
or target compatibility remains pending, rather than silently included.

Earlier full-library and grouped-header totals are SOURCE INVENTORY/FORMAT
RESEARCH, not conversion eligibility, successfully converted gameplay actions or
playable-import counts. The library JSON now marks this scope explicitly and
leaves compatible conversion counts unset. Group inspection likewise does not
count a member toward on-court conversion. The category-14 paired-shot and
category-zero gameplay-sequence preparation manifests identify their intended
on-court scope while retaining all unresolved target compatibility gates.

The unpublished generic group-component conversion experiment was deferred;
its private research evidence remains available. No dunk-contest/photo-op group
conversion API or new native installation is published from that experiment.
Broad format readers can remain as reference, but next implementation work is
on proven gameplay contexts, event/selector and target metadata correspondence,
then bounded native loading/ownership. Right-stick controls remain secondary;
the final control policy is still NBA2K14 right-stick default, old layout preset A.

## Whole-library continuation

Current scope is compatible on-court donor families, including dribbling,
running, defense, rebounds, free throws and running shots. See [current runtime ledger](ANIMATION_RUNTIME_ADAPTER.md) for the
complete 4,705-record supplied-IFF audit and native provider routing correction.
Provider selector20 selects serialized category 14 (203 paired entries), whereas
selector 0 selects a separate147-entry four-pair sequence family. The paired
jump-shot additive capacity is 315 total IDs, not 259. Earlier research comparing
category 0 directly with the 112-row CH jump-shot table is superseded on this point;
its format, fallback and component-conversion evidence remains applicable.

> Canonical 21-bone bind correspondence and registration allocation research
> advanced after v1.21. See [ANIMATION_BIND_REGISTRATION.md](ANIMATION_BIND_REGISTRATION.md).
> Full event semantics and playable donor registration remain incomplete.

# Cross-game animation and controls implementation ledger

Owner scope (2026-10-20): research and implement as much NBA 2K11/14 on-court
animation/control behavior as evidence supports, preserve the College Hoops 2K8
backend, keep original controls in preset A and make a modern right-stick layout
the default. Do not open RPCS3. Original game files remain immutable; separate
experimental local outputs are authorized. No blanket gameplay claim follows from
an IFF parser, successful build or executable decompilation.

## What is implemented in the editor

- Archive discovery resolves 21 additional animation/graph bank filenames. Each
  matches a literal filename in a supplied executable and an actual archive CRC;
  these banks appear in Explorer's Animation banks category.
- Animation inventory validates record counts against actual header bounds. The
  previous arbitrary 10,000-record check silently skipped NBA 2K14's main bank.
  Inventory now includes 22,139 SingleMoCap records across standard IFFs, including
  14,679 in nba_animations.iff. Its 4,226 companion 0x39F61D57 records are separate.
- Read-only motion envelope profiles follow confirmed native pointer fixups for
  CH2K8 and NBA 2K11. Reference IDs are distinguished from payload pointers;
  the NBA event-entry list is bounded and checked for its native sentinel.
- The alias inspector reports local source-ID candidates, missing/external IDs,
  ambiguities and cycles without calling them resolved gameplay dependencies.
- Motion selection collection envelopes have distinct observed strides: NBA
  2K11 uses 20 bytes; NBA 2K14 uses 28. Neither profile enables an import writer.
- Seven prior PR branches (#31â€“#37) are consolidated with ancestry retained.
  Legacy saves, override compatibility checks, faces, SDAT v3 reads, scorebug
  contracts, executable research documentation and uniform editing are preserved.
  The renamed roster-open button's GUI regression expectation is updated; added
  synthetic Legacy tests cover layout rejection, truncation and outer-byte
  preservation. A draft Legacy PR is not treated as gameplay-certified save use.

## Native evidence from supplied Ghidra and original disassembly

Focused Ghidra projects use PowerPC big-endian 64-bit/32-bit addresses, OPD-derived
TOC contexts and the supplied PS3 script conventions. Direct disassembly verifies
function starts and import calls; the nearest OPD alone is insufficient because
local functions do not all have OPD entries. Game code/project exports remain
private and are not bundled with the editor.

| Revision | Confirmed native route | Consequence |
| --- | --- | --- |
| CH2K8 | Motion relocation at 0x1E9C0 touches +0x30/+0x34/+0x38/+0x3C and a pointer tail at +0x40 sized by +0x10 & 0x3F | The older envelope cannot be populated using NBA offsets. |
| CH2K8 | Resource reference resolver/handler at 0x241E0/0x24478 uses +0x30 as source identity for an unresolved +0x38 | Mirror/reference rows are not standalone packed pose streams. |
| NBA 2K11 | Relocation at 0x15F24 touches +4/+0x24/+0x28/+0x2C/+0x30/+0x34, tail +0x38, plus 12-byte entries through an INT_MIN sentinel | Added pointer/event dependencies must be converted, not copied. Event meanings are unresolved. |
| NBA 2K11 | Reference handler at 0x1C604 uses source identity +0x28 and resolution field +0x30 | Old CH alias offsets would read the wrong source key. |
| NBA 2K14 | Native 0x74A41C dispatch distinguishes 0x60900D71 from 0x449E4AC7 and iterates the latter with a 28-byte stride | Shared type hashes do not establish identical collection layouts. |
| CH2K8 | Imported cellPadGetData (NID 0x8B72CDA1) reaches poller 0x7B2358 via call 0x7B26F0 | Raw analog decoding is established; gameplay action mapping remains downstream. |
| NBA 2K11 | Same authenticated import reaches poller 0x861454 via call 0x8617C0 | This is an input-device boundary, not a portable dribble implementation. |
| NBA 2K14 | Same import reaches poller 0xB5DAF0 via call 0xB5DC00 | Copying this poller would not supply the Pro Stick gameplay system. |

The native relative-pointer helper adds signed field value minus one to the
field address, leaving zero null. In unresolved motion records the source-ID field
must be handled before treating that location as a pointer. Actual CH crowd
samples yielded 125 packed records and 125 aliases with local candidates; NBA
2K11 siganims_generic yielded 333 packed and 333 aliases. Both produced zero
envelope errors/cycles. This does not establish compatible skeletons or poses.

Native dribble graphs are separate 0x0D53D4B3 resources. The supplied 2K11 dribbler
graph decodes to 770,144 bytes; 2K14 to 2,611,944 bytes, with different contents and
header organization. The exact-name CRC of `animgraph` matches this type hash,
and each executable contains ANIMGRAPHRESOURCEHANDLER metadata. Graph opcode,
transition/blending and contact semantics are not decoded. NBA 2K14's motion.iff
also has three unresolved 0x9D34E89E resources; these are not relabeled skeletons.

Control-menu reflection was traced at CH 0x6BC12C. Its localized entries include
Controller Setup, and a native menu descriptor names ControllerConfigMenu. This
is menu registration rather than the downstream dribble/shooting action map.
Stock tutorial text explicitly warns that some drills depend on Default controls;
changing a preset requires checking those consumers as well. A global left/right
axis swap is not an implementation of the requested controls.

## Executable-held motion data â€” read-only follow-up

Archive counts above are not a total gameplay-library count. The supplied CH2K8
and NBA 2K11 decoded executables contain large pools with the observed full-body
mask 0x001DF7DD and motion-envelope pointer layouts. A new
`inspect-embedded-motion` command locates this family in writable PT_LOAD ranges,
checks header/tail bounds and maps absolute dependency addresses. Unlike the IFF
profile, these native rows already contain absolute pointers. Zero-filled runtime
memory is reported explicitly instead of being exported as file data.

Read-only supplied-copy results: CH2K8 **7,055 candidates**, NBA 2K11 **18,831
candidates**, no rejected mask hits and no unbacked dependency starts in either.
These are structurally validated candidates, not 7,055/18,831 independently
identified playable clips. Header fields, aliases outside this family, stream
lengths, runtime registration, duplicate uses and complete coverage remain
unresolved. The generic header inspector retains its raw +0x20 label. The newer full-body
timeline check below establishes duration for that bounded NBA11 profile.
No observed equivalent-family match establishes an NBA 2K14 embedded profile.

Focused CH Ghidra/disassembly establishes a related selection route:

- Function 0x234B98 indexes an eight-byte pointer/flag table. Negative indices
  select zero; indices above 0x457 select fallback 0x458. A zero flag returns the
  pointer; a nonzero flag selects a pointer at group +16 times the object's +0x20
  selection value, then +4. This does not prove what each category/variant means.
- Function 0x234B20 recognizes index -2 as an object's explicit pointer at +0x8C
  and otherwise returns the flagged group pointer. Local motion-header pointers
  are present in the native table and other group structures.
- Function 0x234A18 joins a separate hashed lookup table with 12-byte metadata
  rows. Its presence is not evidence that every embedded clip has a known name.

The inspector writes metadata only, including explicit `complete_library=false`,
`pose_decoded=false` and `import_supported=false`. It neither decrypts SELF files
nor exports an entire executable data segment as an alleged portable library.
Original EBOOT remains untouched. The low-level normalized input getter has also
been traced at CH 0x7B1F14 through bridge 0x121B0; downstream action semantics and
preset save/default paths remain unestablished.

## Packed pose translation â€” 2K11 to CH2K8

A bounded packed-channel converter is implemented in `formats/motion_frames.py`.
This is the first actual stream translation, not a complete animation-bank port.
It handles the observed four-channel XYZ SoA layout: each group occupies 24 bytes;
rotation/translation counts are six-bit fields at +0x10, and each frame occupies
24 times ceil((rotation count + translation count)/4). Packed rotations precede
packed translations; partial groups retain their padding.

Native CH routines 0x204FC/0x20AF0 and NBA11 0x16464/0x16DAC establish the shared
smallest-three quaternion representation. Each component is signed 15-bit scaled
by 23/(32*16384); the omitted positive component is reconstructed from the unit
sphere. The first two words' high bits select its component permutation. CH uses
selector times four in LVSL/VPERM, while NBA11 uses 12 minus selector times four.
Changing conventions therefore toggles only those two selector bits. Packed
components, signed translations (1/128), frame order and unused bytes remain exact.
Native quaternion order is WXYZ: both frame decoders initialize absent rotations
to (1,0,0,0). Native mirror signs and skeleton/bone routing are separate from
these channels.

The scalar offline decoder uses mathematical square root, whereas native VMX uses
an estimate/refinement. It is not advertised as bit-exact floating-point emulation.
The stream transcoder preserves encoded values and does not re-quantize them.
Unknown layouts/profiles, mismatched extents, invalid quaternion values and counts
outside the native fields are rejected. Source-overwrite guards apply to the CLI.

Read-only/private-copy checks across 32 observed streams per game: CH1,106 frames /
18,802 quaternion channels /159,264 bytes; NBA11 644 frames /10,948 quaternion
channels /92,736 bytes. All decoded pose-channel values agree across conversion;
reverse conversion reproduces every original byte. These are channel-level checks,
not native runtime, retargeting, contacts, jump-shot timing or bank registration.
First converted stream samples remain private; no game assets are committed.

The supplied PS3 Ghidra scripts explicitly warn that Cell LVLX/LVRX are unsupported.
Local backed-up language additions now decode those loads using aligned 16-byte
reads and byte-offset shifts; this removes the former sampler decompilation
truncation. Semantics were checked against the public
[RPCS3 instruction reference](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/Cell/PPUInterpreter.cpp).
No emulator was launched. Raw disassembly remains the check on decompiler output:
for example, Ghidra's existing LVSL pseudocode can incorrectly suggest r0 supplies
an address when its RA field means zero.

## Adaptive timing and root translation

NBA11 native sampler 0x1B764 reads a byte timing table through header +0x24.
Its low15-bit keyframe count is in +0x14; each interval is the corresponding byte
plus one. The final byte is not an interval. The native sampler accumulates those
ticks, finds bracketing keyframes, computes their blend fraction and reads poses
through +0x28. CH native 0x226B4 instead uses fixed-rate frame indexing.

All9,574 distinct inspected NBA11 full-body timelines satisfy cumulative ticks =
recorded duration (+0x20) times rate (high byte +0x10) times time-scale (+0x1C),
within float precision. This establishes duration for this observed profile;
ignoring the time-scale produced misleading mismatches. No alternate +0x14 bit15
packing was found in this inspected family; that native branch is not implemented.

`resample_nba11_frames` expands the irregular ticks into fixed samples at the same
tick rate. Retain the donor rate/time-scale when a future container adapter writes
headers; a stock15-Hz assumption changes playback speed. Existing keyframes retain
their exact packed bytes after selector conversion. Inserted rotations use shortest
arc mathematical SLERP and bounded quantization; positions use linear interpolation.
This is an offline geometric approximation, not bit-exact reproduction of the native
VMX interpolation polynomials. Synthetic quantization checks bound quaternion
angular error below0.0002 radians on the seeded fixture.

Native root sampler 0x17BF4 reads +0x2C using the same timeline. CH 0x2027C uses
fixed ticks through +0x34. Both use signed-halfword XYZ at1/8 scale; +0x14 bit31
selects a six-byte root row, otherwise an eight-byte row includes heading. The
heading word participates in native angle conversion. The root converter linearly
interpolates authored signed words as those samplers do, retaining mirror flags
for the eventual header adapter; it does not invent angle-wrap correction.

Private checks:32 donor pose streams expand644 keys to4,642 fixed frames, retaining
every source key byte. Root checks cover33 streams /4,757 fixed samples, including
10 without heading; all source key samples are exact. Earlier broad packed-channel
audit passes3,727 distinct CH streams /247,373 frames /35,621,712 bytes and9,574 NBA11
streams /341,823 frames /49,278,288 bytes, with exact reverse-byte preservation.
These results cover the identified header/mask family, not every game animation.

The destination executable also contains an explicit21-entry index/name map at
0x933F40 (root, hips/femurs/knees/ankles, thorax, clavicles/shoulders/arms/hands and
head). The old global SKEL sample has21 entries in352 bytes. This does not prove
NBA11 bind transforms, hierarchy or compatible missing translation channels.
The CH 8-byte event records carry an integer and float; NBA11 records add an optional
payload pointer in a12-byte row. A private endpoint-fingerprint comparison finds99
unambiguous candidate pairs;43 also align in event count and normalized times.
These suggest26 event-ID mappings, but one donor ID maps to multiple CH IDs and
uses distinct payload words. Endpoint agreement is not full-motion equivalence;
none of these candidates is installed as an event conversion table. Observed event IDs differ, so dropping the third
word or applying a uniform ID offset is not a supported event conversion.

## Adding jump-shot choices â€” native requirements

The next offline phase now provides [event/payload dependency inspection and a
guarded table bridge](ANIMATION_EVENT_BRIDGE.md). It preserves marker order and
exact time bits, requires explicit caller-reviewed mapping evidence and blocks
unknown payload schemas. It does not install the candidate correspondences above
as a semantic dictionary. Native audit:3,727 CH tables/17,897 rows and9,574 NBA11
tables/49,639 rows; zero extent errors. NBA11's +0x34 counted membership pairs are
also bounded, with their second words left opaque. This closes the offline table
format/writer phase, not the remaining runtime/event-semantic dependencies.

Owner requirement is additive: retain every original shot and append donor styles.
CH getter/setter 0x69E938/0x69E94C read/write one byte at logical player +0x73
(editor row +0x83); the editor's current accepted range remains 0..111. Native
initialization at 0x69D410 loads 0x6F as the existing option maximum. A byte has
additional representational capacity, but this alone does not register a new shot.

Native table 0x9DD5F0 contains 112 records with a 40-byte stride. Runtime readers
at 0x3213D4/0x321454/0x321538/0x3247DC/0x326404/0x32BE20 use its shared TOC pointer.
The last two words of each record are motion pointers; other fields are also read
into playback state. Their complete timing/handedness meanings remain unresolved.
Index112 currently reaches a different adjacent structure, so permitting that ID
without extending the native table would be unsafe.

All112 named shot styles were privately mapped to224 distinct motion headers.
Their6,890 referenced frames pass packed-channel conversion/reverse-byte checks;
this catalogs the existing baseline, not added styles or certified gameplay.

Additive support must preserve the first112 records/IDs, append fully compatible
motions and playback metadata, extend labels/option registration, establish safe
runtime allocation and update every consumer. No stock record is replaced, no
unsupported choice is exposed and no speculative executable/table patch is enabled.

## Explicit remaining implementation

**No donor animation is yet playable in CH2K8. No new default/control preset is
installed. No smoother gameplay or entire on-court system port is claimed.**

Remaining dependencies include unhandled packed/auxiliary track and time formats,
donor per-bone names/order/bind poses and retargeting, root integration, ball/hand/foot contacts,
paired interaction events, animation ID/variant selection, blend/transition graph
execution, shooting/defense/AI consumers and memory limits. Players/teams BIN
payloads remain opaque and must not be confused with an already decoded clip bank.

For controls, trace the gameplay-specific dribble and shooting consumers after
analog normalization, map preset save/load and reset/default paths, implement a
context-aware modern layout, retain original behavior in preset A and account for
training/post/defensive/menu consumers. No speculative executable patch is enabled.

## Reproduce supported investigation

```
python -m choops_py.research.animation_compat CH_JB NBA11_JB NBA14_JB --output output/research/animation-current.json
python -m choops_py.cli rip NBA14_JB output/rips/nba14 --file nba_animations.iff --raw-iff
python -m choops_py.cli inspect-animation-links EXTRACTED_BANK.iff college-hoops-2k8 output/research/ch-links.json
python -m choops_py.cli inspect-animation-links EXTRACTED_BANK.iff nba-2k11 output/research/nba11-links.json
```

For an isolated packed-channel stream with confirmed counts (not an entire IFF):

```
python -m choops_py.cli transcode-motion-frames POSE_STREAM.bin nba-2k11 college-hoops-2k8 17 4 38 output/research/converted-pose-stream.bin
```

Counts are rotations, translations and frames. The output is a channel stream,
not an installable IFF or executable; `gameplay_ready` remains false. Original
bone maps, mirrors, auxiliary tracks/events and native registration are required.

For an isolated NBA11 pose stream and its exact keyframe-count timing bytes:

```
python -m choops_py.cli resample-motion-frames POSE.bin TIMING.bin 17 4 output/research/fixed-pose.bin --root-track ROOT.bin --root-output output/research/fixed-root.bin
```

Add `--root-without-heading` only for the observed six-byte root mode. Both root
options are required together; all inputs and distinct output paths are validated
before writing. No headers, bone bindings, auxiliary tracks, events or runtime
registries are written. The result still reports `gameplay_ready=false`.

For an already decoded private ELF analysis copy:

```
python -m choops_py.cli inspect-embedded-motion ANALYSIS.ELF college-hoops-2k8 output/research/ch-embedded.json
python -m choops_py.cli inspect-embedded-motion ANALYSIS.ELF nba-2k11 output/research/nba11-embedded.json
```

The embedded command accepts bounded ELF64 big-endian PowerPC executables with
32-bit load addresses. Reports contain executable addresses and source identity;
keep actual-game reports private. Its supported mask family is not universal.

Use the matching profile. The links command rejects NBA 2K14 because its packed
motion envelope is not established. It reports local candidates rather than
silently resolving cross-bank references. Source assets, reports and executable
analysis copies are local, excluded from Git. No RPCS3 or testing JB is used.

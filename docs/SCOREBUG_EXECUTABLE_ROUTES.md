# Expanded read-only executable search for scorebug alternatives

The owner requested searching beyond the previously checked HUD and generic
overlay paths. This pass finds a concrete additional Director-to-scorebug-message
route and ungated current-team name getters. It does not establish a completed
persistent scorebug, and does not authorize executable changes.

## Search scope and limits

The existing vanilla Ghidra project uses PowerPC:BE:64:A2ALT-32addr/default with
the documented two-TOC setup. A fresh inventory exports 39,100 identified functions
as 40,288 nonoverlapping body ranges. A local whole-image index scans all supplied
ELF segments, rather than only the HUD address interval. It records:

| Indexed evidence | Count |
| --- | --- |
| Aligned direct-branch patterns into the native code interval | 169,501 |
| Those patterns without a containing recovered Ghidra function | 21,424 |
| Aligned words whose values fall in mapped memory | 1,426,789 |
| Checked lwz loads through r2 in functions with an established OPD TOC | 59,983 |
| Keyword-matching ASCII / UTF-16-BE strings | 664 |
| Unique caller/target edges after exact TOC-veneer normalization | 108,737 |

These are search indexes, not claims that every entry is an active call or
pointer. The raw branch scan can encounter embedded data; mapped numeric words
can be false references. Function recovery, indirect dispatch and computed
addresses remain incomplete. The TOC query covers the checked instruction form,
not every load/address-construction pattern. Strings are filtered search leads,
not a complete symbol list. This pass did not decompile all 39,100 functions.

The graph/query reports, executable-derived tables and decompilation stay local.
Selected leads below were then checked with fresh Ghidra exports and instructions.
The original executable and analysis ELF remain unchanged.

## Strongest new route: the scorebug message system

Native 0x50D350 obtains the current home team through 0x57F050, reads its first
text pointer (+0), wraps it through 0x1E1610 and assigns the result. Native
0x50D3D0 does the corresponding operation for the away team through 0x57F064.
Neither passes through the main HUD's 0x4EEB3C name-suppression gate. A third
getter, 0x50D450, selects the opponent relative to a message's supplied team.

The first two descriptors are 0xA31F38 / 0xA31F40. They occupy indices 2/3 in
the argument-provider table at 0x125A3E50. This is a separate table from both the
main fixed text registry and the generic Director overlay definitions.

The message-definition table beginning at 0x125A37D4 has observed 20-byte rows:
channel, another native field, and three formatting descriptors. The inspected
span before the next table contains 83 rows; that is not an independently
recovered declaration of every valid native message ID.

Observed message 37 selects channel 3 and these formatting functions:

| Column | Formatter | Observed inputs |
| --- | --- | --- |
| 0 | 0x5154F0 | Native category/caption argument |
| 1 | 0x5155E4 | Current home name, then a native statistic value |
| 2 | 0x515744 | Current away name, then a native statistic value |

Both side formatters use English localization ID 0x6BF728B5. Its existing argument
0 is the school-name text and argument 1 is the value. The current internal
candidate deliberately retains only argument 1 for compact comparison values;
that prior formatting decision is not evidence that this controller lacks names.
A separate held component now retains uppercase argument 0 instead.

Native consumers connect this to the actual scorebug:

- 0x4F0CC0 / 0x4F0E1C obtain core popup text through 0x509D88 / 0x509E38.
- 0x4F0F64 / 0x4F101C / 0x4F1104 / 0x4F12C0 obtain comparison columns from the
  selected message channel and native presentation phase.
- 0x509528 selects channel storage at root 0x12C9B720 with stride 0x4D4.

### Data-driven activation command

Director command **0x3D** has category 13 and descriptor 0xA31AB8, entering
0x50A5A8 -> 0x50A18C -> 0x509548. The dispatcher at 0x77E728 reads eight bytes
and passes them in r3..r10. It does not read an overlay-definition index or the
four-byte float operand used by command 0x163.

The wrapper resolves a supplied context selector and converts the duration byte
to a float. The request builder stores a remaining duration, its reset duration,
and a repeat count. The exact conversion and argument shuffle were checked in
instructions; do not copy the generic overlay FLT_MAX bit pattern into this
eight-byte command.

A narrow real-data example is verified independently of the provisional wider
script scan: group 44, record 80940, next record 80964. Its body at +12 decodes
0x3D with bytes [38,23,108,1,0,5,0,0], then a zero-byte stream sentinel and two
zero padding bytes. This corrects the earlier index-decoder interpretation of
two bytes as token 0 and one byte as padding: 0x5A708 checks one byte first.
The native shuffle supplies repeat count 1 and duration 5 seconds. The complete
activation phase of event 44 remains unproven. The example proves the command
boundary/argument form, not permission to repurpose that event or a persistent
name implementation. No Director mutation for this new route is installed.

The verified argument order is message ID, statistic selector, actor selector,
repeat count, statistic period/context, duration seconds, an unresolved native
presentation subtype, and an unresolved flag. Actor selectors at most 100 use
0x56509C; larger selectors use 0x564D28. Do not interchange these selectors with
generic overlay command 0x166's different context namespace.

### Internal startup-request probe

A separate, uninstalled probe copies group 187's verified starting-lineup
transaction, retaining its 12-byte scheduler header, wait/reset, away/home
contexts, original five-second duration, definition 4, submission and termination.
It appends 0x3D with arguments [37,23,102,255,0,255,0,0] before the terminator.
The startup actor now uses instruction-checked selector 102: 0x564D28's table
case reaches 0x564ED0 -> 0x57F050. Selector 101 reaches the away getter; 108 instead
uses event accessor 0x2E7950. The existing group-44 request retains its original
108. The team's context precheck remains native; no selector registration changes.
The old transaction remains intact; only one group record reference redirects
to the appended copy. Leading references, literal indices, token map, other
groups and every unrelated original byte remain exact. The decoded resource
grows by 40 bytes. This is a finite nominal 65,025-second request, not proof of
uninterrupted display, event-phase ownership or surviving every scene transition.

The public writer still rejects generic DRCT growth. A private, narrowly guarded
container experiment accepts only this copied transaction, one redirected pointer
and the known request shape in a sole DRCT block at logical offset zero. It
retains the source's physical archive extent and reparses the exact new resource.
It does not expose an arbitrary script writer or relocate unknown resource types.
Recompression retains verified prefix tokens and appends literals; a formerly
EOF-clipped backreference must be shortened/re-encoded before appending data.
The generic greedy recompressor did not fit this source's physical capacity.
Synthetic refusal/round-trip/EOF regression tests cover the scoped alternative.

The archive and decoded probe remain private research outputs, separate from
the two-IFF candidate. They are neither an installation nor a packaged candidate.

### Lifetime and coexistence still need resolution

The message system has four channels, distinct from the three generic overlay
slots. 0x5099B4 updates a current message's countdown when its active/display
conditions permit, resets duration on expiry, decrements its repeat count and
advances/removes entries. Larger finite duration/repeat requests are a lead to
investigate; an uninterrupted lifetime is not proved by the integer fields.

There is a concrete conflict: 0x509C54 prefers a nonempty channel 3 over channel 2,
then falls back to channel 1.
Messages 5..36 in the inspected table use channel 2, while 37/38 use channel 3.
Injury message IDs 64..76 use channel 1, and run report 77 also uses channel 1.
Keeping a comparison permanently selected can therefore hide both ordinary player
stat messages and injuries. That must be resolved before promotion. Generic overlay wait
counting is a different subsystem, but its absence here does not prove that no
other wait, reset or scene transition affects message display.

Channel 0 is separate: the checked core popup providers explicitly request that
channel, rather than using 0x509C54. It includes the native points/general-stat
messages and foul/violation messages 39..63. The channel-2 conflict concerns the
additional leader/stat-line/foul-situation panels in 5..36; it does not mean that
every points, foul or rebound popup is blocked. The generic injury announcement
63 also uses channel 0; the detailed injury/return-status messages use channel 1.

The next investigation is the message channel's activation, reset, arbitration
and script-trigger ownership, plus preserving the requested statistic popups.
The eight-byte command and six-bone component provide a narrower concrete lead
than repeatedly extending the generic overlay timer.

### Injury coexistence: another data-driven route to investigate

Ten complete group-127 injury transactions have now been independently decoded
through their termination and zero padding using instruction-verified operand
widths. Each retains the native prefix commands 18B/18C/181, four 17C commands
and 18F; then requests 3D with actor 10, one repeat and six seconds. There are
also **1F and 29 commands after the injury request**. A replacement that assumes
the request is the transaction's last action would discard native behavior.
IDs 72/75/76 were not located by this bounded check; that is not proof that the
other injuries lack triggers. The broader provisional scanner is still incomplete.

A possible separate finite overlay can retain the injured player and expose a
subtitle without occupying comparison channel 3:

| Required part | Instruction-checked route |
| --- | --- |
| Current injury actor | 3D actor 10 -> 0x565388 -> 0x49EEE4 -> 0x2E6248 |
| Same actor for generic overlays | 166 selector **3** -> 0x713030 -> the same accessor |
| Shared event context | 0x3F8020 reads running program +0x1C; 0x5B238 returns program +0x10 and 0x712EF4 reads its +0x0C |
| Generic subtitle provider | Registry row 0x953F54 -> descriptor 0xA41768 -> 0x71073C, active instance +0x54 |
| Subtitle setter | Command **15F**, 0x199F64, pending field 0x12948E38 = request +0x54 |
| Literal operand | Category 0 -> 0x5AA08 -> two-byte literal index via 0x5A7E8 |

Command 15E writes a different field; copying actor 10 into command 166 would
also select a different player accessor. These distinctions are important when
preserving context. Existing generic scenes have player-name/subtitle bindings.
The compact scene and request components below remain uninstalled and lack
native verification. Every original injury transaction remains intact; only
selected references in the probe redirect to copied, extended transactions.
Player-stat channel 2 still needs its own coexistence solution.

### Held injury scene and request components

A separate component now reskins vanilla OVERLAYCACHE / violation_a, native
definition 26 in the 0x1267BB04 table (stride 0x7C). Its entry 0x1267C79C uses
the broad text-provider table at +0x38 = 0x953558. The component keeps all four
instances, their original bone counts, all three provider identities and all six
animation rows. It hides the jersey-number field and old textured artwork,
retains the original untextured background's material fade, and authors a slight
dark gradient over X [-301,84], Y [-173,-151]. Separate centered player-name and
subtitle fields use Stratum2 25. This is authored placement, not native projection
or simultaneous-popup collision verification. Other consumers of violation_a
would share this reskin.

The two font aliases now reuse their distinct existing string spans in place;
the header stays exactly 12,244 decoded bytes and the payload 12,248. This avoids
changing the CDF resource's logical size or offsets. A paired container probe
appends only recompressed physical chunks and redirects the selected descriptor.
All original CDF bytes remain an exact prefix; all native resource words/logical
offsets, unrelated descriptors, metadata and animation rows remain exact. Both
parts reparse to the authored component. No generic logical SCNE growth is enabled
by this private adapter.

A request component copies the ten checked injury programs and
adds reset/context/15F subtitle/six-second duration/definition-26/submission after
their existing 3D injury requests. It retains every original command, scheduler
header, original program and following action. Exactly the selected group-127
record pointers redirect to the copies. Ten authored injury/return-status strings
are appended through a new literal table; all 78 original indices and exact
UTF-16 streams are copied, using forward references. Every unrelated original
resource byte remains exact and the pointer index reparses.

The component now also has a complete, uninstalled Director IFF probe. A combined
variant adds the independently checked startup name transaction at the end of
that resource, retaining all old programs, ten literal additions and all unrelated
source bytes. The combined decoded resource is 487,752 bytes; the physical IFF is
202,752 bytes, 6,144 larger than the source extent. Its sole DRCT resource remains
at logical offset zero. Only the three observed outer size fields change; the
NAME trailer remains exact and the result reparses to the verified decoded data.
This does not enable a public arbitrary DRCT writer.

Read-only planning against vanilla accepts all five existing-asset replacements:
the two current candidate IFFs plus the held Director and overlaycache pair.
Four assets relocate and the IFF metadata fits in place; no asset identities or
source entry count are added. This is a plan, **not a built JB** or installed
candidate. No injury activation, CDF override or candidate change is installed. The remaining
unlocated injury types, run report and leader/stat panels still need consideration;
the duplicate native channel-1 report would also remain visible if the name layer
did not activate.

### CDF scene capacity correction in the builder

The vanilla overlaycache pair has 21 SCNE records with varying decoded chunk
sizes. Its block descriptors advertise maxima: 121,494 header bytes and 1,499,440
payload bytes, matching the largest observed chunks. The old builder required
each chunk to equal the maximum, so it rejected this valid scene bank.

Validation now permits smaller H7-wrapped chunks only when **every native resource
type word** is SCNE (0xE26C9B5D) and has two offsets. Each decoded chunk must be
nonempty and within its declared block maximum, checked before decompression.
Editable NAME labels cannot
activate this profile. Other resource profiles and uncompressed chunks retain
their existing exact-size checks; compressed-stream bounds remain strict. The
texture-slot writer is unchanged. Synthetic cases cover capacity failures, false
NAME labels, corruption, existing texture imports and a growing paired-asset
roundtrip with original source/data preservation.

### Team ordering and native text-placement checks

Fresh exports/instructions confirm that message 38 uses the same fixed current-
home/current-away school getters as message 37: provider-table +8/+0x0C, with
value providers +0x28/+0x2C. Its normal timeout request therefore does not change
the name sources to an actor-relative ordering. No timeout event is rewritten.

The topbar draw path 0x4F5220..0x4F5270 copies the resolved SCNE text pose, adds
the cached slot's X offset and adds 250 to Z. The slot constructor at 0x4EF400
initially clears those offsets. The 0x4F24F0 column adjuster is conditional on
finding the named divider instances; channel number alone is not enough to
assume its computed shifts apply. Do not bake speculative column compensation
into authored markers. Final projection and applicable runtime scene gates remain
unverified; the component still records authored placement before native handling.

### Refined read-only command leads

The earlier provisional scanner missed operand readers after shared dispatcher
joins. Instruction checks now follow the joined paths, including category 15's
u16 plus byte, category 16's literal index plus signed u16, category 55's two u16s
plus signed u16, and category 41's flag-controlled signed-u16 operands. Native
0x5A708 checks a one-byte zero sentinel before command-index decoding. A bounded
public is_stream_end helper now exposes that separate preflight; it does not
discover boundaries or interpret operands.

The refined private scan has 6,419 zero-tail terminations and 98 terminations
with nonzero trailing data across the 6,517 referenced records; no former
truncation/index error remains. It finds 99 3D leads, with no message IDs 5..36
in those leads. These are still caller-derived +12 starts and inferred record
ends. Nonzero tails, indirect/runtime sources and unclassified metadata prevent
claiming a complete script disassembly or proving channel 2 unused. Selected
transactions must continue to be checked independently before mutation.

## Possession arrow added to the required layout

The owner added a possession arrow to the objective. Reserve a small indicator
in each team's lower row, immediately before its score cell, clear of the sixth-
man strips: planned away X [-166,-156], home X [40,50], Y [-204,-198]. Its active
side needs a genuine alternating-possession source; current ball control alone
would not prove the college possession-arrow state.

The checked bottom-bar pCone1 is a 540-expanded-vertex, two-material ring/glare
mesh with initially transparent diffuse alpha, not evidence of a driven arrow.
The native arrow asset request at 0x2BFB58 belongs to the drill-challenge renderer
(source-path evidence and separate resource root), not a regular-scorebug binding.
Some high-half CRC candidates do not construct the complete requested hash and
must not be counted as matches. No static, permanently active or guessed-side
arrow was added. A reliable possession binding/trigger remains required.

### Additional live statistic routes

The school-name comparison also has a genuine native value argument. A checked
straight-line initializer at 0x50AAD0..0x50B1E4 supplies 24 caption entries;
constant propagation of its actual loads/stores agrees with selected Ghidra
exports and the vanilla localization. The 12-byte statistic mapping is at
0x125A3668. Useful entries include:

| Comparison selector | Native statistic code for game contexts | Interpretation supported by the route |
| --- | --- | --- |
| 11 | 15 | Foul statistic; team accessor descriptor 0xA13788 -> 0x1624D8 |
| 23 | 72 | Timeouts; descriptor 0xA1B850 -> 0x229468 reads the selected side's live timeout object |

0x50D25C / 0x50D208 force the current home/away team before 0x50CE38 formats
the value. Period/context 0 passes period 0 to the native stat accessor;
context 5 obtains the current native period selector from 0x12C18CA0 +0x14.
This is a useful lead for current-period foul totals, not yet proof that every
half/overtime reset matches the desired bonus rules. The timeout getter itself
does not consume a period argument. Selector 13 is turnovers, **not timeouts**.

The original side template can carry both school name and this one value. The
held name-only component deliberately omits that value. A single comparison
request does not supply simultaneous independent foul, timeout, rank and bonus
fields; no completed combined permanent row is claimed. Priority, projection,
text sizing and native display still require resolution.

## Held comparison-name component

An internal component starts from vanilla scorebug_topbar and English. It retains
the six-bone g_top_bar owner; the source's zero animation-row count stays zero.
It uses the existing home
marker and two away presentation bindings, hides the caption, and degenerates
only declared artwork strip indices while preserving restart markers and vertex
attributes. All four text bindings resolve their original native marker hashes.

Names use Stratum2 40 at owner scale 0.25, centered at X -217 / -11 with pen
Y -172.875 before native adjustments, white text, dark shadows and a 126-unit
width limit. This is authored placement, not measured native projection.

The held English part uses uppercase argument 0 from the original side template,
preserving IDs, pool extents and unrelated bytes. It omits the statistic only in
this isolated name component. It is not installed into the candidate and is not
an acceptable replacement for the requested full stat-popup behavior. No package
or runtime-visibility claim is made.

## Other whole-image leads

| Route | Checked evidence | Remaining limit |
| --- | --- | --- |
| Separate player-card renderer | 0x1A59C -> 0x217B10 -> 0x217540; reads current team +0 school text and +0x0C nickname, draws through 0x214FD0 -> 0x9D048 | Root 0x12A863B0 selects one team from a supplied player's side; state 2, time handling and source object govern display |
| Its lifecycle | 0x214C6C selects state/source/scene; 0x214DB8 clears state, scene and source; 0x21442C advances scene/time | Not an independently proved permanent two-team layer; parking it may interfere with its presentation owner |
| Alternate contextual formatter | 0x719E98 uses current-team getters and can call 0x76520C or read team +4 depending on native state | Descriptor 0xA41CA0 is in the alternate registry at 0x1267CB1C; not an activation bridge to the regular HUD |
| Additional school-name descriptor reference | 0x76520C descriptor 0xA446A0 occurs at 0x9E8C90 and is referenced by native node/table data | Following parent data reaches CoachMenu_MenuFlowAcceptCoachContractMenu; no IFF-controlled HUD invocation established |
| Other direct school-name caller | 0xA3468 calls 0x76520C through a TOC veneer | Associated native menu data identifies MemoryCardMenu_Delete; not a persistent game HUD |
| Arena graphics | 0x5611AC selects jumbotron_team_%03d.iff / generic variants and passes them to 0x560E28 | Shows asset selection, not roster-font rendering or a usable scorebug texture binding; no arena assets modified |

## Verification and delivery state

The private component reparses, marker/pose bounds and animation-count checks pass;
unrelated localization/vertex bytes remain preserved. The existing private
scene-contract/comparison-template suite passes **21 tests**. The scoped private
Director container suite passes **16 tests**. The private paired-scene container
suite adds **7 tests**; combined private run: **44 passed**. The
read-only injury audit checks ten full transactions, and the caption initializer
inventory checks all 24 caption entries. Fresh Ghidra exports cover actor,
subtitle and statistic routes. Added 100/38 instruction-verified actor-switch
edges to the analysis database only; the decompiler still does not recover these
switches, so the selected cases are supported by instructions, not its completion
flag. Public Director/audit plus CDF/import suites: **41 passed**, including ten
new CDF cases and the earlier eight sentinel regression/bounds cases. F lint
passes for the changed builder; F/I lint passes for the new tests. The prior
178-test result is historical, not a fresh test of this update. The held paired
injury scene and combined Director IFF reparse with provider/animation/bone/source-
preservation checks. The five-asset archive plan succeeds without building a JB. These
helpers are not gameplay tests.

Analysis ELF and current two-IFF candidate hashes remain exact. No EBOOT, uniform,
roster color, protected build, emulator or full JB changes. Names, permanent
counters/ranks and final native appearance remain unfinished. The full objective
and no-packaging-before-names constraint remain in force.

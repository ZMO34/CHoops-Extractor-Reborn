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
0x3D with bytes [38,23,108,1,0,5,0,0], then token 0 and one zero padding byte.
The native shuffle supplies repeat count 1 and duration 5 seconds. The complete
activation phase of event 44 remains unproven. The example proves the command
boundary/argument form, not permission to repurpose that event or a persistent
name implementation. No Director mutation for this new route is installed.

### Lifetime and coexistence still need resolution

The message system has four channels, distinct from the three generic overlay
slots. 0x5099B4 updates a current message's countdown when its active/display
conditions permit, resets duration on expiry, decrements its repeat count and
advances/removes entries. Larger finite duration/repeat requests are a lead to
investigate; an uninterrupted lifetime is not proved by the integer fields.

There is a concrete conflict: 0x509C54 prefers a nonempty channel 3 over channel 2.
Messages 5..36 in the inspected table use channel 2, while 37/38 use channel 3.
Keeping a comparison permanently selected can therefore hide ordinary player
stat messages. That must be resolved before promotion. Generic overlay wait
counting is a different subsystem, but its absence here does not prove that no
other wait, reset or scene transition affects message display.

The next investigation is the message channel's activation, reset, arbitration
and script-trigger ownership, plus preserving the requested statistic popups.
The eight-byte command and six-bone component provide a narrower concrete lead
than repeatedly extending the generic overlay timer.

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
scene-contract/comparison-template suite passes **21 tests**. Public source is
unchanged from the prior 178-test result. Native helpers are not gameplay tests.

Analysis ELF and current two-IFF candidate hashes remain exact. No EBOOT, uniform,
roster color, protected build, emulator or full JB changes. Names, permanent
counters/ranks and final native appearance remain unfinished. The full objective
and no-packaging-before-names constraint remain in force.

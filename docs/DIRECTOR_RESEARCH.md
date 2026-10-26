# Director command resource: read-only research

The scorebug owner prefers school names, accepting nicknames only as a fallback.
The current investigation includes data-driven logic beyond SCNE styling, while
keeping the executable immutable. Nothing in this document certifies a working
persistent name layer or authorizes writing an unknown script format.

The expanded executable search identifies a separate Director 0x3D route into
the native scorebug message system, outside the generic overlay definitions
below. See SCOREBUG_EXECUTABLE_ROUTES.md for its verified operand form, ungated
home/away getters and unresolved message-channel priority conflict.

## Native evidence and resource structure

Vanilla Director.iff contains one DRCT record named director. Its decoded part
begins with 0x1FF1DF58. Native 0x59778 requests Director.iff; resource handlers
0x5A380 / 0x5A430 call relocation 0x58DC8 and registration 0x590B0.
0x58DC8 relocates these observed fields:

| Field | Observed use |
| --- | --- |
| +6, u16 | Number of reference pointers beginning at +0x20 |
| +0x0C, u32 | Number of UTF-16 literal-string pointers |
| +0x14 | Relative pointer to the literal-string pointer table |
| +0x18 | Relative pointer to a fixed 223-entry group pointer table |
| +0x1C | Relative pointer to a big-endian u16 command map |
| Group +0 | Number of referenced records at group +0x1C |
| Group +8 through +0x18 | Five relocated section pointers; semantics opaque |

The original resource indexes 1,430 leading references, 78 strings, 98 non-null
groups and 6,517 record references. These counts are not interchangeable. Header
bytes +4/+5, other packed fields, group +4 and record bodies remain opaque here.
The reader preserves repeated references instead of inventing unique ownership.

Command reader 0x5AA50 reads a byte using 0x5A79C. If it is below header +0x10,
it appends another byte as a 16-bit index; 0x59700 supplies that threshold check.
0x59724 resolves the index through the u16 command map. This indexes a native
12-byte dispatch table at 0x1270BF80; the encoded byte is not the command number.
The vanilla threshold is 1. Operand boundaries must be established separately.
Searching for matching byte values inside arbitrary operands is not a valid
script disassembly.

Dispatcher 0x77D2C0 branches through 62 argument-shape categories. Instruction
checks establish category 1 calls without operands, category 2 consumes the
numeric reader 0x5A9D4 and category 4 consumes one byte through 0x5A79C before
calling its registered descriptor. Other categories are not fully decoded. Numeric reader 0x5A9D4 calls the
four-byte big-endian reader 0x5A864, stores the returned word and loads it as an
IEEE float (instruction check at 0x5A9E8/0x5A9EC), rather than numerically
converting the integer as one decompiler view suggests. Ghidra initially omitted most switch destinations;
62 instruction-verified computed edges were added to the analysis database only.
Its function-body coverage improved, but the decompiler still reports an
unrecovered switch. Instruction checks, not decompileCompleted, support the claims.

## Concrete overlay commands

| Command | Category | Native function | Observed effect |
| --- | --- | --- | --- |
| 0x15A | 1 | 0x1993C0 | Reset pending overlay request and set pending flags |
| 0x15B | 1 | 0x199510 | Submit pending request through 0x194820 |
| 0x15C | 1 | 0x1997F0 | Invoke overlay cancellation filter 0x192E5C |
| 0x15D | 1 | 0x199850 | Invoke all-slot reset 0x1930A4 |
| 0x163 | 2 | 0x1996F8 | Write pending request duration |
| 0x166 | 4 | 0x199400 | Resolve and append typed player/team context |
| 0x16D | 4 | 0x199710 | Write selected overlay slot |
| 0x16E | 4 | 0x199728 | Write overlay definition index |

The pending structure at 0x12948DE4 has a four-byte preceding wrapper at
0x12948DE0. This distinction matters: command 0x163 writes wrapper +0x10, which
is request +0x0C; command 0x16E writes wrapper +0x50, request +0x4C. 0x194820
copies the request into an active instance. The timer update 0x193448 skips
countdown decrement for its sentinel value and can hold the entrance plateau.
This exposes a genuine data-command route to investigate lifetime, rather than
an asset-only animation extension. An existing correctly bounded script using
these commands, its activation phase and cancellation behavior still need tracing.
The later internal request probe below changes two proven fields in a separate
output. No Director override is installed in the deployable candidate.

There are three native overlay slots. A long-lived name overlay must coexist
with their replacement/cancellation behavior and the game's ordinary popups.
The presence of a duration setter alone does not establish that coexistence.
The regular scorebug still uses its separate fixed-provider registry.

## School-name provider rather than nickname fallback

In the generic overlay registry, team1city / team2city bind to descriptor
0xA41690 -> 0x70E7FC. Observed rows include 0x953264 / 0x95327C and
0x953804 / 0x953858, with selectors 0/1. Except for its explicit state branches,
0x70E7FC calls 0x76520C, using the runtime team's u16 roster identity at +0x15A.
That resolves through 0x75C7D8 -> 0x75C6CC -> 0x1BCAEC -> 0x75BA30.
The last wraps the resolved roster row's first text pointer. The formatter can
add a prefix based on that row's flags; this is not the nickname +0x0C pointer.
One definition-specific branch (index 9) does use the nickname instead, and
0x5CCADC == 1 is another explicit branch. These conditions must remain part of
compatibility analysis. The opening_intro_a table itself does not bind these city
fields, so simply adding them to that scene is insufficient.

This establishes a school-name provider for further data-controller work. It
does not establish that its callback table can be used permanently in gameplay.
The existing opening nickname route is documented in SCOREBUG_PREGAME_NAMES.md.

## Reader API and verification

choops_py.research.director.inspect_director(decoded_part) returns only bounded
references, strings, groups and opaque metadata. decode_command(data, position,
end) decodes one command at a caller-proven boundary; it does not discover the
boundary, parse arbitrary operands, execute code or modify data. No GUI writer or
CLI script-patching action is exposed.

Synthetic tests cover repeated-reference preservation, short/extended indices,
truncated operands, invalid stream bounds, missing/out-of-range pointers,
malformed counts and alignment. The real vanilla resource parses read-only.
The focused scorebug plus Director suite has 168 passing cases, including 16 new
Director cases. Native appearance and persistent names remain unverified; no
emulator, full JB or candidate package is created.


## Existing request sequence and further limits

A concrete record in group 187 contains this decoded overlay sequence: a wait
operation (0x158), pending-request reset, context 0x88, context 0x87, duration
5.0, definition 4, submission, then stream termination. Definition 4 is the
native starting_lineup resource. Context selector 0x87 branches through
0x2E78F0 -> 0x57F050 (home); 0x88 branches through 0x2E7920 -> 0x57F064 (away).
Thus this request supplies away context first, home second. The native event
callback 0x2C9508 requests event 187 through 0x3F7424. The complete phase ownership
and later cleanup of this particular event are not yet established.

Command 0x158 has an initial callback returning 1 (0x199740), and a follow-up
callback (0x199754) checking overlay activity. Program runner 0x5AAD0 distinguishes
first execution and resumed execution through 0x5A764. This supports a wait/yield
interpretation of the sequence, rather than treating every command as a one-time
immediate call. No wait or scheduling operation was removed.

Native definition 25 selects GAMEDATA / player_name, uses the broad table at
0x953558 containing school/city bindings, and has a very large default duration.
Its original SCNE has team-city, nickname and player-name fields. That makes it
a resource to investigate for a compact school-name layer; it is not yet a
persistent gameplay consumer with both contexts. Definition 4's table at
0x95324C also has the school/city providers. Definition 3 (opening_intro_a) has
its separate three-row nickname/arena table. These tables cannot be freely
interchanged by renaming SCNE fields.

An experimental local scan inferred operand widths from native case blocks to
locate further request candidates. It encounters invalid command-map indices and
incomplete streams; apparent termination alone does not validate a disassembly.
It remains local, read-only and provisional, and is not the public reader's
contract or an accepted script writer. The verified primitive decoder and narrow
request evidence must not be confused with fully recovered script grammar.
Safe authoring still requires proven body boundaries, activation ownership,
ordinary-popup coexistence and cancellation behavior. No name-layer asset or
Director command modification is installed in this pass.


## Compact school-name component, held for activation research

The original player_name SCNE has three text records and a four-bone text owner
b_EndQuarter. Its record text_team1city already uses provider team1city; record
text_team1name uses team1name. The private component retains those record and bone
names, changing only the latter provider to team2city. The original playername
field is alpha zero. Both school fields use white text, dark shadows, centered
alignment and a native width limit. The text-owner scale is 0.25; Stratum2 40
produces an intended cap height of 13.25 authored world units and a 126-unit
maximum width. Pen centers target X -217 / -11, Y -172.875 before animation and
native projection. Actual native appearance is not verified.

The component preserves all 20 source animation rows and the four-bone owner;
no skeleton or pose-array growth. Existing animation offsets can still affect
entrance/exit appearance. Original card artwork is hidden by degenerate declared
triangle-strip indices, preserving restart markers and all vertex attributes.
Both text marker hashes resolve to the unchanged source bones. The component is
not installed into the current archive candidate, packaged or provided as a
usable test build. No Director mutation is installed. Persistent activation and
three-slot coexistence remain required before this can satisfy gameplay names.

The shared developer text-style helper now writes the provider property with
bounds/type/alias guards, independently of record/owner/bone identities. Three
new synthetic cases exercise that separation and preservation, malformed/shared
property refusal and invalid-value/no-op behavior. Focused suite including all
text-style cases: 178 passed. This is source/format verification, not game output.

## Lifetime and cancellation cross-check: activation probe rejected for promotion

Instruction checks and a fresh Ghidra export establish the exact countdown
sentinel: constant 0xA52460 has float bits 0x7F7FFFFF, the maximum finite float.
0x1935F4 compares the remaining duration with this value; unequal values are
decremented at 0x193664. A negative duration requests cancellation at 0x193678.
**-1 is a request-initialization default, not the active no-expiry sentinel.**
An earlier private probe used -1 before this cross-check; it was corrected and
was never installed, packaged or presented as a working candidate.

| Operation | Instruction-checked behavior | Consequence for a permanent name layer |
| --- | --- | --- |
| Timed-overlay wait, command 0x158 | Follow-up 0x199754 calls 0x192904; active instances with remaining duration >= approximately 0.05 are counted | FLT_MAX names keep this wait pending until another path cancels them |
| All-overlay wait, command 0x159 | Follow-up 0x1997AC calls 0x192958; every active instance is counted | A different countdown value does not exempt a live name layer |
| Filtered cancellation, 0x192E5C | Checks active state, kind and +0x290; a special kind-2 case also checks +0x26C | Does not protect against explicit slot cancellation or replacement |
| Play-call popup, 0x7180DC | Cancels slot 0 with 0x192C7C, removes side slot 1/2 with 0x192F7C, then submits its own request | Slot 0 is not a permanent reserved name slot; side slots are also reused |
| Slot submission, 0x194820 | A selected occupied slot is cleaned up before copying the new request | Choosing another slot alone does not establish coexistence |

The play-call path selects definitions 13/14 (overlay_nba9/overlay_nba10), not
definitions 5/6 for substitutions. It supplies one team context. Repurposing that
popup would also require proving the second team's context and preserving the
original popup behavior; it does not automatically restore two names.

SCNE animation extension does not establish a second lifetime mechanism.
Cancellation 0x192C7C starts an exit phase using definition timing; 0x196E14 reads
definition +0x54 and 0x196E48 reads +0x54 plus +0x58. The update eventually cleans
up the instance. Those timing fields belong to the registered native definition
table, not the scene's authored animation length. Visibility wrappers 0x1995F0 /
0x199644 call 0x192BE0 / 0x192BF8; they do not change the wait-counting rules.
No safe data-owned exemption or independent gameplay name lifetime is proven.

The private probe starts from vanilla Director and the exactly matched group-187
request. It changes only the four-byte duration operand to FLT_MAX and the
one-byte definition operand from 4 to 25. Decoded length, complete pointer index
and all other decoded bytes are exact; the output archive reparses. This is a
five-byte bounded experiment in a separate local output, not a general DRCT
writer or a valid gameplay solution. It remains outside the archive candidate.
Removing global waits, looping the entire pregame event, using nonfinite timer
values or suppressing normal popup cleanup is not an established solution.

Verification: fresh exports of the wait/countdown/cancellation functions and
pending-request wrappers, cross-checked against instructions with the documented
PowerPC/TOC setup. No executable changes or emulator runs. Required persistent
school names remain unfinished; the probe must not be promoted on structural
checks alone.

## Direct Director-to-HUD command search

A read-only scan of the native dispatch table found 473 consecutive entries
with accepted category/descriptor shapes before the first rejected row. This is
an inspected prefix, not an independently recovered table-length declaration.
An OPD-based, instruction-aligned direct-branch scan searched paths of at most
three functions into the nearby HUD address range 0x4EE000..0x4F9000. That address
range contains several controllers; an address hit is not a scorebug text setter.

Fresh Ghidra exports and instruction checks distinguish the immediate hits:

| Command | Native target | Observed writes/use |
| --- | --- | --- |
| 0x39 | 0x4F60A4 | Inserts a numeric item into an eight-entry list at 0x12C7F420, skipping duplicates |
| 0x41 | 0x4EE47C | Resolves a native team and sets a side-state flag; no string assignment |
| 0x42 | 0x4EE4F4 | Decrements the nonzero scorebug suppression counter at root +0x0C |
| 0x43 | 0x4EE520 | Increments that counter, then invokes 0x706BAC |
| 0x57 | 0x4F65A8 | Populates separate queue state rooted at 0x12C7F3F0 using a resolved object, timer, numeric fields and geometry calculations |

0x4EE1C0 checks the suppression counter at 0x4EE218/0x4EE220. The 0x42/0x43
pair therefore changes scorebug visibility, not the normal-mode school-name
provider gate. The separate queue root is also distinct from the fixed main
text registry at 0x12C7E2A0. Short paths from commands 0x154/0x156 reach that
separate queue's getters through 0x732B20 / 0x4A77A0 / 0x4A7674; those hits do not
establish writes to main city/name strings.

None of these checked hits supplies a Director command that assigns a roster
name to the existing fixed scorebug fields. This is a bounded negative finding:
indirect dispatch, deeper paths and unclassified data remain outside its scope.
No commands, counters or visibility flags were modified. A direct HUD setter
cannot be assumed merely because a dispatch target is near the HUD code.

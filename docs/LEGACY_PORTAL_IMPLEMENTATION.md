# Native transfer portal: implementation contract and remaining proof

This is revision-specific read-only research on the supplied CH2K8 PS3 executable.
It is an implementation investigation, not an installed portal or a compatibility
certificate. Original inputs remain unchanged. The owner requires ordinary in-game
recruiting, CPU/user transfers, tunable activity, TR class/redshirt labels, one
persistent randomly chosen motivation per player, and retained statistics/team
history. An external save-editing transfer workflow does not satisfy that goal.

## Readiness decision

**A concrete native design is plausible, with identified intervention points.
The complete feature is not yet ready to implement safely.** Callback sequencing,
frequency arithmetic and storage contracts are now substantially stronger than
the earlier feasibility assessment. However, proxy initialization, node capacity,
reservation rollback, the native poll adapter and native load/resume proof
remain open. These are correctness gates, not optional presentation polish.

Static tracing cannot certify a modified executable's runtime behavior. A stock
roster with uninitialized recruits is not an offseason state. No emulator run,
modified EBOOT or testing JB is part of this research pass. Do not mark a gate
verified merely because an offline model or a proposed hook has been written.

## Calendar sequences recovered from native callback data

The relevant operations are indirectly dispatched, explaining the absence of
ordinary direct callers in earlier scans. Dispatcher `0x0C249C`, reached through
`0x49C844`, traverses twelve-byte entries containing a menu reference, callback
function descriptor and optional predicate. It can pause for a menu or callback;
a list of function addresses alone is not a save/resume state machine.

The postseason sequence at `0x12652FE4` has 53 entries. Relevant ordinals:

| Ordinal | Callback | Confirmed role |
| --- | --- | --- |
| 1 | 0x5B4E50 | Reset and generate outgoing transfer candidates |
| 2 | 0x5B3674 | Season processing, including stored statistics-school attribution |
| 34 | 0x5BCCF4 | Automatic destination selection |
| 49 | 0x5BC990 | Reconcile source/destination recruiting counters, conditionally |

The later sequence at `0x12652F0C`, installed by `0x5B3438`, has 17 entries:

| Ordinal | Callback | Confirmed role |
| --- | --- | --- |
| 0 | 0x5B4BC0 | College class/status progression and departing-player removal |
| 1 | 0x5BC250 | Existing transfer membership finalizer |
| 2 | 0x5B61D8 | Ordinary recruit conversion and roster filling |
| 4 | 0x5B3238 | Calls new-season initialization 0x5A5190 |

New-season initialization calls history shifting `0x75ED04`, then annual recruit
regeneration `0x75B0D0`. Ordinary conversion increments recruit class before
allocating/clearing a college player. Portal proxies must be intercepted before
that increment, not just before the final membership-add call.

The optional predicates and intervening menus remain important. The sequence
ordinals establish relative ordering, not that all entries execute continuously
or that a saved game resumes at an arbitrary callback address. The native context
and enclosing save paths have been located; their complete resume contract is
not certified without a phase-specific state and native validation.

## Transfer activity and tunability

`0x5B4E50` reads three bits at player logical +0x88, shift 3. `0x5A7230` increments
that state when a confidence/evaluation condition holds, subject to other filters.
The three-bit write wraps; it is not a proven eight-level menu enum or a saturating
counter. `0x5B4BC0` clears it during annual progression.

The second selection value is now identified: player logical +0x70 is **Confidence**,
confirmed by the existing named getter `0x69E910`. `0x744C40` scales that raw byte
by native float32 0.01. This is not minutes played or a second overall rating.
The separate evaluation comes from `0x74AA30` and is position-dependent.

Stock selection requires all native filters, nonzero state, a random draw below
`clamp((state-1)/3,0,1)`, and scaled confidence strictly below float32
`evaluation * 0.66`. State 1 has zero stock chance; multiplying it cannot admit
more players. A deliberate nonzero-state floor broadens that population without
removing the native state-zero exclusion or graduation/unavailability checks.

`research/transfer_tuning.py` specifies, offline:

- Intensity multiplier 0..10, applied to the stock conditional chance.
- Independent nonzero-state probability floor 0..1, applied after multiplication.
- Confidence/evaluation threshold ratio 0..2; stock default is float32 0.66.
- Annual entry cap 0..400; zero disables entries. This is a limit, not a quota.

Defaults reproduce the confirmed arithmetic using single precision. The caller
must supply the actual native evaluation and remaining eligibility result.
These are proposed native controls, **not installed game settings**. A native
implementation must freeze the candidate set after generation, bound sorting
and preserve eligibility. It must not globally edit shared constants or promise
a percentage of all players from a conditional probability table.

The native queue holds 400 active records plus one insertion scratch row. Raising
that limit requires a separate storage/serializer/consumer audit. The native
automatic selector also limits per-school arrivals to three; a new configurable
arrival policy must replace that rule deliberately, not confuse it with available
scholarship capacity. The first prototype should retain the 400 active-row bound.

## Proposed persistent proxy binding, without invented metadata fields

A potential design reserves additional recruit records after the original 2,000
prospects, mapping proxy `base + queue_ordinal` to the original saved transfer row.
This avoids replacing existing HS/JUCO records and avoids placing pointers or
custom flags into unknown roster bytes. It remains a proposal pending a complete
allocation, initialization and lifecycle implementation.

The native queue contains original player, source and destination references.
Serializer/loader `0x5BC660` / `0x5BC854` preserve row order and rebase all three
columns. `0x5BCA74` sorts during insertion; binding before the final insertion
would associate proxies with the wrong players. `0x5BC398` clears destinations
without reordering. Direct callers of insertion/reset were found in generation;
this does not prove there are no indirect consumers. Freeze the queue before
creating proxies, prohibit insertion/reset while bindings are active and validate
every row against its original/source before acting on it.

The recruit directory/accessors use an actual count and 0xD8 stride.
Roster serializer/rebaser `0x1BF28C` loops header +0x48 records using per-record
`0x753DE0`; restoration `0x1BDEFC` loops the same count using `0x753D90`.
Both per-record routines handle the two name references. This supports dynamic
serialization, not a blanket guarantee that every consumer supports expansion.
The enclosing Legacy save includes the roster separately from the fixed native
aggregate; do not replace a dynamic envelope with a guessed constant file offset.

A fixed reserved proxy range can identify portal records without borrowing an
unmapped bit. Their internal recruiting class should stay in an established
native class, with class 3 a candidate for the prototype. Display providers
`0x6AD5B8` / `0x6AE140` index class-label tables directly: writing college class
codes into recruit class is unsafe. Render TR FR/SO/JR/SR and (RS) from the original
college player; do not change academic class merely to display a label.

A concrete proposed priority encoding uses three existing valid native preference
profiles: Hometown 24, Playing time 33, and ranking-adapter 32. Their respective
rank-zero native motivations are hometown, playing time and big program. Setter
0x752AE0 and getter 0x753AB4 cover the existing seven-bit field at +0x40 shift7;
native recruit serialization retains it. For a positively identified portal proxy,
profile32 would dispatch the custom current-poll scoring/display adapter. It does
not change ordinary big-program semantics. Decode these values as portal motives
only after validating reserved-range identity and queue binding. Ordinary HS/JUCO
prospects legitimately use the same profiles and must not be reclassified.

The offline API specifies this encoding and rejects unassigned proxy profiles.
This establishes a typed persistence location; it does not prove the complete
proxy lifecycle. Draw once at entry and retain the profile through recruiting,
save/load and commitment. Annual regeneration must not overwrite it while the
candidate is active. Do not store state in unproven padding or redraw on screen
entry. The native random draw, scoring and display adapters remain uninstalled.

## Concrete recruit-capacity obstacle

CPU routine `0x5C9974` scans exactly 2,000 recruits, with immediate comparisons at
`0x5C9B10` and `0x5C9CA4`. It sorts pointer/value pairs in a separate 16,000-byte
buffer beginning at `0x12EE993C`, addressed through TOC slot `0xA617E8`.
Changing only the roster count leaves additional proxies out of CPU processing;
changing only the loop count overflows the original sort buffer.

Another constant, TOC `0xA6171C`, has the same value but is the **end of a preceding
32-byte array** used by destructor `0x5C3888`, not a second sort-buffer accessor.
Do not redirect both merely because their values match. The next region begins
at `0x12EED7BC`; extending the original buffer in place would overwrite it.
A replacement allocation/access path must preserve those neighboring regions.

Additional inactive proxy records also need filtering: the stock CPU loop checks
commitment before considering records and cannot simply be pointed at hundreds
of uninitialized zero records. Keep original prospect behavior, skip inactive
reserved proxies, size scratch storage to the validated total, and exclude unused
slots from UI/interest/action processing. Rankings have separate fixed capacities
and must not silently displace the original prospects to make transfers visible.

## Offers, commitments and scholarship reservations

The action dispatch tables were resolved from their relative branch entries;
Ghidra's initial C output omitted their cases. Confirmed native behavior:

| Operation | Native evidence |
| --- | --- |
| Offer eligibility | Action 6 in 0x5C6C00 checks a valid school-list node, calendar permission, positive school +0x2A8 high nibble, and no existing offer |
| Add offer | Action 6 in 0x5C67FC sets second-pool node word +6 bit 7 and subtracts 0x10000000 from school +0x2A8 |
| Withdraw offer | Action 7 clears that bit through 0x5C36CC and refunds 0x10000000 |
| Withdrawal guard | Action 7 in 0x5C6C00 requires an offered school and an uncommitted recruit |
| Commitment | 0x5C8CD8 sets recruit +0x40 bit31, decrements school +0x2A8 bits24..27, rebuilds the selected interest head and refunds losing offers |
| Destination read | 0x5C4B60 resolves the committed interest-head school's index |

Native CPU signing calls 0x5C8CD8 from 0x5C9974. A portal commitment must revalidate
that an offer and destination reservation exist, then reconcile the saved transfer
destination with that committed school. Repeating a callback must not decrement
counters twice. Do not additionally apply native 0x5BC990 to portal entries after
ordinary recruiting has already consumed their destination reservations.

Keeping original players on source rosters during recruiting is the proposed
history-safe approach. Do not credit a source departure merely on portal entry:
an unsigned player can otherwise return to a source that already spent that
scholarship. A locked commitment may release projected source capacity once;
cancellation would require a complete reservation rollback. Exact source-credit
reconciliation with HS/JUCO commitments and native removal counters remains an
implementation gate. Packed nibbles must never wrap underflow/overflow.

For final membership changes, preflight the complete batch before source removal,
including the 18-player physical roster limit and scholarship limit. Remove all
validated departures before adding arrivals to support school-to-school cycles.
Verify resulting membership; native add 0x764548 returns void and can reject a full
team or evict a walk-on. A successful function call is not proof of a successful
transfer. Preserve unknown player bytes, identity and all history records.

The existing incoming-transfer decline callback calls 0x5BC398. It must not clear
a portal destination behind a locked recruit commitment. Disable that old action
for portal rows or implement the complete cancellation transaction. No such native
behavior has been installed.

## History and unsigned-player policy

Create a recruiting proxy, never a replacement college player. Retain the original
on its source roster until the membership phase so native class progression and
history shifting can still find it. Leave unsigned players on that source through
the deadline rather than invoking the existing zero-destination release branch.
Returning unsigned players to their source is a proposed default, not an observed
native portal feature or an owner-confirmed final policy.

Proxy statistics ID +0x2E must be empty or independently owned, never an alias of
one of the original player's five history IDs: recruit cleanup 0x75DBE8 frees it.
Route career/history UI through the original player when appropriate. Keep older
school attribution intact. Intercept proxies before ordinary class advancement,
player allocation, 308-byte clearing/conversion, and unsigned walk-on fallback.

Annual 0x75B0D0 clears recruiting flags and statistics and can regenerate records.
Cleanup 0x5C5FF8 releases interest lists and school-side nodes. Portal cleanup must
run in a phase where neither committed conversions nor those queues still use the
proxy. Leave no stale bindings into a newly sorted transfer queue the following
year. The two independent 16,000-node pools are not spare unlimited capacity;
audit both, reserve a bounded portal budget, and establish exhaustion handling
without depriving ordinary recruiting of required nodes.

## Priority inputs still needed

- Playing time: native 0x764050 supplies position-specific depth/opportunity, not
  projected minutes. A minutes projection must account for graduated players,
  locked departures, pending HS/JUCO commitments and other signed transfers.
- Hometown: native 0x75C248 supplies geometric separation. International/missing
  locations and units remain to be validated; do not label an unknown scale km.
- Rankings: the native selector labels in 0x5C235C/0x5C2834 establish modes
  0 Media, 1 Coaches, 2 Mid Major, 3 RPI and 4 conference champion. 0x5BDB44
  retrieves a school by mode and list position; 0x5BDA8C returns25 for modes0..2.
  Media uses the current snapshot index; 0x5BD210 returns its count and must be
  checked before lookup because index -1 means no current snapshot. Use mode0
  or mode1 Top25 order and treat absent schools as unranked. Do not substitute
  recruit/class rank or prestige. The native adapter remains to be installed.
  The read-only aggregate reader now exposes these saved tables. A different
  menu named TeamStats Poll reads wins/losses, illustrating why names alone are
  insufficient evidence.

## Saved polls exposed in the editor

The existing 0x5BDCD8/0x5BE02C component is now identified as ranking/poll state.
It remains exactly0x1D54 bytes; its component key is retained for compatibility.

| Component-relative span | Established contents |
| --- | --- |
| +0 | Signed Media snapshot index, -1 or0..19 |
| +4..+0xAF3 | 350 eight-byte RPI rows |
| +0xAF4..+0xBC3 | 26 Coaches rows; only25 displayed ranks |
| +0xBC4..+0xC93 | 26 Mid-Major rows; only25 displayed ranks |
| +0xC94..+0x1CD3 | 20 Media snapshots of26 rows each |
| +0x1CD4..+0x1D53 | 16 conference-champion reference rows |

Rows contain a school pointer plus a preserved raw word; complete raw-word
semantics are not assigned. Saved pointers are roster-base-relative, not field-
relative. The aggregate inspector resolves exact school anchors, reports invalid
or duplicate schools within displayed lists, preserves rank positions across blank
rows and never promotes the extra stored row into rank26. A missing current Media
snapshot does not make stale historical rows current. Correspondence between a
supplied roster and aggregate, and the phase of the other tables, remain unverified.

## Evidence and acceptance

Private Ghidra passes were cross-checked against original instructions. A private
read-only auditor verifies both callback sequences/order, the two hardcoded CPU
limits, scratch-region arithmetic, confidence getter/scaling and unchanged source.
Public documentation includes addresses and interpretations, not proprietary code,
raw dumps, game assets, private paths or fingerprints.

Required before claiming the full design implementation-ready:

1. Implement and inspect a complete valid proxy initialization/visibility path;
   preserve all original HS/JUCO prospects and route TR class/RS safely.
2. Establish both node-pool budgets and the exact scratch allocation/lifetime
   path; prove allocation failure cannot publish partial candidates.
3. Complete commitment/source-credit/withdrawal/decline reconciliation, including
   ordinary recruits, capacity races, repeated callbacks and transfer cycles.
4. Bind the identified poll/preference routes and location/opportunity metrics to
   validated portal proxies; verify one priority survives each lifecycle boundary.
5. Verify native save/load/resume contracts, phase protection and annual cleanup
   with actual phase-specific state. Then build a revision-guarded separate
   executable prototype and perform owner-run multi-season acceptance.

Required runtime cases: CPU/user entry and offers, unsigned return, commit/decline,
full destinations, no offers, queue saturation, both pools near exhaustion,
source/destination cycles, class/redshirt/sit-out policy, identical history before
and after signing, in-game save/reload during recruiting, season rollover and a
second transfer season. A passing Python policy test does not pass these cases.

Current follow-up: [history ownership](LEGACY_HISTORY_OWNERSHIP.md) and
[scheduling / tournament limits](LEGACY_SCHEDULING.md).

# Legacy backend map and portal integration

Read-only research on the supplied PS3 College Hoops 2K8 executable revision.
Addresses are revision-specific virtual addresses. Original executable and game
data remain unchanged. This is a partial backend map, not a completed portal or
a claim that every Legacy byte is understood.

## How the systems fit together

The roster supplies players, schools, coaches, conferences and allocated recruit
records. Legacy also has native state outside that roster. Editing the embedded
roster alone does not inspect or update all of Legacy.

| System | Established | Unresolved for the portal |
| --- | --- | --- |
| Calendar/season context | Annual initialization reaches recruit regeneration; separate rollover converts signed recruits | Exact portal window and resume transitions |
| Recruiting | 0xD8 records, class/preference fields, two 16,000-node pools, four queues | Safe proxy reservation, all queue operations and persistent binding |
| Transfer selection | Candidate queue, conditional frequency gates, scored destinations | Named meanings of all filters and configurable frequency |
| Commitment | Commitment bit, school counter, interest rebuild and queues/messages | Transfer reservation, cancellation and repeated callbacks |
| Membership | Source removal, destination addition, reusable player pool | Atomic signing with capacity guarantees |
| Statistics/history | Five player-owned IDs, shared 24-byte records, stored historical school, rollover and free/reclaim paths | Native portal calendar integration and runtime continuity |
| Save/load | All 17 native aggregate component sizes and order | Enclosing USERDATA location across variants and full field semantics |
| Other Legacy systems | Bounded serialized regions mapped | Schedule, coaching, awards, rankings, tournaments and finances not comprehensively decoded |

The intended new flow is candidate selection → reserved recruit proxy bound to
the original player → CPU/user recruitment → commitment → validated membership
change → season progression. This is a design target. Current native recruiting
and transfer flows are separate and cannot simply be connected at one call.

Ordinary rollover `0x5B61D8` obtains a reusable player through `0x744298`, rebuilds
it with `0x7570EC`, then calls destination add `0x764548`. A transfer must bypass
conversion and retain its original player. The existing transfer finalizer's
unsigned path can return that player to reusable storage; it must not run while
the player remains recruitable. Keeping a name or numeric ID alone cannot prove
that career totals and historical school attribution survive.

## Native aggregate: complete boundaries, partial semantics

Size routine `0x595C20`, serializer `0x595D64` and loader `0x595FB0` independently
establish the order below. All 17 constant size getters were checked against
original PowerPC instructions; paired save/load orders were checked with Ghidra.
The total is **0x15D1CC bytes (1,429,964)**. Offsets begin at the aggregate passed
to these routines, **not the start of a save or USERDATA**. The zero-length
component is real and does not shift subsequent components.

| Component | Offset | Bytes | Save / load routine |
| --- | --- | --- | --- |
| Legacy context, partial | 0x000000 | 0xC9F8 | 0x5A1244 / 0x5A15A8 |
| Empty component | 0x00C9F8 | 0 | 0x73D89C / 0x73D8AC |
| Unresolved | 0x00C9F8 | 0x4228 | 0x58CA40 / 0x58CA9C |
| Unresolved | 0x010C20 | 0x7F8 | 0x5B8290 / 0x5B82C8 |
| Recruiting | 0x011418 | 0x415A4 | 0x5C5468 / 0x5C57B0 |
| Unresolved | 0x0529BC | 0x5210 | 0x5CD7E8 / 0x5CD99C |
| Unresolved paired reference arrays | 0x057BCC | 0xC0 | 0x5C29CC / 0x5C2BEC |
| Statistics free stack | 0x057C8C | 0x7D04 | 0x75E2B8 / 0x75E314 |
| Seasonal box-score bank | 0x05F990 | 0x92004 | 0x597F94 / 0x598178 |
| Unresolved reference component | 0x0F1994 | 0x1D54 | 0x5BDCD8 / 0x5BE02C |
| Unresolved reference component | 0x0F36E8 | 0xA28 | 0x590B50 / 0x591294 |
| Unresolved indexed/reference component | 0x0F4110 | 0x1B5C | 0x592C20 / 0x592E80 |
| Unresolved reference component | 0x0F5C6C | 0x2198 | 0x770280 / 0x7704B8 |
| Transfers | 0x0F7E04 | 0x12D0 | 0x5BC660 / 0x5BC854 |
| Unresolved 0x480-stride component | 0x0F90D4 | 0x63D80 | 0x5AEEF0 / 0x5AF088 |
| Unresolved reference component | 0x15CE54 | 0x358 | 0x5FA838 / 0x5FA960 |
| Unresolved raw tail | 0x15D1AC | 0x20 | 0x5B9208 / 0x5B9240 |

Several serializers temporarily subtract the roster base from live pointers,
copy the component, then restore pointers. Matching loaders reverse this.
Serialized references, live addresses and the roster's own field-relative
encoding are distinct contracts.

## Transfer identity diagnostics

The transfer component holds a signed count followed by 401 twelve-byte records.
Only 400 are active capacity; one extra record supports insertion/sorting. Active
columns are original player, source school and destination school. Zero destination
means unsigned, not malformed. Roster-base wrapper `0x4A36A4` resolves to
`0x1BDD0C`, which returns the roster base used for serialization rebasing.

The inspector resolves exact anchors: player physical row +16 and school row +48.
Arbitrary in-bounds pointers are insufficient. It reports null required references,
misaligned/invalid anchors, duplicate players and equal source/destination schools.
Inactive storage is hashed without interpreting stale scratch entries as active.
These checks establish structural identities against the supplied roster, not
provenance, legal membership or history continuity. A different roster with the
same layout can still resolve; correspondence remains explicitly unverified.

## Additional reference-bank evidence

The 0x92004 component holds a count plus 1,024 records of stride 0x248. Save/load
visit two sets of twelve reference columns per active row at row +8 + side*0x120
+ slot*24. Nonzero columns are roster-base-relative on disk. The inspector checks
those exact columns and counts references outside the roster; adjacent bytes stay
uninterpreted. Live and simulated game writers establish seasonal box scores;
player participant slots also store a player index. New-season initialization
clears the active count. This is separate from persistent player history.
The insertion/search path `0x597D10` bounds the bank at 1,024 records
and can recycle entries. This is not proof of unlimited historical storage or a
fully understood career-history bank.

## Tool integration

Open **Recruiting diagnostics… → Legacy backend** in Roster Editor. The overview
and component map work without an offseason save. **Inspect native Legacy
aggregate…** accepts a separately identified aggregate of exactly 0x15D1CC bytes;
it does not guess or extract one from a whole save. Select a component to view
its bounded audit or explicit error. A failed component audit does not hide other
boundaries. Recruiting audits reuse the existing backend; transfer identity and
reference-bank checks are new. Source changes invalidate delayed worker results.

CLI: `inspect-legacy-backend ROSTER_FILE NATIVE_AGGREGATE.bin OUTPUT.json`.
The roster may use a supported wrapper. Both inputs are protected from output
overwrites. Reports are separate JSON, never game-data CSV columns. Reports may
contain game-derived metadata and should remain private.

Exact size does not establish executable revision, roster correspondence or full
Legacy validity. No transfer/sign/save mutation or executable patch is exposed.
The in-game portal remains the goal; inspection supports native integration.

## Next native integration gates

1. Integrate the established history ownership chain with portal calendar handling,
   including unsigned players missed by roster-only rollover and allocator reclamation.
2. Trace calendar dispatch and save/resume boundaries around transfer finalization
   and ordinary recruit conversion.
3. Establish durable proxy-to-player binding and reservation that survives annual
   recruit regeneration without overwriting HS/JUCO prospects.
4. Prove scholarship capacity reservation, atomic signing/cancellation and repeated
   callback behavior before installing a revision-guarded native experiment.
5. Verify identity, totals, affiliation, eligibility, unsigned players and multiple
   seasons of save/load in game. No such runtime verification is claimed here.

Detailed recruiting evidence and requested interest policy:
[LEGACY_TRANSFER_PORTAL.md](LEGACY_TRANSFER_PORTAL.md).

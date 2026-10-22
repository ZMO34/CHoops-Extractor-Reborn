# Player statistics and historical school ownership

Read-only native research on the supplied CH2K8 PS3 revision. This continuation
establishes the persistent storage/ownership chain required by the transfer
portal. It does not install the portal or certify runtime preservation.

## Authoritative ownership chain

| Owner or operation | Confirmed contract |
| --- | --- |
| Player | Five u16 statistics IDs at logical player +0x18..+0x20, editor raw row +0x28..+0x30 |
| Recruit | One u16 statistics ID at recruit +0x2E; getter/setter 0x7537E0 / 0x7537F4 |
| Shared statistics table | Roster directory count +0x40, pointer +0x44; record stride 24, accessor 0x1BC62C |
| ID validity | 0x75DB70 accepts 1..15999; ID zero is reserved. Both 0 and 0xFFFF produce no history record |
| Stored school | Record word +0x14, bits 14..22; getter 0x75E434, setter 0x75E824 |
| Career aggregation | 0x75E39C sums a requested packed statistic across the player's five linked slots |
| Release | 0x75EC0C pushes a valid ID to the shared free stack, then clears the player's slot |
| Free stack | Native component 0x7D04: signed count plus 16,000 u16 storage cells; initializer exposes 15,999 usable IDs |

The raw roster table windows have biased origins. Player logical origin is raw
+16 and school logical origin is raw +48. Readers validate logical spans rather
than rejecting the stock arena/team windows' intentional physical overlap.

School attribution is not inferred from current membership. Season-processing
routine `0x5B3674` iterates each school's players and passes that school's native
index to `0x75E824(player, school, 0)`. The historical-name formatter `0x6A07B8`
reads the stored school through `0x75E434`, resolves that school, and uses its
name. Filter `0x567AB4` compares a prior history slot's school against a school
index. Thus older linked records carry their own affiliation. A current-season
record's metadata may not yet have been finalized by season processing.

The complete 24-byte record must survive, including packed totals and flags whose
individual names are not all established. The inspector preserves all six words
and a full-record hash; it does not add speculative stat or award editors.

## Rollover and allocation

`0x75ED04` visits players on school rosters, shifts four IDs toward older slots,
clears slot zero, and resets the allocator's reclamation-age cursor to four.
This is history-slot progression, separate from academic class/redshirt changes.
Native new-season initialization `0x5A5190` calls it at `0x5A5A78`.

The statistical setter/allocator `0x75EF94` allocates when current slot zero has
no valid ID. It pops the free stack, clears the selected 24-byte record and binds
the ID to the player. If the stack is empty, it can scan eligible schools' players,
detach an older history ID, clear that record and reuse it; the reclamation-age
cursor decreases if necessary. The inspected selection helper's complete school
eligibility meaning is not established. This behavior is not a guaranteed
history-preserving allocator and must not be called blindly by portal integration.

Recruit cleanup `0x75DBE8` returns recruit statistics IDs to the same stack.
Ignoring recruit ownership would make a free/owned audit incomplete. The reader
reports shared references rather than assuming every alias is illegal: lifecycle
phase and recruit-to-player transitions still matter. Unreferenced records are
not automatically leaks or safe new allocation capacity.

## Distinct game box-score storage

The native 0x92004 aggregate component is a game box-score bank, not the career
record owner. Writers `0x5AA190` and `0x5D1B10` populate two sets of twelve
24-byte participant rows under a game key. The player route `0x598C04` stores
both a player reference and its roster index. The alternate participant route
uses a different setter; not every participant is silently called a player.
`0x597CD4` clears the bank's active count during new-season initialization, at
`0x5A5A88`. Career/history preservation must protect the separate roster-backed
statistics table and player ID links, not just copy this seasonal box-score bank.

## Portal preservation contract

1. Retain the original player object, its five history IDs and every referenced
   statistics record. Do not run ordinary freshman conversion or release those IDs.
2. Retain older records' stored school bits and packed totals. Current membership
   changes must not rewrite previous school attribution.
3. Cover annual rollover exactly once. An unsigned player detached from all school
   rosters is absent from `0x75ED04`'s traversal and would otherwise miss the shift.
4. Establish calendar ordering relative to school-attribution finalization and
   ordinary signing. Do not relabel an old current-season record as the new school.
5. Preserve free-stack ownership and prevent reclamation from discarding required
   history. The 16,000-record backing table is not unlimited storage.
6. Verify CPU/user entry, signing, unsigned players, cancellation, capacity failure,
   save/load and multiple seasons in game before claiming continuity certification.

Correction to the earlier transfer trace: finalizer `0x5BC250` increments
**source-school +0x2A4**, not a player +0x2A4 field. Its first loop follows the
queue's source column; independent TOC aliases establish player/source/destination
column order. This is school-side state and must not be treated as a player-history
counter. The original no-destination reusable-player-pool hazard still applies.

## Tool and evidence

**Recruiting diagnostics… → Player history** lists player IDs, linked records,
stored schools and hashes without changing data. **Legacy backend** inspects the
statistics free-stack component and attempts an ownership cross-check. Missing
history directories remain an explicit ownership-unavailable diagnostic.

CLI: `inspect-legacy-history ROSTER_FILE OUTPUT.json [--free-state STACK.bin]`.
The optional stack must be an identified 0x7D04 serialized component. Inputs are
protected from output overwrites. Reports are private JSON, not game-data CSVs.

Stock source inspection finds 16,000 allocated records with uninitialized player
history IDs (0xFFFF); these are accepted as empty, not thousands of false errors.
Synthetic checks cover school attribution independent of current membership,
player/recruit aliases, free-stack collisions, table bounds and untouched bytes.
Native static ownership is mapped; a full live lifetime graph and playable portal
remain unverified. No original EBOOT/save/game asset was changed.

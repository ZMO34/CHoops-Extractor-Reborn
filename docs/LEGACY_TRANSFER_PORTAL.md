# Legacy transfers and a recruitable portal: feasibility

Read-only native research, 2026-10-21, on the supplied PS3 College Hoops 2K8
revision. Addresses are revision-specific virtual addresses, not universal file
offsets. Original executable, saves and game archives remain unchanged. No
emulator, gameplay test, executable patch, editor feature or JB build is supplied.

## Assessment

**Higher transfer activity has concrete native control points. A recruitable
transfer portal is plausible, but is a larger Legacy-system change.** The most
promising initial design extends the game's existing transfer list and destination
selection while retaining existing player objects and the final membership commit.
Routing transfers through ordinary recruiting is a second, less established route:
the recruiting record, eligibility, interest, scholarship and calendar contracts
have not been shown compatible with existing college players.

The game does not simply choose a random destination for each transfer. Its
assignment routine scores eligible schools and retains the best candidate. This
provides a specific interception point for user recruitment decisions. Neither a
fully recruitable pool nor increased transfer rates have been implemented here.

## Confirmed transfer pipeline

| Stage | Native entry | Observed behavior |
| --- | --- | --- |
| Generate outgoing queue | `0x5B4E50` | Resets queue, checks Legacy context +0x204, traverses schools and players, applies eligibility/state and chance/value gates, then enqueues candidates. The exact setting name of +0x204 is unresolved. |
| Insert/sort candidate | `0x5BCA74` | Stores a 12-byte row: player pointer, source-school pointer, destination-school pointer initially zero. Orders rows using the position-aware player evaluation at `0x74AA30`. |
| Select destinations | `0x5BCCF4` | Scores candidate schools using capacity/availability, a per-school arrival counter, player/school values, distance and other terms; excludes matching source/destination school identities. Retains the best score rather than a random school index. Full term semantics remain incomplete. |
| Finalize transfer | `0x5BC250` | Removes players from source membership, updates a player count byte, sets scholarship and Transfer sit-out status, then adds destination membership. A zero destination takes a separate removal path; it is not a proven safe uncommitted portal state at finalization. |
| Reconcile school state | `0x5BC990` | Adjusts packed school counters around the queued source/destination records. Precise neighboring counter meanings require further tracing. |
| Save/load queue | `0x5BC660` / `0x5BC854` | Serializes count plus 0x12CC bytes, temporarily rebases the three pointer columns against the roster base, and restores native addresses. The enclosing save-file offset is not established. |

Queue count is held at `0x12EA4C74`; rows begin at `0x12EA39A8`.
The serialized span is **401 twelve-byte records**, while insertion increments
active count only below **400**. The extra row permits insertion/sorting at a full
queue; it is not evidence that the save can safely hold arbitrary extra transfers.
Do not enlarge count independently of all loops, scratch storage and serializers.

The prior sit-out experiment changes only the Transfer-code insertion at
`0x5BC334`. It does not create a portal, increase transfer frequency, change
existing saves' eligibility, or make destination selection interactive.

## Transfer frequency controls

At `0x5B4F0C..0x5B4FA4`, the candidate generator extracts
`state = (player_anchor_word_0x88 >> 3) & 7`, skips zero, and computes:

```
chance = clamp((state - 1) / 3.0, 0.0, 1.0)
queue_candidate only if random_value < chance
                  and secondary_player_value < 0.66 * position_evaluation
```

The random helper `0x7C5430` constructs a float in [0, 1) from PRNG bits. The
chance formula is confirmed by the instructions and constants, not an inferred
menu label. For state values 1, 2, 3 and 4+, the chance gate is respectively 0,
about 33%, about 67% and 100%. **These are conditional gate probabilities, not the
percentage of all players who transfer.** Other filters and the second gate still
apply. The exact meaning and writers of this three-bit state are not established;
calling it a proven dissatisfaction or transfer-demand field would be premature.

The second gate uses `0x74AA30` (position-aware weighted player evaluation) and
`0x744C40` (player +0x70 byte converted through `0x742BD0`). The latter's precise
localized meaning is unconfirmed. Constants are 3.0 at `0xA61340` and approximately
0.66 at `0xA6133C` in this revision. Candidate filters also inspect the upper nibble
of player anchor +0x84 and bit 0x20 at anchor +0x0A. Do not remove these as if they
were redundant probability checks.

Possible scoped changes, still proposals:

- Add an explicit transfer-intensity multiplier to this chance calculation.
  Multiplication alone cannot create candidates in states whose base chance is
  zero; broadening that population needs a deliberate additional rule.
- Raise the 0.66 threshold to allow more otherwise-eligible players past the
  secondary gate. This changes which players qualify, not just randomness.
- Retain eligibility filters, queue capacity, ranking and scholarship checks;
  trace state generation before promising a particular annual transfer count.

Do not globally replace shared float constants. Any future experiment should
scope changes to this consumer, match the executable revision and preserve an
immutable original. A visible intensity setting is not yet exposed by the tool.

## Portal implementation options

**Preferred initial route: a separate transfer-recruiting list backed by existing
college-player identities.** The executable already registers
`PlayerTransferListMenu`, `PlayerTransferTeamMenu` and `PlayerIncomingTransferMenu`.
Source/destination text providers at `0x69F298` / `0x69F42C` query the queue through
`0x5BC4F4` / `0x5BC5A0`. The incoming-menu callback at `0x69F1B4` can, after a
positive confirmation result, call `0x5BC398` to clear a player's destination.
This proves an existing menu-to-assignment mutation route; it does not establish
an offer, signing action or user-selected destination setter.

A portal could expose this list before automatic assignment/finalization, let
users pursue candidates, reserve eligible scholarship spots, retain CPU decisions
for unclaimed candidates, then use the existing finalizer once. The exact calendar
window, cancellation semantics, commitment locking and reentrant/save-resume
behavior must be established first. Leaving zero destinations until the existing
finalizer runs is unsafe: its zero branch is not an offer-waiting state.

**Ordinary recruiting integration:** `RecruitCard_ABLMenu` resolves separate card
callbacks, including `0x6A4534`, with its own selection/context state and paths
through `0x5E05B0`, `0x5E0838` and `0x5E07B8`. That is a concrete starting point,
not proof that appending a player pointer makes a valid recruit. A transfer must
retain identity, class, remaining eligibility, statistics, appearance and history;
copying it into a freshman record risks duplication, resets and broken links.

The existing Legacy save adapter edits only the recognized embedded roster and
preserves outer mode state. It does not expose the serialized transfer queue or
recruiting contracts, so CSV or roster reassignment alone is not native portal
recruiting.

## Remaining work and acceptance gates

1. Trace callers/state transitions for generation, destination selection, counter
   reconciliation and finalization; identify the user-interactive window.
2. Trace the three-bit state writers and both player-value consumers to named
   fields; measure candidate counts on user-supplied season snapshots.
3. Establish transfer/recruit list ownership, filters and scholarship reservation;
   choose a dedicated list or prove an adapter for ordinary recruiting.
4. Locate enclosing save sections and prove save/load, cancellation and season
   resume without duplicate identities or double membership commits.
5. Prepare a separate revision-guarded experiment only after those contracts are
   understood. Runtime acceptance remains owner-run: CPU/user teams, full rosters,
   no eligible destination, queue saturation, class/eligibility, save/reload and
   multi-season progression. No compatibility certification is claimed.

## Verification

Ghidra focused tracing produced 17 function reports across two passes, cross-checked
against original PowerPC disassembly and literal constants. A private read-only
audit verifies source digest and byte equality, the exact subtraction instruction,
frequency constants, all eight state-gate values and 401-record span arithmetic.
This checks static interpretation, not runtime distribution or save compatibility.
No proprietary listings, source bytes, game assets, local paths or fingerprints
are published. The public change is documentation only.

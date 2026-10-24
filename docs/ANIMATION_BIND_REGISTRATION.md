## Paired on-court shot planar metadata investigation

`research.shot_planar.inspect_pair_planar` now makes read-only root-derived
proposals for category-14 paired shots, retaining both lanes and the complete
bank-set fingerprints. It selects this established gameplay family explicitly;
non-gameplay banks and group conversion are not included. Across the supplied
203 entries /406 lane references every proposal passes bounded source inspection.
These are proposals, not compatible conversion or playable-import totals.

The represented-trajectory average samples ROOT POSITION AT PLAYBACK DURATION,
not the final padded key, subtracts time zero, divides by duration, applies the
native 1/8 position scale and mirrors X from mode bit30. Speed is the norm of the
resulting X/Z components. Source byte-delta key times and CH fixed key times are
handled separately. Cyclic interpretation, invalid timing/coverage, wrong rigs,
incorrect root extents and float32 overflow reject; unknown authoring semantics
remain unapproved. Outputs identify themselves as estimates, with no automatic
metadata contract and no target compatibility claim.

Read-only `audit_stock_planar` validates registered CH motion extents and compares
against all224 existing paired-shot headers. All224 estimates agree with the
stored planar X/Z within one root-step velocity resolution (0.125/duration;
comparison epsilon1e-5), maximum per-axis error0.0471587181 native units/second.
This supersedes the earlier naive endpoint comparison for THIS CONTEXT; it does
not prove the original authoring algorithm or authorize estimates for running,
rebounding or other transition contexts automatically. Root quantization and
original authoring differences remain material limits on exact recovery.

Native root routines NBA11 0x17BF4 /CH 0x2027C were inspected. A bounded synthetic
full-root instruction probe could not execute NBA11's VMX instruction at0x17C08:
Ghidra reports an unimplemented vectorSplatImmediateSignedByte user operation.
No full-root native execution or VMX bit-exact claim is made. The numeric
reference and stock corpus check remain separately identified evidence.

Bulk pair inspection also exposed repeated full-bank decompression in the shared
collection-entry helper. Collection reads now use the same bounded decoded-block
cache as tracks; entry parsing remains fresh so a caller cannot poison later
rows through mutation. This preserves the existing combined128-MiB decoded-byte
limit and strict type/span checks; it is not a process-memory guarantee.

# Canonical bind and additive registration investigation

This update proves the observed 21-bone motion-space bind correspondence, adds
read-only audits, and begins bulk preparation of NBA11 pose components. It does
not finish all event semantics, register a donor shot, install controls, or make
an NBA11 animation playable. Runtime/gameplay verification has not been run.

## Bind retargeting

The CH parent table at `0x1000A0C0` and NBA11 table at `0xA1CBB8` have identical
21-parent assignments. The corresponding 336-byte local rest-translation tables
at CH `0x10009F70` and NBA11 `0xA1CC10` are byte-identical. Default channel routes
at CH `0x10000100` and NBA11 `0x9D8D88` contain the same 21 `(0,i,i)` triples.
Native CH `0x236254` / NBA11 `0x38919C` convert 21 local rotations, add these rest
translations and walk the same parent hierarchy. The quaternion matrix routines
are CH `0x21154` / NBA11 `0x16840`. These consumers were checked in Ghidra and raw
disassembly; matching table sizes alone were not used as bind evidence.

For this canonical motion rig, retargeting is identity in bone space plus the
established packed-quaternion selector conversion. The backend rejects changed
parents/routes, differing rest vectors, nonfinite values and unsupported masks.
The NBA11 unpacked-pose decoder branch is explicitly rejected rather than read
as packed data. None of the observed 18,831 headers uses that branch.
It does not claim compatibility for arbitrary skins, the separate 32-bone NBA11
SCNE deformation rig, twist bones, or muscle/cloth simulation.

Both games use low-word rotation mask `0x1DF7DD`. CH stores it at header +4;
NBA11 at +8. Translation masks are at +0xC in both games; CH +8 is the upper
translation word, not the low mask. Header +0x10 declares channel counts. All
7,055 observed CH headers have 17 rotations and six translations. The 18,831
NBA11 headers have 17 rotations with four, five, six, seven or eight translations.
The adapter preserves each declared mask and track count. It does not invent
missing translation channels or replace native absent-channel behavior.

```
python -m choops_py.cli inspect-motion-bind NBA11_ANALYSIS.ELF CH_ANALYSIS.ELF output/research/bind.json
```

Inputs must be decoded ELF64 big-endian PowerPC analysis copies from the observed
profiles. Outputs report `gameplay_ready=false`. The API
`retarget_canonical_frames` validates both binds and the donor header before
converting an isolated packed pose stream; it is not a complete clip writer.

## Additive shot registration

The existing 112 playback rows at `0x9DD5F0` have a 40-byte stride and use shared
TOC pointer `0xA58608`. Six observed readers load it before indexing. The selected
style remains an unsigned byte at player +0x73, read/written by `0x69E938` and
`0x69E94C`. The editor range initializer at `0x69D410` sets maximum 111.

The native property constructor uses TOC **0xA64A94**, not the main gameplay TOC
0xA54AC8. Using the wrong TOC here produces misleading decompiler references.
The localized-name array has its own start pointer `0xA662CC` and destructor end
pointer `0xA661FC`. Native initialization writes exactly 112 cells through R9
between `0x696A60` and `0x6970EC`. Destructor code around `0x694CF0`/`0x694D08`
walks the selected range backwards through the string-reference destructor.
Adjacent property pointers `0xA66200` and `0xA66118` must remain unchanged.

The string cells use tagged references. An arbitrary UTF-16 address ORed with one
is not a valid substitute for an existing localization key. Runtime handling at
`0x1E0D64` skips release of tagged cells, while `0x1E0DF8` creates tagged references.

```
python -m choops_py.cli inspect-shot-registration CH_ANALYSIS.ELF output/research/shot-registration.json
```

The audit checks row count/range agreement, stock-row preservation, byte accessors,
six observed consumers, motion header masks and the original name initializer.
It reports structure compatibility, not exhaustive consumer coverage or runtime
safety. No executable writer is exposed through the editor or CLI.

### Local registration-only experiment

With the owner's authorization for separate executable experiments, a private
decoded ELF probe appends one **stock-backed Generic 1 duplicate**, leaving the
first 112 records byte-identical. It relocates the playback/name arrays into
verified zero file padding of the writable load segment, extends that segment's
file/memory sizes, and adjusts the shared pointers and option maximum. It reserves
the complete existing TLS template before allocating. All segment offsets and
special PS3 headers are retained. An exact byte-diff allowlist and reparse pass.

This establishes a bounded allocation experiment, not successful runtime
registration. The output is not a signed SELF, hardware-compatible EBOOT, donor
animation, testing JB or release artifact. Original executables remain unchanged.
The editor does not expose style 112 for ordinary unpatched rosters.

## Event consumers and semantic boundary

Native mirrored-marker selectors CH `0x231BB0` and NBA11 `0x3806D4` establish a
narrow correspondence: NBA11 21/22 swap under the same mirror flag as CH 20/21;
NBA11 23 and CH 22 are invariant third markers. The opt-in API
`mirrored_marker_contract()` returns only these three rules. NBA11 24 and every
other ID are excluded. This proves selector behavior, not anatomical/contact
names or every downstream listener's equivalence. It is not a default ID offset.

Optional payload-consumer inspection exposes individually traced reads:

| NBA11 event | Consumed offsets | Native operation / consumer |
| --- | --- | --- |
| 90 | +0 word | Actor-category comparison, `0x47F4FC` |
| 92 | +0 int, +4 float | Nonzero dispatch selector and clamped random threshold, `0x4D1B9C` |
| 93 | +0 int | Nonzero index forwarded into dispatch tables, `0x43903C` |
| 94 | +0/+4 int | Dispatch/identity table indices, `0x38603C` |
| 173 | +0 int, +0xC float | Selection-table index and event-time window, `0x3839B8` |
| 178 | +0 int | Resource dispatch branches on 59/60/61, `0x655604` |
| 186 | +0 int | Optional addend to a selection value, `0x42EBD8` |

```
python -m choops_py.cli inspect-motion-events NBA11_ANALYSIS.ELF nba-2k11 0xADDRESS output/research/events.json --native-elf --payload-consumers
```

These are confirmed reads, **not complete payload schemas or target enum maps**.
Gaps and unknown bytes are not reinterpreted. Float bits are retained even for
nonfinite payload values; their JSON numeric value is null. Inspection does not
allow the event converter to discard or translate opaque payloads. IDs 89, 176
and 177 still lack an established payload consumer schema in this adapter.

## Bulk preparation and remaining port gates

Private preparation covered all 18,831 identified NBA11 headers, retaining each
header's identity and dependencies independently. All 9,574 distinct packed pose
streams, totaling 341,823 stored keyframes / 49,278,288 pose bytes, converted and
reversed byte-for-byte without errors. This coverage is the observed mask family,
not proof that every animation in NBA11 has been found.

The local component bundle stores converted poses and byte-exact source timing/
root tracks at the original irregular keys. It is explicitly not an IFF or CH
fixed-rate motion bank. Pose deduplication does not merge clip semantics. Only
2,674 event tables contain exclusively the verified selector subset (including
empty tables); **6,900 remain blocked**. This is not 2,674 certified playable clips.
The source files retain their original hashes. Expanding every unique stream to
fixed-rate frames at its current rate would require 1,632,617 frames / 235,096,848
pose bytes, before roots, events or existing CH assets. Most source key intervals
have GCD one, so a simple lower-rate common grid does not materially reduce this
cost. The component bundle deliberately retains source timing instead of loading
an unchecked expanded library into the game's memory.

Remaining gates before an installable port include complete event/ball/contact
mapping, target header flags and velocity metadata, auxiliary tracks, blend and
selection graphs, appended shot playback metadata, runtime memory constraints and
gameplay validation. CH header +0x24/+0x28/+0x2C cannot safely be filled with a
naive root-endpoint velocity: that hypothesis fails on 3,390 of 3,727 stock streams.
No unrelated template velocities or unchecked flags were copied as a workaround.

No RPCS3, hardware run, full-game build or controller remapping was performed.

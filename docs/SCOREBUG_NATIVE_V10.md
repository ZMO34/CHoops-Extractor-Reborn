# Live footer and reference scorebug revision

V10 is the next separate, owner-authorized executable/IFF package after the
user's v5 screenshot showed no scorebug text. It includes executable callbacks,
scene bindings, typography and shaded assets; it is not another labels-only
study. Native visibility remains unconfirmed because repository instructions
prohibit emulator/gameplay execution. Do not describe it as gameplay-certified.

## Live names and foul/bonus rows

The v8 assumption that the existing city providers always populate ABL text was
incorrect. At 0x4EF9A4/0x4EFABC they first call 0x4EED80, which can report success
without assigning the name string in ordinary modes. The direct name path now
selects the active home/away team, checks both pointers and the name pointer,
then calls the existing 0x4EF92C team-name routine (team +4). No team-name artwork,
sample school names or roster membership list is baked into the scorebug.

Separate away/home footer providers occupy the otherwise unused away_city and
gameclock_left registry entries. They display the selected team's current-half
fouls and its earned bonus. The native foul popup provider at 0x50C708 reads the
same team state +0x28, counter +8. State pointers and counters are checked; invalid
or unavailable data produces empty text, overwriting stale content.

Bonus uses the **opponent's** foul state. The double-bonus check calls the native
0x49CAE4 predicate, which also examines its period/overtime state. One-and-one
uses the comparison from 0x3D0F48 against the loaded rules +0x168, rather than a
hardcoded seven-foul threshold. A disabled/nonpositive threshold leaves that
label empty. Display strings are FOULS:n, BONUS and BONUS+.

The authored callback is 648 bytes at 0x89A900, with four side/action wrappers
and native function descriptors. Only dedicated initialization stores are
redirected; shared native provider descriptors are unchanged. Strings reside in
mapped persistent UTF-16 storage. Native integer/string formatting retains owning
handles; temporary handles are destroyed before return. There is no cached game,
foul total, bonus state or team name. Source and installation metadata are in
`examples/scorebug-footer-provider.ppc` and its JSON profile.

## Scene and popup changes

The main scene keeps the ten recovered core fields and adds two footer fields.
Its table has twelve records and its Score_bug skeleton fifteen markers, with
two appended footer markers. Original markers, root/helper and mask indices stay
intact. New markers receive case-sensitive ASCII CRC32 identities at bone +36,
and the new siblings are linked below bug_skeleton. Native 0x7F9AB8 searches the
stored identity, so a matching marker name alone is insufficient. The audit now
reports native_marker_resolved separately and detects stale/mismatched hashes. Forward relative pointers and 16-byte table/property alignment are
checked after relocation. The source fonts remain native. Installed text-matrix
scales differ by role: scores 0.90, period 0.5114, game clock 0.625, shot clock
0.5682, school names 0.625, context 0.4514 and footer 0.50. These are actual IFF
changes, not just preview sizes; projected pixel sizes still need observation.

The comparison strip remains directly above both team panels, ending at the home
score before the clocks. Native type-37/38 provider 1 uses the **home** team via
0x50D350; provider 2 uses away via 0x50D3D0. The former v8 assumed side order was
reversed. Text2 now occupies the home cell and text3 the away cell. Text3_b adds
the native alternate transition binding at the away anchor, sharing an existing
marker without increasing the six-bone topbar. Its native provider selects the
current/transition event according to HUD state; no event is manufactured.

Shaded team panels, pale score plates/dark figures, centered square artwork,
restrained dividers and the corrected helper geometry carry forward from v8.
Both live sixth-man strips remain **under their team's name and above the foul
row**, from X -278 to -153 and -72 to 53, Y -193 to -191. All nineteen native
meter material/threshold draws are retained. Far-right text keeps the installed
timeout, verified NCAA/NIT/conference tournament, conference matchup and College
Hoops Reborn context provider.

Native compact points/foul/violation/injury events, diagnosis/run events and
leader/comparison queues are retained. Binding presence and static provider
traces do not prove every event's admission, clipping, animation or fit. Queue-2
leader text can differ from the television comparison layout. Those are runtime
limitations, not completed display certifications.

## Installation and verification limits

Use the matching v10 EBOOT.BIN, overrides/gamedata.iff and overrides/english.iff in
a separate manual game build. Apply both IFF overrides through the editor's
normal preparation/build workflow; place the supplied executable at
PS3_GAME/USRDIR/EBOOT.BIN in that separate build. Do not mix v5/v8 executable or
scene files. This is a debug/fake SELF, not a retail-signed executable. Preserve
custom English edits separately before applying the supplied matched archive.

No alternating-possession getter, verified tournament seed/region/round, end-cell
comparison logos or dynamic comparison tint is installed. Those reference details
are omitted instead of being represented by fabricated values. This revision
therefore does not establish an exact, fully verified television replica.

The new callback instruction harness covers 26 paths, including side selection,
opponent-owned bonus, changing rule thresholds, nulls, invalid counters, direct
names, stale-state clearing and halftime transitions. External native calls are
stubbed. The harness checks stack/LR/TOC/CR/nonvolatile preservation and rejects
borrowed stack character buffers. Existing context/scene/text/runtime tests also
remain required. Private output checks cover ELF write allowlists, SELF payload
roundtrip, scene reparse/dependencies and untouched record prefixes; any inferred
span growth must be exact known relocated headers or bounded zero alignment.

The final focused suite passes 95 tests. Eighteen packaged fields pass the native
marker-hash/owner/draw checks. ELF write allowlists, SELF roundtrip, source matching,
footer hierarchy, two-IFF preparation/preflight and ZIP CRC/checksums pass.
No full JB or emulator/gameplay run is part of these checks. The user's next
in-game screenshot remains necessary to confirm scores/clocks/names render and
to validate popup fades, stencil/culling, palette appearance and actual font size.

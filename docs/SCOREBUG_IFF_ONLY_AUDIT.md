# IFF-only scorebug: current evidence and limits

This supersedes deployment guidance for the experimental v10/v11/v12 executable
packages. The owner reports a pregame crash after replacing EBOOT and requires
an original executable. No further executable patch or uniform-logo name route
is authorized. The current work is an **unfinished IFF-only candidate**, not a
runtime-certified replacement or a completed automatic-name feature.

## Required result and evidence

| Requirement | Current state | Remaining proof or limitation |
|---|---|---|
| Roster names beside logos | Unresolved | Normal-game providers suppress names; no verified IFF-only bypass |
| Black body, pale score cells, separators | Authored in candidate | Native rendering requires user verification |
| Slight team-color gradient | Vertex RGB 0.95 to 1.0 | Actual palette/shader appearance unverified |
| Logo shape/color | Square quads, full 0..1 UVs, neutral RGBA | Active uniform artwork unchanged; native appearance unverified |
| Score/clock/period text | Existing native providers, marker relocation | Placement and font size require native verification |
| Right-side branding | One-line native literal: College Hoops Reborn | Default-render path established statically, native appearance unverified |
| Sixth-man meter | Existing 19 segment draws and activation, relocated | Fill/transition/appearance unverified |
| Native comparison popup | Existing triggers, side-value/category formatting | Transition/visibility and all event categories unverified |
| Other native context popups | Existing queues/callbacks retained | No new event sources or custom callback installed |
| Permanent foul/bonus/timeout rows | Unresolved | No separate continuously updated providers in main registry |
| Rankings below 26 | Unresolved | No confirmed rank provider/threshold binding in scorebug IFF |

## Team-name investigation

Original initialization registers 14 main text slots. The main loop at
`0x4F4858..0x4F490C` invokes that fixed registry and searches the loaded SCNE by
text record name. Adding an arbitrary SCNE name does not register a provider.

`home_city` and `home_ABL` use `0x4EF9A4`; away counterparts use `0x4EFABC`.
They call `0x4EED80`, which usually delegates to `0x4EEB3C`. In normal game
contexts this returns success without filling a string, skipping the existing
fallback `0x4EF92C` that reads the current team's native name field at +4.
Thus merely changing binding spelling, font, opacity or position does not fix it.
Earlier documentation describing ABL slots as null providers is superseded by
this original-input analysis.

The gate can return zero when `0x5CCADC` returns 1, global mode 4 has +CC equal
1, or modes 7/8 have +D0 equal 2. These are game-context conditions, not established
scorebug-IFF settings. The +2C selector used by `0x5CCADC` is initialized to 2 at
`0x5CC8C0`, reset to 0 at `0x5CC8F8`, and initialized to 1 at `0x5CE2E8`.
No scorebug resource read occurs at those write sites. This does not establish
that changing game context would be safe or appropriate; none is changed.

Shared UI has other genuine TEAMNAME providers:

| Owner namespace | Function | Selector | Context |
|---|---|---|---|
| PLAYERCARD | 0x897C4 | 8 | Selected player and related team |
| PLAYER_PROGRESSION | 0x897C4 | 8 | Same player selection context |
| TEAMCARD | 0x8D10C | 15 | Selected team-card table |

The first two entries use descriptor `0xA0CE30`; TEAMCARD uses `0xA0CFB8`.
Player case `0x8A1E8` reads a related team pointer, while team case `0x8EC18`
uses a selected team from `0x1283E220`. Those callbacks require their controller
context. A copied TEAMNAME field/style does not connect them to the normal HUD.

The font pipe-tag scanner at `0x128DE0` checks 122 entries of stride 0x2C at
`0x12520458`. These are controller icons and UI symbols, including status/rank
icons; none is a current home/away roster-name lookup. Rank icons are not a live
poll-ranking provider. News placeholders such as [TEAMNAME] are not established
as generic font-renderer variables. This narrows known routes; it does not claim
that every unknown resource/engine mechanism has been exhaustively proven absent.

Uniform banks supply the existing dynamic logo texture. The owner explicitly
excludes using that route for names. No uniform bank, logo atlas, or roster name
is modified; no per-matchup baked-name workaround is supplied.

## Pose storage and authored placement

The protected v11 main scene declares 15 bones while retaining the original
13-matrix pose extent followed by strings. The new `scorebug_pose.inspect_contract`
rejects the invalid affine storage. This is concrete structural corruption, not
proof of the exact reported crash instruction or its sole cause.

The candidate retains stock main 13, comparison 6, meter 21 and sixth-topbar 6
bones and pose arrays. Branding reuses an existing dummy marker. New text tables
and property tables remain 16-byte aligned. Source marker hashes/parent ordering
and pose extents are checked; no skeleton extension is used.

Native text loading at `0x6AEF0..0x6AF48` consumes an instance pose. Missing owners
or markers fall back to identity, explaining why apparently valid authored text
can land at the origin. Composition `0x7F8D08` uses bone +10 translations and
parent links. Update `0x829E18` can skip normal updates under mask 0x10; that
freeze mask is not used. Candidate text owners use mask 0x4 to bypass the observed
visibility early-out while retaining pose calculation.

Candidate owner X/Y scale is 0.45, with inverse-compensated marker positions.
Native font setup copies the transform at `0x9BEE8..0x9BF08`, flips its Y basis,
and passes the matrix through font state +70 to the glyph path (`0x124C40..78`).
This is static path evidence, not a gameplay size guarantee. Marker pen positions
are compensated for actual FONT cap bounds, rather than treating the pen as the
ink center. Relevant raw H cap spans are 15 (Stratum2 12), 18 (18 26),
22 (22 32), 34 (25), and 53 (40).

The primary ink center is Y -191.5. Score pen Y is -174.175, clock/period
-180.7, team-name reservation -171.7, and branding -185.2. Names remain gated;
reserving a position does not enable their provider.

The meter's native side offsets remain -185/-337, with Y -153. Authored instance
X scale is 206/152, translation is `-11 - scale*(-185+80)`, local center 80,
width `100/scale`, and Y bounds [-40.5,-38.5]. Predicted final spans are
home [-61,39], away [-267,-167], Y [-193.5,-191.5], inside their name cells.
These predictions require native validation. Activation, runtime colors and all
19 segment draws remain native. The floating sixth-man header is disabled.

## Literal and popup formatting

The static brand reuses `gameclock_left`, an existing default-draw slot, and an
existing dummy bone. The main dispatcher does not test that provider's return
value before normal drawing. Null custom draw routes through `0x4F5B3C` to
`0x49CE24 -> 0x9D048`; style flag 0x10 selects the literal at `0x9D078..98`.
The English literal is isolated and one line. No matchup-context callback is added.

Comparison localization ID `0x6BF728B5` originally supplies uppercase
`{0}: {1}`. The candidate retains only the encoded {1} argument for each side.
Caption ID `0x4EF0F3F7` retains its uppercase directive and encoded {0} argument,
removing yellow markup. The bounded helper rejects unexpected source bytes,
aliased/interior-overlapping strings and repeated/missing arguments. Entry IDs,
string locations and unrelated bytes remain fixed before isolated literal growth.
The strict literal-extension validator is not loosened.

These are shared localization templates: observed original references associate
them with comparison providers, but all native uses/formatting are not runtime
certified. Free-throw presentation still follows the native provider's format;
this does not invent a new makes/attempts callback. Original event triggers and
queues remain unchanged, including the main HUD event lifetime heartbeat.

## Validation and use

The private candidate changes four vanilla-based SCNE records and one English
resource. Authored visual data is reused independently of failed executable,
skeleton and text experiments. Other records preserve their original bytes;
extra inferred spans are classified as exact retained source headers or bounded
alignment, not falsely claimed as equal record lengths. Eight main quad-facing
checks pass. English has a single uncompressed block with equal stored/logical
lengths, preserving the prior compact-table loading contract.

The editor's source-bound preflight accepts exactly gamedata.iff and english.iff
without changing candidate bytes. No EBOOT, uniform override, full JB build or
emulator run is included. The final test counts and commands are in TEST_REPORT.

For a manual test use the original vanilla EBOOT and the candidate's two complete
IFF overrides, replacing prior scorebug overrides. An already patched executable
is not corrected by installing IFFs. Do not deploy v10/v11/v12 executables as
verified repairs. Runtime evidence is required before calling the current visual
candidate ready. Automatic roster names and permanent counters remain open.

## Follow-up: markup, exact colors and shader selectors

The owner requires names before any candidate packaging and explicitly keeps
roster colors exact. No candidate ZIP or replacement executable is produced.

The separate font-markup callback registry at `0x12A9B8` has two observed direct
registration call sites: `0x12A0F4` and `0x12AFF4`. The style initializer installs
LINK, U, /U, B, /B and C:COL through `0x12A824`; icon handlers use `0x12A754`.
This establishes styling/icon callbacks, not current-team text substitution.

An alternate roster-generated name atlas selected by the live team color was
investigated, not installed. The source's 443 team rows have 318 distinct primary
RGB values and 52 duplicate-color groups. Identical colors cannot select different
names in a color-only shader. Encoding unique keys into RGB would violate the
owner's exact-color requirement, so no roster colors were changed.

Native color getter `0x77F38` reads runtime +1A8/+1A9/+1AA through
`0x763DD8`, `0x763DEC` and `0x76390C`, then supplies opaque alpha. The root roster
team pointer resolves to logical row +30, mapping these bytes to logical +1D8,
palette slot 14. The scorebug's `0x4EEC48` updates DiffuseColor; this is RGB data,
not a separate row identifier. The main shader's second material uniform has
semantic 0xEB42E56E and authored (1,1,0,0); its precise role is not asserted.

A bounded material-declaration scan parsed 286 SCNE headers, 289 shader entries
and 142 distinct uniform semantics across vanilla gamedata, gamedataextra,
global and legacy, with no parse errors. None of the checked conventional
TeamID/TeamIndex/SchoolID/PaletteIndex spellings matched a declared semantic.
Negative guessed-name matches are not proof of absence under other names.

The embedded main scorebug Cg revision-6 programs are now parsed directly:
vertex profile 7003 has eight parameters and 176 bytes of microcode; fragment
profile 7004 has three parameters and 48 bytes of microcode. Reflected vertex
inputs are position, base texture coordinates, vertex color and blend indices.
Outputs are position, UV and color, with one internal constant. The fragment
inputs are UV and color. The 11 vertex instructions read the corresponding
attributes, material constants C465/C466, internal C467, indexed transform rows
C40..42, and projection rows C0..3. No usable roster identifier is established.
Register-field interpretation follows the open-source
[RPCS3 vertex-program definitions](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/RSX/Program/RSXVertexProgram.h);
no emulator was launched.

Scanning bounded revision-6 Cg headers in those four banks parsed 816 serialized
program instances without errors. No reflected parameter name or semantic
contained team, school or palette. This includes repeated/shared program data,
not 816 unique shaders. Reflection does not describe every unreferenced built-in
register or prove that every possible custom renderer mechanism is absent.
No shader or unknown register was patched on speculation.

The remaining blocker is an established IFF-controlled bridge from current team
to a name/unique selector in normal gameplay. The known city/ABL text bridge is
native-gated; card controllers have separate state; markup and the audited shader
path do not provide a substitute. A working original-executable IFF example or
new native data-binding evidence could reopen this investigation. The other
developer's screenshot of an MRKS score_bug is not that evidence by itself:
the supplied vanilla/V5 resources do not establish that main-HUD record. The
actual differing resource would be needed to investigate that specific lead.
The goal is unfinished; no compliant automatic-name feature has been delivered.

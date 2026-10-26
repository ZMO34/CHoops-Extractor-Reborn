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
These predictions require native validation. Activation and all 19 segment
draws remain native; the later meter recolor below replaces only RGB curves. The floating sixth-man header is disabled.

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
to a name/unique selector in normal gameplay. The known main city/ABL text bridge
is native-gated; card controllers have separate state; markup and the audited
shader path do not provide a substitute. No compliant automatic-name feature
has been delivered; the candidate remains unpackaged.

## Streetdata MRKS discovery (supersedes the missing-source lead)

The owner identified vanilla streetdata.iff. Its score_bug MRKS record
(case-sensitive identity 0x42265DEF) decompresses to 16,860 bytes and embeds SCNE
at +0xAE0. Fifteen 176-byte text styles include home_city, away_city, home_rank
and away_rank. The SCNE itself has zero text records: these styles belong to the
MRKS wrapper. Native lookup 0x9B2D0 compares uppercase binding CRC at style +0xA0;
+A4 holds the case-sensitive CRC. Merely searching text strings missed this.

The alternate initializer 0x71D1F8 loads MRKS or falls back to SCNE. Its resource
selector 0x718BDC requests scorebug_xenon, scorebug or blackjack_score_bug by
context; a direct request for streetdata's score_bug identity is not established.
Its 24-row provider registry at 0x1267CA00 includes home_city -> 0x71BC94 and
away_city -> 0x71BBD4. Both can reach formatter 0x719038, which populates a name
from current-team +4 without the normal main-HUD suppression helper. The rank
styles are not entries in this registry; live rankings are unproven.

Normal contexts delegate initialization to 0x4F2818 and update to 0x4F313C.
Global-state +0x1AC is one alternate-path condition but also selects the blackjack
resource and is read outside the HUD. It is not established as a cosmetic or
IFF-controlled selector. No flags, resources or executable bytes were changed.
These findings are read-only disassembly evidence pending Ghidra cross-checks;
activation of this existing name provider in normal college gameplay is unresolved.

## Ghidra cross-check and bounded MRKS reader

The restored Ghidra project now has completed PS3 setup, full auto-analysis and
syscall identification. Descriptor-based TOC contexts and database-only inlining
of exact TOC veneers improve the native pseudocode. The alternate resource
selector and formatter conclusions above agree with inspected instruction flow;
repeated-call inlining and some switch reconstruction remain incomplete. The
normal initializer still loads SCNE directly; renaming a MRKS binding does not
change that controller into the alternate MRKS provider registry.

`choops_py.research.scorebug_mrks.inspect_styles` now reads the observed wrapper
without writing it. It bounds the style count/table and embedded scene location,
reports font, flags, color, matrix, model/bone hashes, literal ID, both binding
CRCs and opaque words. Name matching is an explicit small dictionary; unknown
hashes remain unknown, and lower-case CRC mismatches are reported. This reader
locates embedded SCNE but does not certify its complete structure or activation.

Read-only corpus: streetdata score_bug has 15 styles; gamedataextra scorebug_xenon
has nine; global nav_itemselected and nav_item have two each. The global records
contain repeated lookup hashes, so the reader retains both rows and reports
first-match indices rather than treating valid repeated styles as corruption.
The native lookup walks from the beginning. None of those duplicate global
bindings is established as a home/away roster provider.

A bounded string/uppercase-CRC match against the original decoded executable
finds 13 of streetdata's 15 style names. home_rank and away_rank match the
explicit conventional spellings but have no matching executable string in that
scan, and are absent from the observed alternate provider registry. The two
additional scorebug_xenon hashes also have no matching executable string there.
This is negative evidence for those specific names, not proof of no rank code.

No name activation bridge was installed or demonstrated. Existing IFF candidate
geometry, native popup triggers and exact roster colors remain as recorded;
packaging stays held until automatic names work. Next investigate controller
selection/data-binding consumers, not another guessed binding rename.

## Controller consumers and literal/format path audit

Aligned pointer-reference scans of the decoded original find two UTF-16-BE
home_city strings: 0x124B22B8 is referenced by main TOC slot 0xA5DD54, and
0x124D7BC8 by alternate table row 0x1267CA00. away_city similarly has main
0xA5DD60 and alternate 0x1267CA28 consumers. Main ABL strings reference
0xA5DDB0/0xA5DDB4. No additional controller was identified by these particular
string-pointer references. This does not exclude computed hashes or unknown
spellings; it does close the proposed shared-name alias route for these tables.

The main draw loop at 0x4F4858..0x4F490C calls the native descriptor in each of
14 fixed rows before looking up its SCNE style. Style naming selects the row's
presentation, not a new provider. Alternate initialization, update and shutdown
all apply context selection; normal shutdown 0x71BD10 delegates to 0x4EE160.
MRKS presence or a copied style does not establish alternate lifecycle activation.

Ghidra exports plus instruction checks trace literal rendering through 0x9D048:
it copies the supplied string, replaces it with the style +A8 value when flag
0x10 is set, and passes it to 0x9C1EC/0x9C360. Flags 1/2 apply the existing case
formatting with that one supplied string; they do not supply current-team data.
String copy 0x1E0EA4 preserves odd tagged IDs or clones even node pointers.
Formatter construction 0x1E2A8C uses the caller-provided argument count/table;
callback descriptors there are native arguments, not SCNE/localization bindings.
No current-home/away callback was established through this literal path. Branding
uses the fixed literal mechanism; changing its spelling cannot make names dynamic.

The name formatter's 0x1E1610 -> 0x1E2634 path wraps the supplied team +4 text
pointer with a measured length (type-4 string node). Do not confuse this pointer
with a localization ID or treat an on-disk literal ID as an active-team pointer.

The HUD support helpers examined here add no new persistent counter provider:
0x4EE1A4 sets the main active flag, 0x4EDF60 clears a HUD state field, 0x4F24F0
updates existing comparison visibility/placement, and 0x4F215C adjusts existing
transforms for clock presentation. Their decompiled forms retain the documented
TOC/switch limitations; no speculative resource flag was written.

## Current completion/impasse audit

The internal candidate still contains only gamedata.iff and english.iff plus its
validation/preflight records. Preflight passes, but gameplay_verified is false
and native_name_gates_unresolved is true. No replacement EBOOT, uniform override
or package exists in this candidate. Original EBOOT and decoded analysis ELF
remain unchanged against their local recorded hashes.

The required automatic roster names are not achieved. Existing main providers
suppress them in normal contexts; alternate providers require an unestablished
lifecycle/selection bridge. The audited shared-card, literal/format, inline-tag
and material/shader paths have not supplied that bridge. Color-key encoding
violates the owner's exact-color requirement and is excluded, as are uniform
routing and executable edits. These constraints remain in force.

Geometry/backing/shading, native score/clock/period styles, one-line branding,
comparison layout and sixth-man placement are authored with static preservation
checks, but have no native appearance/transition verification. Permanent
foul/bonus/timeout rows and conditional rankings have no established continuously
updated IFF binding. Neither synthetic tests nor the Ghidra database prove those
features complete. The full objective is not achieved and must not be relabeled
as a completed visual-only scorebug.

The current investigation is at an impasse on the required name bridge. A working
original-executable IFF example that renders current-team names, or new native
resource/controller evidence showing such a bridge, would provide a concrete
next step. The streetdata example has now been inspected; its styles alone do
not provide that evidence. Candidate packaging remains held.

## Resumed selector provenance and sixth-man implementation

Ghidra references identify two direct observed writes to match-state +0x138:
0x2B0304 clears it during 0x2B02B8 teardown, and 0x2B0788 sets it during
0x2B06B4 initialization. The setter also changes +D0/+D8, +19C, +1A0, +1A4,
+1A8, +21C/+220/+224 and selects records from native table 0x1256CEC0.
Those records include side/player-count data and coordinate arrays. Native
0x5D63A0 calls it and then 0x5D5DEC; 0x65C9C0 also sets the other alternate
predicate through 0x2B177C. These are coupled match-mode setup paths, not an
established cosmetic IFF selector. No mode flag was changed.

The normal name gate's +2C source has observed writes in 0x5CC898 (2),
0x5CC8F0 (0) and 0x5CE15C (1). The last also resets and constructs per-team
state. Its exact phase meaning is not asserted here. This trace does not prove
an IFF-owned switch or authorize modifying saves/gameplay to force names.

The sixth-man strip now has a concrete IFF-only reskin. All 19 material
DiffuseColor animation references resolve uniquely to the 19 animation IDs.
Native 0x82E3B0 selects four channels from flags 0x00F0088F: RGB use scalar
curves and alpha is constant. 0x82E194 samples N cubic intervals with N+1 time
boundaries. Every observed RGB interval has zero cubic/quadratic/linear terms;
its fourth coefficient is the held value. This is a color track, not a bone
translation. The implementation refuses nonconstant curves, looped/unknown
layouts, nonfinite values, mismatched bindings or different alpha.

`choops_py.modding.scorebug_meter.reskin_meter` appends aligned monochrome
RGB curves using the union of the original channel boundaries and the clamped
maximum native RGB value at each interval. This preserves the visible peak
brightness/fill/pulse steps while replacing green/red color changes with white
and dark states. Alpha, output buffers, shader/material bindings, activation,
thresholds and native timing arguments are retained. Only the 19 curve-array
pointers change in the original header extent; every other original byte and
the complete vertex/index part remain exact. The real candidate adds 6,048
header bytes before archive recompression. No new callbacks or executable edits.

Ghidra 0x76A714 resets poses, samples these color animations, applies side offsets
and composes with the instance through 0x829D40/0x7F8D08. The candidate's 21 bone
rest transforms are identity and its 19 animations bind only color. The authored
vertex/owner transform plus native offsets gives home X about [-61,39], away
[-267,-167], Y [-193.5,-191.5]; color changes cannot move those vertices. This
strengthens the static placement evidence, but is not GPU/gameplay verification.

The private vanilla-based candidate was regenerated and source-bound editor
preflight accepts its exact two IFF bytes. No full JB or package was created.
Automatic names remain mandatory and unfinished; permanent counters/rank routes
remain unresolved. The resumed goal remains active with this concrete meter
implementation progress; the earlier impasse audit is not a completion claim.

## Regular 5-on-5 resource routing confirmation

The normal HUD path at 0x71D998 delegates to 0x4F2818. Its main resource getter
0x4EE710 calls 0x841810 with namespace 0x3DF16510, record 0x3E691786 and type
0xE26C9B5D. Those equal CRC32("GAMEDATA"), CRC32("scorebug_bottombar") and
CRC32("SCNE"); the original gamedata.iff contains that exact record and type.
This is direct static evidence for the traced regular-game route.

Streetdata's score_bug is a different identity (0x42265DEF), type MRKS. The
alternate selector 0x718BDC requests scorebug_xenon, scorebug or
blackjack_score_bug, not that exact streetdata name. No normal 5-on-5 loader
request for streetdata's MRKS has been established. Its name/rank styles are
reference material, not proof that ordinary gameplay consumes them. The current
candidate edits gamedata's real main scorebug; no streetdata override is included.
This is original-executable analysis, not an emulator capture of live loading.

## LAYT and frontend-binding investigation

Read-only inventory of frontend, frontend_sync, global, gamedata and gamedataextra
finds 135 LAYT records. Relevant examples include teamcompare, offball_play,
on_court_players, heat_check, freethrow_meter and team_matchup. Scene nodes refer
to SCNE/MRKS artwork; template nodes refer to nested LAYT resources. No fields
were patched on the basis of guessed layout flags.

The native initializer 0x12E4F8 copies binding pointers from its caller's second
argument into the layout root. Nested-template calls reuse that same argument.
Consequently, merely nesting teamcompare or teamcard artwork in another layout
does not select that screen's native binding table. A layout transplant has not
established an always-visible HUD with its own roster callbacks.

A useful additional provider does exist: teamcompare's text table at 0x12510FC4
uses descriptor 0xA0CFD0 -> 0x8FBB8. Selectors 6/7 correspond to text_teamaway
(0xA3583DDB) and text_teamhome (0x74D193DA). Their branch targets 0x8FF50/0x8FFCC
read the current away/home team through 0x57F064/0x57F050, then wrap team +0 text.
These fields are absent from the original teamcompare_backdrop SCNE's text rows.
They are real frontend name providers, but not additions to the main HUD's fixed
14-row registry, and no normal-HUD activation bridge is installed.

Initializer 0x12E4F8 can also resolve a binding-record +8 ID through 0x12C730.
Registrar 0x12BE84 hashes a name and stores its descriptor in a global pair table.
The observed direct registration calls at 0xC2E74 register four callbacks:
Skin Scene Callback (0xC333C), Skin Scene Callback - Pop When Done (0xC2DB8),
Registration Text Callback (0xC3174), and Dismiss Text Callback (0xC3258).
The skin callbacks control scene visibility; none of these inspected handlers
supplies current-team names. Direct-call enumeration does not prove there are
no indirect registrations. Scanned type-0 scene nodes in the 135 LAYTs have zero
serialized lists at +3C/+40/+44/+48; a safe authored name-binding example has not
been found. Unknown layout/callback fields remain read-only.

Ghidra exports for this work were checked against descriptor entry boundaries.
An address-like descriptor field that landed inside 0x5DFC28's body was rejected;
the temporary inferred function was removed from the analysis database. The local
export helper now refuses to create an undefined entry unless OPD-backed. Raw
address-looking words are not sufficient evidence of a callable function.

The next unresolved distinction is whether any original live-game UI consumer
can legally receive a roster-capable binding table through data. These frontend
findings do not yet solve the scorebug's mandatory team-name requirement.

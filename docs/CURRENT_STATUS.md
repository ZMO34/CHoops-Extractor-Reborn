# Scorebug popup runtime inspection

A read-only decoded-ELF inspector validates the observed 83-type popup dispatch
table, 119 provider slots, four queues and two priority levels. Native queue
updates use a draw-pass heartbeat; priority is independent of provider count.
Localization templates use mixed tokens, so literal-only insertion is not a
validated dynamic formatter. No executable writes or new in-game layout claims.
See SCOREBUG_RESEARCH.md.

# Adaptive pose/root translation follow-up

NBA11's variable keyframe timeline is now established and converted to fixed CH
samples, with original keys preserved exactly, interpolated/quantized inserted
poses and optional6/8-byte root tracks. All9,574 inspected distinct timelines
match rate/time-scale/duration. Broad channel checks pass13,301 distinct streams
across CH/NBA11,589,196 frames;32 donor pose/33 root resampling checks pass.

All112 stock shot styles are cataloged through224 motion references. The additive
native table/registration change, complete event/auxiliary conversions, donor bind
mapping, gameplay consumers and modern-control defaults remain unfinished. No new
shot choice is exposed and no original is replaced. No installable donor bank or
EBOOT patch is produced. See ANIMATION_GAMEPLAY_PORT.md; no RPCS3/testing JB.

# Packed-pose conversion and additive shot research

Implemented lossless translation of the observed CH2K8/NBA11 packed quaternion
selector convention, preserving all remaining components, translations, padding
and frame order. Private checks on32 streams per game preserve decoded channels
and reverse byte identity. This is a packed-channel converter; no playable donor
clip, new jump-shot option, full animation system or control preset is installed.

Native research locates the112-entry jump-shot playback table, its40-byte stride,
paired motion pointers, shared readers and UI option maximum. New choices must
append records and extend registration, retaining existing IDs. Simply enabling
ID112 would read an adjacent unrelated structure. No table/EBOOT patch is applied.
Skeleton/contact/event/auxiliary-track mappings, allocation and complete playback
semantics remain unresolved. See ANIMATION_GAMEPLAY_PORT.md. No RPCS3/testing JB.

# Executable-held animation inspection

Read-only indexing now covers the observed native full-body motion-header family
inside decoded CH2K8/NBA11 executables: 7,055/18,831 structurally mapped candidates
in supplied analysis copies. Ghidra confirms CH native pointer/group selection,
including fallback handling. Candidate metadata is not a decoded or complete clip
library. Added a bounded research CLI; no executable/animation writer.

Owner control target remains modern right-stick default, original controls in
preset A. Neither that change nor a donor gameplay-animation port is implemented.
Packed pose codecs, skeleton/contact retargeting, transition graphs and gameplay
consumers remain unresolved. No RPCS3, executable edits or testing JB. See
ANIMATION_GAMEPLAY_PORT.md for evidence, commands and remaining work.

# Animation investigation and pending-PR integration

Seven prior PR branches (#31–#37) are merged through PR #38, retaining source
changes and ancestry. Windows/Linux CI and clean exact-head portable checks pass.
The integration exposed one stale GUI button-label expectation, now corrected,
and adds Legacy wrapper regressions. No prior runtime caveat is promoted to a pass.

New supported work: 21 researched motion bank names/categories, corrected large
animation-bank inventory, native CH/NBA11 envelope and NBA11/14 collection
inspection, and local alias candidate/cycle reports. Ghidra traces native fixups,
reference handlers and controller polling in all three games. The old 2K14 count
was incomplete; corrected standard-IFF SingleMoCap count is 22,139.

Donor gameplay animations, smoothness improvements, new right-stick default and
original controls in preset A remain unimplemented. No guessed bank transplant
or global analog swap is enabled. See ANIMATION_GAMEPLAY_PORT.md for exact native
evidence and remaining dependencies. Original games are unchanged; no RPCS3/JB.

# Player-face research follow-up

Read-only PS3 analysis established the per-player dedicated likeness selector
(logical +0x8C low nibble; biased editor +0x9C), its seven original-player mappings,
paired albedo/normal banks, FRFG presets, shared high/bench heads and three stored
morph groups. Most stock players use seeded generation. Added a read-only inventory
command; no face writer, GUI editing, EBOOT patch or direct NBA cyberface port.
See [player-face evidence and limits](PLAYER_FACE_RESEARCH.md). All seven extracted
albedos round-trip DDS/GTF in memory. Later NBA donor extraction variants remain
explicit blockers; unknown face semantics are not invented.
# NBA 2K11 donor research

The supplied PS3 2K11 archive now opens read-only through observed NPD v3 SDAT
authentication; v4 behavior and SDAT writer blocking remain unchanged. Inventory:
6,974 entries, 1,040 resolved PNG names, 4,705 identifiable SingleMoCap records.
Selected texture/arena/floor/audio blocks decode; full animation/mesh transfers
and 2K11 roster editing remain unimplemented. See [donor ratings and evidence](NBA2K11_DONOR_ASSESSMENT.md).
Best near-term donors are adapted artwork/audio; newer AI/physics/blending are
not imported by copying assets. No RPCS3, EBOOT edits or real/testing JB.
# Unreleased — native scorebug text contract guards

Focused Ghidra analysis of the owner-authorized combined experiment confirms
16-byte text/property alignment is required by native vector loads. The bounded
scorebug text helper now rejects misaligned tables before editing them. It also
supports `max_width` in whole authored units (1–4096), preserving the integer
property type, enabling the native shrink-to-fit flag and retaining literal and
alignment bits when edits are combined. Missing/shared properties fail closed.

The earlier combined companion cloned misaligned property blocks and reused
score identities/markers for city labels. These are confirmed structural defects;
Python parsing alone did not establish native compatibility. Private experimental
repairs continue in PR #36. Source EBOOT/game inputs remain immutable; executable
patching is not added to the editor. Native custom stats callbacks must retain
text-tag parsing and timing; a global replacement with the plain renderer would
lose those effects. Runtime visual correctness is not certified.

# Unreleased — scorebug test05 visual corrections

User screenshots establish that native test04 still has no ordinary-game school
names, washed-out palette panels, dividers, overlapping sixth-man lettering and
clipped popup text. Test05 retains the enlarged body/logos/score/clock font sizes,
removes dividers, restores authored vertex RGB 0.1 instead of 0.72, and moves both
old text-mask meshes outside the HUD. Popup styles regain opacity and centered
white text; their anchors/backing now cover the same right-side section.

Only one native sixth-man label remains, using the existing null-callback ABL
slot and stock localization ID. The other ABL slot displays title-case native
College Hoops / Reborn. Duplicate topbar label loops and bitmap label are disabled.
The 19 live meter draws remain intact; their complete span grows from 85x4 to
125x5 world units. Both native team translations fit inside the existing header.

Read-only executable analysis shows the city-name provider deliberately leaves
ordinary-game names empty. Renaming the SCNE bindings did not enable them. The
owner explicitly declined an optional executable patch: **keep EBOOT read-only;
leave team names unresolved**. No name/logo texture hack or executable patch is
included. Previous claims of completed live team names are superseded.

Local test05 includes five gamedata SCNEs and the compact direct-read English IFF.
Source inputs remain unchanged. Runtime appearance/popups still need user testing;
static checks cannot certify in-game appearance. No emulator or new JB build.
Continues PR #32; documentation and asset-free profiles are maintained.

# Unreleased — native test04 startup-crash correction candidate

User crash logs show a startup asynchronous-IFF-loader access violation at
0x00845E14, reading 0x4D4C0002. The built English archive matches native test04;
branding token bytes appear in the failing thread. The build also contains many
other overrides, so a complete runtime exclusion of those inputs is not claimed.

The generic growth path unnecessarily retained the original English table and
appended a new complete table, expanding its decoded block from 1,847,762 to
3,695,588 bytes. Localization now requires a sole complete block at offset zero,
validates all existing entries, and writes one uncompressed table (1,847,812 bytes).
Equal stored/logical descriptor lengths select the native direct-read branch,
bypassing the compressed path implicated by the log. Other resource writers retain
their existing behavior. Local test04-crashfix ZIP keeps all five scene edits.

This is a targeted correction candidate, not a gameplay-certified root-cause fix:
the exact cause of corruption inside the compressed native load is not established.
User retesting is required. Do not use the superseded native test04 English IFF.
No emulator launch, executable write or new JB build. Continues PR #32.

# Unreleased — scorebug test04 native branding and live team names

Test04 connects home_city/away_city callbacks beside the logos and selects actual
Stratum2 25 styles for scores, period and clocks. Narrow gray separators replace
full-panel overlays; opaque popup/header backing is restored. College Hoops / Reborn
is now title-case **native text**, using the existing sixth-man label draw path and
a new isolated English localization ID. Font, RGB, alpha and shadow values match the
clock. The small left 6th Man label becomes matching native-glyph texture artwork.

Two IFFs are required: five SCNEs in gamedata.iff and one added tagged literal ID in
english.iff. All 257 other gamedata records, all 21,637 existing localization rows,
the opaque sentinel and old token pool remain intact. Branding shares the original
sixth-man scene's visibility; disabled-feature/mode states and popup transitions
still require user testing. No executable/font-bank/roster edit, emulator run or
test04 JB build. Local native test04 ZIP; code continues PR #32.

# Unreleased — scorebug test03 alignment refinement

Supersedes test02 artwork/layout: continuous rectangular backing, rectangular
panel borders, clipped palette rectangles without the stock vertex gradient,
larger square team logos and authored score text, narrower/lower body, native
Stratum2 right-hand lettering, and black sixth-man/message backing geometry.
Read-only executable research establishes separate home/away meter translations;
all 19 meter draws and live palette/logo bindings remain intact. Five gamedata
SCNEs change; 257 other records remain identical. User runtime testing is still
required for text transforms, popup event states and meter animation. No emulator,
executable modification or new JB build. Local test03 ZIP; code continues PR #32.

# Unreleased — scorebug test02 and authored HUD editor

Bounded experimental scene editing, sixth-man/text-anchor inventory and test02
asset evidence are in SCOREBUG_RESEARCH.md. Restores the prior team RGB multiplier,
rectifies team-logo UVs, attaches CHRB to a fixed left quad, adds fixed right-side
COLLEGE HOOPS/REBORN artwork and adjusts authored meter/message placement.
Runtime messages/timing and dynamic tournament labels are not newly implemented.
No executable edits, emulator runs or real/testing JB. Local user-test ZIP only;
no game assets in Git. Current public application release remains v1.19.
# Combined scorebug correction candidate

Owner-authorized private Ghidra follow-up identifies misaligned cloned native
text properties and reused score marker identities in the broken combined test.
A single combined candidate now uses aligned independent city markers, native
font width fit, original stats tag parsing and a conditional stats-only backing
hook instead of a permanent main-bar plane. Native event popup visibility remains
separate. Modern three-point and transfer experiments remain present.

Five edited scenes, 257 untouched records, two-archive preparation/preflight,
SELF round-trip and nine bounded wrapper paths pass. Source files are unchanged;
only one executable plus two IFFs/docs is packaged locally. No emulator or JB.
Appearance/PS3/gameplay compatibility are not certified. See EBOOT_EXPERIMENT_01;
PR #32 owns the separate public native-alignment/width-fit editor guards.

# Local executable experiment 01 — 2026-10-19

The owner authorized separate experimental copies for modern NCAA arc/corner
scoring, native scorebug names and removal of new-transfer sit-out assignment.
[Experiment evidence and limits](EBOOT_EXPERIMENT_01.md) records five private
variants, a companion scorebug package, preservation checks and manual test order.
Original executables/game inputs are unchanged. No executable patching is added
to the editor and no patch code, game assets or executable copies enter Git.
Static audits, 60,000 geometry samples, 30,000 transfer-mask cases and companion
two-archive preparation/preflight pass. Boot/gameplay/physical-PS3 compatibility,
new text-node/span acceptance and existing-save eligibility remain unverified.
No emulator, real/testing JB, merge or release. This narrow local authorization
supersedes the earlier refusal only for these prototypes.

Cleanup removes 1,502 generated fixture folders, 99 standalone synthetic IFFs,
three disposable caches and two clean review worktrees. Active regression sources
and user inputs/builds remain.
Historical release/test package deletion was blocked by automatic approval review
and remains pending specific owner approval; see experiment notes.

# Read-only executable modernization research — 2026-10-19

[Executable modernization candidates](EBOOT_MODERNIZATION_RESEARCH.md) ranks
native scorebug names, camera customization, broadcast presentation and rules
against actual executable evidence. Newly traced CameraMenu event handlers use
bounded 44-byte records; Game Rules initialization takes several mode-dependent
paths. Neither establishes a one-constant modern-rules or FOV patch. Replay,
indicator and autosave routes are distinguished from unproven runtime semantics.
The smallest known executable candidate is the native-name fallback investigated
in separate PR #32; the owner declined applying it, so names remain unresolved.
No production feature or EBOOT changed. No emulator or real/testing JB.
# Unreleased — editable garment meshes and modern-fit experiment

Models / Courts has source-aware uniform OBJ collection export, guarded reimport
and a conservative modern-fit preset. Actual source inventory covers 21 cloth
IFFs / 33 SCNE–Clth pairs: all five necklines and thin/regular/fat builds, plus
three shorts builds, including individual and aggregate container routes.
The preset shortens shorts by 20% and tightens the jersey torso by up to 7%.
Source assets stay immutable. Rest XYZ is updated in SCNE and matching Clth;
topology, UVs and all other attributes/unknown data are preserved.

This is an experimental rest-shape workflow. Native packed cloth constraints,
body collision and normal/tangent regeneration remain unresolved; static output
does not certify animation/fit. No NBA cloth writer or new topology. See
[uniform mesh evidence and editing instructions](UNIFORM_MESH_EDITING.md).

# v1.19 rebuild compatibility follow-up

Unreleased Legacy save support recognizes the observed 2K8 `USERDATA` profile and
exposes its embedded roster through the roster editor. The copy writer is fixed-
extent and verifies every byte outside that region remains unchanged. Legacy-mode
state after the embedded roster is still unmapped and read-only; a single save
cannot establish the meaning of those fields.
PR #30's merged override changes were reviewed against all v1.16-v1.19 release
tags; their histories and features remain present. The isolated merge passes
portable checks (602 passed, 10 skipped, 2 deselected). Nine additional synthetic
cases verify named/numeric folder DDS priority, legacy spelling resolution,
complete IFF discovery, invalid index/root rejection and append/repack raw BIN
preservation. See [the compatibility review](PR30_COMPATIBILITY_REVIEW.md).
No runtime claim or additional merged feature PR is implied by this review.

Folder DDS imports now consistently support a flat image targeting an existing
cubemap in both legacy and Python-manifest paths (standard IFF and CDF). This
updates +X and preserves the other five base faces; complete cubes still replace
all six faces. Direct texture editing remains strict. Reports identify +X imports.
No cube flag is removed and no 2D image is duplicated across the other faces.

IFF failures now identify archive, input role and magic, with corrective GUI
advice. Invalid containers remain rejected; opaque bytes are not guessed/repaired.
The legacy Reborn Overrides V5.5 layout is recognized through direct numeric
source-TOC folders, including nested TXTR/DDS artwork and complete IFF replacements.
Its `icon_tatoo` record spelling maps to the source's `icon_tattoo` record. Raw
`.bin` replacements such as `cribmusic.bin` retain their bytes without IFF parsing.
The supplied frontend_sync/legalpage ZIP passes preparation and build preflight
against original 2K8. The locally supplied halftime complete HDR cube preserves
all supplied artwork, scene headers and image capacity. Original inputs unchanged.
The exact supplied ZIP also passes preparation/preflight in an isolated v1.16
checkout. Its generic screenshot failure is not reproduced; the offending input
or differing source/workspace is still needed to establish that specific cause.
No RPCS3 or real/testing JB. Integrates research PR #28; no animation port added.

# v1.18 foundation (retained context)

This release integrates the NBA support/split-header repair from PR #25 and the
key/center-circle court guide from PR #26, then refreshes the public documentation.
The [support matrix](FEATURE_MATRIX.md) is the concise contract. Earlier status
entries are preserved in [history](history/STATUS_THROUGH_V117.md).

## Delivered

- Automatic observed College Hoops/NBA archive layouts; read-only NBA 2K14 SDAT
  banks, authenticated reads, extended descriptors and supported ZLIB IFF blocks.
- Separate detected NBA 2K9/2K14 roster side editors with confirmed fields,
  preserved wrappers/unknown bits, undo/redo and guarded text writes. College Hoops
  remains a distinct model with broader ratings/CSV/comparison tools.
- Split-bank archive header/TOC reading and append/repack preservation. Missing or
  truncated banks retain exact expected/actual details. GUI override/build errors
  include persistent Problem / Suggested fix / Details guidance.
- Independent thin court reference toggles: border, 3-point and key/center circle.
  Authored stock geometry is raised one game unit; actual floor rendering is untouched.
- Documentation index, practical workflows, troubleshooting, per-game matrix,
  testing map and release procedure. Historical status/results separated; stale
  dependency snapshot/unpublished beta draft removed; wrapper test consolidated.

## Still unresolved

NBA 2K14 authenticated JB writing/signature generation, complete NBA ratings and
text growth, all College Hoops unknown bytes, universal engine text ceilings,
complete runtime shader/palette modes, newer cloth/jersey artwork binding and
validated cross-game animation porting. College Hoops has no independent secondary
position field established; do not confuse NBA evidence with that schema.
No new alternate assets or removed D1 actions are added.

## Verification and maintenance

See [TEST_REPORT.md](TEST_REPORT.md) and the release PR for exact-head results.
Only synthetic fixtures, Qt/CLI/frozen smoke and read-only research are used.
RPCS3/gameplay NOT RUN; real/testing JB NOT BUILT; EBOOT NOT EDITED.
Both Codex instances must maintain current docs and the generated handoff on each
update. Document evidence and unknowns; never replace uncertainty with a label.

## Research follow-up — modern features

[Backport feasibility](MODERN_FEATURE_BACKPORTS.md) ranks practical artwork/roster
updates, 2K9 animation conversion, broadcast bindings and indirect companion ideas.
No backport is implemented; modern runtime features remain distinct from assets.

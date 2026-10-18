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

# v1.19 rebuild compatibility follow-up

Folder DDS imports now consistently support a flat image targeting an existing
cubemap in both legacy and Python-manifest paths (standard IFF and CDF). This
updates +X and preserves the other five base faces; complete cubes still replace
all six faces. Direct texture editing remains strict. Reports identify +X imports.
No cube flag is removed and no 2D image is duplicated across the other faces.

IFF failures now identify archive, input role and magic, with corrective GUI
advice. Invalid containers remain rejected; opaque bytes are not guessed/repaired.
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

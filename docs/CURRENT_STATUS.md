# Unreleased — scorebug test04 live names and native font styles

Test04 connects the existing ABL text slots to registered home_city/away_city
callbacks while retaining their original bone bindings. Scores, period and clocks
select the actual Stratum2 25 style instead of an authored basis scale that runtime
rebuilds. Full-panel frames become narrow gray separators, with an opaque popup
backing in the main bottom scene. Branding reads College Hoops / Reborn in title
case using matching FONT glyphs, RGB and shadow artwork. It remains texture-based:
identical live-font shader/filtering and all event-state positions are not certified.
No executable/localization/font-bank edit, emulator run or test04 JB build. Local
asset ZIP and existing PR #32; source/public application release stays unchanged.

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

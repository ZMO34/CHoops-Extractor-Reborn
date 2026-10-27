# IFF-only scorebug: partial visual test

The owner goal calls for a usable test folder even when dynamic features remain
blocked. The local `output/scorebug-test/` is that **experimental, partial visual
test**, replacing the earlier indefinite hold on testing deliverables. It is not
a completed automatic-name scorebug or a claim of successful gameplay rendering.
Game-derived files and the offline preview remain local, outside Git.

## Included changes

Only two complete archives are supplied: `overrides/gamedata.iff` and
`overrides/english.iff`. Three vanilla SCNEs change:

| Scene | Change |
| --- | --- |
| scorebug_bottombar | Black backing, pale score cells, thin separators, centered square logo quads, mild 0.95–1.0 team-panel gradient, native text styles/markers and one-line branding |
| 6th_man_meter | Inside-panel placement and monochrome RGB curves, retaining native 19-segment activation, alpha and pulse/fill timing |
| 6th_topbar | Hide the former floating meter header/artwork |

English adds only the isolated College Hoops Reborn literal. All 21,637 original
table entries, including the opaque sentinel, retain their mapping/token storage.
The stock scorebug_topbar comparison scene and its localization templates are
retained. This removes the earlier candidate's unnecessary comparison edits.

The layout retains main 13, meter 21 and sixth-topbar 6 bones/pose storage. Logo
quads are 32×32 with full 0–1 UVs and neutral tint. Existing logo resource routing
remains dynamic; uniform assets are not edited. Original roster RGB values are
untouched; the allowed subtle gradient shades the rendered panels only.

No EBOOT, Director, overlaycache, roster or uniform replacement is included.
Held name/injury/Director probes are excluded. Original event dispatch, queues
and priorities remain native. Their transitions and placement still need testing.

## Apply manually

1. Start CHoops Studio with `.\.venv\Scripts\python.exe -m choops_py.studio`.
2. Open the vanilla JB source matching `source_preconditions.json`. The supplied
   complete archives were built from vanilla, not by editing an old test build.
3. In Explorer, choose **Select overrides folder**, then select
   `output/scorebug-test/overrides`. Preview Selected overrides if desired.
4. Use the normal manual builder to produce your copied Reborn installation.
   When combining with your usual Reborn overrides, these two complete archive
   files supersede earlier replacements of the same archives. Resolve any other
   edits to gamedata/English before building; do not overwrite your only originals.
5. Retain the original executable. If the test installation still contains an old
   experimental EBOOT, restore your original copy yourself before testing. IFF
   replacements cannot undo executable changes. Protected V11/build folders stay
   preserved as historical evidence.

The folder also includes a source-bound `overrides.json` staging manifest and
`import_options.json` permitting required archive growth. CLI users can inspect
it with `list-overrides` / `validate-mod`. Raw IFF files belong in overrides;
copying them next to the numbered USRDIR archive banks does not apply the mod.

`manifest.json` records sizes, SHA-256s, changed record identities, preservation
checks, feature status and verification limits. No CDF companion is required.
`offline-preview.png` uses decoded SCNE geometry and native FONT glyphs with
authored width fitting. Scores/time are samples; logo slots and meter footprints
are placeholders. It does not simulate GPU projection, live palette injection,
native kerning, logo artwork selection or message timing.

## Owner gameplay checklist

- Reach a normal 5-on-5 game with the original executable; confirm black backing,
  separators, pale score cells and one-line branding appear.
- Check 0, two-digit and three-digit scores, period/OT, running game clock and
  shot clock for centered placement, size, clipping and origin-screen text.
- Try contrasting/light/dark teams. Check panel brightness, exact roster input
  colors and logo proportions/color. Existing transparent padding inside each
  logo image may affect apparent size even with square quads.
- Check each side's sixth-man activation, rising/falling fill, peak pulse and
  deactivation. It should stay within the team panel without the floating label.
- Trigger native scoring/stat, foul/bonus, free-throw, timeout and injury messages;
  check placement, text, disappearance and return to the base bug. No custom
  callback or permanent popup has been installed.
- Confirm no crash at startup, lineup, warmups, normal play, halftime or overtime.
  Report a screenshot and which two archive checksums were staged.

Names will remain blank in ordinary contexts: that is an explicitly unresolved
feature, not an installation failure. Permanent foul/bonus/timeout rows, rankings,
contextual tournament branding and an accurate possession arrow are not supplied.
No static or guessed possession side is drawn.

## Remaining native dependency

The newly checked comparison route reads real school names, but initialization
explicitly clears its enable flag, and activation plus drawing test that flag.
No checked IFF command reenables it. A startup queue request alone is insufficient.
Generic long-duration name overlays also conflict with native waits/slot reuse.
Neither route is promoted. See [executable route evidence](SCOREBUG_EXECUTABLE_ROUTES.md)
and [the broader audit](SCOREBUG_IFF_ONLY_AUDIT.md).

The next useful step is owner testing of this isolated visual foundation. Further
name work needs new activation/binding evidence rather than repeating the same
negative searches. This does not prove every unknown data route impossible.

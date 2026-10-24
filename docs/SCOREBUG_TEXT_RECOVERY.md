V8 is historical. The subsequent native name/footer callbacks, smaller installed
text scales and corrected comparison provider order are documented in
[SCOREBUG_NATIVE_V10.md](SCOREBUG_NATIVE_V10.md). Neither version is gameplay-certified.

# Screenshot-driven text recovery and broadcast layout

The user's 2026-10-24 gameplay screenshot shows logos and geometry but no score,
clock, names or branding. It contradicts any assumption that v5's structural and
synthetic checks established working text. V5 is superseded. The new private v8
set is a recovery candidate; in-game text recovery remains unconfirmed.

The supplied references call for shaded team panels, pale score cells with dark
figures, compact dark clock/context cells, and a comparison strip directly above
the two team panels. The additional free-throw reference shows an away value,
centered category and home value in that strip. These guide actual asset edits;
example text in an offline study is not gameplay evidence or baked game text.

## Shared text dependency restored

All twelve main-bar v5 text records name `Score_bug` as their model owner. The
previous geometry suppression collapsed every index in that model, producing
zero non-degenerate indexed triangles. Its text mask was also suppressed. Logos
are separate models, consistent with the visible symptom. This is a shared
structural regression worth restoring, **not proof of the engine's visibility
or stencil behavior**. Font lookup, native culling and GPU state remain outside
the diagnostic.

V6 starts the main scene from stock instead of extending its text/skeleton
structures. It retains the stock ten-record text table at its original offset,
all thirteen bones, and the root helper and text-mask index streams. Core
score/period/clock font aliases, zero-width values and width flags remain stock;
only their anchors/colors change. Decorations and the twelve unused transparent backing quads are suppressed
separately. Narrow low-contrast dividers separate the clock/context cells.

The existing ABL records now carry the live team names using their native
providers and default renderer. The original player_info record keeps its
marker/model but changes its provider identity to home_city for the right-hand
context. The context initialization hook moves from 0x4EF760 to 0x4EF5A4;
its descriptor store moves from row+0x824 to row+4. The old ABL hook is restored.
Thus the context provider no longer consumes either team-name binding. The
860-byte context provider and existing string-ownership checks are unchanged.

`inspect_text_dependencies(parts)` in scorebug_text provides a read-only owner,
marker and submitted-index audit. It reports unresolved markers and zero-owner
triangles without claiming native visibility. All ten v8 main records resolve
against their original markers and an owner with two indexed triangles. A
synthetic regression demonstrates how suppression affects all labels sharing an
owner, while a separate mask retains its own draws. Malformed indices/draws and
unbounded draw counts are rejected. This is a diagnostic, not a new writer or a
certification that every submitted triangle is visible.

## Reference layout and shading

The main panel occupies [-360,-208.5,360,-174.5]. Team-color panels retain their
native palette material identities and gain an authored RGB ramp 0.100..0.165.
The dark body texture shades from RGB48/51/56 to RGB9/10/12. Pale score textures
shade from RGB252/253/254 to RGB219/222/226; score text uses RGB14/16/19. Existing
logos and Reborn branding art remain separate. Native fonts and strings, rather
than baked score/name artwork, remain the game text path.

Away/home score boxes are [-148,-208.5,-112,-174.5] and
[58,-208.5,94,-174.5]. Team names sit on the upper row; clock/period/shot-clock
anchors remain compact to the right. The native sixth-man meter's nineteen
material draws remain intact. Its authored span is [20,-40,145,-38], with a
separate local native offset array [-298,-92], placing the two fills at
[-278,-153] and [-72,53], Y[-193,-191], under their corresponding school names.
Both observed consumers of the replaced TOC slot (0x76A8B8/0x76A9E8) belong to the
same meter routine, 0x76A714. Other roster colors/thresholds are not rewritten.

There is no always-on synthetic foul/bonus/possession footer. Those accurate live
getters and bindings still need separate work; empty space must not contain fake
numbers. Region/round/seed strings from the television references are likewise
not invented by this asset update.

## Above-team statistics strip

The comparison bounds are [-318,-174.5,94,-150.5], ending at the home score cell
rather than extending over the clocks/context. The topbar gains the registered
text1/text2/text3 bindings with title/away/home centers at X -112.5/-260/35.5 and
baseline Y -166.25. Two existing records use their existing markers. The third
reuses the preexisting text_6th_man marker, keeping all six skeleton bones.
Property blocks and the three-record table are 16-byte aligned; forced sixth-man
literal bits are cleared so provider strings can display.

The native larger-panel dispatch already searches this loaded topbar scene.
Existing queue selection and visibility drive these fields. No new event is
injected or forced on. Queue-3 comparisons have three providers; actual event
admission/content, including which basketball sequence produces a free-throw
comparison, still requires user observation. Queue-2's two-provider leader lists
can require different spacing and remain a runtime-fit concern. Do not claim that
all injury, leader and comparison layouts are now verified from binding presence.

The blackbar backing and its existing info text move into the same upper-team
region. The unwanted edge-on helper triangle stays degenerate. Existing compact
event text anchors move to two lines above the team panels. Native event timing
and the prior conditional backing hook are retained, so their fade alignment is
also a manual validation item.

## Preservation and verification

Five SCNEs change. Original bytes for 257 other stock records remain at the start
of their inferred spans. One unchanged scorebug_logo_bloom header span grows by
9,088 bytes: that tail is checked to equal the exact old, unreferenced topbar
header, not arbitrary padding or silently accepted changed data.

The matching executable preserves v5's context provider and event hook code,
changes only the checked registration sites/stub, adds a checked local meter
offset array in zero padding and updates its isolated TOC slot/load extent. SELF
payload roundtrip and exact diff allowlists pass. Original supplied inputs and
previous packages remain unchanged. The matched English archive is unchanged.
Both IFFs prepare and preflight without building a JB.

Focused scorebug tests: **68 passed**, including four new dependency-audit
regressions and the earlier callback instruction harness. New-test Ruff E/F/I
passes. Five changed scenes reparse with no preview warnings, and every new
text/model/marker reference resolves in the private dependency audit.

An offline layout study illustrates spacing, native glyph artwork and example
values/logo placeholders. It does not simulate runtime palette math, font state,
clip/stencil/culling, animation or native event admission. It must never be used
as evidence that missing text is fixed in-game. No emulator/gameplay test was run
and no automatic/testing JB was built. Next manual evidence is a screenshot with
scores/clocks visible and a naturally admitted comparison popup in the matching
v8 executable/IFF set.

## Centered study revision after user feedback

The user found the first study too large and insufficiently centered. The revised
study uses ink bounding boxes within explicit cells, uniform glyph scaling and
role-specific cap heights: score targets 32 px, clock 22, shot clock 20, period
and team names 18, context 13, comparison title 18 and values 20. Cell padding may
reduce the final ink height slightly. All numeric ink centers differ from their
cell centers by at most half a pixel. The glyphs are not stretched independently
in X/Y. Team names align left within their own upper row, as in the references.

Brand/team image quads are square and centered in the game assets. Score anchors
retain the stock-relative vertical centering offset rather than the previous
low guessed baseline. Comparison value anchors move to the centers of their
specified value cells. No new native font bank is installed: **the game font
sizes remain uncalibrated** until text can be observed. The study's exact pixel
sizes are a visual target, not a native projection measurement.

The more detailed study shows ranks, foul/bonus/possession footer text, placeholder
team logos and a tinted popup end cell from the reference. Those are explicitly
reference targets; their live bindings/tint are not supplied or faked by v8.
The native game package retains its existing team logos and native event data.

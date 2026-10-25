> Superseded: the v11 gameplay screenshot shows backing returned but main text
> at screen center, dark team panels and distorted logos. See
> [the v12 correction](SCOREBUG_V12_PLACEMENT_REPAIR.md).

# V10 gameplay failure and rendering repair

The user supplied a v10 gameplay screenshot and confirmed copying its EBOOT and
applying both IFF overrides. It shows missing backing/score plates, missing main
text, distorted logos and a floating sixth-man label. V10 failed; its 95 tests
and structural checks did not establish a usable scorebug. Do not attribute this
result to an assumed installation mistake or repeat v10's readiness claims.

## Confirmed geometry regression

The private quad helper changed vertex positions from the stock right-bottom,
right-top, left-bottom, left-top ordering to the opposite ordering while keeping
indices 0,1,2,3. Stock main body has positive projected area +8572.639; v10's body
has -24480. The v10 score plate similarly has -1224. Team-color and logo meshes,
which remain visible in the screenshot, retain positive facing. This is a
concrete culling-risk regression, not just a triangle-count difference.

V11 changes the eight deliberately rectangular body/branding/score/divider and
comparison strips to 2,3,0,1 and degenerates their remaining indices to the new
last index. Changing only the first four indices would introduce a third triangle
at the old tail; the repair rejects that too. Each repaired part has exactly two
positive-facing projected triangles. Header, vertex, material and draw counts
remain intact. The new read-only inspect_xy_winding audit distinguishes positive,
negative and edge-on triangles; it does not certify GPU visibility.

## Native text transform and legacy mask

At 0x6AEF0 the loader resolves a marker, then 0x6AF2C..0x6AF48 copies its live pose
matrix into the font structure. The edited SCNE text basis is not the final font
transform on this path. Consequently the previous installed-scale claim was too
strong. V11 hooks only the default main scorebug call at 0x4F5B44 and writes the
actual live font matrix, zero additional position vector and alpha 1 immediately
before tail-calling the existing native renderer import 0x49CE24.

The wrapper reads the native registry index r27, supplies per-role scale/anchor
and Z250 for rows 0..11, and leaves event rows 12/13 and unsupported rows unchanged.
It retains the provider DString, native font key, colors, fit flags and metadata.
No string is baked or allocated. The tail call preserves the original LR, stack
and TOC-import behavior; only volatile r9/r10, vector0, FPR0 and CR7 are used.
The source and exact role table are in examples/scorebug-main-text-draw.*.

Native horizontal alignment mode 3 subtracts half the measured line width at
0x128A70..0x128A84; this supports the retained centered alignment setting rather
than guessing from a preview. Actual glyph fitting and vertical position still
require the new in-game result.

The old text_nodeMask is not the Score_bug text-owner skeleton. Its nearly
transparent material has alpha 0.01, and 0x4F215C treats that named instance
separately with a +700 Z translation versus +200 for ordinary main meshes. The
old mask is inappropriate for the relocated broadcast layout. V11 degenerates
its draw indices while preserving the independent Score_bug owner/markers.
The mask restoration in v8/v10 should not be treated as a proven text fix.

## Logos and sixth-man elements

The stock team-logo UVs use a vertical crop about 0.2546..0.7837. V10 replaced it
with 0..1. V11 keeps the centered square screen quads but restores the source UV
crop as a rectangle, removing the old shear. Neutral source vertex RGBA is copied
exactly. Team-logo texture pixels and palette/material identities are unchanged.
Appearance across arbitrary logo assets remains an observation item.

The floating 6th_topbar label/backing is disabled by text count zero and degenerate
geometry, retaining its skeleton and all other data. The live nineteen-draw meter
scene/state stays present. Its dedicated offset array is now ordered home/right
then away/left (-92,-298), consistent with the stock right/left slot layout.
Final live meter placement needs verification; the previous static offset-span
calculation alone did not establish what the screenshot would display.

## Verification and status

113 focused tests pass. Sixteen new instruction cases cover every main draw row,
pass-through event/invalid rows, matrix/alpha writes and preservation of provider
arguments, native style metadata and nonvolatile registers. Native graphics and
font routines are not executed. Two winding regressions distinguish the exact
failure class missed by triangle-count audits.

Private matched output changes three v10 SCNEs; all other record slices remain
exact. Eight facing checks, logo crop/color checks, scoped ELF writes, callback
source matching, SELF payload roundtrip and two-IFF preparation/preflight pass.
The ZIP passes CRC/checksums. No supplied game/previous output is modified, no
emulator/gameplay test runs and no full testing JB is created.

The user has been given the matching v11 executable/IFF candidate for a gameplay
check. This task remains open until that result confirms the backing, scores,
clocks, names, logos and meter placement. A static pass is not completion.

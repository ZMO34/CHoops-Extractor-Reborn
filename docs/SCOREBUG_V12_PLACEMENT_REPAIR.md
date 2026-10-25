# V12 main text placement, panel brightness and logo mapping

The supplied v11 gameplay screenshot confirms that backing and pale score cells
render. It also shows text clustered at screen center, dark team panels and
compressed/stretched logos. V11 is not a completed scorebug.

## Text dispatch correction

V11 intercepts only the default renderer call at 0x4F5B44. The main HUD also has
custom draw callbacks: initialization at 0x4EF598/0x4EF5CC/0x4EF6DC installs several
of them, and 0x4F4A48 loads the selected callback before choosing custom/default.
Consequently a default-call-only hook cannot establish placement for every field.
This proves a coverage defect; it does not by itself explain every centered glyph
in the screenshot. No claim is made that all runtime causes have been reproduced.

V12 replaces the callback-selection load at 0x4F4A48 with a bounded setup branch.
Rows 0..11 receive explicit scalar matrix/position writes to the live font r30,
then jump to the existing native standard-text call preparation at 0x4F5B3C.
This makes rendering consistent across these fields. The old v11 default-call
hook is restored to its original instruction, avoiding double application.
Rows 12/13 and invalid rows execute the displaced callback load and return to
0x4F4A4C, retaining the event callback path.

The affine basis carries per-role scale with zero matrix translation. Position
is supplied separately at font +0x40/+0x44/+0x48. Native 0x9BEB8 adds those values
to matrix translation at +0x30/+0x34/+0x38 before glyph rendering. This separates
the position from the marker pose; scalar accesses avoid vector-alignment
assumptions. Provider strings, font keys, colors, widths and style flags remain
unchanged. The wrapper uses volatile r9/r10/CR7 only, leaves LR/stack/TOC alone,
and resumes native code that sets the draw arguments. Dedicated custom main
presentation effects, including the shot-clock custom color path, are bypassed;
the live shot-clock value and native standard styles remain.

The intended role anchors/scales remain in the authored setup JSON. Names are
above foul rows; scores occupy the two pale cells; period/gameclock/shotclock
occupy their dark cells; context occupies the far-right cell. V12 does not add
unverified extra popup providers or change the comparison popup experiment.

## Brightness and aspect correction

Both team-color quads were multiplied by RGB 0.10 at the bottom and 0.165 at the
top. V12 changes only their RGB to a neutral 0.85-to-1.0 gradient. Native team
palette/material ownership and alpha are retained; dark backing and pale score
textures are unchanged. Score text RGB remains 14/16/19.

V11 used a rectangular source UV crop (about 0.962 wide by 0.529 high) on square
32-by-32 world quads. That mapping samples unequal U/V spans, so it cannot preserve
square texture proportions. Read-only inspection of the supplied team-logo bank
confirms square 256-by-256 DXT5 textures. V12 uses the complete 0..1 square UV
rectangle on the existing square quads, retaining neutral source vertex colors.
Logo pixels, material IDs, geometry positions and strip indices are unchanged.
This corrects the mapping rather than stretching texture pixels or baking teams.
Arbitrary replacement logo assets still require an in-game appearance check.

## Verification

149 focused tests pass, including 33 new setup instruction/dispatch cases over
all core/event/invalid rows and null/custom callback selections. They check
native position consumption, nonvolatile/argument preservation, unchanged style
metadata and scratch bounds. These are CPU instruction/semantic checks, not
native GPU execution. New-test Ruff E/F/I passes.

Private output reparses both IFFs; only one SCNE record differs. All other record
slices are exact. Logo UV/neutral RGB, scoped panel writes, retained positive
quad winding, original default-call restoration, new setup source matching,
ELF write allowlist and SELF payload roundtrip pass. Two-IFF stage/preflight and
ZIP CRC/checksums pass. The source v11 ZIP remains unchanged.

No emulator/gameplay run or full testing JB was made. V12 needs user gameplay
verification; neither these tests nor this document certify final placement,
font sizing, palette appearance or all requested reference features.

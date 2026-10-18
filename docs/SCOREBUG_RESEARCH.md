# Scorebug research — authored assets, runtime routing pending

Read-only stock archive inspection on 2026-10-15 identifies the following records.
Names identify authored resources; they do not alone prove which runtime path is
active. No executable edits are implemented. The bounded experimental authored-layout
editor and test02 evidence below supersede the initial artwork-only scope.

| Archive | Record | Type | Evidence |
|---|---|---|---|
| gamedata.iff | scorebug_bottombar (55) | SCNE | 23 parts; six embedded textures |
| gamedata.iff | scorebug_topbar (250) | SCNE | text_nodeMask and g_top_bar; one texture |
| gamedata.iff | scorebug_blackbar (135) | SCNE | group_blackbar_text |
| gamedata.iff | scorebug_logo_bloom (260) | SCNE | klogo_Score_bug |
| gamedata.iff | scorebug_bloom (25) | TXTR | Separate artwork |
| gamedata.iff | scorebug_info_blk (39) | TXTR | Separate artwork |
| gamedata.iff | scorebug_logos (60) | TXTR | Separate artwork |
| gamedata.iff | scorebug_scanlines (143) | TXTR | Separate artwork |
| gamedata.iff | shotclock (174) | TXTR | Clock-related artwork; numeric binding pending |
| gamedataextra.iff | scorebug_ps3 (1) | SCNE | Five parts; two textures |
| gamedataextra.iff | scorebug_xenon (2 / 3) | MRKS / SCNE | Separate marker and scene records |

The bottom-bar parts include Score_bug, drop_shadow, top_greybar, bot_greybar,
color_1, color_2, logo1, logo2, frame1..7, frame8_glare, frame9_glare, ncaa2k8,
g_2K_circle_logo and text_nodeMask. Its embedded texture slots are:

| Slot | Dimensions | Encoding |
|---|---|---|
| 0 / 1 | 64 × 64 | DXT1 |
| 2 | 128 × 128 | DXT5 |
| 3 | 256 × 256 | DXT5 |
| 4 | 128 × 128 | DXT5 |
| 5 | 512 × 256 | DXT1 |

The PS3/Xenon scenes both have polySurface50, Score_bug, group2, mesh_slider2 and
titlebar_plane1, with 256 × 128 and 128 × 64 DXT5 textures. Their relation to the
free-throw meter (the neighboring LAYT record) is a hypothesis, not proof that
these scenes control the main score overlay. overlaycache.iff contains 21 scenes,
including halftime_box_score, but no explicitly named scorebug record.

Reproduce the inventory without extracting artwork or building a JB:

```powershell
python -m choops_py.formats.scorebug "YOUR_JB_ROOT"
```

This prints JSON record identities, part names, logical block sizes and texture
layouts. Current Explorer/texture tools can inspect and replace confirmed TXTR or
SCNE texture slots using their exact names, original dimensions, alpha and mip
layout. Preserve scene parts, materials and record names. This is an artwork-only
starting point; it does not promise a complete layout redesign or validated game
behavior. A record index is supporting evidence for this input, not a portable
replacement key; use exact record names.

Next research: map score/period/game-clock/shot-clock/team-name fields to authored
nodes, trace team-color/logo bindings and animation/visibility states in read-only
EBOOT consumers, distinguish broadcast modes and console variants, then prove
which layout/material parameters can change without executable edits. Moving or
removing scorebug nodes is deferred until these dynamic bindings are understood.

## Test02 — authored layout, sixth man, messages and fixed right label

The user-tested test01 showed the network logo inside the first team panel,
distorted team logos, bright team plates and an unadjusted sixth-man widget.
This update adds a bounded `choops_py.modding.scorebug_layout` editor and a local
asset package. It is an experimental asset revision, not runtime certification.

### Concrete corrections and edit boundaries

- Test01 replaced original vertex RGB 0.1 with 1.0 on color_1/color_2. Restore the
  authored 0.1 values rather than changing team roster palettes. Dynamic material
  IDs and external uniform-logo bindings remain unchanged.
- The original team-logo quads are sheared. Rectify both positions and half2 UVs
  to square rectangles, retaining the live logo materials rather than baking team
  logos into the background. Changing positions without their UVs can distort art.
- CHRB2K is now on the fixed left background `polySurface17`, not the old
  `g_2K_circle_logo` object. The latter's vertex alpha is zero; runtime movement of
  that named object cannot move the newly embedded logo. The exact transform that
  displaced test01 is not established by the user's screenshot alone.
- The background consists of seven independent restart strips with gaps/overlap;
  blindly mapping one logo across all strips creates seams. The editor verifies
  the exact u16 restart topology, uses its first complete quad, and makes remaining
  vertices transparent. Index values/counts, materials and resource IDs stay intact.
- Existing `ncaa2k8` geometry/texture slot 3 supplies fixed two-line **COLLEGE HOOPS /
  REBORN** artwork in the right panel. Only this static material's declared
  DiffuseColor alpha is raised from 0.6 to 1.0. No dynamic tournament round, region,
  seed, team name or foul widget is fabricated. The static text is raster artwork.

### Separate sixth-man resources

All four edited records are SCNEs inside **gamedata.iff**:

| Record | Authored change |
| --- | --- |
| scorebug_bottombar | Main plates/logos, fixed branding/right label and message anchors |
| 6th_man_meter | Existing 19 meter draws retained; local rectangle x60..145, y−2..2; RGB ×0.7 |
| 6th_topbar | Header rectangle x−300..−150, y−155..−142; th_man anchor (−298,−150) |
| scorebug_topbar | Alternate two-anchor header; lt_6th_man (−298,−150), rt_6th_man (−68,−150) |

The meter is a separate local-coordinate scene: its original vertices span roughly
x62.52..129.76 and y−4.43..4.44. The header text's original anchor is near
(−185.05,−156.66). Their different coordinate spaces matter; drawing the meter
at absolute bottom-bar bounds would be incorrect. Runtime fill/value/material
selection is retained. Exact placement in every away/home activation state still
needs user testing. No meter threshold/gameplay logic is changed.

### Message and text placement

SCNE header +0x4C is the text-record count and +0x50 a relative table pointer.
Observed records are 144 bytes: name pointer +64, two authored translations at
+48 and +96. Each selected text also has a uniquely named independent marker
containing two matching translation copies. The editor changes all four X/Y copies
and preserves Z, rotations, name/ID/font data and unrelated bytes. It refuses
missing or ambiguous markers rather than guessing a new text object.

| Bottom-bar name | Original X/Y | Test02 X/Y |
| --- | --- | --- |
| player_info | 44.30 / −175.54 | 274 / −147 |
| bottombar_textNode_1 | 13 / −175.54 | 274 / −147 |
| bottombar_textNode_2 | 13 / −203.30 | 274 / −132 |

These move authored candidate event/info positions above the right label. They do
not create messages, change event timing, resize runtime font boxes or prove that
all three nodes are used in every mode. `scorebug_blackbar` separately contains
an `info` anchor at local (0,−4); it is deliberately unchanged because a runtime
parent positions that scene. Other popup/overlay banks are not globally shifted.

Read-only executable data contains UTF-16 registrations for `home_score`,
`away_score`, `gameclock`, `shotclock`, `quarter`, `home_ABL`, `away_ABL`,
`bottombar_textNode_1` and `bottombar_textNode_2`. On the inspected image, file-offset
pointer slots 0xA4DDB8 and 0xA4DDC4 reference the latter two strings. `player_info`
exists in the SCNE but was not found as an exact UTF-16 executable string; that
absence does not prove it is unused. Dynamic text contents remain runtime-owned.
Full event dispatch, font/style selection, visibility and animation tracks are
not established. Do not infer new tournament text support from an empty panel.

### Reusable tool and verification

```powershell
python -m choops_py.formats.scorebug YOUR_JB
python -m choops_py.modding.scorebug_layout input.scne layout.json output/edited.scne
```

The inventory includes sixth-man scenes and named authored text anchors. The [test02 geometry profiles](examples/scorebug-test02-layout.json) contain only
configuration, with no game assets. Select the profile object for one named scene.
A layout
profile has `parts` keyed by exact part name and `text` keyed by exact anchor name.
Part options: bounds [left,bottom,right,top], rectify_uv, single_quad, rgb_scale,
z_offset, hide. Only observed split float3/float4, half2 UV/restart-strip layouts
are writable; others fail. This is a developer CLI, not a new GUI panel.

Synthetic tests cover UV/aspect rectification, interleaved unknown words, alpha,
paired text translations, restart indices and rejection. Actual preparation checks
verify unchanged block sizes and all 258 unedited IFF records, material identities,
valid texture layouts and source immutability. Static inspection images omit live
text and team logos and are not screenshots of game behavior. RPCS3/gameplay NOT
RUN; EBOOT NOT EDITED; real/testing JB NOT BUILT. The local test ZIP contains
user-owned derived game assets and is not committed or uploaded to the repository.

Next user checks: left CHRB placement during intro/score transitions; both logos'
aspect; team-color accuracy; sixth-man empty/filled states for home and away;
message length/clipping during fouls, substitutions and timeouts; collision with
clocks and right artwork. Further runtime bindings need evidence from those states.


## Test03: continuous panels and native lettering

Test03 supersedes test02 geometry/artwork. Runtime reference images revealed
cutout corners, strip gaps, a detached sixth-man fill, a strong panel gradient
and undersized non-native static lettering. The game resources, not the runtime
screenshots alone, establish the following changes:

- `polySurface16` consists of seven separate restart strips with spaces between
  them. One validated independent quad now covers the whole backing; the other
  strips are transparent. Index buffers and resource identities stay unchanged.
- The shared frame atlas contains slanted transparent corners. Straight rectangular
  artwork and rectified UVs replace them. Team colors stop inside the panel edges;
  a continuous opaque backing covers joins. This addresses spill for all schools,
  rather than special-casing Florida.
- Team plates used vertex RGB ranging from 0.1 to 1.0. Test03 uses a uniform 0.72
  multiplier; palette material bindings remain live. This removes the authored
  gradient, but is not a claim of colorimetric equivalence to a television feed.
- The body spans X −360..360, Y −208.5..−168.5; shadow reaches −211.5. Compared
  with test02, width decreases from 760 to 720 world units and the body moves down
  13.5 units. Team logos are square 38-unit quads. Scores use a 1.25 authored basis
  scale. Font resources, score strings and callbacks remain unchanged; runtime
  interpretation of the authored scale still needs user verification.
- Read-only meter rendering code indexes two X translations, −185 and −337, then
  subtracts 153 from Y. Its existing 19 material/draw bindings are preserved.
  Local X60..145 and Y−15.5..−11.5 place the meters at X−125..−40 or −277..−192,
  Y−168.5..−164.5. Both fit inside the black header X−340..−35,
  Y−168.5..−152.5. Labels sit before each respective meter; the small slanted black
  decoration is hidden independently of the rectangular background.
- A fifth scene, `scorebug_blackbar`, receives a right-side backing rectangle
  X55..360, Y−168.5..−138.5. Only its four visible background vertices move;
  the unrelated three-vertex dummy draw remains byte-identical. Its `info` text
  has a translated parent marker: the confirmed marker offset is preserved, not
  flattened into the text's local position. Bottom-bar candidate popup anchors
  move above the same region. This changes authored placement, not message event
  dispatch or visibility. All foul/rebound/points states need manual confirmation.

### Actual game font, not a platform font substitute

The bottom-bar author properties explicitly name **Stratum2 22 32** for score,
clock and period nodes, **Stratum2 18 26** for info/team text, and **Stratum2 12**
for sixth-man labels. `fonts.iff` contains the corresponding FONT resources.
Test03's static COLLEGE HOOPS / REBORN artwork uses the **STRATUM2_22_32** atlas.
No font bank or executable is modified.

Observed FONT structure: first/last codepoint are big-endian U16 at +0/+2;
space advance is U32 +12; +8 is a relative map pointer. The map repeats the
codepoint range and points from +4 to a contiguous 96-byte glyph table. Each glyph
has U32 advance at +0, four float4 corner records at +16, and UV rectangle at +80.
An embedded TXTR begins at FONT header +32, with a separate image block. The green
channel contains coverage; taking DXT1 alpha instead would produce solid boxes.
`native_font_art.render_line` composes those glyphs with recorded advances and
bearings. It rejects missing characters and invalid/out-of-bounds metrics.
Kerning tables remain undecoded: this uses native artwork and advances, not a
claim of identical runtime kerning. The artwork keeps the 22-pixel cap height in
an inferred half-scale HUD canvas (11 world units); actual runtime sizing must
be checked against the user's next screenshot.

### Updated developer profile options

[Test03 profiles](examples/scorebug-test03-layout.json) retain only asset-free
geometry configuration. Select one named scene object for the CLI. A part may
contain one operation or a list applied in order. Additional bounded options:
`straighten` removes shear without changing UVs; `vertex_range` is a half-open
[first,last] range within one existing stream; `rgb` sets a uniform RGB value
without replacing material palette bindings. Bounds are recomputed over the
whole stream so an untouched dummy draw is not excluded by a partial edit.
Text accepts either [x,y] or an object with `position`, optional `scale`, and a
confirmed `marker_offset`. The latter is checked against source world/local
copies before writing and retained afterward. A scale changes the authored 3x3
basis, preserving resource pointers, translation Z and marker offsets.

The local test03 ZIP contains five SCNE overrides with their matching DDS files,
plus a separate complete stock-based gamedata IFF alternative. Use one route only.
The scene route preserves unrelated custom gamedata edits. Replacing just SCNEs
while retaining test02 DDS would restore the old atlas through DDS priority.
257 other stock records, all original inputs, block sizes, live logo/palette IDs,
all 19 meter draws and unrelated dummy vertices are checked for preservation.
Static inspection and import/build preflight are not gameplay certification.
No RPCS3, EBOOT writes or new real/testing JB. Derived assets remain local.


## Test04: live roster names and actual text style selection

The user's test03 screenshot establishes that the team names are absent, the
horizontal panel overlays remain intrusive, and texture lettering differs from
live HUD text. Test04 changes the following:

- The bottom-bar dispatcher registers `home_city` and `away_city`, in addition to
  scores/clocks. Those names are absent from the original bottom scene. The existing
  home_ABL/away_ABL text **record names** now bind to those two callbacks. Their
  `Score_bug` parent and ABL bone names remain unchanged. The callbacks select the
  current game teams and their text IDs; names are not baked for one matchup or
  copied from a particular private roster. Special game modes can select alternate
  team-label paths. Exact display/clipping still needs user testing.
- Scores, half/period, game clock and shot clock use the actual `Stratum2 25` font
  alias. Test03 only scaled the authored text-record basis. The runtime style loader
  reconstructs its matrix from the named parent/bone, so that basis edit is not a
  dependable font-size control. Test04 does not rely on it.
- Gray section separators are narrow vertical geometry, with gray top/bottom edges.
  The shared atlas is solid gray, so no full-panel transparent frame silhouette
  crosses the colored name panels. Former frame8_glare is a black popup backing
  using the existing untextured black material, above the right side of the body.
  It is always visible; it is not newly wired to popup event visibility.
- Right popup candidate anchors move 25 world units left from test03. This corrects
  the displacement observed in the supplied screenshot while retaining the native
  message callbacks. The separate parented blackbar stays in the test03 layout;
  it was not sufficient to back all bottom-bar popup callback states on its own.
- The sixth-man header's visible draws use its existing untextured black material,
  avoiding the partial texture-backed enclosure. All 19 live meter draws remain.
- Branding is **College Hoops / Reborn**, not all caps. Its texture uses native
  STRATUM2_25 glyphs at the same chosen font size, RGB 222/222/222 and shadow
  10/10/10 with the native negative-X/positive-Y shadow direction. The right box is
  widened to 132 world units so title-case text fits without squeezing its width.
  Clock and shot-clock centers/separators are adjusted accordingly. The branding
  material copies the known white left plate's sampler/state, retaining its own
  texture resource. It is still textured geometry, not a new native text callback.
  Identical runtime shader/filtering cannot be claimed. A native constant-text
  registration/localization route remains unresolved; executable editing is barred.

### Corrected serialized text-property layout

The text record's +80 relative pointer leads to a property object with count at
+0. Its entries start at +16, each 32 bytes: **16-byte value, U32 type, U32 key,
8 reserved bytes**. Reading a value after the key misassociates it with the next
property. This corrects the earlier informal test03 property-offset investigation.
The font-atlas identity was correct, but some claimed scalar associations were not.

Confirmed style keys from the read-only loader:

| Key | Purpose / observed value |
| --- | --- |
| 0x7714781F | Default localized text key, not font alias |
| 0xBF045BDB | Font alias, e.g. Stratum2 22 32 |
| 0x6109EA5A / 0x97DE0310 / 0x6814845A | Main RGB components, 222 each |
| 0x53C67207 / 0x661F09B0 / 0x7DFC668B | Shadow RGB components, 10 each |
| 0x4884F64A / 0x3F83C6DC | Shadow X/Y offsets, −0.75 / +0.5 |
| 0xE27EC83B / 0xAE7E1958 | Parent scene instance / bone names |

`scorebug_text.inspect_styles` reads bounded tables. `edit_styles` appends new
UTF-16 strings and changes only selected font/name pointers. It preserves original
strings, bone bindings, property types/keys, text counts and vertex buffers; duplicate
bindings and invalid properties are rejected. Header growth is explicit and handled
by the existing expanding IFF writer. Native bindings and font styles are asset-free
[configuration](examples/scorebug-test04-text-styles.json); separate
[geometry profiles](examples/scorebug-test04-layout.json) omit the generator's
explicit draw-material reassignment and texture artwork. These are developer APIs,
not a new scorebug GUI mode or a claim that geometry JSON alone recreates the ZIP.

Read-only English localization inspection found a tagged string table and literal
character tokens. No localization writer, new translation IDs or fallback guesses
are enabled. Native constant branding and exact live-font rendering remain open.
No EBOOT/font bank/roster/uniform archive is changed. All five edited records reparse,
all other 257 stock gamedata records remain identical, and scene-only overrides pass
preparation/build preflight. No test04 JB, RPCS3 or gameplay test is run automatically.

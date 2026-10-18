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

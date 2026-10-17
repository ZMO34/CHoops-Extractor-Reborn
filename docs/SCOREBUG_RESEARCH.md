# Scorebug research — authored assets, runtime routing pending

Read-only stock archive inspection on 2026-10-15 identifies the following records.
Names identify authored resources; they do not alone prove which runtime path is
active. No executable edits or scorebug geometry writer are implemented.

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

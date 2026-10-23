# Scorebug context and recurring line investigation

Research date: 2026-10-23. This is native disassembly, focused Ghidra analysis,
localization inspection and source-bound archive analysis. No emulator/gameplay
run, automatic/testing JB or public executable patcher was used. Local experiment
outputs are private; no game assets or executable bytes are published here.

## Findings that change the implementation plan

The previous package is a prototype. Having native popup providers in the
executable does not establish that the redesigned scorebug displays all of them.
An inventory of every readable text-style table in its gamedata finds
`player_info`, `bottombar_textNode_1`, `bottombar_textNode_2` and blackbar `info`.
It finds **no authored `text1`, `text2`, `text3` or `text3_b` records**. Those names
have registered native providers for the larger statistics queues. This is a
concrete asset-binding gap, not proof that another archive can never supply them.
The earlier broad claim that points/fouls/rebounds/injuries were all complete
must therefore be read as provider preservation, not verified display coverage.

The random lines also need more than alpha-zero hiding. The current prototype
still submits hidden frames/masks/helper geometry and transparent surplus quads.
A private correction now degenerates only their selected index spans. It retains
all SCNE headers, vertex streams, bones, materials and draw record counts. Native
runtime state updates still see the same models; unwanted indexed triangles no
longer rasterize. This addresses concrete geometry risks, not every possible
cause of an in-game line.

## Geometry evidence and correction

| Observed item | Evidence | Bounded local correction |
| --- | --- | --- |
| Popup helper | `scorebug_blackbar/group_blackbar_text` has seven vertices and two 48-byte draws: first/count 0/4 and 4/3. Only the first quad was resized. | Keep indices 0..3; replace 4,5,6 with 4,4,4. |
| Edge-on helper triangle | Vertices 4..6 have Y about 181.803, X about 143.335..154.826 and Z about -73.188..-61.697; its XY projection is a horizontal segment far from the backing at Y -168.5..-138.5. | Suppress its indexed area; preserve its records/bones. It is a line-risk candidate, not a screenshot-confirmed root cause. |
| Old frames and masks | Main-bar frames, glare, old lettering, cone, skeleton helper and text mask remain in draw lists after relocation or alpha hiding. | Collapse their non-restart indices to one existing valid vertex; preserve 0xFFFF restart words. |
| Surplus backing quads | `polySurface16/17` each retain seven independently restarted quads. Only the first is needed; six have alpha zero. | Keep each first quad; degenerate the six surplus quads in each mesh. Alpha zero alone does not establish depth/stencil behavior. |
| Separate topbar mask | Its vertices were moved to approximately -2000 coordinates, but the draw was retained. | Degenerate its indices rather than depend on clipping. |
| Texture seams | Both current topbar texture-0 images decode to solid opaque black (128x128); main-bar texture 0 is solid RGB8, texture 2 is solid RGB115/117/123. | No new texture rewrite. The historical script's gray border is absent from this candidate. |

The correction changes 30 explicitly checked index spans across three SCNEs;
259 other records remain identical to the scorebug-only v1 input. No index edit
aliases another mesh index buffer or any vertex stream. All five HUD SCNEs reparse;
the two archives prepare/preflight. Main backing meshes now each produce two
triangles; the blackbar produces two, with no helper triangle. The 19 native
sixth-man draws, their materials, vertices, event callbacks and all executable
bytes remain unchanged from v1. V1's scoped SELF checks and nine bounded popup
instruction paths remain applicable to those identical executable bytes.

Remaining line hypotheses include overlapping active topbar geometry, stock
shadow outlines, palette/shader state, viewport/aspect transforms and transition
state. Parser success cannot certify GPU depth/stencil/scissor state. The current
wrapper uses native scene pose upload/draw routines; it is not a demonstrated
render-state isolation boundary. Do not advertise a complete line fix without
user observations identifying whether a line follows a popup, meter or scene.

## Popup content is already richer than the visible asset coverage

The observed table at 0x125A37D4 has 83 rows of 20 bytes, 119 non-null provider
slots and four queues. Queue priority is independent of provider count.
Localization templates below were resolved from the provider paths, preserving
native formatting arguments and color tags; templates are not proof of admission
in every gameplay mode.

| Types | Queue | Available native content |
| --- | --- | --- |
| 0..4 | 0 | Compact points/stat values; some use a dynamic stat label. |
| 5..26 | 2 | Team/player leaders, player stats and comparison categories. |
| 27..33 | 2 | Foul situation, leading scorers, career/season/last-season scoring, stat line. |
| 34..36 | 2 | Double-double, triple-double and quadruple-double milestones. |
| 37..38 | 3 | Three-provider comparison panels; exact event meanings need caller verification. |
| 39..62 | 0 | Fouls, turnovers and violations, including team/personal foul totals and tied ball. |
| 63 | 0 | Initial player-injury notice. |
| 64..76 | 1 | Diagnosis and can/cannot-return updates. |
| 77 | 1 | Scoring run with team, run and elapsed-span arguments. |
| 78..82 | 0 | Game point, clear ball, uncleared turnover, ten-second violation and foul out. |

Some entries are clearly shared with other modes. Do not force clear-ball/game-
point or NBA-like event templates into ordinary college gameplay merely because
they exist in the table. Do not rename a parameterized template with the isolated
ASCII literal writer: it does not preserve arbitrary format/tag contracts.

`bottombar_textNode_1/2` consume queue 0 through mode-specific gates at 0x4F0CC0
and 0x4F0E1C. Native `text1/text2/text3/text3_b` select the queue-2/3 providers;
0x4F12C0 explicitly selects provider 1 for queue 2 and provider 2 for queue 3,
then applies the HUD state at +0x28. Those additional authored bindings need
independent markers/styles and a proven loaded-scene path. Adding labels alone
cannot safely replace that state machine. Queue 1 also needs its complete loaded
binding/caller route checked; retaining injury providers is insufficient.

Queue admission at 0x5096F4 orders by event+0x1C priority and resets displaced
lifetimes. Queue update at 0x5099B4 uses durations and an update gate; 0x509B80
is a draw-pass heartbeat, not a callback acknowledgment. Preserve this pass,
repeat policy and priority ordering. A second custom timer would allow blank
backings, stale messages and conflicts with diagnosis/stat panels.

The existing conditional backing hook intercepts only the two wrappers at
0x4F1EB8 and 0x4F1ECC. They set argument 3 to one before entering the colored
stats renderer at 0x4F1620. Other wrappers set it to zero. Its current 0.7..1.9
phase gate is not a global visibility contract for every popup queue. Full
coverage needs backing opacity and visibility tied to the selected channel.

## Native context sources located

### Calendar tournament discrimination

Calendar formatter 0x5E4254 contains a branch at 0x5E4B94 that calls
0x58C8B0 with the selected calendar entry's +8 word. Success emits English
ID 0xF2CA6305 (NCAA tournament game day). Otherwise 0x58C674 is tested and
success emits 0x7DBD0049 (NIT tournament game day). The remaining path obtains
native context through 0x5A2158/0x75F9B0, tests 0x73D840, and formats a named
tournament with 0x73FF00 and ID 0xE673B17F.

Disassembly and focused decompilation show 0x58C8B0 tries schedule groups
0x5A..0x5F; 0x58C674 tries 0x55..0x59. Both call 0x58C420, which obtains a
native record and checks up to 32 stored dates against converted date bounds.
These are calendar predicates; **they are not proven current-game tournament
IDs or safe classifiers for an arbitrary HUD object**. Reusing them requires the
actual launched game's date/context, mode checks and invalidation after load.

0x73D808 obtains a native object through 0x4A1FF4 and reads U16 +0x1A;
0x73D840 passes that selector to 0x58C420. Do not confuse this object-specific
field with a roster team/conference field merely because the offsets coincide.

### Season versus conference versus national labels

Formatter 0x6783AC has a relative switch with 13 entries; Ghidra does not recover
all branch bodies, so the switch table and original instructions were inspected.
The block at 0x678960 compares the result of 0x5A0CEC with the caller's value:
if smaller, it chooses National Tournament (0x7FE36CED). Otherwise it obtains
context via 0x5A2158/0x75F9B0/0x73D808, requires a selector other than -1,
requires nonzero 0x58C15C, and compares the caller's value to that result before
choosing Conference Tournament (0x796D6F2F). The fallback is NCAA Season
(0x25CBDB35). 0x58C15C finds the minimum nonzero word among up to 32 record
entries. This establishes a native distinction but not a fully typed HUD ABI.

### Timeout calling team

0x719E98 has a useful independent route: it checks current state equals 0xE,
compares current-state +0x32C with another native team selector, and chooses
home/away getters 0x57F050/0x57F064. It formats TIMEOUT using ID 0x0505C3F9.
The selected team can take native name-formatting variants, including 0x76520C,
which reads team +0x15A and calls 0x75C7D8. Additional legacy/mode handling can
append content through 0x719604. Do not replace this with a remembered possession
team: timeout callers and possession need not match. The binding lifetime and
native meaning of state 0xE still require validation at the scorebug hook.

## Proposed logic, with installation status explicit

The following is an implementation specification, not installed executable code.
Keep the event layer separate from the persistent right-hand context label.

1. Resolve current game mode and both live teams; validate data ownership and
   generation after loading/starting a game. Missing or ambiguous data yields
   College Hoops / Reborn. Never retain yesterday's Legacy context.
2. Verified national tournament game: March Madness or native round text, with
   NCAA/NIT kept distinct. Never infer postseason solely from the month.
3. Verified conference tournament game: resolve the current conference's display
   name and append Tournament. Same-conference teams alone are insufficient.
4. Verified regular matchup in the same current conference: conference Matchup.
   Read current realigned membership; do not hardcode ACC/SEC team lists or use
   logo/artwork IDs as conference identity.
5. Otherwise render College Hoops / Reborn through the native text renderer.
6. Independently display native events with their queue priority, provider count,
   name/arguments, opacity, transition and lifetime. Give diagnosis/milestone
   panels enough lines; do not overwrite live event text with promotional text.
7. Pause/replay/HUD option changes clear or hide the appropriate layer. Decide
   explicitly whether branding should remain visible when sixth-man is disabled;
   the current reused scene/binding does not prove an always-on hook.

| Feature | Current evidence | Next required proof |
| --- | --- | --- |
| NCAA/NIT/conference labels | Native calendar predicates and label consumers located. | Launched-game context/date and safe update callback. |
| Timeout team card | Native caller selection and formatting found. | Scorebug binding/visibility and remaining-timeout getter. |
| Injury diagnosis/scoring-run cards | Queue-1 providers and templates found. | Full loaded-scene binding and transition route. |
| Leaders/milestones/comparison cards | Native queues/providers found; four expected authored bindings absent from inspected gamedata. | Add independently aligned records/markers and verify scene dispatch. |
| Possession arrow | Native tied-ball notice exists. | Actual alternating-possession getter; ball handler is insufficient. |
| Bonus/double-bonus | Foul totals/templates exist. | Active rule settings and native penalty getter; avoid fixed thresholds. |
| Team timeout pips | UI labels exist. | Team-specific live counts, timeout categories and reset behavior. |
| Rank/record/seed | Legacy context exists elsewhere. | Active game roster/team identity and postseason seed ownership. |
| Sixth-man display | 19 original live material draws retained. | Active options, full/partial fill and transitions observed by user. |

## Verification and remaining work

Private correction checks: 30 bounded index spans, three edited scenes, 259
other v1 records exact, all SCNE header/vertex data exact, native meter data exact,
executable and English archive exact to v1, two-archive staging/preflight passed.
The source input remains unchanged. Both topbar texture slot-0 images are solid
black; no current border texture change is necessary.

Focused Ghidra inspection covered five context consumers and six dependencies;
original PPC instructions were used to resolve switch-table omissions. Full
gamedata text-style inventory found the four missing statistics names above.
No new context selector or queue injection has been installed. Runtime behavior,
PS3 debug-SELF acceptance, fade-state behavior and the exact cause of the user's
observed lines remain unverified. Next: close loaded-scene/provider coverage and
current-game context ownership before adding a native context callback.

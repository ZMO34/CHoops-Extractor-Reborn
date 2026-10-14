# Roster semantic evidence and supported edits

## Appearance and signature controls

Read-only executable registration metadata links localized captions, paired
getters/setters, maximum option indices and caption arrays. +0x34 is the maximum
**index**, not the number of entries: adjacent array addresses corroborate the
inclusive last option (Bald, Red, Beard Style 6, Sideburns 3, Tattoo 12, Strong,
Freethrow 23 and Bigs 19). Unknown source codes remain unchanged until edited.
No new assets or executable modifications are required.

| Field | Raw player offset | Bits | Writable options | Getter |
|---|---|---|---|---|
| Hairstyle | 0x8C u32 | 7..12 | 0..36 | 0x69ED94 |
| Hair colour | 0x90 u32 | 13..15 | 0..4 | 0x69EF54 |
| Beard | 0x90 u32 | 21..23 | 0..6 | 0x69EE94 |
| Sideburns | 0x90 u16 | 0..1 | 0..3 | 0x69EF14 |
| Left shoulder tattoo | 0x84 u32 | 17..20 | 0..12 | 0x69E9DC |
| Right shoulder tattoo | 0x84 u32 | 13..16 | 0..12 | 0x69EA1C |
| Left biceps tattoo | 0x84 u32 | 9..12 | 0..12 | 0x69EA5C |
| Right biceps tattoo | 0x84 u32 | 5..8 | 0..12 | 0x69EA9C |
| Left forearm tattoo | 0x84 u32 | 1..4 | 0..12 | 0x69EADC |
| Right forearm tattoo | 0x88 u32 | 28..31 | 0..12 | 0x69EB1C |
| Post animation | 0x84 u32 | 21..25 | 0..7 | 0x69E99C |
| Free-throw animation | 0x84 u32 | 26..31 | 0..21 | 0x69E960 |

Jump shots at 0x83 now use all 112 exact game labels (Generic, Athletic, Guards,
Bigs); writable IDs remain 0..111. Free-throw captions deliberately skip 16,
as the game's table does. Tattoos and signature animations share packed words;
mask-preservation/undo tests guard every neighbouring field. Existing body build,
muscle tone, complexion, equipment, scholarship, class and redshirt controls remain.
All new scalars automatically participate in source-bound CSV and selective
comparison through the shared backend. No personal input data is included.

## Position and text evidence boundary

0x69DAA8/0x69DABC read/write the complete position byte at raw +0x3B. Adjacent
+0x3C begins scaled shooting ratings, not a secondary position. The localized
player bindings contain one Position control. This establishes the supported
primary field; it does not establish another independent field or prove that
none exists elsewhere. No speculative secondary writer is supplied.

Confirmed text-entry capacities and copy-on-write growth are described in
ROSTER_SCALE_AND_PREVIEWS.md. Entry-buffer capacities are not a universal renderer
ceiling. Fields without confirmed engine limits are not capped to the old string
allocation. Complete semantics for every remaining byte are not claimed.

Keyboard-entry limits are displayed as advisory values rather than enforced as engine ceilings. External text edits grow the string heap safely; the tool does not claim a universal game rendering limit.

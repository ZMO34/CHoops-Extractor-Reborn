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
primary field. The owner confirmed that secondary positions do not exist; that
search is closed and no secondary-position writer is supplied.

Confirmed text-entry capacities and copy-on-write growth are described in
ROSTER_SCALE_AND_PREVIEWS.md. Entry-buffer capacities are not a universal renderer
ceiling. Fields without confirmed engine limits are not capped to the old string
allocation. Complete semantics for every remaining byte are not claimed.

Keyboard-entry limits are displayed as advisory values rather than enforced as engine ceilings. External text edits grow the string heap safely; the tool does not claim a universal game rendering limit.

## Shared formatter representation ceiling

Read-only tracing establishes an upper representation bound of **65,535 UTF-16
units**, excluding NUL, for the common text-argument descriptor. Conference name
formatter 0x73FF00 calls 0x49E1B4 → 0x1E1610 → 0x1E2634. The latter obtains a
unit count via 0x11DF0 → 0x7C5818 (lhz until NUL, pointer difference divided by
two) and stores it with `sth` at descriptor +0xA. Serializer 0x1E1C00/0x1E1C4C
retains that u16. A count of 65,536 wraps to zero rather than retaining the text.

The shared backend therefore blocks larger new text values, including CSV and
comparison edits, with no mutation. This bound is separate from the adapter's
file-size guard and each keyboard buffer. It does not prove that every menu can
display 65,535 units, or establish smaller field-specific/combined-name limits.
Qt's default QLineEdit limit of 32,767 is removed so it cannot silently truncate
text before backend validation. Existing unchanged source values stay preserved.

## Current conference and coverage continuation

See CONFERENCE_ASSETS.md for the exact conference-logo route and newly traced
tournament index. Research coverage records `known_bit_mask` and
`unresolved_bit_mask` for every row byte, including packed player properties and
shoes. Fully known bytes, partially known bytes and known bit counts are separate;
unknown bits remain protected. Structural pointer classification is not proof of
all history/legacy meaning. Roster text dialogs show a live orange border beyond
confirmed game keyboard limits, measured in UTF-16 units. The warning does not
truncate text or impose an invented engine limit.

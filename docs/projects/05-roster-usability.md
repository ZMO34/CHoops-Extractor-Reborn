# Roster usability

Implemented confirmed choices. Handedness is 0 L and 1 R, traced through the localized Hand option array. Headband is No/Yes; home sock color is Black/White. Their packed edits preserve unrelated bits and use dropdowns.

The property viewer also labels verified build, muscle tone, appearance color, eye color, sock length and T-shirt choices. Enum values outside recovered choices remain explicit raw/unknown values. Binary values are not universally treated as booleans: muscle tone means Buff/Ripped, while sock color means Black/White.

Verified with packed-neighbor preservation tests and existing undo/round-trip checks.

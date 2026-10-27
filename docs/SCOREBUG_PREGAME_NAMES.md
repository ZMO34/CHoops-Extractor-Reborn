# Pregame nickname overlay investigation

**Name-source correction:** later roster and native checks show the generic
`team1city` / `team2city` provider normally supplies geographic location, not
school name. The broad generic table separately offers short-school-name
`team1name` / `team2name` providers; their persistent gameplay activation remains
unproven. See SCOREBUG_EXECUTABLE_ROUTES.md and DIRECTOR_RESEARCH.md. The
pregame-specific `team1namerecord` / `team2namerecord` providers below still
read plural nicknames; their similar names do not make the two tables identical.

The owner accepts automatic roster nicknames as well as school names. Their
screenshot shows Wildcats / Flyers below two logo towers, with the arena name
below. This is a different scene from the frontend team_matchup LAYT screen.
The scorebug goal still requires these names to remain beside the logos during
regular gameplay; a pregame-only reposition is not completion.

## Original resource and text providers

Vanilla overlaycache.iff is CDF-backed (0xF0985030), with its compressed scene
streams in overlaycache.cdf. Its 21 records include opening_intro_a, not merely
texture artwork. The decoded opening scene has three SCNE text records:
team1namerecord, team2namerecord and stadium. Each uses Stratum2 22 32 and starts
with alpha zero, so initial authored opacity alone does not describe visibility.
The source archive, CDF payload and executable are read-only.

Original executable analysis uses the documented Ghidra PowerPC A2ALT-32addr /
default setup and descriptor-specific TOCs. The native overlay descriptor array
begins at 0x1267BB00, registered with count 27 by 0x709EA0 -> 0x1971F4. Entries
are 0x7C bytes; index 3 at 0x1267BC74 selects opening_intro_a. Its name pointer is
0x124D74D0 and its text-binding-table pointer is 0x953528.

The text table contains 12-byte rows:

| Uppercase binding CRC | Binding | Provider descriptor | Selector |
| --- | --- | --- | --- |
| 0xD941FA55 | stadium | 0xA416B0 | 0 |
| 0x062025C7 | team1namerecord | 0xA416B8 | 0 |
| 0x9FC243C6 | team2namerecord | 0xA416B8 | 1 |

Descriptor 0xA416B8 points to 0x70EE00. It obtains the context team through
0x70938C, then wraps the runtime team's text pointer at +0x0C. Instructions at
0x70EE4C and 0x70EEE8 confirm that field access. This is the observed nickname
source, separate from the main HUD's gated city/abbreviation provider. In mode 2
it also supports a record-formatting branch; copying its output assumptions to
all modes is not warranted.

Context helper 0x70938C bounds a selector against the instance's context count.
It handles typed team/player context entries, and can select current home/away
teams through 0x57F050 / 0x57F064. The SCNE does not supply the roster context by
itself. The side order must come from the original activation caller, not a guess
based solely on labels team1/team2.

## Why copying this scene is insufficient

Generic overlay draw 0x197D9C walks SCNE text and uses the selected native binding
table. Main scorebug draw 0x4F442C instead invokes its own fixed 14-row provider
registry. Its initializer 0x4EF400 explicitly assigns each name/provider/draw
triple; adding a team1namerecord row to the main scene does not assign 0x70EE00.
That initializer also identifies event rows 12/13: providers 0x4F0CC0 / 0x4F0E1C
and draw wrappers 0x4F1ECC / 0x4F1EB8 -> 0x4F1620. The latter does per-glyph
popup rendering and consumes animated opacity; it is not the standard shrink-to-
width drawing path. No alpha override or purported popup width fix was installed.

The overlay update at 0x193448 advances instance time and invokes removal through
0x192C7C. Timing getters 0x196DD8, 0x196E14 and 0x196E48 read descriptor fields
+0x4C/+0x50/+0x54/+0x58. For opening_intro_a those are 0, 1, 4.5 and 1. Exit
phase timing is therefore owned by the native descriptor, not inferred from the
SCNE's last animation key. 0x192C7C can transition to the exit phase or deactivate
the instance, invoking 0x1970E0 and associated callbacks. Simply extending the
asset animation does not remove that lifecycle.

This establishes a real alternate roster-nickname provider and its exact scene,
but no IFF-controlled persistent activation route yet. Reusing it for the
scorebug would require a proven data-owned trigger/lifetime/context route, or an
existing always-active consumer with that provider table. Neither is installed.
No EBOOT edit, guessed callback pointer, uniform routing or roster-color encoding
was added. The candidate is not packaged and automatic names remain unfinished.

An initial read-only inspection also located the director DRCT resource in
Director.iff; its inner format is not decoded. It is not evidence that a script
can safely request a permanent overlay. Unknown fields remain read-only.

## Internal candidate preservation correction

Comparing the opening scene's text-row metadata exposed an unrelated assumption
in the private text-row clone helper: it replaced word +0x44 with a CRC of the
new binding. That field is not established as the binding hash and differs
across source scene families. The helper now preserves the donor word verbatim;
it does not assign a speculative semantic label. This changes three cloned rows:
one branding row and two comparison value rows. Their donor words in these
sources are zero. Other original row words, geometry and skeleton counts remain
preserved by the existing rebuild checks. This is a preservation correction,
not a claim that native text visibility or automatic names are fixed.

The internal vanilla-based two-IFF candidate was regenerated. Twenty-one local
scene/comparison checks pass, three real clone/donor word comparisons pass, and
source-bound preflight prepares the exact two candidate files. No full JB,
emulator run, ZIP, or new test package was created. Required names and native
appearance are still unverified.


## Follow-up: school-name preference and Director commands

The owner prefers school names, retaining nicknames as a fallback. Subsequent
research finds a location formatter and actual Director command
operations for pending overlay selection, context, duration and submission.
This supersedes the earlier purely undecoded-DRCT status; it does not yet prove
persistent activation or safe script writing. See DIRECTOR_RESEARCH.md for exact
functions, table identities, reader API and verification limits.

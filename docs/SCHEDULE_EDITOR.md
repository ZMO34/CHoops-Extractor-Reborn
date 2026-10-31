# Season schedule editor

## Why realignment did not change schedules

The roster payload stores a complete pre-built regular season. New Legacy-mode
saves copy it. Conference realignment (`move_team_to_conference`) only rewrites
the reciprocal team/conference links, so the stored games keep the original
2007-08 conference pairings. Use **Roster Editor → Season schedule… → Rebuild
conference games…**, then save a roster copy, before starting a new Legacy.
Existing Legacy saves are not changed.

## Format evidence (roster payload offsets)

- Header `+0x30` = slot count, `+0x34` = relative pointer (bias 1). The stock
  and 2026-27 community rosters both hold 5,523 slots of 20 bytes directly
  after the teams table.
- Record: `u32 key, u16 team1, u16 team2, u32 flags, u16 site, u16, u32`.
- Key = `year-2000 << 25 | month-1 << 21 | day << 16 | minutes << 5 | index`.
  Stock opener 2007-11-09 decodes from `0x0F49....`; all 4,523 stock keys are
  sorted and unique, months fall in Nov–Mar.
- Flag bit 27 (`0x08000000`) marks conference games: stock conference-game
  clusters exactly match the original team-index conference blocks.
- Dated games come first, then explicit empty markers (`teams 0x7FFF, site
  0xFFFF`, 64 in stock), then all-zero records (936). The editor never writes
  the zero records: Legacy mode appends its own early-season tournament,
  postseason and classics games there (about 270 in observed saves), so they
  must stay free. Editor capacity = dated games + empty markers (4,587 stock).
- In Legacy saves the same table records results: bit 29 (`0x20000000`) marks
  played games, and the last two fields hold scores. Tournament games use flag
  `0x13000000` and a real site (arena) value.
- Team index = roster `teams` row index (0–338 current D1 in stock).

Unresolved: which stored team is home (kept in stored order, shown as Team 1 /
Team 2); meaning of `site` (0xFFFF except one stock game) and the trailing
fields (always 0); whether all-zero tail records are usable. Unknown bits are
preserved on every write.

## Editor behavior

- Lists all games with date, tip-off, teams, conference flag and whether the
  teams are conference-mates now; filter by team, search, or show mismatches.
- Add / edit / delete games. Conference flag can be automatic (same current
  conference), forced on or off. Duplicate keys get the next free index or a
  spare tip-off time.
- Rebuild per conference (spin box per conference; "Keep stored games" leaves a
  conference untouched; unchanged conferences default to Keep): drops
  conference games between former members, re-flags games between current
  members, keeps stored meetings that fit a circle-method round robin cut at the
  target, trims extra meetings over the target, and places the missing meetings
  on existing conference dates without double-booking (one rest day preferred).
  Targets above a double round robin repeat meetings. Teams outside 22–32 total
  games are reported. Over-capacity plans are refused.
- Balance game totals (default 24–31): removes non-conference games from teams
  over the maximum, against the busiest opponents first, then adds
  non-conference games for teams under the minimum against teams that are not
  conference-mates and have not met, on existing non-conference dates without
  double-booking. Conference games are never removed; teams that cannot be
  fixed are listed.
- Every write is one undoable roster edit, reparses the table, and rejects any
  change outside the table range.

## Season year

Legacy mode generates its tournament games in its own season year and keeps
only month/day of the stored games' calendar. Stock executables run 2007-08,
matching stock roster dates. A 2026-27 executable patch generated its
tournaments in Nov-Dec 2026 while the stored games stayed in 2007-08: the
season-schedule screen showed no games for a team and the sim stopped advancing.
**Season year…** (CLI `--season-year`) moves every game to the chosen season,
keeping month, day and tip-off; Feb 29 games move to Feb 28 or Mar 1 when the
target year is not a leap year, avoiding double-booking. Match the year to the
executable you play with.

## Conference tournaments

Conference +0x1E is the tournament calendar offset: the conference tournament
starts on March <offset> of the season's second year (2026-27 Legacy save:
AEC/Patriot brackets on March 5, MAAC/Big Sky/Summit on March 6, SWAC on
March 10, matching offsets 5, 6 and 10). Every member must finish all
regular-season games, conference and non-conference, by March <offset - 1>:

- Conferences whose members still had games on or after the start day (A-Sun,
  Sun Belt, Horizon, MVC, OVC) got no tournament records at all.
- NEC (offset 4) had one member with a regular-season game on March 4. Its
  bracket was created without the play-in game, leaving "Stony Brook vs TBD"
  unfillable, and the sim could not advance past March 4/5.

The owner's realigned community roster already had 24 games on or after a
team's tournament start; route 96 conferences have no tournament and no limit.
Rebuild re-places conference games before each deadline, removes non-conference
games on or after either team's deadline, and balancing never adds games past
it. The report counts remaining games on or after a team's tournament start.

Conference +0x1C is the tournament qualifier count. Native construction copies
it without clamping into 16 entrant slots, and qualifier selection reads that
many ranked members (see the Legacy scheduling research). Realignment can leave
counts above membership (Atlantic Sun 10 with 5 members, Pacific-12 12 with 7).
Rebuild lowers such counts to min(members, 16) by default (CLI
`--keep-tournament-slots` to skip); counts are only ever lowered.

## Command line

```
roster-schedule-report INPUT
roster-schedule-rebuild INPUT OUTPUT [--target CONF=GAMES]... [--keep-former] [--balance MIN:MAX]
                        [--season-year YEAR] [--no-rebuild] [--keep-tournament-slots]
```

`CONF` is a conference index, abbreviation or name. Without `--target`,
changed conferences use the default target and unchanged conferences are kept.
The output is a separate roster copy with an `.edit_report.json`.

## Verification

`tests/test_roster_schedule.py` (synthetic fixtures). Read-only check on a
private community roster: 4,523 → 4,572 games after rebuild, 0 conference flag
mismatches, 0 double-booked team dates, save/reparse valid, all bytes outside
the table identical. Balancing that copy (24–31): 18 removed, 21 added, every
current D1 team at 24–31 games, still 0 double-booked dates. Not
gameplay-tested; no emulator run. Season year 2007 → 2026 on that copy: 9 Feb 29
games moved, 0 double-booked dates. The tournament-year diagnosis comes from
read-only comparison of owner-supplied Legacy saves. Tournament check on the
installed 2026-27 copy: 13 qualifier counts lowered (only those conference
fields changed outside the table); with the start-day rule 18 conference games
moved and 1 non-conference game removed, leaving 0 games on or after a team's
tournament start and every D1 team at 24-31 games.

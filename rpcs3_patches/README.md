# RPCS3 game patches (College Hoops 2K8, BLUS30078)

`BLUS30078_imported_patch.yml` is an RPCS3 patch file for the 2026-27
year-patched EBOOT (V4.2 base build, PPU hash
`cd3a6cffbf5c1930053d0873658d0f3c46e19c8b`). Copy it to
`<RPCS3>/patches/imported_patch.yml` (or import it from Manage > Game Patches)
and enable the entries you want. These are emulator patches only; the editor
does not patch executables.

| Group | Entries |
| --- | --- |
| Frame rate | 60 FPS (all screens): also set Vblank Rate 60 in the game's custom config |
| Poll rank | Scorebug (`#5 DUKE`), Legacy Team Select (`#6 ILLINOIS`), pregame matchup card (`#6 Fighting Illini (13-0)`) |
| Scorebug record | Scorebug team names with poll rank and season record (`#5 DUKE 12-3`); replaces the poll-rank scorebug entry |
| Recruits | Taller centers, taller guards/wings, skilled PF/C, international tiers |
| Transfers | Frequency levels, unhappiness levels, no sit-out |
| Quick Game | LT/RT team cycling in conference member order (alphabetical once the roster's member lists are sorted) |
| Rules | 30-second shot clock (was 35) |
| MyPlayer | Sit on the bench with your player (needs the game's Player Lock ON) |
| Coach Carousel | No minimum years at your school before your coach gets job offers |
| MyPlayer v2 | Bench, ratings that grow from your game stats, a starting lineup on merit, and a chosen position (Off / PG / SG / SF / PF / C in Game Settings) |
| NCAA Tournament | 68 teams with a four-game First Four (Stage 1, plus a DEBUG copy that logs the bracket build); First Four on the Tournament Tree (Stage 2) |

Each entry's `Notes` field describes what it changes and which entries it must not
be combined with.

## Poll-rank code caves

The Team Select and matchup entries are RPCS3 `calloc` blocks at the game's own
STR_FROM call sites (Team Select 0x6E42D8, matchup mascot 0x70EEEC). They make the
original call, look the team up in the media poll (0x5BDB44, slots 0-24), and when
ranked rewrite the text with the game's formatter and English templates `#{0}` and
`{0} {1}`. The scorebug entry replaces the two scorebug name providers in place.

Do not turn the Team Select STR_FROM call into a nop: another path (0x6E4724)
branches in just before it, and doing so crashed the game.

## Scorebug season record

`Scorebug: team names with poll rank and record (#5 DUKE 12-3)` puts RPCS3 `calloc`
blocks at the two scorebug team-name providers (home 0x4EF9A4, away 0x4EFABC; the
stock first word at both is `cmpdi r3,0`). Each block is a whole replacement
provider that returns to the caller itself, so it has no size limit. It builds the
name and poll rank exactly like the poll-rank entry, then appends the record with
the game's formatter and English template 0x4F6600F7 `{0} {1}-{2}`.

The record comes from the pregame matchup card, which formats `({0}-{1})`
(0x3DE3C74B) natively at 0x70F5D0: it gets the team through 0x70938C, which
returns the same per-game team objects as the scorebug (0x57F050 home, 0x57F064
away), and reads wins and losses as bytes at team +0x1FC and +0x1FD. The card shows
the record only when the game-mode word (0x4A3924, library 0x72330) is 2; the
scorebug block uses the same check, and also leaves out a 0-0 record. Which
named mode the value 2 is has not been established beyond this shared gate.

Enable it instead of `Scorebug: team names with poll rank (#5 DUKE)` and
`Scorebug: team names`; all three patch the same providers. Like the poll-rank
entry it drops the provider's game-mode-4 special text. Regenerate and check with:

```
cd rpcs3_patches/tools
python record_test.py          # interpreter run of the real cave bytes
python record_write.py         # (re)write the entry into BLUS30078_imported_patch.yml
```

## Quick Game team cycling

LT/RT normally steps through a conference in team-table order, so teams moved in by
realignment appear after the conference's original schools. The entry places
`calloc` blocks at the library walkers nthTeamInConference (0x1BF690),
nextTeamInConference (0x1BF93C) and prevTeamInConference (0x1BF82C). For every
conference except 32 (the all-D1 list) they walk the conference member list
(roster conference +0x6E0, count +0x870) with the game's own team filter.

Do not try to get this order by moving team records in the roster: the game keys
something outside the roster on table position, and a reordered table crashed it.

## Shot clock

The reset value is the float 35.0 at library TOC +0x6714 (0xA5B1DC), read only by
the shot-clock reset code (0x3C80B4, 0x3C8568, 0x3C8580), which stores it as the
live, reset and maximum shot clock (game state +0x280/+0x284/+0x288). The entry
writes 30.0 there.

## MyPlayer bench

The game's own Player Lock (Options > Game Settings; settings block 0x1283958C,
word +0xF8) stops every automatic switch of the controlled player, but a substitution
still hands control to the sub: the five on-court slots of a team stay fixed (list
head 0x12ACCDC0, next slot +0x5C) and a sub swaps the player data (slot+0x04, with its
controller record at slot+0x10) into the same slot. The controller record's first
word is the user number, -1 for CPU; 0x29CA70 swaps two records.

`MyPlayer: sit on the bench with your player` is a code cave at the start of the
per-frame control update 0x29DCBC (controller 1, Player Lock ON only). It remembers
your player (the one you control when play starts, or after a pause in which you
picked someone else). While he is off the court, the controller record of whoever
holds your controller is swapped into a spare record inside the cave, so the CPU
plays the whole team; when he is back in any slot, control is swapped to him. Its
four state words and the spare record live at the start of the cave (jumped over).
The settings block and the slot layout were found with the `myplayer_*` probes.

### MyPlayer v2: progression and merit lineup

`MyPlayer: bench, progression from game stats, starting lineup on merit` replaces the
bench entry (enable only one; both hook the same place). It identifies your player by
the name pointers of his per-game object (slot+0x64, +0/+4), finds his roster row
(roster header *(0x1252F5E8+8), players at +0xC, stride 0x134) and his team row.

Progression: his box score is at *(obj+0x14)+4 (index 0 = game total). Every frame the
cave compares the counters with the last values it saw and, for each new made shot,
rebound, assist, steal or block, adds hundredths to ratings (stored x100, cap 99) both
in the game object and in the roster row; a turnover costs 0.02 Ballhandling. Gains
per unit are the `GAINS` table in `tools/myplayer_mode.py`. The roster change persists
only when the roster or Legacy is saved.

Merit lineup: when a new game starts (new object, or counters back to zero), the
game's own CPU lineup routine 0x51CE24(team, 0) and rotation routine
0x771254(team, 1, 0) run on his team (TOC 0xA64A94), so starters and minutes follow
the current ratings; the new order shows from the next game. AST/STL/BLK/TO offsets
(0x120..0x12C) are inferred from the box-score column order.

Position (v2.1): the option row (Game Settings table at 0x12F352C0, 0x5C per row,
built by the static constructor 0x67F8B8) is switched from widget type 5 (ON/OFF
pill) to type 7 (text list, as Play Mode / Attendance) by a cave on its type store
`stw r12,0x2E0(r9)` at 0x681004. A text-list box is as wide as the widest caption
its +0x24 function measures (0x68541C: table r6, indices r4..r5 via 0x4A1214); a cave
there and `li r5,5` at 0x685428 make it measure the six captions instead of Off / On.
The MyPlayer option in Game Settings then cycles Off, Point Guard,
Shooting Guard, Small Forward, Power Forward, Center (settings +0xF8 = 0..5; from Off
the first step is Point Guard). Three small caves replace the option's two arrow
handlers (stores at 0x685364 / 0x6853B0, which flipped the word with `v == 0`) and
the caption lookup (0x68B014), which now indexes a six-entry table: the game's own Off
caption (*0x12839474) and the english.iff strings 0x1732BE2F, 0x6204EEE1, 0x579CFFC9,
0x79A66D2B, 0x1941965F (Point Guard .. Center); english.iff is unchanged. Game code
reads the word only as zero / non-zero (0x4BDD94, 0x67E8F4). On a change of value, on
the first frame, and when a new game starts without your player on the team you
control, your player becomes the on-court teammate whose roster position (row +0x2B,
0 PG .. 4 C) matches, else the player you control. After the lineup routines run, he
is swapped into the starting row of the depth chart (team row +0xCC: 7 rows x 5
position words, cleared by 0x51CE24) at that position. Not verified in game: whether
the settings save keeps values above 1, and whether the depth chart holds roster row
pointers (if it does not, the swap finds nothing and changes nothing).

Transfer (v2.2; alphabetical since v2.7: the arrows step to the next / previous
school by short name, a-z folded, skipping teams without a name, with Off at both
ends; v2.8: right arrow (row +0x18) steps forward, only current D1 teams, team type
at team row +0x2BC bits 15..17 = 0): a 19th Game Settings row, "Transfer", cycles Off and every school
(team row +0x00, the short name; UTF-16 pointer shown through 0x1E1000). The menu
reads row i at menu+0x1C + i*0x5C and the count at menu+0x40 (0x13009C, 0x13A6DC;
Game Settings menu at 0x9EEE24); a cave at the settings constructor's last store
(0x683FC8) copies the 18 rows into a 19-row buffer, adds the new row (template: the
MyPlayer row; own max / value / arrows / caption / width functions through OPDs
built at run time) and repoints the menu. The choice and your player's roster and
team rows live at 0x13076F00 (last page of the BSS, after its end 0x13076138), so
it is lost when the game closes. Legacy's offseason transfer pass (0x5BC250) works
through a list at 0x12EA39A8 (12-byte entries: player, old team, new team; count
*0x12EA4C74): remove (0x7644B8) then mark transfer + redshirt 2 and add (0x764548).
A cave at its start appends your player (or retargets his entry) and clears the
choice. (v2.2 also had a MyPlayer-only cave on `oris r0,r0,0x800` at 0x5BC334; v2.4
drops it because it shares that address with the existing "Transfers: No sit-out"
entry, which already makes every transfer eligible at once.) Not verified in game: the school-name pointer offset (derived from roster
slots at file +0x6C vs runtime +0x3C), and that the pass runs after the choice.

Coach follows the transfer (v2.3): the carousel probe (`tools/myplayer_carousel.py`)
showed the openings list at 0x12D9CE88 (0x14-byte entries: team, previous team,
previous coach, hire, flags; count *0x12D9E9E0, current *0x12D9E9E4), the candidate
list at 0x12D9EA00 (7 entries: coach, score; built by 0x5934A0 for the current
opening) and user profile 0 at 0x12E30DC8 + 0x28 (+4 = that user's coach). The
season-end review 0x594BDC opens jobs through 0x5930D4, 0x765E38 and
0x593884(team, coach, reason); a cave after its team loop (0x594EE8) does the same
for the Transfer school unless your coach (+8 team index) is already there, and a
cave at the candidate builder's epilogue (0x5935D8) puts your coach first for that
opening, so the dialog 0x5940A8 offers you the job and accepting runs the game's own
move (old school opened with reason 2, user flags copied, profile updated by
0x5999CC). The choice is cleared once both your player and your coach are there.
Not verified in game.

Player follows coach (v2.5): when the carousel accept code (0x5940A8) makes user 0's
coach the coach of a new school (`stw r30,0x30(r31)` at 0x5946DC, r28 = his previous
school), a cave moves your player from r28 to r31 at once with 0x7644B8 / 0x764548 and
sets his transfer flag (+0x8C bit 31). Your player is SCR_ROW if he is on r28's
roster, else r28's depth-chart starter at the MyPlayer position, so it also works when
he has not played a game since the game was started. Not verified in game.

Coach Carousel years limit (`tools/carousel_years.py`, separate entry): a coach's
years at his school are coach +0x24 (0x73A07C). The candidate builder skips an
employed coach with 1 year or less (`cmpwi cr7,r3,1` at 0x5937C8); a cave passes the
test for user 0's coach only. The carousel screen shows "you have not been with your
current team long enough" from the same test; `bgt` at 0x63616C becomes `b`.
Not verified in game.

Camera: the game's camera table (*TOC-0x7A8C = 0x12C75498, 31 rows of 0x2C: +0 mode,
+4 caption) already has a Player Lock camera (mode 0x20, caption 0xC80F7FBB). It
follows the controlled player and, sharing the relabelled caption, shows as
"MyPlayer" in Camera Options; with the bench patch it follows your player.

## NCAA First Four (68 teams)

The stock field is 65 teams with one play-in game (event 90: the two lowest automatic
bids, winner to East 16). Stage 1 turns this into a four-game First Four without
changing the save layout, so it can be enabled in an existing Legacy before Selection
Sunday:

| Game | Teams | Day | Winner to |
| --- | --- | --- | --- |
| event 90 | two lowest automatic bids | Tuesday | East 16 |
| event 2 | next two lowest automatic bids | Tuesday | South 16 |
| event 3 | last at-large team in vs first team out | Wednesday | Midwest 11 |
| event 4 | second and third teams out | Wednesday | West 11 |

Events 2-4 are the 2K Sports Classic first-round events, which are finished by March.

- Selection (0x5C1D30; also the projection screen 0x5BFCDC) marks the four lowest
  automatic bids as play-in teams. The NIT fill (0x5C2124) leaves out the three best
  teams outside the field, which become the extra at-large play-in teams.
- The bracket builder (0x590084) is replaced. It points link-table rows 0-2 at the
  regionals, and falls back to the stock builder if the field does not have four
  play-in teams. The real selection stores automatic bids as type 0 and at-large as
  type 1, so the builder reads the at-large type from the best candidate.
- While events 2-4 hold a play-in game (state type 3, two teams), the five readers of
  the event record table (0x58C270, 0x58F234, 0x58F600, 0x58F700, 0x58F8A4) use event
  90's record, giving the "NCAA Play-in Game" name and schedule config.
- NCAA appearances (0x5C19E0) are credited from the built bracket, so all 68 teams
  count; play-in teams get the seed of the slot their game feeds.
- The season reset does not restore link rows, so eventBuild (0x58F848) and game finish
  (0x58F310) put the Classic rows back to (e, 6, e-1) whenever events 2-4 are built or
  finish as holiday events.

Stage 2 (needs Stage 1) covers the Tournament Tree. Its NCAA pages are every type-3
event with games in event order, so events 2-4 already appear before event 90. The
NCAA tree is one bracket with a single play-in box; the entry makes that box show the
open First Four page's game (0x65A548), makes LT/RT step from the page on First Four
pages (0x65FD60, 0x65FE98), and redraws the bracket and places the cursor on the box
when a new First Four page's game is not on screen yet (0x65A264). It also hides seeds
on those pages (0x65DC28, 0x65DCA0) and shows "PLAY-IN GAME WINNER" in every regional
slot a First Four game feeds (0x65DF24, 0x65DE88, 0x65DEE0, 0x65E7F4; in Legacy the
unknown team is drawn from 0x65DE88). The Selection Sunday Show finds a team's region
(0x5E89BC) only in events 91-94 and 90; Stage 2 also gives teams in events 2-4 the region
their game feeds. Its seed lookup is unchanged, so play-in teams show no seed, as in stock. The show's data step
fills each regional's empty slot with the teams of the First Four game feeding it (0x5EC420,
0x5EC43C; an 11-seed slot gets the first team, 0x5EC438/0x5EC44C), and the game presentation
seed (0x5F9A08) gives First Four teams 16 or 11. Its First Round Games boxes name each
play-in matchup ("Team A vs. Team B", template 0x0018C1FB) instead of "Play-in Winner"
(0x5E6034). Stage 1's undecided 11-seed slots crashed the show's commentary (a line
reads the opponent's conference, 0x5EA374); Stage 2 gives the commentary the first team of the
feeding First Four game whenever its featured team is empty (0x5E92A8). The show's play-in team
values (speech variables 0x7E/0x7F, 0x5E925C/0x5E9274) name the First Four game feeding the
current matchup, or no team for a matchup without one.

### Selection Show commentary

The announcer's lines come from the `director` record in Director.iff, run on the game's
script VM (0x77D2C0, one native call per step; opcodes map through the record's import
table). The show only raises a generic event (0xD9); the dispatcher (0x592C0) builds
candidates with a compiled line tree (0x60310), whose conditions are value expressions
evaluated by 0x5BABC (facts via 0x77F670 and 0x77F798), then tries them in order through
the line check 0x59D30 and starts the first that passes. Three things kept the play-in
line to East:

- The 1-16 line group is the only one with play-in lines, and its tree reaches them only
  when the matchup's team 1 is in region 91 (East), where stock's single play-in game went.
- Every show line has repeat setting 0 (once per show), and 0x59C6C stamps a line when it
  plays, so East used it up.
- The group's seed lines are always available as alternatives.

Stage 2 adds three caves. 0x5BABC returns team 1's seed as 1 and its region as 91 for the
group's two feature expressions whenever a First Four game feeds the current matchup, so
fed 1-16 and 6-11 matchups take that branch. 0x59D30 lets the play-in lines (team A, then
team B) play for fed matchups, refuses them elsewhere, and holds back that group's seed
lines for fed matchups. 0x59C6C does not stamp the two play-in lines. The group's nodes are
recognised by their bytecode, so Director.iff stays stock. A school with no recorded
name clip (for example one that joined Division I after 2007) is not spoken.

## Tools

`tools/` holds the generators and offline checks (Python, `keystone-engine` and
`capstone`; paths to the decrypted EBOOT and the RPCS3 patch file are set at the
top of each script):

- `rank_asm.py`: scorebug providers; `rank_interp.py` runs them in a small PPC64
  interpreter with modeled game calls (Unicorn's PPC64 is not usable here).
- `rank_hook_asm.py`: shared assembler (hand-encoded branches, position
  independent) and the poll-lookup body.
- `rank_site_asm.py`, `rank_site_test.py`, `rank_site_write.py`: Team Select and
  matchup caves, their tests, and the writer that updates the patch file.
- `probe_asm.py`, `probe_test.py`, `probe_patch_write.py`: diagnostic probes that
  write `TAG caller-address [text]` to `log/TTY.log` through sys_tty_write. This is
  how the real name call sites and the team cycler were found; leave them out of
  normal play. Besides text and an index, a probe can log the stack back chain
  (`bt_test.py`) or dump six words from a register or computed address.
- `show_probe_write.py`: the Selection Show commentary probe entry (variables, tokens,
  director facts and their values, speech stream lookups; not shipped).
- `cycler_asm.py`, `cycler_test.py`, `cycler_step_test.py`: Quick Game cycling
  caves and their tests.
- `first_four_asm.py`, `first_four_test.py`, `ff_debug_test.py`: First Four Stage 1
  caves (and the DEBUG builder report) and their tests.
- `first_four_tree_asm.py`, `first_four_tree_test.py`: Stage 2 Tournament Tree and
  Selection Show caves and their tests. The commentary tests read a locally extracted
  `director` record from Director.iff (game data, not included; path at the top).
- `ff_patch_write.py`: writes the three NCAA Tournament entries into the patch file.
- `tree_probe_write.py`: diagnostic Tournament Tree navigation probes (not shipped).
- `myplayer_bench.py`: the MyPlayer bench cave and its patch entry.
- `myplayer_mode.py`: MyPlayer v2 (bench, progression, merit lineup) and its patch entry.
- `myplayer_probe.py`, `myplayer_scan.py`, `myplayer_court.py`: diagnostic probes
  used to find it (menu controller table, settings block scan, user-controlled slot
  and team list every ~3 s); not shipped.

These checks only model the game. Confirmed in-game: all three poll-rank entries
(scorebug, Team Select, matchup card), the transfer entries, Quick Game cycling, the
30-second shot clock, the MyPlayer bench, and both NCAA Tournament stages (four play-in games, winners in
East 16 / South 16 / Midwest 11 / West 11, appearance credit, the next season's 2K
Sports Classic, the four play-in pages on the Tournament Tree, and the Selection Show
naming every First Four matchup on screen and in the commentary: East and South 1-16,
Midwest and West 6-11).

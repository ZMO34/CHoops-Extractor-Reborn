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
| Recruits | Taller centers, taller guards/wings, skilled PF/C, international tiers |
| Transfers | Frequency levels, unhappiness levels, no sit-out |

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
  how the real name call sites were found; leave them out of normal play.

These checks only model the game. Confirmed in-game: scorebug rank and the transfer
entries. Not yet confirmed in-game: the Team Select and matchup rank caves (the Team Select crash fix above has only been checked offline).

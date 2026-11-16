"""MyPlayer v2.2: bench + progression from game stats + starting lineup on merit + position + transfer.

Transfer (v2.2): see transfer_sources().

Position (v2.1)
  The MyPlayer option in Game Settings (Player Lock, settings +0xF8) cycles Off,
  Point Guard, Shooting Guard, Small Forward, Power Forward, Center (0..5; turning it
  on from Off gives Point Guard). See menu_sources(). When the value changes, on the
  first frame, and at a new game where your player is not with the team you control,
  your player is taken from the on-court players of your team whose roster position
  (row +0x2B) matches; if nobody matches, the player you control. After the lineup
  routines run, forcepos puts him in the starting row of his team's depth chart
  (team row +0xCC, 7 x 5 words, column = position) at the chosen position, swapping
  with whoever was there. A manual pick (pause, choose someone else while your player
  is on court) still works as before.

One code cave at the start of the per-frame control update 0x29DCBC (see
myplayer_bench.py for the bench mechanics). Runs for controller 1 while the game's
MyPlayer setting (Player Lock, settings 0x1283958C + 0xF8) is ON.

Your player
  Identified by the two name pointers at the start of his in-game player object
  (court slot + 0x64 -> object; object +0x00 / +0x04 are copies of his roster row's
  name pointers), so the identity is the same player in every game. Captured as
  before (first frame, or after a pause in which you picked someone else).

Roster row and team row (found once per capture)
  Roster header R = *(0x1252F5E8 + 8): players count R+0x08, rows R+0x0C (0x134 each,
  getter 0x1BB970); teams count R+0x28, rows R+0x2C (0x2C0 each, getter 0x1BBB58).
  His row has the same name pointers. His team row lists him in its roster slots
  (+0x3C, count halfword +0x158).

Progression (while he is on court)
  Game totals are read from his game stats block S = *(object + 0x14) + 4 (index 0 =
  whole game, as the box score's stat getters 0x1625xx read them): FTM +0x08,
  2PM +0x10, 3PM +0x18, OREB +0x100, DREB +0x104, AST +0x120, STL +0x124, BLK +0x128,
  TO +0x12C. Each new made shot / rebound / assist / steal / block / turnover adds
  the gains in GAINS (hundredths of a rating point, ratings are stored x100 at
  +0x2C + 2 * index, capped at 99.00) to both his in-game object (effect now) and his
  roster row (kept by Legacy saves). A drop in a counter (new game) only resets it.

Starting lineup on merit
  When a new game is detected (his game object changes, or his counters drop back to
  zero because a new game reuses the object), the game's own CPU routines
  0x51CE24(team, 0) (lineup) and 0x771254(team, 1, 0) (rotation / minutes) run on his
  team row, the same pair the game runs for CPU-managed teams (e.g. 0x6FA008). The
  result is used from the next game on.

Block data (jumped over):
  +0x00 ME0  +0x04 LAST  +0x08 PARK  +0x0C TB  +0x10 SPARE (0x40)  +0x50 ME1
  +0x54 ROW  +0x58 OBJ   +0x5C..+0x7C counters (9)  +0x80 TEAM  +0x84 POS
"""
import os
import sys

import myplayer_probe as P
import myplayer_bench as B

HOOK = 0x29DCBC
SWAP = 0x29CA70
LINEUP, ROTATION = 0x51CE24, 0x771254
TOC2 = 0xA64A94                      # TOC of the 0x5xxxxx-0x7xxxxx module (lineup / rotation code)
LOCK_FLAG = 0x1283958C + 0xF8
PLAYERS = 0x12ACCDC0
ROSTER = 0x1252F5E8                  # *(this + 8) = roster header
GAP = 0x01000000
TITLE = 'MyPlayer: bench, progression from game stats, starting lineup on merit (requires MyPlayer ON)'

ME0, LAST, PARK, TB, SPARE, ME1, ROW, OBJ, CNT, TEAM, POS = 0x00, 0x04, 0x08, 0x0C, 0x10, 0x50, 0x54, 0x58, 0x5C, 0x80, 0x84
DATA_WORDS = 0x88 // 4
ROW_POS = 0x2B                       # roster row: position code byte (0 PG .. 4 C; file row +0x3B)
DEPTH = 0xCC                         # team row: depth chart, 7 rows x 5 positions (words), cleared by 0x51CE24
DEPTH_WORDS = 35

# The MyPlayer (Player Lock) option in Game Settings: its two arrow handlers and its caption.
MENU_RIGHT, MENU_LEFT, MENU_TEXT = 0x685364, 0x6853B0, 0x68B014
MENU_TYPE = 0x681004                 # static constructor: stores the option's widget type (5 -> 7)
MENU_WIDTH = 0x68541C                # option's box-width function: caption table load
MENU_MAX = (0x6853F4, 0x38600001, 0x38600005)     # option's max-value function: li r3,1 -> li r3,5

# Transfer (v2.2). Shared words in the last page of the game's BSS (segment ends at
# 0x13076138; this 4 KB page is mapped with it and otherwise unused): the menu row,
# the main cave and the transfer-pass cave all reach them by absolute address.
SCR = 0x13076F00
SCR_DEST, SCR_ROW, SCR_TEAM, SCR_FORCE = 0x0, 0x4, 0x8, 0xC   # DEST: 0 = stay, k = team index k - 1; FORCE: opening to offer you
SEASON_REVIEW_END = 0x594EE8         # season-end coach review, after its team loop (li r0,0)
CANDIDATES_END = 0x5935D8            # carousel candidate-list builder, epilogue (r28 = current opening entry)
FIRE_PREP, FIRE_DETACH, ADD_OPENING = 0x5930D4, 0x765E38, 0x593884
OPENINGS, OPENINGS_COUNT = 0x12D9CE88, 0x12D9E9E0   # 0x14-byte entries: team, previous team, previous coach, hire, flags
OFFERS, OFFER_SLOTS = 0x12D9EA00, 7  # candidate coaches for the current opening: coach, score (float)
PROF_COACH = 0x12E30DC8 + 0x28 + 4   # user profile 0 + 4: that user's coach (0x599ABC); +0 = his school
COACH_MOVED = 0x5946DC               # carousel accept: stw r30,0x30(r31) (new school's coach = hire)
TEAM_REMOVE, TEAM_ADD = 0x7644B8, 0x764548   # (team, player), as the transfer pass calls them
TRANSFER_PASS = 0x5BC270             # offseason transfer pass, first instruction after the prologue (lwz r0,0(r9); r9 = count)
TRANSFER_LIST, TRANSFER_MAX = 0x12EA39A8, 400     # entries of 12 bytes: player row, old team, new team
SIT_OUT = 0x5BC334                   # oris r0,r0,0x800: redshirt status 2 (transfer, sits a year)
SETTINGS_END = 0x683FC8              # last store of the settings-table constructor (stw r8,0x444(r10))
GS_MENU = 0x9EEE24                   # Game Settings menu: +0x18 rows end, +0x1C rows begin, +0x40 row count
GS_ROWS, GS_COUNT, ROW_SIZE = 0x12F34FE0, 18, 0x5C
MYPLAYER_ROW = 0x12F352C0            # template for the new row (type 7, same min / visibility functions)
TRANSFER_LABEL = 0xE9782C83          # english.iff "Transfer"
STR_FROM_TEXT, STR_ASSIGN = 0x4A2034, 0x49D604   # stubs: string handle = UTF-16 text / = handle
MAIN_TOC = 0xA64A94
TEAM_TYPE = 0x2BC                    # team row: type (bits 15..17): 0 = current D1 (schema TEAM_TYPES)
WIDTH_LAST = (0x685428, 0x38A00001, 0x38A00005)   # li r5,1 -> li r5,5 (last caption index)
OFFON = 0x12839474                   # the game's shared Off / On caption table (filled at boot)
POSITION_TEXT = (0x1732BE2F, 0x6204EEE1, 0x579CFFC9, 0x79A66D2B, 0x1941965F)   # english.iff: Point Guard .. Center

RATING = ('Shooting (Close)', 'Shooting (Med.)', 'Shooting (3 Pt.)', 'Free Throws', 'Layups', 'Dunking',
          'Shoot Off Dribble', 'Shoot In Traffic', 'Standing Dunk', 'Ballhandling', 'Passing', 'Stamina',
          'Low Post Off.', 'Low Post Def.', 'Off. Rebounding', 'Def. Rebounding', 'On Ball Def.', 'Blocking',
          'Stealing', 'Speed', 'Def. Awareness', 'Off. Awareness', 'Clutch', 'Commits Fouls', 'Quickness',
          'Vertical', 'Strength', 'Hustle', 'Durability', 'Consistency')
R = {n: i for i, n in enumerate(RATING)}

# stat: (offset in S, [(rating, gain per unit in hundredths)])
GAINS = [
    ('2PM', 0x010, [('Shooting (Close)', 6), ('Shooting (Med.)', 4), ('Layups', 3), ('Shoot In Traffic', 2)]),
    ('3PM', 0x018, [('Shooting (3 Pt.)', 15), ('Shoot Off Dribble', 3)]),
    ('FTM', 0x008, [('Free Throws', 12)]),
    ('OREB', 0x100, [('Off. Rebounding', 15)]),
    ('DREB', 0x104, [('Def. Rebounding', 12)]),
    ('AST', 0x120, [('Passing', 12), ('Ballhandling', 4), ('Off. Awareness', 3)]),
    ('STL', 0x124, [('Stealing', 20), ('On Ball Def.', 5)]),
    ('BLK', 0x128, [('Blocking', 20), ('Def. Awareness', 3)]),
    ('TO', 0x12C, [('Ballhandling', -2)]),
]
assert len(GAINS) == 9


def hl(v):
    return P.hi_lo(v)


def bench_src():
    """The bench logic of myplayer_bench (v1.1) with name-pointer identity; ends at 'benchdone'."""
    return f"""
    li 16, 0
    li 17, 0
    lwz 18, {ME0}(14)
    lwz 23, {ME1}(14)
    lis 9, {hl(PLAYERS)[0]}
    ori 9, 9, {hl(PLAYERS)[1]}
    lwz 15, 0(9)
walk:
    cmplwi 7, 15, 0xffff
    ble 7, walked
    lwz 9, 0x10(15)
    cmplwi 7, 9, 0xffff
    ble 7, nxt
    lwz 0, 0(9)
    cmpwi 7, 0, 0
    bne 7, notu
    mr 16, 15
notu:
    cmpwi 7, 18, 0
    beq 7, nxt
    lwz 9, 0x64(15)
    cmplwi 7, 9, 0xffff
    ble 7, nxt
    lwz 0, 0(9)
    cmpw 7, 0, 18
    bne 7, nxt
    lwz 0, 4(9)
    cmpw 7, 0, 23
    bne 7, nxt
    mr 17, 15
nxt:
    lwz 15, 0x5C(15)
    b walk
walked:
    lwz 0, {PARK}(14)
    cmpwi 7, 0, 0
    bne 7, decide
    cmpwi 7, 16, 0
    beq 7, decide
    lwz 0, {POS}(14)
    cmpw 7, 0, 25
    bne 7, bypos
    cmpwi 7, 18, 0
    beq 7, bypos
    cmpwi 7, 19, 0
    beq 7, decide
    lwz 0, {LAST}(14)
    cmpw 7, 0, 16
    beq 7, decide
    cmpwi 7, 17, 0
    bne 7, capture
    lwz 3, 0x64(16)
    bl rowof
    lwz 4, {TEAM}(14)
    bl inteam
    cmpwi 7, 3, 0
    bne 7, decide
bypos:
    stw 25, {POS}(14)
    lwz 22, 0x3C(16)
    addi 21, 25, -1
    lis 9, {hl(PLAYERS)[0]}
    ori 9, 9, {hl(PLAYERS)[1]}
    lwz 15, 0(9)
posloop:
    cmplwi 7, 15, 0xffff
    ble 7, capture
    lwz 0, 0x3C(15)
    cmpw 7, 0, 22
    bne 7, posnext
    lwz 3, 0x64(15)
    bl rowof
    cmpwi 7, 3, 0
    beq 7, posnext
    lbz 0, {ROW_POS}(3)
    cmpw 7, 0, 21
    beq 7, capfrom
posnext:
    lwz 15, 0x5C(15)
    b posloop
capture:
    mr 15, 16
capfrom:
    lwz 9, 0x64(15)
    cmplwi 7, 9, 0xffff
    ble 7, decide
    lwz 18, 0(9)
    lwz 23, 4(9)
    stw 18, {ME0}(14)
    stw 23, {ME1}(14)
    li 0, 0
    stw 0, {OBJ}(14)
    stw 0, {ROW}(14)
    stw 0, {TEAM}(14)
    mr 17, 15
    b findrow
decide:
    cmpwi 7, 18, 0
    beq 7, benchdone
    cmpwi 7, 17, 0
    bne 7, oncourt
    cmpwi 7, 16, 0
    beq 7, benchdone
    lwz 0, {PARK}(14)
    cmpwi 7, 0, 0
    bne 7, reclaim
    lwz 3, 0x10(16)
    addi 4, 14, {SPARE}
    bla {hex(SWAP)}
    li 0, 1
    stw 0, {PARK}(14)
    li 0, 0
    stw 0, {LAST}(14)
    b benchdone
reclaim:
    lwz 9, 0x10(16)
    li 0, -1
    stw 0, 0(9)
    b benchdone
oncourt:
    cmpw 7, 16, 17
    beq 7, settle
    cmpwi 7, 16, 0
    beq 7, fromspare
    lwz 3, 0x10(16)
    lwz 4, 0x10(17)
    bla {hex(SWAP)}
    b settle
fromspare:
    lwz 0, {PARK}(14)
    cmpwi 7, 0, 0
    beq 7, benchdone
    addi 3, 14, {SPARE}
    lwz 4, 0x10(17)
    bla {hex(SWAP)}
    li 0, 0
    stw 0, {PARK}(14)
settle:
    stw 17, {LAST}(14)
    b benchdone
"""


def find_src():
    """After a capture: roster row with the same name pointers, then the team row listing it."""
    return f"""
findrow:
    lis 9, {hl(ROSTER)[0]}
    ori 9, 9, {hl(ROSTER)[1]}
    lwz 9, 8(9)
    cmplwi 7, 9, 0xffff
    ble 7, decide
    lwz 10, 8(9)
    lwz 11, 0xC(9)
    lwz 24, 0x28(9)
    lwz 20, 0x2C(9)
rowloop:
    cmpwi 7, 10, 0
    ble 7, decide
    lwz 0, 0(11)
    cmpw 7, 0, 18
    bne 7, rownext
    lwz 0, 4(11)
    cmpw 7, 0, 23
    beq 7, rowfound
rownext:
    addi 11, 11, 0x134
    addi 10, 10, -1
    b rowloop
rowfound:
    stw 11, {ROW}(14)
teamloop:
    cmpwi 7, 24, 0
    ble 7, decide
    lhz 10, 0x158(20)
    cmplwi 7, 10, 18
    ble 7, slotcount
    li 10, 18
slotcount:
    addi 12, 20, 0x3C
slotloop:
    cmpwi 7, 10, 0
    ble 7, teamnext
    lwz 0, 0(12)
    cmpw 7, 0, 11
    beq 7, teamfound
    addi 12, 12, 4
    addi 10, 10, -1
    b slotloop
teamnext:
    addi 20, 20, 0x2C0
    addi 24, 24, -1
    b teamloop
teamfound:
    stw 20, {TEAM}(14)
    lis 9, {hl(SCR)[0]}
    ori 9, 9, {hl(SCR)[1]}
    stw 11, {SCR_ROW}(9)
    stw 20, {SCR_TEAM}(9)
    b decide
"""


def apply(target_reg, rating, n, skip):
    off = 0x2C + 2 * R[rating]
    return f"""    lhz 9, {off}({target_reg})
    add 9, 9, 8
    cmpwi 7, 9, 9900
    ble 7, cap{n}
    li 9, 9900
cap{n}:
    cmpwi 7, 9, 0
    bge 7, flo{n}
    li 9, 0
flo{n}:
    sth 9, {off}({target_reg})
"""


def progress_src():
    src = f"""
benchdone:
    cmpwi 7, 17, 0
    beq 7, out
    lwz 21, 0x64(17)
    cmplwi 7, 21, 0xffff
    ble 7, out
    lwz 9, 0x14(21)
    cmplwi 7, 9, 0xffff
    ble 7, out
    addi 20, 9, 4
    lwz 22, {ROW}(14)
    lwz 0, {OBJ}(14)
    cmpw 7, 0, 21
    beq 7, counters
    stw 21, {OBJ}(14)
"""
    # new game (or first frame): take the counters as they are, then the lineup routines
    for k, (_, off, _) in enumerate(GAINS):
        src += f"    lwz 0, {off}(20)\n    stw 0, {CNT + 4 * k}(14)\n"
    src += f"""    lwz 3, {TEAM}(14)
    cmplwi 7, 3, 0xffff
    ble 7, out
    std 2, 0x108(1)
    lis 2, {hl(TOC2)[0]}
    ori 2, 2, {hl(TOC2)[1]}
    li 4, 0
    bla {hex(LINEUP)}
    lwz 3, {TEAM}(14)
    li 4, 1
    li 5, 0
    bla {hex(ROTATION)}
    ld 2, 0x108(1)
    bl forcepos
    b out
counters:
    li 24, 0
"""
    n = 0
    for k, (_, off, gains) in enumerate(GAINS):
        src += f"""    lwz 5, {off}(20)
    lwz 6, {CNT + 4 * k}(14)
    subf. 7, 6, 5
    beq 0, done{k}
    stw 5, {CNT + 4 * k}(14)
    bge 0, up{k}
    li 24, 1
    b done{k}
up{k}:
"""
        for rating, gain in gains:
            n += 1
            src += f"    li 8, {gain}\n    mullw 8, 8, 7\n"
            src += apply('21', rating, f'o{n}', None)
            src += f"""    cmpwi 7, 22, 0
    beq 7, norow{n}
"""
            src += apply('22', rating, f'r{n}', None)
            src += f"norow{n}:\n"
        src += f"done{k}:\n"
    # a counter went down: a new game reuses the same object, so run the lineup routines again
    src += f"""    cmpwi 7, 24, 0
    beq 7, out
    lwz 3, {TEAM}(14)
    cmplwi 7, 3, 0xffff
    ble 7, out
    std 2, 0x108(1)
    lis 2, {hl(TOC2)[0]}
    ori 2, 2, {hl(TOC2)[1]}
    li 4, 0
    bla {hex(LINEUP)}
    lwz 3, {TEAM}(14)
    li 4, 1
    li 5, 0
    bla {hex(ROTATION)}
    ld 2, 0x108(1)
    bl forcepos
    b out
"""
    return src


def subs_src():
    """Local subroutines (bl / blr).

    rowof:   r3 = in-game player object -> r3 = his roster row, or 0
    inteam:  r3 = roster row, r4 = team row -> r3 = 1 if the team lists him
    forcepos: puts your player (ROW) at your position (MyPlayer value - 1) in the
              starting row of TEAM's depth chart, swapping with whoever was there"""
    return f"""
rowof:
    cmplwi 7, 3, 0xffff
    ble 7, rowno
    lwz 12, 0(3)
    lwz 11, 4(3)
    lis 9, {hl(ROSTER)[0]}
    ori 9, 9, {hl(ROSTER)[1]}
    lwz 9, 8(9)
    cmplwi 7, 9, 0xffff
    ble 7, rowno
    lwz 10, 8(9)
    lwz 9, 0xC(9)
rowl:
    cmpwi 7, 10, 0
    ble 7, rowno
    lwz 0, 0(9)
    cmpw 7, 0, 12
    bne 7, rown
    lwz 0, 4(9)
    cmpw 7, 0, 11
    bne 7, rown
    mr 3, 9
    blr
rown:
    addi 9, 9, 0x134
    addi 10, 10, -1
    b rowl
rowno:
    li 3, 0
    blr
inteam:
    cmplwi 7, 4, 0xffff
    ble 7, inno
    cmpwi 7, 3, 0
    beq 7, inno
    lhz 10, 0x158(4)
    cmplwi 7, 10, 18
    ble 7, inc
    li 10, 18
inc:
    addi 12, 4, 0x3C
inl:
    cmpwi 7, 10, 0
    ble 7, inno
    lwz 0, 0(12)
    cmpw 7, 0, 3
    beq 7, inyes
    addi 12, 12, 4
    addi 10, 10, -1
    b inl
inyes:
    li 3, 1
    blr
inno:
    li 3, 0
    blr
forcepos:
    lwz 3, {TEAM}(14)
    cmplwi 7, 3, 0xffff
    ble 7, fpno
    lwz 4, {ROW}(14)
    cmpwi 7, 4, 0
    beq 7, fpno
    addi 9, 25, -1
    slwi 9, 9, 2
    add 9, 9, 3
    addi 9, 9, {DEPTH}
    addi 10, 3, {DEPTH}
    li 11, {DEPTH_WORDS}
fpl:
    cmpwi 7, 11, 0
    ble 7, fpno
    lwz 0, 0(10)
    cmpw 7, 0, 4
    beq 7, fpf
    addi 10, 10, 4
    addi 11, 11, -1
    b fpl
fpf:
    lwz 0, 0(9)
    stw 4, 0(9)
    stw 0, 0(10)
fpno:
    blr
"""


def source():
    data = '\n'.join(['    .long -1' if i == SPARE // 4 else '    .long 0' for i in range(DATA_WORDS)])
    return f"""
    stdu 1, -0x180(1)
    std 0, 0x70(1)
    mflr 0
    std 0, 0x78(1)
    mfcr 0
    stw 0, 0x80(1)
    std 3, 0x88(1)
    std 4, 0x90(1)
    std 5, 0x98(1)
    std 6, 0xA0(1)
    std 7, 0xA8(1)
    std 8, 0xB0(1)
    std 9, 0xB8(1)
    std 10, 0xC0(1)
    std 11, 0xC8(1)
    std 12, 0xD0(1)
    std 14, 0xD8(1)
    std 15, 0xE0(1)
    std 16, 0xE8(1)
    std 17, 0xF0(1)
    std 18, 0xF8(1)
    std 19, 0x100(1)
    std 20, 0x110(1)
    std 21, 0x118(1)
    std 22, 0x120(1)
    std 23, 0x128(1)
    std 24, 0x130(1)
    stfd 1, 0x138(1)
    stfd 2, 0x140(1)
    stfd 3, 0x148(1)
    stfd 4, 0x150(1)
    std 25, 0x158(1)
    bl getdata
data:
{data}
getdata:
    mflr 14
    lis 9, {hl(LOCK_FLAG)[0]}
    ori 9, 9, {hl(LOCK_FLAG)[1]}
    lwz 0, 0(9)
    cmpwi 7, 0, 0
    beq 7, out
    mr 25, 0
    cmplwi 7, 25, 5
    ble 7, posok
    li 25, 1
posok:
    mftb 0
    lwz 9, {TB}(14)
    stw 0, {TB}(14)
    subf 9, 9, 0
    lis 0, {hl(GAP)[0]}
    cmplw 7, 9, 0
    li 19, 0
    blt 7, nogap
    li 19, 1
nogap:
{bench_src()}
{find_src()}
{progress_src()}
{subs_src()}
out:
    ld 25, 0x158(1)
    lfd 1, 0x138(1)
    lfd 2, 0x140(1)
    lfd 3, 0x148(1)
    lfd 4, 0x150(1)
    ld 14, 0xD8(1)
    ld 15, 0xE0(1)
    ld 16, 0xE8(1)
    ld 17, 0xF0(1)
    ld 18, 0xF8(1)
    ld 19, 0x100(1)
    ld 20, 0x110(1)
    ld 21, 0x118(1)
    ld 22, 0x120(1)
    ld 23, 0x128(1)
    ld 24, 0x130(1)
    lwz 0, 0x80(1)
    mtcrf 0xff, 0
    ld 0, 0x78(1)
    mtlr 0
    ld 0, 0x70(1)
    ld 3, 0x88(1)
    ld 4, 0x90(1)
    ld 5, 0x98(1)
    ld 6, 0xA0(1)
    ld 7, 0xA8(1)
    ld 8, 0xB0(1)
    ld 9, 0xB8(1)
    ld 10, 0xC0(1)
    ld 11, 0xC8(1)
    ld 12, 0xD0(1)
    addi 1, 1, 0x180
"""


def build():
    src = source()
    code = B.assemble(src)
    assert code == B.assemble(src, 0x40010000), 'not position independent'
    first = P.original(HOOK)
    assert first == 0xF821FE71, hex(first)
    return code + first.to_bytes(4, 'big')


def menu_sources():
    """The MyPlayer option cycles Off, Point Guard .. Center (settings +0xF8 = 0..5).

    Stock handlers (0x685344 / 0x685390) flip the word with (v == 0); each cave
    replaces their store `stw r9,0xF8(r11)`. The caption function 0x68AFF0 indexes
    the Off / On table with the word; its cave replaces `lwz r4,0xF8(r9)` and points
    r0 at a six-entry table (Off read from the game's own table, then the english.iff
    position names), which the next instructions index."""
    step = lambda d, wrap: f"""
    lwz 9, 0xF8(11)
    addi 9, 9, {d}
    cmplwi 7, 9, 5
    ble 7, ok
    li 9, {wrap}
ok:
    stw 9, 0xF8(11)
"""
    names = '\n'.join(f'    .long {hex(h)}' for h in POSITION_TEXT)
    text = f"""
    lwz 4, 0xF8(9)
    cmplwi 7, 4, 5
    ble 7, inr
    li 4, 1
inr:
    lis 11, {hl(OFFON)[0]}
    ori 11, 11, {hl(OFFON)[1]}
    lwz 11, 0(11)
    bl tbl
    .long 0
{names}
tbl:
    mflr 10
    stw 11, 0(10)
    mr 0, 10
"""
    # The option's row in the Game Settings table (built by the static constructor
    # 0x67F8B8 at 0x12F352C0, 0x5C per row) has widget type 5 = ON/OFF switch, which
    # draws a fixed OFF | ON pill. Type 7 = text list (Play Mode, Attendance; same
    # function layout) draws the caption function's text. The constructor stores the
    # type with `stw r12,0x2E0(r9)` at 0x681004; this cave stores 7 instead (r0 kept
    # in the ABI's protected zone below the stack pointer).
    widget = """
    std 0, -16(1)
    li 0, 7
    stw 0, 0x2E0(9)
    ld 0, -16(1)
"""
    # Width of the text-list box: the option's +0x24 function (0x68541C) returns the
    # widest caption of table r6, indices r4..r5, via 0x4A1214 (Foul Out passes 0..5).
    # Stock passes the Off / On table and 0..1, so the box fits "Off"; this cave
    # points r6 at the six captions (the function has not saved LR yet, so LR is
    # kept in r0, which its next instruction reloads anyway) and WIDTH_LAST makes r5 5.
    width = f"""
    mflr 0
    bl wtbl
    .long 0
{names}
wtbl:
    mflr 6
    mtlr 0
    lis 11, {hl(OFFON)[0]}
    ori 11, 11, {hl(OFFON)[1]}
    lwz 11, 0(11)
    stw 11, 0(6)
"""
    return [(MENU_TYPE, 0x91890000 | 0x2E0, widget),
            (MENU_WIDTH, 0x80C20878, width),
            (MENU_RIGHT, 0x91200000 | 0xF8 | (11 << 16) | (9 << 21), step(1, 0)),
            (MENU_LEFT, 0x91200000 | 0xF8 | (11 << 16) | (9 << 21), step(-1, 5)),
            (MENU_TEXT, 0x80800000 | 0xF8 | (9 << 16) | (4 << 21), text)]


def labels(src):
    """Byte offset of each label, counted the way B.assemble lays the code out."""
    pos, out = 0, {}
    for l in (l.strip() for l in src.strip().splitlines()):
        if not l:
            continue
        if l.endswith(':'):
            out[l[:-1]] = pos
        else:
            pos += 4
    return out


def resolve(src):
    """Replace @name with (offset of label name - offset of label 'here')."""
    import re
    first = re.sub(r'@(\w+)', '0', src); pos = labels(first)
    return re.sub(r'@(\w+)', lambda m: str(pos[m.group(1)] - pos['here']), src)


def transfer_sources():
    """Transfer To row in Game Settings + MyPlayer in the offseason transfer pass.

    Settings row: the constructor 0x67F8B8 builds every settings row at boot; the
    Game Settings menu (GS_MENU) reads row i at +0x1C + i * 0x5C and the count at
    +0x40 (0x13009C, 0x13A6DC). The cave at the constructor's last store copies the
    18 rows to a buffer of 19, adds a row from the MyPlayer row with its own label and
    functions (OPDs built at run time, TOC 0xA64A94), and points the menu at it.
    Row functions: +0xC max = team count, +0x14 value, +0x18 / +0x1C left / right
    (wrap 0 .. count), +0x20 caption (0: the game's Off; k: team k - 1's short name at
    team row +0x00, a UTF-16 pointer, via 0x1E1000), +0x24 box width 0xC8.

    Transfer pass (0x5BC250, Legacy offseason): the list at TRANSFER_LIST is processed
    as remove from old team (0x7644B8) then add to new team (0x764548). Before it
    runs, the cave adds your player (SCR_ROW, from SCR_TEAM) to the chosen team, or
    retargets his entry if the game already has him transferring, then clears the
    choice. The sit-out cave skips `oris r0,r0,0x800` (transfer redshirt) for him."""
    scr = hl(SCR); ros = hl(ROSTER); off = hl(OFFON)
    count = f"""
    lis 9, {ros[0]}
    ori 9, 9, {ros[1]}
    lwz 9, 8(9)
    lwz 5, 0x28(9)
"""
    rows_words = GS_COUNT * ROW_SIZE // 4
    funcs = ('fmax', 'fget', 'fright', 'fleft', 'fcap', 'fwidth')   # +0x18 is the right arrow, +0x1C the left
    opd = lambda f: f'opd_{f}'
    settings = f"""
    stw 8, 0x444(10)
    bl here
here:
    mflr 12
    lis 4, {hl(GS_ROWS)[0]}
    ori 4, 4, {hl(GS_ROWS)[1]}
    addi 3, 12, @buf
    li 5, {rows_words}
copy:
    lwz 0, 0(4)
    stw 0, 0(3)
    addi 4, 4, 4
    addi 3, 3, 4
    addi 5, 5, -1
    cmpwi 7, 5, 0
    bne 7, copy
    lis 4, {hl(MYPLAYER_ROW)[0]}
    ori 4, 4, {hl(MYPLAYER_ROW)[1]}
    li 5, {ROW_SIZE // 4}
    mr 6, 3
copy2:
    lwz 0, 0(4)
    stw 0, 0(3)
    addi 4, 4, 4
    addi 3, 3, 4
    addi 5, 5, -1
    cmpwi 7, 5, 0
    bne 7, copy2
    li 0, 7
    stw 0, 0(6)
    addi 0, 12, @label
    stw 0, 4(6)
    li 0, 0
    stw 0, 0x34(6)
"""
    for f, field in zip(funcs, (0x0C, 0x14, 0x18, 0x1C, 0x20, 0x24)):
        settings += f"""    addi 0, 12, @{f}
    stw 0, @{opd(f)}(12)
    addi 0, 12, @{opd(f)}
    stw 0, {field}(6)
"""
    settings += f"""    lis 9, {hl(GS_MENU)[0]}
    ori 9, 9, {hl(GS_MENU)[1]}
    addi 0, 12, @buf
    stw 0, 0x1C(9)
    addi 0, 6, {ROW_SIZE}
    stw 0, 0x18(9)
    li 0, {GS_COUNT + 1}
    stw 0, 0x40(9)
    b done
fmax:
{count}    mr 3, 5
    blr
fget:
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    lwz 3, {SCR_DEST}(9)
    blr
{step_src('fright', 1)}{step_src('fleft', -1)}{keycmp_src()}fwidth:
    li 3, 0xC8
    blr
fcap:
    stdu 1, -0x80(1)
    mflr 0
    std 0, 0x90(1)
    std 31, 0x78(1)
    mr 31, 3
    li 0, 0
    stw 0, 0(31)
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    lwz 4, {SCR_DEST}(9)
    cmpwi 7, 4, 0
    beq 7, capoff
{count}    cmplw 7, 4, 5
    bgt 7, capoff
    lwz 9, 0x2C(9)
    addi 4, 4, -1
    mulli 4, 4, 0x2C0
    add 9, 9, 4
    lwz 4, 0(9)
    rlwinm. 0, 4, 0, 31, 31
    bne 0, capoff
    lis 0, 0x1000
    cmplw 7, 4, 0
    blt 7, capoff
    mr 3, 31
    bla {hex(STR_FROM_TEXT)}
    ld 2, 0x28(1)
    b capret
capoff:
    lis 9, {off[0]}
    ori 9, 9, {off[1]}
    lwz 0, 0(9)
    stw 0, 0x70(1)
    mr 3, 31
    addi 4, 1, 0x70
    li 5, 0
    bla {hex(STR_ASSIGN)}
    ld 2, 0x28(1)
capret:
    mr 3, 31
    ld 31, 0x78(1)
    ld 0, 0x90(1)
    mtlr 0
    addi 1, 1, 0x80
    blr
label:
    .long {hex(TRANSFER_LABEL)}
"""
    for f in funcs:
        settings += f"{opd(f)}:\n    .long 0\n    .long {hex(MAIN_TOC)}\n"
    settings += "buf:\n" + "    .long 0\n" * ((GS_COUNT + 1) * ROW_SIZE // 4) + "done:\n"
    settings = resolve(settings)

    tl = hl(TRANSFER_LIST)
    transfer = f"""
    lis 10, {scr[0]}
    ori 10, 10, {scr[1]}
    lwz 3, {SCR_DEST}(10)
    cmpwi 7, 3, 0
    beq 7, tdone
    lwz 4, {SCR_ROW}(10)
    cmpwi 7, 4, 0
    beq 7, tdone
    lwz 5, {SCR_TEAM}(10)
    cmpwi 7, 5, 0
    beq 7, tdone
    lis 11, {ros[0]}
    ori 11, 11, {ros[1]}
    lwz 11, 8(11)
    lwz 12, 0x28(11)
    cmplw 7, 3, 12
    bgt 7, tzero
    lwz 11, 0x2C(11)
    addi 3, 3, -1
    mulli 3, 3, 0x2C0
    add 6, 11, 3
    cmpw 7, 6, 5
    beq 7, tboth
    lis 7, {tl[0]}
    ori 7, 7, {tl[1]}
    lwz 8, 0(9)
    mr 12, 7
    li 3, 0
tscan:
    cmpw 7, 3, 8
    bge 7, tappend
    lwz 0, 0(12)
    cmpw 7, 0, 4
    beq 7, tfound
    addi 12, 12, 12
    addi 3, 3, 1
    b tscan
tfound:
    stw 6, 8(12)
    b tmoved
tappend:
    cmplwi 7, 8, {TRANSFER_MAX}
    bge 7, tdone
    mulli 3, 8, 12
    add 12, 7, 3
    stw 4, 0(12)
    stw 5, 4(12)
    stw 6, 8(12)
    addi 8, 8, 1
    stw 8, 0(9)
tmoved:
    stw 6, {SCR_TEAM}(10)
tboth:
    lis 11, {hl(PROF_COACH)[0]}
    ori 11, 11, {hl(PROF_COACH)[1]}
    lwz 11, 0(11)
    cmplwi 7, 11, 0xffff
    ble 7, tdone
    lhz 0, 8(11)
    lhz 12, 0x15C(6)
    cmpw 7, 0, 12
    bne 7, tdone
tzero:
    li 0, 0
    stw 0, {SCR_DEST}(10)
tdone:
    lwz 0, 0(9)
"""
    # Coaching carousel: open the chosen school's job at the end of the season-end
    # review (0x594BDC, which fires / retires coaches through 0x5930D4, 0x765E38 and
    # 0x593884(team, coach, reason)), then put your coach first in that opening's
    # candidate list (0x5934A0 fills 0x12D9EA00, 7 entries of coach + score; the
    # dialog 0x5940A8 offers the job to a candidate who is a user's coach and runs the
    # game's own move on accept). Done when your coach is already there.
    fire = f"""
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    li 0, 0
    stw 0, {SCR_FORCE}(9)
    lwz 3, {SCR_DEST}(9)
    cmpwi 7, 3, 0
    beq 7, fdone
{count}    cmplw 7, 3, 5
    bgt 7, fdone
    lwz 9, 0x2C(9)
    addi 3, 3, -1
    mulli 3, 3, 0x2C0
    add 30, 9, 3
    lis 11, {hl(PROF_COACH)[0]}
    ori 11, 11, {hl(PROF_COACH)[1]}
    lwz 11, 0(11)
    cmplwi 7, 11, 0xffff
    ble 7, fdone
    lhz 0, 8(11)
    lhz 12, 0x15C(30)
    cmpw 7, 0, 12
    beq 7, fdone
    lis 9, {hl(OPENINGS_COUNT)[0]}
    ori 9, 9, {hl(OPENINGS_COUNT)[1]}
    lwz 8, 0(9)
    lis 7, {hl(OPENINGS)[0]}
    ori 7, 7, {hl(OPENINGS)[1]}
fscan:
    cmpwi 7, 8, 0
    ble 7, fopen
    lwz 0, 0(7)
    cmpw 7, 0, 30
    beq 7, fforce
    addi 7, 7, 0x14
    addi 8, 8, -1
    b fscan
fopen:
    lwz 31, 0x30(30)
    mr 3, 30
    li 4, 0
    bla {hex(FIRE_PREP)}
    mr 3, 30
    bla {hex(FIRE_DETACH)}
    mr 3, 30
    mr 4, 31
    li 5, 1
    bla {hex(ADD_OPENING)}
fforce:
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    stw 30, {SCR_FORCE}(9)
fdone:
    li 0, 0
"""
    shift = ''.join(f"""    lwz 0, {8 * k}(7)
    stw 0, {8 * k + 8}(7)
    lwz 0, {8 * k + 4}(7)
    stw 0, {8 * k + 12}(7)
""" for k in range(OFFER_SLOTS - 2, -1, -1))
    candidates = f"""
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    lwz 10, {SCR_FORCE}(9)
    cmpwi 7, 10, 0
    beq 7, cdone
    cmplwi 7, 28, 0xffff
    ble 7, cdone
    lwz 0, 0(28)
    cmpw 7, 0, 10
    bne 7, cdone
    lis 11, {hl(PROF_COACH)[0]}
    ori 11, 11, {hl(PROF_COACH)[1]}
    lwz 11, 0(11)
    cmplwi 7, 11, 0xffff
    ble 7, cdone
    lis 7, {hl(OFFERS)[0]}
    ori 7, 7, {hl(OFFERS)[1]}
{shift}    stw 11, 0(7)
    lis 0, 0x42C8
    stw 0, 4(7)
cdone:
    ld 0, 0xF0(1)
"""
    sitout = f"""
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    lwz 9, {SCR_ROW}(9)
    cmpw 7, 9, 11
    beq 7, keep
    oris 0, 0, 0x800
keep:
"""
    return [(SETTINGS_END, 0x910A_0444, settings),
            (TRANSFER_PASS, 0x8009_0000, transfer),
            (SEASON_REVIEW_END, 0x3800_0000, fire),
            (COACH_MOVED, 0x93DF_0030, follow_src()),
            (CANDIDATES_END, 0xE801_00F0, candidates)]


def keycmp_src():
    """keycmp: r3, r4 = team numbers k (team index + 1) -> r3 <0 / 0 / >0, ordering by
    the short name shown in the Transfer row (UTF-16 at team row +0x00, a-z folded to
    A-Z), then by k. Teams without a usable name sort first. Leaf; uses r0, r5-r12."""
    ros = hl(ROSTER)
    name = lambda k, dst, tag: f"""
    addi {dst}, {k}, -1
    mulli {dst}, {dst}, 0x2C0
    add {dst}, {dst}, 9
    lwz {dst}, 0({dst})
    rlwinm. 0, {dst}, 0, 31, 31
    bne 0, {tag}
    lis 0, 0x1000
    cmplw 7, {dst}, 0
    bge 7, {tag}ok
{tag}:
    li {dst}, 0
{tag}ok:
"""
    fold = lambda r, tag: f"""
    cmplwi 7, {r}, 0x61
    blt 7, {tag}
    cmplwi 7, {r}, 0x7A
    bgt 7, {tag}
    addi {r}, {r}, -0x20
{tag}:
"""
    return f"""keycmp:
    lis 9, {ros[0]}
    ori 9, 9, {ros[1]}
    lwz 9, 8(9)
    lwz 9, 0x2C(9)
{name('3', '5', 'kn1')}{name('4', '6', 'kn2')}    cmpwi 7, 5, 0
    bne 7, khave1
    cmpwi 7, 6, 0
    bne 7, kless
    b ktie
khave1:
    cmpwi 7, 6, 0
    beq 7, kmore
kloop:
    lhz 7, 0(5)
    lhz 8, 0(6)
{fold('7', 'kf1')}{fold('8', 'kf2')}    cmpw 7, 7, 8
    bne 7, kdiff
    cmpwi 7, 7, 0
    beq 7, ktie
    addi 5, 5, 2
    addi 6, 6, 2
    b kloop
kdiff:
    subf 3, 8, 7
    blr
kless:
    li 3, -1
    blr
kmore:
    li 3, 1
    blr
ktie:
    subf 3, 4, 3
    blr
"""


def step_src(label, direction):
    """Transfer row arrow: DEST moves to the next (direction 1) or previous (-1) school
    in keycmp order; past the last / first one it is Off (0), and from Off it goes to
    the first / last school."""
    ros, scr = hl(ROSTER), hl(SCR)
    t = label
    # skip i when it is not beyond the current value / not closer than the best so far
    past = 'ble' if direction > 0 else 'bge'
    closer = 'bge' if direction > 0 else 'ble'
    return f"""{t}:
    stdu 1, -0x90(1)
    mflr 0
    std 0, 0xA0(1)
    std 28, 0x70(1)
    std 29, 0x78(1)
    std 30, 0x80(1)
    std 31, 0x88(1)
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    lwz 31, {SCR_DEST}(9)
    li 30, 0
    lis 9, {ros[0]}
    ori 9, 9, {ros[1]}
    lwz 9, 8(9)
    lwz 29, 0x28(9)
{t}loop:
    cmpwi 7, 29, 0
    ble 7, {t}end
    lis 9, {ros[0]}
    ori 9, 9, {ros[1]}
    lwz 9, 8(9)
    lwz 9, 0x2C(9)
    addi 10, 29, -1
    mulli 10, 10, 0x2C0
    add 10, 10, 9
    lwz 0, {TEAM_TYPE}(10)
    rlwinm. 0, 0, 17, 29, 31
    bne 0, {t}next
    lwz 10, 0(10)
    rlwinm. 0, 10, 0, 31, 31
    bne 0, {t}next
    lis 0, 0x1000
    cmplw 7, 10, 0
    blt 7, {t}next
    lhz 0, 0(10)
    cmpwi 7, 0, 0
    beq 7, {t}next
    cmpwi 7, 31, 0
    beq 7, {t}any
    mr 3, 29
    mr 4, 31
    bl keycmp
    cmpwi 7, 3, 0
    {past} 7, {t}next
{t}any:
    cmpwi 7, 30, 0
    beq 7, {t}take
    mr 3, 29
    mr 4, 30
    bl keycmp
    cmpwi 7, 3, 0
    {closer} 7, {t}next
{t}take:
    mr 30, 29
{t}next:
    addi 29, 29, -1
    b {t}loop
{t}end:
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    stw 30, {SCR_DEST}(9)
    li 3, 1
    ld 28, 0x70(1)
    ld 29, 0x78(1)
    ld 30, 0x80(1)
    ld 31, 0x88(1)
    ld 0, 0xA0(1)
    mtlr 0
    addi 1, 1, 0x90
    blr
"""


def follow_src():
    """Your player follows your coach to his new school (carousel accept, 0x5946DC).

    There the accept code (0x5940A8) stores the hired coach r30 as the coach of the
    opening's school r31 (`stw r30,0x30(r31)`); r28 is the coach's previous school
    (0 if he was unemployed). When the coach is user 0's coach, the cave moves your
    player from r28 to r31 with the transfer pass's own calls: 0x7644B8(old, player)
    removes him, 0x764548(new, player) adds him; his transfer flag (+0x8C bit 31) is
    set and his redshirt code is left as it is, so he can play at once.
    Your player: SCR_ROW when he is on the old school's roster, else the old school's
    depth-chart starter at the MyPlayer position (forcepos keeps him there).
    The game sets r3 = r31, r4 = 1 just before the hook for its next call
    (0x5930D4), so the cave restores both on the way out."""
    scr = hl(SCR)
    inteam = lambda reg, team, tag: f"""
    lhz 10, 0x158({team})
    cmplwi 7, 10, 18
    ble 7, {tag}c
    li 10, 18
{tag}c:
    addi 12, {team}, 0x3C
{tag}l:
    cmpwi 7, 10, 0
    ble 7, {tag}no
    lwz 0, 0(12)
    cmpw 7, 0, {reg}
    beq 7, {tag}yes
    addi 12, 12, 4
    addi 10, 10, -1
    b {tag}l
"""
    return f"""
    stw 30, 0x30(31)
    lis 11, {hl(PROF_COACH)[0]}
    ori 11, 11, {hl(PROF_COACH)[1]}
    lwz 11, 0(11)
    cmpw 7, 11, 30
    bne 7, mdone
    cmplwi 7, 28, 0xffff
    ble 7, mdone
    cmpw 7, 28, 31
    beq 7, mdone
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    lwz 3, {SCR_ROW}(9)
    cmplwi 7, 3, 0xffff
    ble 7, bypos
{inteam('3', '28', 'a')}ano:
bypos:
    lis 9, {hl(LOCK_FLAG)[0]}
    ori 9, 9, {hl(LOCK_FLAG)[1]}
    lwz 9, 0(9)
    addi 9, 9, -1
    cmplwi 7, 9, 4
    bgt 7, mdone
    slwi 9, 9, 2
    add 9, 9, 28
    lwz 3, {DEPTH}(9)
    cmplwi 7, 3, 0xffff
    ble 7, mdone
{inteam('3', '28', 'b')}bno:
    b mdone
ayes:
byes:
    stdu 1, -0x80(1)
    std 3, 0x70(1)
    mr 4, 3
    mr 3, 28
    bla {hex(TEAM_REMOVE)}
    ld 4, 0x70(1)
    lwz 0, 0x8C(4)
    oris 0, 0, 0x8000
    stw 0, 0x8C(4)
    mr 3, 31
    bla {hex(TEAM_ADD)}
    ld 3, 0x70(1)
    addi 1, 1, 0x80
    lis 9, {scr[0]}
    ori 9, 9, {scr[1]}
    stw 3, {SCR_ROW}(9)
    stw 31, {SCR_TEAM}(9)
mdone:
    mr 3, 31
    li 4, 1
"""


def menu_caves():
    out = []
    for hook, expect, src in menu_sources() + transfer_sources():
        assert P.original(hook) == expect, (hex(hook), hex(P.original(hook)))
        code = B.assemble(src)
        assert code == B.assemble(src, 0x40010000), 'not position independent'
        out.append((hook, code))
    return out


def notes():
    g = '; '.join(f"{s}: " + ', '.join(f"{r} {v / 100:+.2f}" for r, v in gains) for s, _, gains in GAINS)
    return ("Set MyPlayer in Options > Game Settings to a position (Point Guard, Shooting Guard, Small Forward, Power Forward or Center; Off disables it). Controller 1 only. Replaces the bench-only MyPlayer entry; enable one of them, not both. "
            "Position: your player is your team's on-court player at that position (or the one you control if nobody matches), and the starting lineup always puts him at that position. "
            "Bench: when the CPU subs your player out, the CPU plays; when he checks back in, you control him again. "
            "Progression: every made shot, rebound, assist, steal, block and turnover by your player changes his ratings right away and in the roster (kept when Legacy saves; capped at 99). Per stat: " + g + ". "
            "Starting lineup on merit: at the start of each game the game's own CPU lineup and minutes routines run on your team, so the next game's starters and minutes follow ratings (your player keeps his position). "
            "Transfer: Game Settings > Transfer picks a school (Off = stay). In Legacy's offseason your player moves there (enable 'Transfers: No sit-out' so he is eligible at once), and that school's job opens in the Coach Carousel and is offered to you first; accept it to coach (and control) that school. Whenever your coach accepts a job in the Coach Carousel (any school), your player moves there with him at once. Set Transfer back to Off if you change your mind (otherwise the school's job is opened again next offseason). The choice is kept only until the game is closed, and your player must have played a game in this session.")


def entry():
    code = build(); words = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
    lines = [f'  "{TITLE}":', '    Games:', '      "College Hoops 2K8":', '        BLUS30078: [ All ]',
             '    Author: "Claude Code"',
             '    Notes: "' + notes().replace('"', "'") + '"',
             '    Patch Version: 2.8', '    Patch:',
             f'      - [ calloc, 0x{HOOK:08x}, {len(words)} ] # MyPlayer 2.8']
    lines += [f'      - [ be32, 0x{HOOK:08x}, 0x{w:08x} ]' for w in words]
    for hook, code in menu_caves():
        mw = [int.from_bytes(code[i:i + 4], 'big') for i in range(0, len(code), 4)]
        lines.append(f'      - [ calloc, 0x{hook:08x}, {len(mw)} ] # MyPlayer menu option / transfer cave')
        lines += [f'      - [ be32, 0x{hook:08x}, 0x{w:08x} ]' for w in mw]
    for (at, old, new), note in ((WIDTH_LAST, 'MyPlayer option box width: captions 0..5'),
                                 (MENU_MAX, 'MyPlayer option max value 5 (menu arrows)')):
        assert P.original(at) == old, hex(P.original(at))
        lines.append(f'      - [ be32, 0x{at:08x}, 0x{new:08x} ] # {note}')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    for path in sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BLUS30078_imported_patch.yml')]:
        P.TITLE, P.entry = TITLE, entry
        P.install(path)

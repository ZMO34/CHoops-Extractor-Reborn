"""Scorebug team names with poll rank and season record ("#5 DUKE 12-3").

Two RPCS3 `calloc` blocks hooked at the entries of the stock scorebug team-name
providers (home 0x4EF9A4, away 0x4EFABC). Each block is a complete replacement
provider: it saves its own link register and returns straight to the caller
with `blr`, so RPCS3's automatic branch back to hook+4 is never reached.
Position independent: game functions are called with absolute `bla`.

Text built with the game's own string functions and English templates:
  name     STR_FROM(team +4)                       -> "DUKE"
  rank     "#{0}" (0x12BE2A9D), "{0} {1}" (0xDB12E271) -> "#5 DUKE"  (media poll slots 0-24,
           matched by team ID +0x15E like the existing poll-rank entry; ID 0 never matches)
  record   "{0} {1}-{2}" (0x4F6600F7)              -> "#5 DUKE 12-3"

The record is the pair of bytes the pregame matchup card formats natively as
"({0}-{1})" (0x70F5D0): wins at team +0x1FC, losses at +0x1FD, read from the same
per-game team objects (0x57F050 home / 0x57F064 away). It is added only when the
game-mode word (0x4A3924 -> 0x72330) is 2, the same gate the matchup card uses
before it shows a record, and only when the team has played (wins + losses > 0).

Frame 0x100: handles 0x70 (rank text), 0x78 (name), 0x80 (rank + name),
format ID 0x88, ints 0x8C rank / 0x90 wins / 0x94 losses, argument block 0xA0
(header {0, count} then 12-byte entries {0, &value, type} at 0xA8/0xB4/0xC0),
saved r26-r31 at 0xD0-0xF8, LR in the caller's frame at 0x110.
"""
import struct

import rank_hook_asm as H
from rank_asm import (FMT_PAIR, FMT_RANK, FORMAT, GET_AWAY, GET_HOME, KEY, POLL_ENTRY,
                      STR_ASSIGN, STR_FREE, TOC_INT_TYPE, TOC_STR_TYPE)

STR_FROM = 0x49E1B4
MODE = 0x4A3924            # stub -> 0x72330: returns the global game-mode word
RECORD_MODE = 2            # matchup card shows "(W-L)" only in this mode (0x70F61C)
WINS, LOSSES = 0x1FC, 0x1FD
FMT_RECORD = 0x4F6600F7    # "{0} {1}-{2}" in the English loc table (stock and V5.5)
HOOKS = {'home': (0x4EF9A4, GET_HOME), 'away': (0x4EFABC, GET_AWAY)}
ELF = r'D:/RPCS3 2026/dev_hdd0/game/BLUS30078/USRDIR/EBOOT.elf'

SRC = """
    mflr 0
    stdu 1, -0x100(1)
    std 0, 0x110(1)
    std 31, 0xF8(1)
    std 30, 0xF0(1)
    std 29, 0xE8(1)
    std 28, 0xE0(1)
    std 27, 0xD8(1)
    std 26, 0xD0(1)
    mr. 31, 3
    beq exit
    bla {GET_TEAM}
    mr 30, 3
    mr 28, 1
    cmpwi 7, 30, 0
    beq 7, exit
    li 10, 0
    stw 10, 0x70(28)
    stw 10, 0x78(28)
    stw 10, 0x80(28)
    addi 3, 28, 0x78
    lwz 4, 4(30)
    li 5, -1
    bla {STR_FROM}
    ld 2, 0x28(1)
    addi 26, 28, 0x78
    lhz 27, {KEY}(30)
    cmpwi 7, 27, 0
    beq 7, record
    li 29, 0
loop:
    li 3, 0
    mr 4, 29
    bla {POLL_ENTRY}
    cmpwi 7, 3, 0
    beq 7, next
    lhz 0, {KEY}(3)
    cmpw 7, 0, 27
    beq 7, ranked
next:
    addi 29, 29, 1
    cmpwi 7, 29, 25
    blt 7, loop
    b record
ranked:
    addi 11, 29, 1
    stw 11, 0x8C(28)
    lis 0, {RANK_HI}
    ori 0, 0, {RANK_LO}
    stw 0, 0x88(28)
    li 0, 0
    stw 0, 0xA0(28)
    stw 0, 0xA8(28)
    li 0, 1
    stw 0, 0xA4(28)
    addi 0, 28, 0x8C
    stw 0, 0xAC(28)
    lwz 0, {INT_T}(2)
    stw 0, 0xB0(28)
    addi 3, 28, 0x70
    addi 4, 28, 0x88
    addi 5, 28, 0xA0
    li 6, 0
    bla {FORMAT}
    ld 2, 0x28(1)
    lis 0, {PAIR_HI}
    ori 0, 0, {PAIR_LO}
    stw 0, 0x88(28)
    li 0, 0
    stw 0, 0xA0(28)
    stw 0, 0xA8(28)
    stw 0, 0xB4(28)
    li 0, 2
    stw 0, 0xA4(28)
    addi 0, 28, 0x70
    stw 0, 0xAC(28)
    lwz 9, {STR_T}(2)
    stw 9, 0xB0(28)
    addi 0, 28, 0x78
    stw 0, 0xB8(28)
    stw 9, 0xBC(28)
    addi 3, 28, 0x80
    addi 4, 28, 0x88
    addi 5, 28, 0xA0
    li 6, 0
    bla {FORMAT}
    ld 2, 0x28(1)
    addi 3, 28, 0x70
    bla {STR_FREE}
    ld 2, 0x28(1)
    addi 3, 28, 0x78
    bla {STR_FREE}
    ld 2, 0x28(1)
    addi 26, 28, 0x80
record:
    bla {MODE}
    ld 2, 0x28(1)
    cmpwi 7, 3, {RECORD_MODE}
    bne 7, plain
    lbz 9, {WINS}(30)
    lbz 10, {LOSSES}(30)
    add 0, 9, 10
    cmpwi 7, 0, 0
    beq 7, plain
    stw 9, 0x90(28)
    stw 10, 0x94(28)
    lis 0, {REC_HI}
    ori 0, 0, {REC_LO}
    stw 0, 0x88(28)
    li 0, 0
    stw 0, 0xA0(28)
    stw 0, 0xA8(28)
    stw 0, 0xB4(28)
    stw 0, 0xC0(28)
    li 0, 3
    stw 0, 0xA4(28)
    stw 26, 0xAC(28)
    lwz 9, {STR_T}(2)
    stw 9, 0xB0(28)
    lwz 9, {INT_T}(2)
    addi 0, 28, 0x90
    stw 0, 0xB8(28)
    stw 9, 0xBC(28)
    addi 0, 28, 0x94
    stw 0, 0xC4(28)
    stw 9, 0xC8(28)
    mr 3, 31
    addi 4, 28, 0x88
    addi 5, 28, 0xA0
    li 6, 0
    bla {FORMAT}
    ld 2, 0x28(1)
    b free
plain:
    mr 3, 31
    mr 4, 26
    li 5, 1
    bla {STR_ASSIGN}
    ld 2, 0x28(1)
free:
    mr 3, 26
    bla {STR_FREE}
    ld 2, 0x28(1)
exit:
    ld 26, 0xD0(1)
    ld 27, 0xD8(1)
    ld 28, 0xE0(1)
    ld 29, 0xE8(1)
    ld 30, 0xF0(1)
    ld 31, 0xF8(1)
    ld 0, 0x110(1)
    mtlr 0
    addi 1, 1, 0x100
    blr
"""


def source(side):
    hi = lambda v: hex((v >> 16) & 0xFFFF)
    lo = lambda v: hex(v & 0xFFFF)
    return SRC.format(GET_TEAM=hex(HOOKS[side][1]), STR_FROM=hex(STR_FROM), POLL_ENTRY=hex(POLL_ENTRY),
                      KEY=hex(KEY), STR_ASSIGN=hex(STR_ASSIGN), STR_FREE=hex(STR_FREE),
                      FORMAT=hex(FORMAT), MODE=hex(MODE), RECORD_MODE=RECORD_MODE,
                      WINS=hex(WINS), LOSSES=hex(LOSSES), INT_T=hex(TOC_INT_TYPE), STR_T=hex(TOC_STR_TYPE),
                      RANK_HI=hi(FMT_RANK), RANK_LO=lo(FMT_RANK), PAIR_HI=hi(FMT_PAIR), PAIR_LO=lo(FMT_PAIR),
                      REC_HI=hi(FMT_RECORD), REC_LO=lo(FMT_RECORD))


def build(side, base=0x30000000):
    return H.assemble(source(side), base)


def stock_word(addr):
    """Read one instruction word from the decoded ELF (text segment vaddr 0x10000 = file 0)."""
    data = open(ELF, 'rb').read()
    return struct.unpack_from('>I', data, addr - 0x10000)[0]


if __name__ == '__main__':
    for side, (hook, _) in HOOKS.items():
        code = build(side)
        assert code == build(side, 0x40010000), 'not position independent'
        print(side, 'hook', hex(hook), 'stock word', hex(stock_word(hook)), 'cave words', len(code) // 4)

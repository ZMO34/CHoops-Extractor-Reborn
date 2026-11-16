"""Run the assembled record caves in the PPC64 interpreter (rank_interp) with modeled game calls.

Checks the produced text, the game-mode/record gates, register and stack
preservation, the return to the caller, and that every string handle the cave
creates is freed exactly once.
"""
import sys

import rank_interp as I
import record_asm as R
from rank_asm import FMT_PAIR, FMT_RANK, FORMAT, GET_AWAY, GET_HOME, KEY, POLL_ENTRY, STR_ASSIGN, STR_FREE

BASE = 0x31000000
TEMPLATES = {FMT_RANK: '#{0}', FMT_PAIR: '{0} {1}', R.FMT_RECORD: '{0} {1}-{2}'}
INT_T, STR_T = 0xA18CA0, 0xA18CD8                      # real descriptor values in the main TOC


def run(side, poll, mode, teams, out_obj=0x40008000, keys=None, records=None, base=BASE):
    m = I.Mem()
    code = R.build(side, base)
    m.write(base, code)
    names = {teams[0]: 'DUKE', teams[1]: 'KANSAS'}
    for i, (t, n) in enumerate(names.items()):
        if not t:
            continue
        sp = I.DATA + 0x1000 + i * 0x100
        m.write(sp, n.encode('utf-16-be') + b'\0\0'); m.w(t + 4, 4, sp)
    for ptr, key in (keys or {}).items():
        m.w(ptr + KEY, 2, key)
    for ptr, (w, l) in (records or {}).items():
        m.w(ptr + R.WINS, 1, w); m.w(ptr + R.LOSSES, 1, l)
    m.w(I.MAIN_TOC + R.TOC_INT_TYPE, 4, INT_T); m.w(I.MAIN_TOC + R.TOC_STR_TYPE, 4, STR_T)
    cpu = I.CPU(m, None)
    cpu.r[1], cpu.r[2], cpu.r[3], cpu.lr = I.STACK, I.MAIN_TOC, out_obj, I.RET
    for n in range(14, 32):
        cpu.r[n] = 0x1111000000000000 + n
    nodes, live, st = {}, set(), {'next': I.HEAP, 'out': None, 'err': [], 'freed': 0}

    def text(p):
        s = b''
        while m.read(p, 2) != b'\0\0':
            s += m.read(p, 2); p += 2
        return s.decode('utf-16-be')

    def new_node(s, handle):
        node = st['next']; st['next'] += 0x10; nodes[node] = s; live.add(node); m.w(handle, 4, node)

    def stub(name):
        if cpu.r[2] != I.MAIN_TOC: st['err'].append(f'{name} entered with r2={cpu.r[2]:#x}')
        m.w(cpu.r[1] + 0x28, 8, cpu.r[2]); cpu.r[2] = I.LIB_TOC   # real stubs leave the library TOC

    def clobber():
        for v in (0, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            cpu.r[v] = 0xBAD0 + v

    pc, steps = base, 0
    while pc != I.RET:
        steps += 1
        if steps > 20000: st['err'].append('runaway'); break
        r3, r4 = cpu.r[3] & 0xFFFFFFFF, cpu.r[4] & 0xFFFFFFFF
        if pc in (GET_HOME, GET_AWAY):
            want = GET_HOME if side == 'home' else GET_AWAY
            if pc != want: st['err'].append('wrong team getter')
            clobber(); cpu.r[3] = teams[0] if pc == GET_HOME else teams[1]; pc = cpu.lr; continue
        if pc == POLL_ENTRY:
            if r3 != 0: st['err'].append('poll mode not media')
            clobber(); cpu.r[3] = poll[r4] if r4 < len(poll) else 0; pc = cpu.lr; continue
        if pc == R.MODE:
            stub('MODE'); clobber(); cpu.r[3] = mode; pc = cpu.lr; continue
        if pc == R.STR_FROM:
            stub('STR_FROM')
            if cpu.r[5] & 0xFFFFFFFF != 0xFFFFFFFF: st['err'].append('length not -1')
            clobber(); new_node(text(r4), r3); pc = cpu.lr; continue
        if pc == FORMAT:
            stub('FORMAT')
            fmt = m.u(r4, 4); hdr = cpu.r[5] & 0xFFFFFFFF
            if cpu.r[6] & 0xFFFFFFFF: st['err'].append('FORMAT r6 not 0')
            if m.u(hdr, 4) != 0: st['err'].append('arg header word 0 not 0')
            count = m.u(hdr + 4, 4); vals = []
            for i in range(count):
                e = hdr + 8 + 12 * i
                if m.u(e, 4) != 0: st['err'].append(f'arg {i} word 0 not 0')
                ptr, typ = m.u(e + 4, 4), m.u(e + 8, 4)
                if typ == INT_T: vals.append(str(m.u(ptr, 4)))
                elif typ == STR_T:
                    node = m.u(ptr, 4)
                    if node not in live: st['err'].append(f'arg {i} string handle not live')
                    vals.append(nodes.get(node, '?'))
                else: st['err'].append(f'arg {i} unknown type {typ:#x}'); vals.append('?')
            if fmt not in TEMPLATES: st['err'].append(f'unknown template {fmt:#x}')
            if TEMPLATES.get(fmt, '').count('{') != count: st['err'].append(f'template {fmt:#x} arg count {count}')
            out = TEMPLATES.get(fmt, '?').format(*vals)
            clobber()
            if r3 == out_obj:
                if st['out'] is not None: st['err'].append('output written twice')
                st['out'] = out
            else:
                new_node(out, r3)
            pc = cpu.lr; continue
        if pc == STR_ASSIGN:
            stub('STR_ASSIGN')
            if r3 != out_obj: st['err'].append('assign target is not the output slot')
            if st['out'] is not None: st['err'].append('output written twice')
            node = m.u(r4, 4)
            if node not in live: st['err'].append('assign from dead handle')
            st['out'] = nodes.get(node); clobber(); pc = cpu.lr; continue
        if pc == STR_FREE:
            stub('STR_FREE')
            node = m.u(r3, 4)
            if node not in live: st['err'].append(f'free of dead handle {node:#x}')
            live.discard(node); st['freed'] += 1; clobber(); pc = cpu.lr; continue
        if not base <= pc < base + len(code):
            st['err'].append(f'jumped outside the cave to {pc:#x}'); break
        pc = cpu.step(pc)
    for n in range(14, 32):
        if cpu.r[n] != 0x1111000000000000 + n: st['err'].append(f'r{n} clobbered')
    if cpu.r[1] != I.STACK: st['err'].append('r1 not restored')
    if cpu.r[2] != I.MAIN_TOC: st['err'].append('r2 not restored')
    if live: st['err'].append(f'{len(live)} string handle(s) leaked')
    st['steps'] = steps
    return st


if __name__ == '__main__':
    H, A = I.DATA + 0x100, I.DATA + 0x400              # per-game team copies (scorebug objects)
    RH, RA = I.DATA + 0x4000, I.DATA + 0x4400          # roster records in the poll (same ID, other address)
    base = [I.DATA + 0x8000 + 0x200 * i for i in range(25)]
    keys = {H: 216, A: 322, RH: 216, RA: 322}
    keys.update({b: 1000 + i for i, b in enumerate(base)})
    base[3] = 0
    p1 = base[:]; p1[4] = RH; p1[12] = RA
    rec = {H: (12, 3), A: (7, 9)}
    cases = [
        ('home ranked, legacy', 'home', p1, 2, rec, '#5 DUKE 12-3'),
        ('away ranked, legacy', 'away', p1, 2, rec, '#13 KANSAS 7-9'),
        ('home unranked, legacy', 'home', base, 2, rec, 'DUKE 12-3'),
        ('away unranked, legacy', 'away', base, 2, rec, 'KANSAS 7-9'),
        ('home ranked, other mode', 'home', p1, 0, rec, '#5 DUKE'),
        ('away unranked, mode 1', 'away', base, 1, rec, 'KANSAS'),
        ('home 0-0, legacy', 'home', p1, 2, {H: (0, 0), A: (7, 9)}, '#5 DUKE'),
        ('away 0-1, legacy', 'away', base, 2, {H: (0, 0), A: (0, 1)}, 'KANSAS 0-1'),
        ('home 255-255, legacy', 'home', base, 2, {H: (255, 255), A: (0, 0)}, 'DUKE 255-255'),
    ]
    ok = True
    for name, side, poll, mode, records, want in cases:
        st = run(side, poll, mode, (H, A), keys=keys, records=records)
        good = st['out'] == want and not st['err']; ok &= good
        print(f"{'PASS' if good else 'FAIL'} {name:26s} -> {st['out']!r:18s} ({st['steps']} steps, {st['freed']} frees)", st['err'] or '')
    zero = {**keys, H: 0}
    zpoll = base[:]; zpoll[2] = I.DATA + 0x6000; zero[I.DATA + 0x6000] = 0
    st = run('home', zpoll, 2, (H, A), keys=zero, records=rec)
    good = st['out'] == 'DUKE 12-3' and not st['err']; ok &= good
    print(f"{'PASS' if good else 'FAIL'} ID 0 never matches       -> {st['out']!r}", st['err'] or '')
    st = run('home', p1, 2, (H, A), out_obj=0, keys=keys, records=rec)
    good = st['out'] is None and not st['err'] and st['steps'] < 30 and st['freed'] == 0; ok &= good
    print(f"{'PASS' if good else 'FAIL'} null output slot          -> nothing written", st['err'] or '')
    st = run('away', p1, 2, (H, 0), keys=keys, records=rec)
    good = st['out'] is None and not st['err']; ok &= good
    print(f"{'PASS' if good else 'FAIL'} null team object          -> nothing written", st['err'] or '')
    a, b = R.build('home', BASE), R.build('home', 0x40010000)
    good = a == b; ok &= good
    print(f"{'PASS' if good else 'FAIL'} position independent ({len(a) // 4} words)")
    st = run('away', p1, 2, (H, A), keys=keys, records=rec, base=0x4A000000)
    good = st['out'] == '#13 KANSAS 7-9' and not st['err']; ok &= good
    print(f"{'PASS' if good else 'FAIL'} runs at another base      -> {st['out']!r}", st['err'] or '')
    for side, (hook, _) in R.HOOKS.items():
        good = R.stock_word(hook) == 0x2C230000; ok &= good
        print(f"{'PASS' if good else 'FAIL'} stock word at {side} hook {hook:#x} is cmpdi r3,0")
    sys.exit(0 if ok else 1)

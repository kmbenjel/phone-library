"""Fix B (2026-10-28, regression 27l's diff): THE SCANNER BANDS READ BEFORE THE TURN BOUND EVERY TURNED PAGE. The first look reads
a page's scanner bands (bands(): edge columns/rows more than 60 % dark) before turning it, «a turned image's blank corners hide
them» — but only the generic loop carried them over to the turned page; the turns set later (the projection loop, the lines'
baselines and tracks, fix Q4's confirmed loop) kept only what bands() found on the turned image. خريدة القصر 0648 ص 422:
the black band down the left side (columns 1–12 100 % dark) reads 0.64 in its outermost column turned 0.325° and 0.60 turned
0.45° (the turn's blank wedge) — not over 0.6: no band, the box slid 10 pt onto it. Now whatever turn the page takes, its
bands as scanned, turned with it (fwd_inner: the largest upright rectangle inside), bound its allowed area.
Usage: patch_b.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''        tu = lambda: tu_[0] if tu_ else (tu_.append(Turner(doc, i)) or tu_[0])
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
''', '''        tu = lambda: tu_[0] if tu_ else (tu_.append(Turner(doc, i)) or tu_[0])
        al0 = None
        if mk['box'] is not None and mk['dark'] <= 0.35:     # a tilted text page: turn it level (the sign is checked)
''')
sub('''        if tu_: tu_[0].close()
        mk.pop('xy', None); mk.pop('parts', None)
''', '''        if tu_: tu_[0].close()
        # THE BANDS AS SCANNED BOUND THE PAGE WHATEVER ITS TURN (fix B, 2026-10-28): the generic loop carried them over, the
        # turns set by the projection loop, the baselines and the tracks did not — خريدة القصر ص 422's black band reads 0.64
        # in its outermost column turned 0.325°, 0.60 turned 0.45° (the turn's blank wedge): no band, the box slid onto it
        # (only a side that HAS a band, as decide() reads them: the whole page turned is a rectangle a few pt inside it,
        # which decide() would take for bands on every side)
        if rec.get('skew') and al0 and mk.get('allowed'):
            a_ = fwd_inner(doc, i, {'skew': rec['skew']}, al0); al = mk['allowed']
            bd = [al0[0] > 0.5, al0[1] > 0.5, al0[2] < r.width - 0.5, al0[3] < r.height - 0.5]
            mk['allowed'] = [max(al[0], a_[0]) if bd[0] else al[0], max(al[1], a_[1]) if bd[1] else al[1],
                             min(al[2], a_[2]) if bd[2] else al[2], min(al[3], a_[3]) if bd[3] else al[3]]
            if max(abs(u - v) for u, v in zip(al, mk['allowed'])) > 0.5: rec['band_carried'] = [round(v, 1) for v in al]   # (the
            # turned page alone read: the recipe's band_carried)
        mk.pop('xy', None); mk.pop('parts', None)
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)

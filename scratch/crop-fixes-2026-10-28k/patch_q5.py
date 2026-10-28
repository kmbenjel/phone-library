"""Fix Q5 (2026-10-28, found reviewing 26j: 97 pages 26i turned are unturned in 26j). A turn Q3's new rulers set (the lines'
tracks, the robust baselines) that the second look cannot keep — the tracks read their own turned page off, best_turn finds
nothing near it — is dropped and the page left as scanned (unsure_tilt): القوافي ص 62 (26i −0.95°, the page reading level by
its own ink, 0.125°; the tracks −1.426°, 0.48° from it), خريدة القصر 01 ص 625 (26i 0.5°), المثلث ص 189 (26i 1.15°). A
tilt the owner sees (0.25°) left where 26i had none. The first look already runs the projection loop on these pages (fix
Q4); its turn is now kept as p['loop_turn'] when the new ruler disagrees, and where the second look would drop the new
ruler's turn it tries the loop's turn first, checked as before Q3 (the page reads level by its own ink, ≤ 0.2°:
level_by_proj) → p['loop_fallback']. Pages whose turn is kept are not touched. Usage: patch_q5.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''                if best and best[0] <= 0.2 and abs(bt[0] - best[1]) <= 0.05 + 1e-6:
                    rec['skew'] = best[1]; mk = best[2]; rec['loop_confirmed'] = bt[0]
                    rec.pop('tilt_by_tracks', None); rec.pop('base_robust', None); bt = None; ang = 0.0
''', '''                if best and best[0] <= 0.2 and abs(bt[0] - best[1]) <= 0.05 + 1e-6:
                    rec['skew'] = best[1]; mk = best[2]; rec['loop_confirmed'] = bt[0]
                    rec.pop('tilt_by_tracks', None); rec.pop('base_robust', None); bt = None; ang = 0.0
                elif best and best[0] <= 0.2: rec['loop_turn'] = best[1]   # (the second look falls back on it: fix Q5)
''')

sub('''    def base(i, q, m, robust=False):                  # the lines' baselines of a view (base_tilt), once per view
''', '''    def loop_back(i, p):                              # THE LOOP'S TURN when the new rulers' turn cannot be kept (fix Q5,
        lt = p.get('loop_turn')                       # 2026-10-28: القوافي ص 62 left as scanned, 26i's −0.95° reading level
        if lt is None: return None                    # by its own ink): checked as before Q3 — the page then reads level by
        m2 = look(i, dict(p, skew=lt))                # its own ink (≤ 0.2°)
        if m2.get('xy') is None: return None
        pl = abs(skew_of(m2['xy'], raw=True)[0])
        if pl > 0.2: return None
        for k in ('untreated_tilt', 'tilt_disputed', 'unsure_tilt'): p.pop(k, None)
        p['skew'] = lt; p['level_by_proj'] = round(pl, 3); p['loop_fallback'] = True
        return m2
    def base(i, q, m, robust=False):                  # the lines' baselines of a view (base_tilt), once per view
''')

sub('''            else:
                if p.get('skew'): p.pop('skew', None); p['unsure_tilt'] = True
                mk = m0
''', '''            else:
                m2 = loop_back(i, p) if p.get('skew') else None
                if m2 is not None: mk = m2
                else:
                    if p.get('skew'): p.pop('skew', None); p['unsure_tilt'] = True
                    mk = m0
''')

sub('''            if keep(p, d, r, im, before, m2, m0): p['skew'], mk = d, m2; p['after_tilt'] = round(r, 3); p['after_tilt_image'] = im
            else:
                p.pop('skew', None); p['unsure_tilt'] = True; mk = look(i, p)
''', '''            if keep(p, d, r, im, before, m2, m0): p['skew'], mk = d, m2; p['after_tilt'] = round(r, 3); p['after_tilt_image'] = im
            else:
                m2 = loop_back(i, p)
                if m2 is not None: mk = m2
                else: p.pop('skew', None); p['unsure_tilt'] = True; mk = look(i, p)
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)

"""Fix Q4 (2026-10-28, regression 26j: القوافي للتنوخي 810908d4ed05 ص 89 «centred» failed). Fix Q3 turns a projection page
the baselines cannot read by its lines followed across it (or the robust baselines), and no longer runs the projection's
loop there. On القوافي it moved 9 pages: three by 0.3–0.48° (pp. 22, 62, 102 — what Q3 is for) and four by 0.025–0.05°
(pp. 8, 24, 30, 70) — under the loop's own resolution (its last step is 0.1°: ± 0.05°) and far under what the eye sees
(0.25°). One of those, ص 70 0.8° → 0.825°, moved two thin strokes of its marginal reference «٤/١» out of a «dotted line»
(a text row's dots the dotted-line rule reads at one angle and not at the next) into the margin: 10 pages of 90 printing
in their side margins instead of 9, over the 10 % limit — the book lost its clean margins (owner 2026-10-10's narrow,
centred frame), the box took a photocopy's edge arc back in and ص 84's verse number was cut as a stray.
Now on such a page the loop runs first, as before Q3; its turn stands when the new ruler reads it within 0.05° (the
second look corrects a tracks turn only beyond 0.05° — the two agree), recorded as p['loop_confirmed'] (the reading);
else the new ruler sets the turn, as in Q3. A change no one sees is not made — the pages the regression approved stay as
they were. Usage: patch_q4.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''            bt = None
            if rec.get('tilt_by_proj') is not None and mk.get('text'):
                a3, z3 = gray(page, 1400); a3 = whiten(np.array(a3), z3, sh)
''', '''            def proj_loop():                             # a projection turn: angles around its reading (it is coarse), the
                best = None                              # one after which the page reads level by its own ink is kept
                for k in list(range(-5, 6)):
                    deg = round(rec['tilt_by_proj'] + 0.2 * k, 3)
                    if deg * rec['tilt_by_proj'] <= 0: continue
                    a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                    mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                    if mk2['box'] is None or mk2['xy'] is None: continue
                    lv = abs(skew_of(mk2['xy'], raw=True)[0])
                    if best is None or lv < best[0]: best = (lv, deg, mk2)
                if best:                                 # then ± 0.1° around the best
                    for deg in (round(best[1] - 0.1, 3), round(best[1] + 0.1, 3)):
                        a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                        mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                        if mk2['box'] is None or mk2['xy'] is None: continue
                        lv = abs(skew_of(mk2['xy'], raw=True)[0])
                        if lv < best[0]: best = (lv, deg, mk2)
                return best
            bt = None; looped = False
            if rec.get('tilt_by_proj') is not None and mk.get('text'):
                a3, z3 = gray(page, 1400); a3 = whiten(np.array(a3), z3, sh)
''')

sub('''                    else:
                        bt = base_tilt(a3, mk['paper'], mk['text'], z3, robust=True)
                        if bt is not None: rec['base_robust'] = True
            if bt is not None:
''', '''                    else:
                        bt = base_tilt(a3, mk['paper'], mk['text'], z3, robust=True)
                        if bt is not None: rec['base_robust'] = True
            # THE LOOP'S TURN STANDS WHEN THE NEW RULER CONFIRMS IT (fix Q4, 2026-10-28): the lines followed across the page
            # (or the robust baselines) correct the loop where it is off — on القوافي للتنوخي by 0.3–0.48° — but a turn they
            # read within 0.05° of the loop's (its own resolution; the second look corrects a tracks turn only beyond it) is
            # not changed: ص 70 0.8° → 0.825° moved two strokes of a marginal «٤/١» out of a dotted-line reading into the
            # margin and the book lost its clean margins (10 pages of 90 over the 10 % limit)
            if bt is not None and (rec.get('tilt_by_tracks') is not None or rec.get('base_robust')):
                best = proj_loop(); looped = True
                if best and best[0] <= 0.2 and abs(bt[0] - best[1]) <= 0.05 + 1e-6:
                    rec['skew'] = best[1]; mk = best[2]; rec['loop_confirmed'] = bt[0]
                    rec.pop('tilt_by_tracks', None); rec.pop('base_robust', None); bt = None; ang = 0.0
            if bt is not None:
''')

sub('''            elif rec.get('tilt_by_proj') is not None:    # a projection turn: angles around its reading (it is coarse), the
                best = None                              # one after which the page reads level by its own ink is kept
                for k in list(range(-5, 6)):
                    deg = round(rec['tilt_by_proj'] + 0.2 * k, 3)
                    if deg * rec['tilt_by_proj'] <= 0: continue
                    a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                    mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                    if mk2['box'] is None or mk2['xy'] is None: continue
                    lv = abs(skew_of(mk2['xy'], raw=True)[0])
                    if best is None or lv < best[0]: best = (lv, deg, mk2)
                if best:                                 # then ± 0.1° around the best
                    for deg in (round(best[1] - 0.1, 3), round(best[1] + 0.1, 3)):
                        a2, z2 = gray(tu().page(deg), 500); a2 = whiten(a2, z2, fwd_box(doc, i, {'skew': deg}, sh) if sh else None)
                        mk2 = marks(a2, z2, r.width, fwd_boxes(doc, i, {'skew': deg}, ex0) if ex0 else None)
                        if mk2['box'] is None or mk2['xy'] is None: continue
                        lv = abs(skew_of(mk2['xy'], raw=True)[0])
                        if lv < best[0]: best = (lv, deg, mk2)
                if best and best[0] <= 0.2: rec['skew'] = best[1]; mk = best[2]
                ang = 0.0                                # (the generic loop below is not run for it)
''', '''            elif rec.get('tilt_by_proj') is not None and not looped:
                best = proj_loop()
                if best and best[0] <= 0.2: rec['skew'] = best[1]; mk = best[2]
                ang = 0.0                                # (the generic loop below is not run for it)
            elif looped: ang = 0.0                       # (the loop's turn kept above: the generic loop is not run either)
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)

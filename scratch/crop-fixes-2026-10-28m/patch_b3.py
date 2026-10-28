"""Fix B3 (2026-10-28, the bench of B2 on خريدة القصر 01 0648): BESIDE A SCANNER BAND THE SECOND LOOK KEEPS 4 PT OFF THE PRINT
AND SLIDES OFF THE BAND. decide() slides a frame off a band up to 4 pt from the text (the owner's 10-18 «سواد الطباعة» rule),
but the second look, finding print the first look did not see beside the band, held it with half the book's margin
(13 pt) or — past a 2 % slide — re-centred the frame on it, and the frame went back into the band 15–33 pt: line ends
running to 1 pt from the paper's edge (ص 344 «عليه»، «جماعة» — the regression's case row: the black side in view again —,
ص 400, 551), a table's rules reaching the band (ص 617, 622, 623, 672, 685), a caption set along the edge (ص 25, grown
1.033). B2 brought these out: with the band no ink, the print beside it is no longer one mark with the band. Now, on a
side with a band (its allowed edge more than 1 % inside the page), the frame keeps 4 pt beside the print instead of
half the margin (and of the full margin when it grows), and a frame placed afresh slides off the band as far as the
print allows (4 pt), the other side taking the rest — as decide() does.
Usage: patch_b3.py SRC DST   (SRC = book_crop with fixes L, B and B2: code2/bc_lbb2.py)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''                mg = rec.get('margin_pt') or 0.01 * (c[2] - c[0]); h_ = 0.5 * mg
                def place(u):                            # → the box holding u, and its scale when it had to grow (else None)
                    up = [u[0] - h_, u[1] - h_, u[2] + h_, u[3] + h_]
                    dx = up[0] - c[0] if up[0] < c[0] else (up[2] - c[2] if up[2] > c[2] else 0)
                    dy = up[1] - c[1] if up[1] < c[1] else (up[3] - c[3] if up[3] > c[3] else 0)
                    n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
                    if abs(dx) <= 0.02 * p['w'] and abs(dy) <= 0.02 * p['h'] and inside(up, n, 1.0) \\
                       and n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h']:
                        return n, None
                    cw, ch = c[2] - c[0], c[3] - c[1]
                    sc = max(1.0, (u[2] - u[0] + 2 * mg) / cw, (u[3] - u[1] + 2 * mg) / ch)
                    smax = min(p['w'] / cw, p['h'] / ch)        # never beyond the sheet: the margin gives way first
                    if sc > smax: sc = max(1.0, smax, (u[2] - u[0]) / cw, (u[3] - u[1]) / ch)
                    x2, y2 = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
                    n = [x2 - cw * sc / 2, y2 - ch * sc / 2, x2 + cw * sc / 2, y2 + ch * sc / 2]
                    sx = -n[0] if n[0] < 0 else (p['w'] - n[2] if n[2] > p['w'] else 0); sy = -n[1] if n[1] < 0 else (p['h'] - n[3] if n[3] > p['h'] else 0)
                    return [n[0] + sx, n[1] + sy, n[2] + sx, n[3] + sy], sc
''', '''                mg = rec.get('margin_pt') or 0.01 * (c[2] - c[0]); h_ = 0.5 * mg
                # BESIDE A SCANNER BAND THE FRAME KEEPS 4 PT OFF THE PRINT (fix B3, 2026-10-28), as decide()'s off-band slide
                # does, and a frame placed afresh slides off the band as far as the print allows: line ends, a table's rules,
                # a caption set along the edge run up to the band (خريدة القصر 0648 ص 344, 400, 617, 25) — held with half the
                # margin, or re-centred on them, the frame went back into the band 15–33 pt (a side with a band: its allowed
                # edge more than 1 % inside the page)
                ab = p.get('allowed') or [0, 0, p['w'], p['h']]
                bs = [ab[0] > 0.01 * p['w'], ab[1] > 0.01 * p['h'], ab[2] < 0.99 * p['w'], ab[3] < 0.99 * p['h']]
                def off_band(n, u):
                    n = list(n)
                    for k0, k1, lim in ((0, 2, p['w']), (1, 3, p['h'])):
                        lo, hi = (ab[k0] - n[k0]) if bs[k0] else 0, (n[k1] - ab[k1]) if bs[k1] else 0
                        if lo > 1 and hi <= 0: sh = min(lo + 1, (ab[k1] if bs[k1] else lim) - n[k1], max(0, u[k0] - 4 - n[k0]))
                        elif hi > 1 and lo <= 0: sh = -min(hi + 1, n[k0] - (ab[k0] if bs[k0] else 0), max(0, n[k1] - u[k1] - 4))
                        else: continue
                        if abs(sh) >= 0.5: n[k0] += sh; n[k1] += sh; p['band_slide'] = round(sh, 1)
                    return n
                def place(u):                            # → the box holding u, and its scale when it had to grow (else None)
                    e_ = [4 if bs[k] else h_ for k in range(4)]
                    up = [u[0] - e_[0], u[1] - e_[1], u[2] + e_[2], u[3] + e_[3]]
                    dx = up[0] - c[0] if up[0] < c[0] else (up[2] - c[2] if up[2] > c[2] else 0)
                    dy = up[1] - c[1] if up[1] < c[1] else (up[3] - c[3] if up[3] > c[3] else 0)
                    n = [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]
                    if abs(dx) <= 0.02 * p['w'] and abs(dy) <= 0.02 * p['h'] and inside(up, n, 1.0) \\
                       and n[0] >= 0 and n[1] >= 0 and n[2] <= p['w'] and n[3] <= p['h']:
                        return off_band(n, u), None
                    cw, ch = c[2] - c[0], c[3] - c[1]
                    f_ = [4 if bs[k] else mg for k in range(4)]
                    sc = max(1.0, (u[2] - u[0] + f_[0] + f_[2]) / cw, (u[3] - u[1] + f_[1] + f_[3]) / ch)
                    smax = min(p['w'] / cw, p['h'] / ch)        # never beyond the sheet: the margin gives way first
                    if sc > smax: sc = max(1.0, smax, (u[2] - u[0]) / cw, (u[3] - u[1]) / ch)
                    x2, y2 = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
                    n = [x2 - cw * sc / 2, y2 - ch * sc / 2, x2 + cw * sc / 2, y2 + ch * sc / 2]
                    sx = -n[0] if n[0] < 0 else (p['w'] - n[2] if n[2] > p['w'] else 0); sy = -n[1] if n[1] < 0 else (p['h'] - n[3] if n[3] > p['h'] else 0)
                    return off_band([n[0] + sx, n[1] + sy, n[2] + sx, n[3] + sy], u), sc
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)

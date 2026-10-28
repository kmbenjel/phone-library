"""Fix B4 (2026-10-28, the bench of B2 variant H + B3 on خريدة القصر 01 0648, bench-b3-b): TWO FAULTS B2 BROUGHT IN, BOTH
WHERE A BAND THE TURNED PAGE LOST MEETS THE PAGE.
(1) A TABLE'S GRID IS NO EDGE SHADOW. B2's rule for the paper's grey rim along a lost band (touching the band's turned edge,
    ≥ 40 % long, thin by its ink: area over length ≤ 6 %) also takes a table's ruled grid whose outer rule touches the band:
    tall, and its ink per row is a few rules. ص 636, 637, 638 (tables between black bands): the grid read as the band's rim,
    left out of the content, and the allowed area cut to the grid's far end — 362, 410, 431 pt into the text (the frames
    came out right only because the text block held every slide; the second look's «nothing in a band» tests would have
    let any print beyond it go). The rim lies ALONG the band: its breadth is its own thickness (≤ 6 %, as the plain shadow
    rule) and the band edge's own slant over its rows.
(2) NOTHING IN A SCANNER BAND IS DODGED. A sliver of the band's turned edge at the top corner (47–54 pt long, one pixel
    beyond band_mask's allowance) is a «line» beside the text; decide() dodged it up and down before its off-band slide —
    which takes the frame out of the band anyway — and ص 389, 579, 585 stand 12–15 pt higher in their frames than every
    page around them (text top 20.2 / 23.8 / 17.7 pt inside the frame, their neighbours 33–37; 27l and L+B 35.1 / 38.1 /
    30.2). A mark whose centre lies beyond the allowed area on a side that has a band is the band — in it, or in the wedge
    between its turned edge and the upright limit carried inside it (ص 389, 637: 5–6 pt; the second look's 1 % margin, the
    first bench of B4, left them dodged): the slide keeps it out, the dodge does not move for it (p['band_undodged']).
Usage: patch_b4.py SRC DST   (SRC = book_crop with fixes L, B, B2 and B3: code2/bc_lbb3.py)"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''    # beside it with it as its «detached pieces» (ص 694: «٣١٠»، «٢٨٨» — the text block 32 pt short). Touching the band's
    # edge where it lies outermost along the mark, long along it, thin by its ink (its area over its length: slanted)
    if band is not None:
        for i, s in enumerate(objs, 1):
            if i in shadow: continue
            y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
            if hgt[i] >= 0.4 * H and area[i] / hgt[i] <= 0.06 * Wd:
                l_, r_ = eL[y0:y1][eL[y0:y1] > 0], eR[y0:y1][eR[y0:y1] > 0]
                if len(l_) and x0 <= l_.min() + 1: shadow.add(i); allowed[0] = max(allowed[0], (x1 + c0) / scale)
                elif len(r_) and x1 >= Wd - r_.min() - 1: shadow.add(i); allowed[2] = min(allowed[2], (x0 + c0) / scale)
            elif wid[i] >= 0.4 * Wd and area[i] / wid[i] <= 0.06 * H:
                t_, b_ = eT[x0:x1][eT[x0:x1] > 0], eB[x0:x1][eB[x0:x1] > 0]
                if len(t_) and y0 <= t_.min() + 1: shadow.add(i); allowed[1] = max(allowed[1], (y1 + r0) / scale)
                elif len(b_) and y1 >= H - b_.min() - 1: shadow.add(i); allowed[3] = min(allowed[3], (y0 + r0) / scale)
''', '''    # beside it with it as its «detached pieces» (ص 694: «٣١٠»، «٢٨٨» — the text block 32 pt short). Touching the band's
    # edge where it lies outermost along the mark, long along it, thin by its ink (its area over its length: slanted), and
    # lying along it: no broader than 6 % and the band edge's own slant over its rows (fix B4 — a table's ruled grid whose
    # outer rule touches the band is tall and thin by its ink too: ص 636, 637, 638, the allowed area cut 362–431 pt deep)
    if band is not None:
        for i, s in enumerate(objs, 1):
            if i in shadow: continue
            y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
            if hgt[i] >= 0.4 * H and area[i] / hgt[i] <= 0.06 * Wd:
                l_, r_ = eL[y0:y1][eL[y0:y1] > 0], eR[y0:y1][eR[y0:y1] > 0]
                if len(l_) and x0 <= l_.min() + 1 and wid[i] <= 0.06 * Wd + l_.max() - l_.min():
                    shadow.add(i); allowed[0] = max(allowed[0], (x1 + c0) / scale)
                elif len(r_) and x1 >= Wd - r_.min() - 1 and wid[i] <= 0.06 * Wd + r_.max() - r_.min():
                    shadow.add(i); allowed[2] = min(allowed[2], (x0 + c0) / scale)
            elif wid[i] >= 0.4 * Wd and area[i] / wid[i] <= 0.06 * H:
                t_, b_ = eT[x0:x1][eT[x0:x1] > 0], eB[x0:x1][eB[x0:x1] > 0]
                if len(t_) and y0 <= t_.min() + 1 and hgt[i] <= 0.06 * H + t_.max() - t_.min():
                    shadow.add(i); allowed[1] = max(allowed[1], (y1 + r0) / scale)
                elif len(b_) and y1 >= H - b_.min() - 1 and hgt[i] <= 0.06 * H + b_.max() - b_.min():
                    shadow.add(i); allowed[3] = min(allowed[3], (y0 + r0) / scale)
''')

sub('''        tbx = p.get('text') or bx                    # a line beside the text (a scan line, an edge, print damage) is dodged
        avoid = (p.get('blots') or []) + [ln for ln in (p.get('lines') or []) if tbx and not (ln[0] >= tbx[0] - 1 and ln[2] <= tbx[2] + 1 and ln[1] >= tbx[1] - 1 and ln[3] <= tbx[3] + 1)]
''', '''        tbx = p.get('text') or bx                    # a line beside the text (a scan line, an edge, print damage) is dodged
        avoid = (p.get('blots') or []) + [ln for ln in (p.get('lines') or []) if tbx and not (ln[0] >= tbx[0] - 1 and ln[2] <= tbx[2] + 1 and ln[1] >= tbx[1] - 1 and ln[3] <= tbx[3] + 1)]
        # NOTHING IN A SCANNER BAND IS DODGED (fix B4, 2026-10-28): a mark whose centre lies beyond the allowed area on a side
        # that has a band — in the band, or in the wedge between its turned edge and the upright limit carried inside it — is
        # the band, kept out by the off-band slide below. Dodged first, it moved the page for nothing: خريدة القصر 0648 ص 389,
        # 579, 585, 637, a sliver of the band's turned edge at the top corner (5–11 pt beyond the limit), the frame 10–15 pt
        # down — the text that much higher than on every page around it. (The stains moved with the content above are
        # measured back where the allowed area was read)
        al4 = p.get('allowed')
        if al4 and avoid:
            mv4, nbl, nav = p.get('move') or [0, 0], len(p.get('blots') or []), len(avoid)
            def in_band(v, d):
                cx_, cy_ = (v[0] + v[2]) / 2 - d[0], (v[1] + v[3]) / 2 - d[1]
                return ((al4[0] > 0.5 and cx_ < al4[0]) or (al4[2] < p['w'] - 0.5 and cx_ > al4[2])
                        or (al4[1] > 0.5 and cy_ < al4[1]) or (al4[3] < p['h'] - 0.5 and cy_ > al4[3]))
            avoid = [v for k, v in enumerate(avoid) if not in_band(v, mv4 if k < nbl else [0, 0])]
            if len(avoid) < nav: p['band_undodged'] = nav - len(avoid)
''')

open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)

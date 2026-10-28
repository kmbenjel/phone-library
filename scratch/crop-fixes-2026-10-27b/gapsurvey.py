"""gapsurvey.py VERSION [-j J] — every page a regression run's recipe reads by its baselines (tilt_by_base), read again as
scanned (1,400 px, the text block of marks()) by base_angles and by a copy that also tells, per line, the longest run of
empty chunks (a gap: an index row «– entry ……… page number», a table) and the angle of the longest run of inked chunks alone.
Why (2026-10-28): مشتبهات القرآن ص 178, an index page standing level (its columns' edges 0.2–0.4°), was turned 1.425° by Q:
each row's fit ran from the page number's digits (their densest row above the Arabic baseline) across the gap to the entry
→ +1.1 to +1.6° on every row, IQR 0.12. → gap-survey.tsv: book, page, skew, tilt_by_base, base_tilt as is, without the gap
lines (A), with the gap lines read on their longer side (B), lines, gap lines, keeping a gap line only when its longer
side alone reads within 0.5° of it (C), leaving out a line split by a gap of a quarter of it whose smaller part is
1–2 chunks — a page number or a label set apart from the text (D), and the number of such lines"""
import sys, os, json, glob, csv
sys.path.insert(0, '/home/k/projects/phone-library/scripts'); sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))
import numpy as np, pymupdf
from scipy import ndimage
from concurrent.futures import ProcessPoolExecutor
import book_crop as bc
C = '/home/k/.cache/phone-library/crop-regress/'
D = os.path.dirname(os.path.abspath(__file__))

def fit(P):
    P = np.array(P, float)
    for _ in range(2):
        f = np.polyfit(P[:, 0], P[:, 1], 1); res = np.abs(P[:, 1] - np.polyval(f, P[:, 0]))
        if len(P) > 6: P = P[res < max(np.percentile(res, 75), 0.5)]
    return float(np.degrees(np.arctan(np.polyfit(P[:, 0], P[:, 1], 1)[0])))

def lines(a, paper, tb, z, K=16):
    """base_angles' lines (the same reading), each → (y, angle, longest empty run / K, angle of the longest inked run or None)"""
    if tb is None: return []
    H, W = a.shape; mx, my = 0.02 * W, 0.01 * H
    x0, y0 = max(0, int(tb[0] * z - mx)), max(0, int(tb[1] * z - my)); x1, y1 = min(W, int(tb[2] * z + mx)), min(H, int(tb[3] * z + my))
    if x1 - x0 < 50 or y1 - y0 < 50: return []
    ink = np.clip((paper - a[y0:y1, x0:x1].astype(float)) / max(paper, 1), 0, 1); bw = x1 - x0; out = []
    prof = ndimage.uniform_filter1d(ink.sum(1), max(3, int(0.0065 * W))); lab, n = ndimage.label(prof > 0.02 * prof.max())
    for k in range(1, n + 1):
        ys = np.nonzero(lab == k)[0]; r0, r1 = ys[0], ys[-1] + 1
        if r1 - r0 < 0.009 * W: continue
        pad = int(0.3 * (r1 - r0)); b = ink[max(0, r0 - pad):r1 + pad]
        xs = np.nonzero(b.sum(0) > 0.5)[0]
        if len(xs) < 2 or xs[-1] - xs[0] < 0.25 * bw: continue
        b = b[:, xs[0]:xs[-1] + 1]; e = np.linspace(0, b.shape[1], K + 1).astype(int); pts = []; js = []
        for j in range(K):
            pr = ndimage.gaussian_filter1d(b[:, e[j]:e[j + 1]].sum(1), 1.0)
            if pr.max() < 0.25 * (e[j + 1] - e[j]): continue
            r = int(np.argmax(pr))
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]; r = r + (0.5 * (pr[r - 1] - pr[r + 1]) / den if den < 0 else 0)
            pts.append(((e[j] + e[j + 1]) / 2, r)); js.append(j)
        if len(pts) < 6: continue
        have = set(js); gap = run = 0
        for j in range(K):
            run = run + 1 if j not in have else 0; gap = max(gap, run)
        runs, cur = [], []
        for j, p in zip(js, pts):
            if cur and j != cur[-1][0] + 1: runs.append(cur); cur = []
            cur.append((j, p))
        runs.append(cur); best = max(runs, key=len)
        side = fit([p for _, p in best]) if len(best) >= 6 else None
        # runs split at gaps of 4+ empty chunks (a quarter of the line): the smallest run's size
        big, cur2, prev = [], 0, None
        for j in js:
            if prev is not None and j - prev - 1 >= 4: big.append(cur2); cur2 = 0
            cur2 += 1; prev = j
        big.append(cur2)
        out.append((round(((r0 + r1) / 2 + y0) / z, 1), round(fit(pts), 3), gap / K, None if side is None else round(side, 3), min(big) if len(big) > 1 else None))
    return out

def tilt(an):
    if len(an) < 6: return None
    iq = float(np.subtract(*np.percentile(an, [75, 25])))
    return round(float(np.median(an)), 3) if iq < 0.3 else None

def read(arg):
    h, items = arg; doc = pymupdf.open(C + h + '.pdf'); out = []
    for i, sk, tb_ in items:
        try:
            tu = bc.Turner(doc, i); page = tu.page(0, 0, 0)
            w = page.rect.width; a, z = bc.gray(page, 1400); a = np.array(a); tu.close(); m = bc.marks(a, z, w)
            L = lines(a, m['paper'], m.get('text'), z) if m.get('paper') else []
            asis = tilt([l[1] for l in L]); G = [l for l in L if l[2] >= 0.25]
            A = tilt([l[1] for l in L if l[2] < 0.25])
            B = tilt([l[1] if l[2] < 0.25 else l[3] for l in L if l[2] < 0.25 or l[3] is not None])
            Cv = tilt([l[1] for l in L if l[2] < 0.25 or (l[3] is not None and abs(l[3] - l[1]) <= 0.5)])
            Dv = tilt([l[1] for l in L if not (l[4] is not None and l[4] <= 2)])
            out.append((h, i + 1, sk, tb_, asis, A, B, len(L), len(G), Cv, Dv, sum(1 for l in L if l[4] is not None and l[4] <= 2)))
        except Exception as e:
            out.append((h, i + 1, sk, tb_, 'ERR', str(e)[:60], '', 0, 0))
    doc.close(); return out

if __name__ == '__main__':
    args = sys.argv[1:]; J = 1
    if '-j' in args: k = args.index('-j'); J = int(args[k + 1]); del args[k:k + 2]
    v = args[0][:10]; OUT = f'{D}/gap-survey-{v}.tsv'
    done = {(r[0], int(r[1])) for r in csv.reader(open(OUT), delimiter='\t')} if os.path.exists(OUT) else set()
    jobs = []
    for f in sorted(glob.glob(f'{C}*.{v}*.json')):
        h = os.path.basename(f)[:12]; R = json.load(open(f))
        it = [(i, p.get('skew'), p.get('tilt_by_base')) for i, p in enumerate(R['pages'])
              if p.get('tilt_by_base') is not None and (h, i + 1) not in done]
        for k in range(0, len(it), 12): jobs.append((h, it[k:k + 12]))
    with open(OUT, 'a') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(read, jobs):
            for r in part: fo.write('\t'.join('' if x is None else str(x) for x in r) + '\n')
            fo.flush()
    print('done', OUT)

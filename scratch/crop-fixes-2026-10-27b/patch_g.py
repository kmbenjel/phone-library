"""Fix G (2026-10-28, regression 26i's diff): A LINE SPLIT INTO A LABEL AND ITS TEXT IS NO BASELINE. base_angles fits each
line's baseline through its column chunks; on an index row «– entry ……… page number» the fit runs from the number's digits
(their densest row above the Arabic baseline) across the empty middle to the entry: مشتبهات القرآن (d319e06e78d0) ص 178, a
level index page (its columns' edges stand within 0.2–0.4°), read +1.1 to +1.6° on all 8 rows (IQR 0.12) and fix Q turned it
1.425°. The entries alone read anything (−4.2 to +0.2°). Now a line whose inked chunks fall in parts split by a gap of a
quarter of the line or more (4 of the 16 chunks), the smallest part 1–2 chunks — a page number or a label set apart — is left
out. Two hemistichs of a verse (parts of 4+ chunks each) stay: on خزانة الأدب ج 1 the verse lines are the steadiest rulers.
Surveyed on every page 26i reads by its baselines (gapsurvey.py, variant D).
Usage: patch_g.py SRC DST"""
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

sub('''        b = b[:, xs[0]:xs[-1] + 1]; e = np.linspace(0, b.shape[1], K + 1).astype(int); pts = []
        for j in range(K):
            pr = ndimage.gaussian_filter1d(b[:, e[j]:e[j + 1]].sum(1), 1.0)
            if pr.max() < 0.25 * (e[j + 1] - e[j]): continue      # (a chunk with little ink on any row: no baseline)
            r = int(np.argmax(pr))
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]; r = r + (0.5 * (pr[r - 1] - pr[r + 1]) / den if den < 0 else 0)
            pts.append(((e[j] + e[j + 1]) / 2, r))
        if len(pts) < 6: continue
''', '''        b = b[:, xs[0]:xs[-1] + 1]; e = np.linspace(0, b.shape[1], K + 1).astype(int); pts = []; js = []
        for j in range(K):
            pr = ndimage.gaussian_filter1d(b[:, e[j]:e[j + 1]].sum(1), 1.0)
            if pr.max() < 0.25 * (e[j + 1] - e[j]): continue      # (a chunk with little ink on any row: no baseline)
            r = int(np.argmax(pr))
            if 0 < r < len(pr) - 1:
                den = pr[r - 1] - 2 * pr[r] + pr[r + 1]; r = r + (0.5 * (pr[r - 1] - pr[r + 1]) / den if den < 0 else 0)
            pts.append(((e[j] + e[j + 1]) / 2, r)); js.append(j)
        if len(pts) < 6: continue
        # a label set apart (2026-10-28, مشتبهات القرآن ص 178: an index row's page number across the empty middle — its
        # digits' densest row above the entry's baseline tilted every row's fit 1.1–1.6°): parts split by a gap of a quarter
        # of the line, the smallest of 1–2 chunks → no baseline; two hemistichs (4+ chunks each) stay
        parts, n_, prev = [], 0, None
        for j in js:
            if prev is not None and j - prev - 1 >= K // 4: parts.append(n_); n_ = 0
            n_ += 1; prev = j
        parts.append(n_)
        if len(parts) > 1 and min(parts) <= 2: continue
''')
open(dst, 'w', encoding='utf-8').write(s)
print('patched', dst)

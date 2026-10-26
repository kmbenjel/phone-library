"""projrules.py [J] — every page the 26g recipes turn by the projection (tilt_by_proj): its long rules across the page
(hrules, first look at 500 px) and the projection's reading with those rules whitened → projrules.tsv"""
import sys, os, json, glob
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')

def one(arg):
    h, items = arg; out = []
    doc = pymupdf.open(C + h + '.pdf')
    for i, rec in items:
        page = doc[i]; a, z = bc.gray(page, 500); a = np.array(a)
        st = rec.get('stamp'); ex = [bc.pad_box(b, page.rect.width) for b in st or []] + (rec.get('dots') or [])
        mk = bc.marks(a.copy(), z, page.rect.width, ex or None); hr = mk.get('hrules') or []
        if not hr: out.append((h, i + 1, rec.get('tilt_by_proj'), rec.get('skew'), 0, '', '', '')); continue
        paper = mk.get('paper') or 255; b = a.copy(); H, W = b.shape
        for r in hr:
            y0, y1 = max(0, int(r[2] * z) - 3), min(H, int(r[4] * z) + 4); x0, x1 = max(0, int(r[1] * z) - 3), min(W, int(r[3] * z) + 4)
            b[y0:y1, x0:x1] = 255
        t0 = bc.proj_signed(a, paper); t1 = bc.proj_signed(b, paper)
        tb = mk.get('text') or mk.get('box')
        where = ['in' if tb and r[2] >= tb[1] + 0.03 * (tb[3] - tb[1]) and r[4] <= tb[3] - 0.03 * (tb[3] - tb[1]) else 'edge' for r in hr]
        out.append((h, i + 1, rec.get('tilt_by_proj'), rec.get('skew'), len(hr), ' '.join(f'{r[0]:.2f}@{r[2]:.0f}{w[0]}' for r, w in zip(hr, where)), t0, t1))
    doc.close(); return out

if __name__ == '__main__':
    J = int(sys.argv[1]) if len(sys.argv) > 1 else 2; jobs = []
    for f in sorted(glob.glob(C + '*.b32a237bbf*.json')):
        h = os.path.basename(f)[:12]; R = json.load(open(f))
        it = [(i, {k: p.get(k) for k in ('tilt_by_proj', 'skew', 'stamp', 'dots')}) for i, p in enumerate(R['pages']) if p.get('tilt_by_proj') is not None and p.get('skew')]
        for k in range(0, len(it), 40): jobs.append((h, it[k:k + 40]))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'projrules.tsv'), 'w') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs):
            for row in part: fo.write('\t'.join(map(str, row)) + '\n')
            fo.flush()

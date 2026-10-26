"""sheetline.py [J] — the projection-turned pages of projrules.tsv that hold long rules: each rule's reach past the text
core (left / right, share of the page width) and length; a «sheet line» = reaching ≥ 5 % past the core on both sides;
the projection again with the sheet lines whitened → sheetline.tsv"""
import sys, os, json, glob
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc, numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
C = os.path.expanduser('~/.cache/phone-library/crop-regress/'); D = os.path.dirname(os.path.abspath(__file__))

def one(arg):
    h, items = arg; out = []
    doc = pymupdf.open(C + h + '.pdf')
    for i, rec in items:
        page = doc[i]; W = page.rect.width; a, z = bc.gray(page, 500); a = np.array(a)
        st = rec.get('stamp'); ex = [bc.pad_box(b, W) for b in st or []] + (rec.get('dots') or [])
        mk = bc.marks(a.copy(), z, W, ex or None); hr = mk.get('hrules') or []; core = mk.get('core'); tb = mk.get('text') or mk.get('box')
        if not hr or not core: continue
        desc, sheet = [], []
        for r in hr:
            l_, r_ = (core[0] - r[1]) / W, (r[3] - core[2]) / W; ln = (r[3] - r[1]) / W
            sl = l_ >= 0.05 and r_ >= 0.05
            desc.append(f'{r[0]:+.2f}° y{r[2]:.0f}-{r[4]:.0f} x{r[1]:.0f}-{r[3]:.0f} past {l_:+.2f}/{r_:+.2f} len {ln:.2f}{" SHEET" if sl else ""}')
            if sl: sheet.append(r)
        t0 = bc.proj_signed(a, mk.get('paper') or 255); t1 = None
        if sheet:
            b = a.copy(); H, Wp = b.shape
            for r in sheet:
                b[max(0, int(r[2] * z) - 3):min(H, int(r[4] * z) + 4), max(0, int(r[1] * z) - 3):min(Wp, int(r[3] * z) + 4)] = 255
            t1 = bc.proj_signed(b, mk.get('paper') or 255)
        out.append((h, i + 1, rec.get('tilt_by_proj'), rec.get('skew'), f'core x{core[0]:.0f}-{core[2]:.0f} y{core[1]:.0f}-{core[3]:.0f}', ' | '.join(desc), t0, t1))
    doc.close(); return out

if __name__ == '__main__':
    J = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    want = {}
    for l in open(f'{D}/projrules.tsv'):
        r = l.rstrip('\n').split('\t')
        if r[4] != '0': want.setdefault(r[0], set()).add(int(r[1]) - 1)
    jobs = []
    for h, pgs in sorted(want.items()):
        R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1]))
        it = [(i, {k: R['pages'][i].get(k) for k in ('tilt_by_proj', 'skew', 'stamp', 'dots')}) for i in sorted(pgs)]
        for k in range(0, len(it), 30): jobs.append((h, it[k:k + 30]))
    with open(f'{D}/sheetline.tsv', 'w') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs):
            for row in part: fo.write('\t'.join(map(str, row)) + '\n')
            fo.flush()

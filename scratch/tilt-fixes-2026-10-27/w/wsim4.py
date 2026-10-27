"""wsim4.py W.jsonl OUT.txt [-j J] — guard W step 3 (bc_w3) end to end — the print's certificate and the fallback included —
on every page guard W (bc_w2, from the stored views) refuses: kept / re-turned by its lines / left as scanned — wsim2's verdict lines, for the pages
that matter (the rest are kept by both)"""
import sys, os, json
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
import numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D + '/code'); sys.path.insert(0, D)
import bc_w3 as bc
import wsim3_eval as ev                 # (verdict(): V0 on bc_w2's rules)
C = '/home/k/.cache/phone-library/crop-regress/'
RECS = {os.path.basename(l.strip())[:12]: l.strip() for l in
        open('/tmp/claude-1000/-home-k-projects-phone-library/fcd8d325-9813-40ca-94ce-bd6c86424307/scratchpad/w/wsim2-list.txt')}

def view(doc, i, p, d):
    tu = bc.Turner(doc, i); q = dict(p, skew=d); page = tu.page(d, *(p.get('move') or [0, 0])); a, z = bc.gray(page, 1000); a = a.copy()
    if p.get('sheet'): a = bc.whiten(a, z, bc.fwd_box(doc, i, q, p['sheet']))
    ex = [bc.pad_box(b, page.rect.width) for b in p.get('stamp') or []] + (p.get('dots') or [])
    exf = bc.fwd_boxes(doc, i, q, ex) if ex else []
    mk = bc.marks(a, z, page.rect.width, exf or None)
    sh = abs(bc.skew_of(mk['xy'], raw=True)[0]) if mk.get('xy') is not None else None
    for x in exf: a[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
    T = bc.line_tracks(a, mk['paper'], mk.get('text'), z) if mk.get('paper') else []
    tu.close(); return T, sh

def one(arg):
    h, items = arg; doc = pymupdf.open(C + h + '.pdf'); out = []
    for i, p in items:
        try:
            d = p['skew']; t0, _ = view(doc, i, p, 0.0); t1, _ = view(doc, i, p, d); L = bc.lines_read(t0, t1, d); tw = bc.two_angles(L)
            if tw:
                cert, R = bc.print_turn(t0, t1, d)
                if cert: out.append((h, i + 1, d, 'kept by the print', R)); continue
            if not tw: out.append((h, i + 1, d, 'kept', None)); continue
            m = round(round(float(np.median([v[1] for v in L])) / 0.025) * 0.025, 3); res = ('left', [(round(v[1], 2), round(v[2], 2)) for v in tw][:6])
            if abs(m) >= bc.SKEW_MIN:
                t2, sh = view(doc, i, p, m); L2 = bc.lines_read(t0, t2, m)
                if L2 and not bc.two_angles(L2) and sum(1 for v in L2 if abs(v[2]) <= 0.2 + 1e-6) >= 0.8 * len(L2) and sh is not None and sh <= 0.2 + 1e-6:
                    res = ('re-turned', m, round(float(np.median([v[2] for v in L2])), 3), round(sh, 3))
            out.append((h, i + 1, d, res[0], res[1:]))
        except Exception as e: out.append((h, i + 1, p['skew'], 'ERR', repr(e)[:80]))
    doc.close(); return out

if __name__ == '__main__':
    args = sys.argv[1:]; J = 3
    if '-j' in args: k = args.index('-j'); J = int(args[k + 1]); del args[k:k + 2]
    pick = {}
    for l in open(args[0]):
        r = json.loads(l)
        if 'err' in r: continue
        _, w0 = ev.verdict(r['t0'], r['t1'], r['d'])     # (W3 refuses a subset of W's pages)
        if w0: pick.setdefault(r['h'], set()).add(r['g'])
    jobs = []
    for h, gs in pick.items():
        R = json.load(open(RECS[h])); it = [(g - 1, R['pages'][g - 1]) for g in sorted(gs)]
        for k in range(0, len(it), 6): jobs.append((h, it[k:k + 6]))
    print(sum(len(g) for g in pick.values()), 'pages', flush=True)
    res = []
    with ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs): res += part
    res.sort()
    with open(args[1], 'w') as fo:
        for h, g, d, k, x in res: fo.write(f'{h} p. {g} turn {d}: {k} {x}\n')
    print('done', flush=True)

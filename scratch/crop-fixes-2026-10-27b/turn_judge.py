"""turn_judge.py OLD NEW [BOOK …] [-j J] — every page whose turn differs between two regression runs (recipes in the regression
cache, by book_crop md5 prefix), judged by two rulers read on the page AS SCANNED: the lines' baselines (book_crop.base_angles
at 1,400 px, lines more than 1° from their median left out — two lines run together — at least 6 lines within an IQR of 0.3°)
and the lines followed across the page (book_crop.line_tracks at 1,000 px, reliable lines, their median; it also tells two
angles). A turn d leaves «angle − d» by either (both rulers are linear in the turn). → turn-judge.tsv (resumable cache of the
readings) and a summary by cause: how much tilt the old and the new turns leave, and every page the new one leaves worse
(≥ 0.05° more, or over 0.2°) by the rulers that read it"""
import sys, os, json, glob, csv, collections
sys.path.insert(0, '/home/k/projects/phone-library/scripts'); sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))
import numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
import book_crop as bc
C = '/home/k/.cache/phone-library/crop-regress/'
D = os.path.dirname(os.path.abspath(__file__)); OUT = f'{D}/turn-judge.tsv'

def recipe(h, v):
    f = sorted(glob.glob(f'{C}{h}.{v}*.json'))
    return json.load(open(f[0])) if f else None

def cause(p, q):
    for k, c in (('two_angles', 'two angles (left)'), ('turn_by_tracks', "the lines' turn"), ('level_by_print', 'the print'),
                 ('proj_sheet_line', 'sheet line'), ('base_found', 'baselines found (R)'), ('level_by_base', 'baselines, level by them'),
                 ('tilt_by_base', 'baselines, other check')):
        if q.get(k) is not None: return c
    if q.get('level_by_proj') is not None: return 'projection'
    return 'other'

def read(arg):
    h, items = arg; doc = pymupdf.open(C + h + '.pdf'); out = []
    for i, p in items:
        try:
            tu = bc.Turner(doc, i); page = tu.page(0, 0, 0); w = page.rect.width
            a14, z14 = bc.gray(page, 1400); a14 = np.array(a14); a10, z10 = bc.gray(page, 1000); a10 = np.array(a10); tu.close()
            m14 = bc.marks(a14, z14, w); m10 = bc.marks(a10, z10, w)
            an = np.array([v[1] for v in bc.base_angles(a14, m14['paper'], m14.get('text'), z14)]) if m14.get('paper') else np.array([])
            if len(an): an = an[np.abs(an - np.median(an)) <= 1.0]
            iq = float(np.subtract(*np.percentile(an, [75, 25]))) if len(an) >= 6 else None
            b = round(float(np.median(an)), 3) if iq is not None and iq < 0.3 else None
            T = [t for t in (bc.line_tracks(a10, m10['paper'], m10.get('text'), z10) if m10.get('paper') else [])
                 if t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3 and not (len(t) > 5 and t[5])]
            ta = [t[1] for t in T]; tq = float(np.subtract(*np.percentile(ta, [75, 25]))) if len(ta) >= 5 else None
            tr = round(float(np.median(ta)), 3) if tq is not None and tq < 0.3 else None
            out.append((h, i + 1, b, len(an), None if iq is None else round(iq, 3), tr, len(ta), None if tq is None else round(tq, 3)))
        except Exception as e: out.append((h, i + 1, None, 0, None, None, 0, None))
    doc.close(); return out

if __name__ == '__main__':
    args = sys.argv[1:]; J = 1
    if '-j' in args: k = args.index('-j'); J = int(args[k + 1]); del args[k:k + 2]
    old, new, books = args[0], args[1], args[2:]
    if not books: books = sorted({os.path.basename(f)[:12] for f in glob.glob(f'{C}*.{new}*.json')})
    have = {}
    if os.path.exists(OUT):
        for r in csv.reader(open(OUT), delimiter='\t'): have[(r[0], int(r[1]))] = r
    pairs, jobs = {}, []
    for h in books:
        A, B = recipe(h, old), recipe(h, new)
        if not A or not B: continue
        ch = [i for i, (p, q) in enumerate(zip(A['pages'], B['pages'])) if (p.get('skew') or 0) != (q.get('skew') or 0)]
        pairs[h] = (A, B, ch)
        it = [(i, None) for i in ch if (h, i + 1) not in have]
        for k in range(0, len(it), 10): jobs.append((h, it[k:k + 10]))
    if jobs:
        with open(OUT, 'a') as fo, ProcessPoolExecutor(J) as ex:
            for part in ex.map(read, jobs):
                for r in part: fo.write('\t'.join('' if x is None else str(x) for x in r) + '\n'); have[(r[0], r[1])] = [str(x) if x is not None else '' for x in r]
                fo.flush()
    f = lambda s: float(s) if s not in ('', None) else None
    S = collections.defaultdict(lambda: collections.defaultdict(list)); flag = []
    for h, (A, B, ch) in pairs.items():
        for i in ch:
            p, q = A['pages'][i], B['pages'][i]; r = have.get((h, i + 1))
            if not r: continue
            d0, d1 = p.get('skew') or 0.0, q.get('skew') or 0.0; c = cause(p, q)
            for name, val in (('baselines', f(r[2])), ('tracks', f(r[5]))):
                if val is None: continue
                r0, r1 = val - d0, val - d1; S[c][name].append((abs(r0), abs(r1)))
                if c != 'two angles (left)' and (abs(r1) >= abs(r0) + 0.05 or abs(r1) > 0.2):
                    flag.append((h, i + 1, c, name, d0, d1, round(r0, 3), round(r1, 3)))
            if f(r[2]) is None and f(r[5]) is None: S[c]['unread'].append(1)
    print(f'{old} → {new}: pages whose turn changed, by cause — the tilt left by the old | new turn (mean |°|, n read)')
    for c in sorted(S):
        parts = []
        for name in ('baselines', 'tracks'):
            v = S[c][name]
            if v: parts.append(f'{name} {np.mean([x[0] for x in v]):.3f} | {np.mean([x[1] for x in v]):.3f} (n {len(v)})')
        print(f'  {c}: ' + '; '.join(parts) + (f'; unread {len(S[c]["unread"])}' if S[c]['unread'] else ''))
    print(f'\nleft worse or over 0.2° by a ruler: {len(flag)}')
    for x in sorted(flag): print('  ', x)

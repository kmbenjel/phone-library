"""Regression check for scripts/book_crop.py: every page the method once got wrong, or the owner pointed at, must come out
right before a new sample is shown (owner, 2026-10-08: «أن تعرف المنهج العام الذي ستتوقع به الخطأ»).
Cases: data/improve/crop-regression.tsv (phone path, page, check, expected, note). The books are fetched once from the phone
(Unicode-normalised lookup, guarded path) into ~/.cache/phone-library/crop-regress/ and analysed with book_crop.plan();
results are cached per (book bytes, book_crop.py) so an unchanged method is not re-run.
Usage: python3 scripts/crop_regress.py        → one line per case (PASS/FAIL) and a summary; exit 1 on any FAIL"""
import csv, hashlib, json, os, subprocess, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import book_crop as bc, pymupdf
CACHE = os.path.expanduser('~/.cache/phone-library/crop-regress')
N = lambda s: unicodedata.normalize('NFC', s)

def local_copy(path):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, hashlib.md5(N(path).encode()).hexdigest()[:12] + '.pdf')
    if os.path.exists(out): return out
    idx = [l.split('\t')[0] for l in open(os.path.join(ROOT, 'data/phone/index-now.tsv'), encoding='utf-8')]
    hits = [p for p in idx if N(p) == N(path)]
    if len(hits) != 1 or not hits[0].endswith('.pdf'): raise SystemExit(f'not on the phone (index-now): {path}')
    subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', '--retries', '3', 'phone:Books/' + hits[0], out], check=True)
    return out

def recipe(pdf):
    me = hashlib.md5(open(os.path.join(ROOT, 'scripts/book_crop.py'), 'rb').read()).hexdigest()[:10]
    key = os.path.join(CACHE, os.path.basename(pdf)[:-4] + f'.{me}.json')
    if os.path.exists(key): return json.load(open(key))
    rec = bc.plan(pdf); json.dump(rec, open(key, 'w'), ensure_ascii=False); return rec

def forward(page, p):
    """maps original-page points to the reader's frame (turned, moved), like the content transform"""
    m = pymupdf.Matrix(1, 0, 0, 1, 0, 0)
    try:
        mv = p.get('move') or [0, 0]; deg = p.get('skew') or 0
        tm = page.transformation_matrix; mb = bc.raw_box(page.parent, page.xref, 'MediaBox'); cx, cy = (mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2
        fwd = pymupdf.Matrix(1, 0, 0, 1, -cx, -cy) * pymupdf.Matrix(deg) * pymupdf.Matrix(1, 0, 0, 1, cx, cy) * pymupdf.Matrix(1, 0, 0, 1, mv[0], -mv[1])
        m = ~tm * fwd * tm
    except Exception: pass
    return lambda x, y: pymupdf.Point(x, y) * m

def check(row, rec, pdf):
    path, page, what, expect = row[0], int(row[1]), row[2], row[3]
    p = rec['pages'][page - 1]; crop = p.get('crop')
    if what == 'turn':
        got = 'yes' if p.get('skew') else 'no'; return got == expect, f'turned {p.get("skew")}'
    if what == 'parity':
        got = 'yes' if any(float(v) for v in (rec.get('parity_offsets') or {}).values()) else 'no'
        return got == expect, f'offsets {rec.get("parity_offsets")}'
    if rec.get('decision') != 'crop': return False, rec.get('decision')
    if what == 'centred':
        if not crop: return False, 'page left whole'
        b = p['box']; cxb, cxc = (b[0] + b[2]) / 2, (crop[0] + crop[2]) / 2
        return abs(cxb - cxc) <= 0.02 * (crop[2] - crop[0]), f'content centre {cxb:.0f}, box centre {cxc:.0f}'
    if what in ('out', 'in'):
        if not crop: return what == 'out', 'page left whole'
        r = [float(v) for v in expect.split(',')]
        doc = pymupdf.open(pdf); f = forward(doc[page - 1], p)
        pts = [f(r[0], r[1]), f(r[2], r[1]), f(r[2], r[3]), f(r[0], r[3])]
        x0, x1 = min(q.x for q in pts), max(q.x for q in pts); y0, y1 = min(q.y for q in pts), max(q.y for q in pts)
        overlap = x0 < crop[2] and x1 > crop[0] and y0 < crop[3] and y1 > crop[1]
        inside = x0 >= crop[0] and x1 <= crop[2] and y0 >= crop[1] and y1 <= crop[3]
        return (not overlap) if what == 'out' else inside, f'region {x0:.0f}–{x1:.0f}, box {crop[0]:.0f}–{crop[2]:.0f}'
    return False, 'unknown check ' + what

def main():
    rows = [r for r in csv.reader(open(os.path.join(ROOT, 'data/improve/crop-regression.tsv'), encoding='utf-8'), delimiter='\t')
            if r and not r[0].startswith('#')]
    fails = 0; recs = {}
    for r in rows:
        pdf = local_copy(r[0])
        if pdf not in recs: recs[pdf] = recipe(pdf)
        ok, why = check(r, recs[pdf], pdf)
        fails += not ok
        print(('PASS' if ok else 'FAIL'), r[0].rsplit('/', 1)[-1][:45], 'p.', r[1], r[2], r[3], '—', why, '|', r[4] if len(r) > 4 else '', flush=True)
    print(f'{len(rows) - fails}/{len(rows)} pass')
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()

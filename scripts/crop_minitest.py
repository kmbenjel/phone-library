"""Quick test of book_crop on the pages the owner marked (data/crop/owner-marked-2026-10-14.tsv): for each book, an extract —
each marked page with 20 pages either side, plus the first and last two pages — analysed with book_crop.plan(), then
before/after images of the marked pages. Output: ~/.cache/phone-library/crop-minitest/<run>/<sheet id>/ (recipe.json, map.json,
images). Usage: python3 scripts/crop_minitest.py RUN [sheet id …]   (reusable while the method is being fixed)"""
import sys, os, json, re, time, hashlib, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'scripts')); os.chdir(ROOT)
import book_crop as bc, pymupdf
N = lambda s: unicodedata.normalize('NFC', s)
run = sys.argv[1]; only = set(sys.argv[2:])
OUT = os.path.expanduser(f'~/.cache/phone-library/crop-minitest/{run}'); os.makedirs(OUT, exist_ok=True)
for l in open('data/crop/owner-marked-2026-10-14.tsv', encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    n, rep, p, why = l.rstrip('\n').split('\t')[:4]
    if only and n not in only: continue
    d = os.path.join(OUT, n)
    if os.path.exists(os.path.join(d, 'recipe.json')): continue
    os.makedirs(d, exist_ok=True)
    src = os.path.expanduser('~/.cache/phone-library/crop-regress/') + hashlib.md5(N(p).encode()).hexdigest()[:12] + '.pdf'
    marked = sorted({int(f[1:5]) for f in os.listdir(os.path.expanduser(f'~/.cache/phone-library/crop-sheets/{n}')) if re.match(r'p\d{4}-', f)})
    doc = pymupdf.open(src); k = doc.page_count
    keep = sorted({0, 1, k - 2, k - 1} | {j for m in marked for j in range(max(0, m - 21), min(k, m + 20))})
    doc.select(keep); ex = os.path.join(d, 'extract.pdf'); doc.save(ex, garbage=3); doc.close()
    import crop_batch as cb
    while not cb.room(): time.sleep(30)               # a book starts only with ≥ 3 GB free (2026-10-18 03:05)
    t = time.time(); rec = bc.plan(ex, min(3, cb.governed(3))); json.dump(rec, open(os.path.join(d, 'recipe.json'), 'w'), ensure_ascii=False)
    sp = {int(k) for k in (rec.get('split') or {})}       # a split sheet becomes two pages: later pages shift by one each
    at = lambda j: j + sum(1 for k in sp if k < j)
    mp = {str(m): at(keep.index(m - 1)) for m in marked}; json.dump({'pages': keep, 'marked': mp, 'split': sorted(sp)}, open(os.path.join(d, 'map.json'), 'w'))
    try: bc.sheet(ex, rec, d, [(i, 'marked') for i in sorted(set(mp.values()) | {0, 1})])
    except Exception as e: print('SHEET FAIL', n, repr(e)[:150], flush=True)
    print(time.strftime('%T'), n, rec.get('decision'), f'{time.time() - t:.0f}s', len(keep), 'pages', flush=True)

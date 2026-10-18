"""Regression check for scripts/book_crop.py: every page the method once got wrong, or the owner pointed at, must come out
right before a new sample is shown (owner, 2026-10-08: «أن تعرف المنهج العام الذي ستتوقع به الخطأ»).
Cases: data/improve/crop-regression.tsv (phone path, page, check, expected, note). Whole books: no page keeps a tilt after
turning, and no page that both tilt measures see as tilted is left unturned (owner 2026-10-08: «ولم نبق شيئا من الميل»). The books are fetched once from the phone
(Unicode-normalised lookup, guarded path) into ~/.cache/phone-library/crop-regress/ and analysed with book_crop.plan();
results are cached per (book bytes, book_crop.py) so an unchanged method is not re-run.
Usage: python3 scripts/crop_regress.py        → one line per case (PASS/FAIL) and a summary; exit 1 on any FAIL"""
import csv, hashlib, json, os, subprocess, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import book_crop as bc, pymupdf
from book_crop import inside
CACHE = os.path.expanduser('~/.cache/phone-library/crop-regress')
N = lambda s: unicodedata.normalize('NFC', s)

def local_copy(path):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, hashlib.md5(N(path).encode()).hexdigest()[:12] + '.pdf')
    if os.path.exists(out): return out
    idx = [l.split('\t')[0] for l in open(os.path.join(ROOT, 'data/phone/index-now.tsv'), encoding='utf-8')]
    hits = [p for p in idx if N(p) == N(path)]
    if not hits:                                     # renamed since the case was written: followed through the change log,
        import crop_batch as cb                      # only to the first name of its chain that is on the phone (the log
        fwd, _ = cb.moves(); have = {N(p): p for p in idx}; q, seen = path, set()   # also holds the crop's own swaps)
        while N(q) not in have and q in fwd and q not in seen: seen.add(q); q = fwd[q]
        hits = [have[N(q)]] if N(q) in have else []
    if len(hits) != 1 or not hits[0].endswith('.pdf'): raise SystemExit(f'not on the phone (index-now): {path}')
    subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', '--retries', '3', 'phone:Books/' + hits[0], out], check=True)
    # a book already cropped on the phone: its original bytes are the first <original size> bytes (the crop is an appended
    # revision), proven by the logged MD5 — the method is always tested on the book as it was scanned
    logged = [r[4] for r in csv.reader(open(os.path.join(ROOT, 'data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t')
              if len(r) > 4 and r[1] == 'crop' and N(r[2]) == N('Books/' + hits[0]) and 'original ' in r[4]]
    if logged and 'crop undone' not in logged[-1]:
        n0 = int(logged[-1].split('original ')[1].split(' B')[0]); m0 = logged[-1].split('md5 ')[1].split(';')[0]
        if os.path.getsize(out) > n0:
            with open(out, 'r+b') as f: f.truncate(n0)
        if hashlib.md5(open(out, 'rb').read()).hexdigest() != m0:
            os.remove(out); raise SystemExit(f'original bytes not recovered for {path}')
    return out

def recipe(pdf):
    me = hashlib.md5(open(os.path.join(ROOT, 'scripts/book_crop.py'), 'rb').read()).hexdigest()[:10]
    key = os.path.join(CACHE, os.path.basename(pdf)[:-4] + f'.{me}.json')
    if os.path.exists(key): return json.load(open(key))
    import crop_batch as cb, time
    while not cb.room(): time.sleep(30)               # a book starts only with ≥ 3 GB free (2026-10-18 03:05)
    try: jobs = int(open(os.path.join(ROOT, 'data', 'crop', 'workers')).read().strip())   # the memory governor's number
    except (OSError, ValueError): jobs = int(os.environ.get('JOBS', 3))
    rec = bc.plan(pdf, max(1, jobs)); json.dump(rec, open(key, 'w'), ensure_ascii=False); return rec

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
    if what == 'turn':                               # turned or not as expected — and a turned page reads level
        got = 'yes' if p.get('skew') else 'no'
        lvl, img = p.get('after_tilt'), p.get('after_tilt_image')     # both measures must read the turned page level
        # (a two-column page is judged by its columns' line starts — the whole-page measures are fooled by the gutter; a
        # projection turn is verified level on the page's own ink, without them: اللآلئ ج 2 ص 469, 2.6° → 0.1°)
        ok = got == expect and (got == 'no' or (lvl is not None and img is not None and ((lvl <= bc.LEVEL and img <= bc.IMG_LEVEL)
             or (p.get('curved') and lvl <= bc.CURVED and img <= bc.CURVED) or (p.get('level_by_lines') is not None and max(lvl, img) <= 0.35)
             or (p.get('level_by_edge') is not None and lvl <= 0.2)
             or (p.get('level_by_columns') is not None and p['level_by_columns'] <= 0.15)
             or p.get('reduced') is not None)
             or (p.get('level_by_proj') is not None and p['level_by_proj'] <= 0.2))) \
             and (expect == 'no' or not p.get('untreated_tilt'))
        return ok, f'turned {p.get("skew")}, left after turning {lvl} (image {img}){" curved" if p.get("curved") else ""}, untreated {p.get("untreated_tilt")}'
    if what == 'cropped':                              # cropped, not left whole (a book without print in its margins)
        got = 'yes' if p.get('crop') else 'no'
        return got == expect, f'crop {p.get("crop")}, enlarged {p.get("enlarged")}, book clean margins {rec.get("clean_margins")}'
    if what == 'cover':                                # a cover photographed on the bed or a sheet: shown alone (cover_rect)
        return (p.get('kind') == 'cover') == (expect == 'yes'), f'kind {p.get("kind")}, cover {p.get("cover")}'
    if what == 'figures_in':                           # a picture or plate beside the text: wholly shown
        sh = p.get('show') or p.get('crop'); fg = p.get('figures') or []
        if expect == 'yes' and not fg: return False, f'no figure found (kind {p.get("kind")}, crop {crop})'
        return all(inside(b, sh, 1.0) for b in fg) if sh else p.get('crop') is None, f'figures {fg}, shown {sh}'
    if what == 'scale1':                               # shown at the book's size: not shrunk for a stamp, a line, a flaw
        sc = p.get('scale'); return (sc is not None and abs(sc - 1) <= 1e-3) == (expect == 'yes'), f'scale {sc}, crop {crop}'
    if what == 'parity':
        got = 'yes' if any(float(v) for v in (rec.get('parity_offsets') or {}).values()) else 'no'
        return got == expect, f'offsets {rec.get("parity_offsets")}'
    if rec.get('decision') != 'crop': return False, rec.get('decision')
    if what == 'xcentre':                              # the shown part's centre lies at X ± T pt (a measured anchor: the page
        if not p.get('show'): return False, 'no frame'   # number, a centred heading)
        x, t = (float(v) for v in expect.split('±')); s = p['show']; c = (s[0] + s[2]) / 2
        return abs(c - x) <= t, f'centre {c:.1f} (expected {x}±{t}), anchored {p.get("anchored_x")}'
    if what == 'centred':
        if not crop: return False, 'page left whole'
        b = p['box']; cxb, cxc = (b[0] + b[2]) / 2, (crop[0] + crop[2]) / 2
        return abs(cxb - cxc) <= 0.02 * (crop[2] - crop[0]), f'content centre {cxb:.0f}, box centre {cxc:.0f}'
    if what in ('out', 'in'):
        crop = p.get('show') or crop                    # what the reader sees (a page shrunk to the book's box included)
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
    # (one book's recipe in memory at a time, read again from the cache when needed: holding all of them made this process
    # 1.3 GB, the memory pen overflowed beside its workers and the governor's brake killed the run six times, 2026-10-18)
    fails = 0; recs = {}; cur = (None, None)
    import time
    for r in rows:
        pdf = local_copy(r[0])
        if pdf not in recs:
            cur = (None, None)
            t0 = time.time(); cur = (pdf, recipe(pdf)); recs[pdf] = True; print(f'   (analysed {os.path.basename(pdf)} in {time.time() - t0:.0f} s)', flush=True)
        elif cur[0] != pdf: cur = (pdf, recipe(pdf))
        ok, why = check(r, cur[1], pdf)
        fails += not ok
        print(('PASS' if ok else 'FAIL'), r[0].rsplit('/', 1)[-1][:45], 'p.', r[1], r[2], r[3], '—', why, '|', r[4] if len(r) > 4 else '', flush=True)
    keep_flat = {(local_copy(r[0]), int(r[1])) for r in rows if r[2] == 'turn' and r[3] == 'no'}   # pages the owner/test says stay as they are
    cur = None
    for pdf in recs:                                 # whole books: ONE page size (owner 2026-10-09: «فيجب اطّراده في جميع الكتب»)
        rec = recipe(pdf)
        if rec.get('decision') not in ('crop', 'level'): continue   # — applied for real, every page's size read back — and no note cut
        out = pdf[:-4] + '.regress-out.pdf'
        try:
            info = bc.apply(pdf, rec, out)
            ok, why = True, (f'{info["pages"]} pages, all {rec["size"]}; shrunk to fit {len(rec.get("scaled") or [])}, on blank paper {len(rec.get("bands") or [])}'
                             if rec['decision'] == 'crop' else f'level only: {info["turned_or_moved"]} pages turned, every page its own size')
        except AssertionError as e: ok, why = False, str(e)
        finally:
            if os.path.exists(out): os.remove(out)
        cut = [i + 1 for i, p in enumerate(rec['pages']) if p.get('notes_cut')]
        if cut: ok = False; why += f' | marginal notes cut on pages {cut[:12]}'
        fails += not ok
        print(('PASS' if ok else 'FAIL'), os.path.basename(pdf), 'one page size:', why, flush=True)
    for pdf in recs:                                 # whole books: no tilt kept after turning, none left that both measures see
        rec = recipe(pdf); rt = rec.get('residual_tilt') or []; ut = [x for x in rec.get('untreated_tilt') or [] if (pdf, x) not in keep_flat]
        if rt or ut: fails += 1
        print(('PASS' if not (rt or ut) else 'FAIL'), os.path.basename(pdf), 'pages still tilted after turning:', rt[:12],
              '| tilted (both measures) but not turned:', ut[:12], '| curved, brought below sight:', (rec.get('curved') or [])[:12],
              '| disputed (the image shows no tilt):', (rec.get('tilt_disputed') or [])[:12])
    print(f'{fails} failures')
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()

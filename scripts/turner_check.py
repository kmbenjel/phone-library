"""Is book_crop.Turner exact? Every view it draws compared byte for byte with a fresh turned() document — the proof that
the speed-up changes nothing (2026-10-26: the first Turner was not exact where a page's image is less than 90 % shown —
MuPDF drew a later view from the whole decoded image; see Turner's docstring). Run it again after any PyMuPDF/MuPDF
upgrade or change to Turner, whole_shown or odd_drawing. Books: the regression's local copies
(~/.cache/phone-library/crop-regress/<hash>.pdf); «<hash>.split» = the book split as book_crop.plan splits spreads.
Views: turns and moves that make an image pass from whole to part and back (up to 5° and 60 pt), at 1,000 and 500 px.
Usage: python3 scripts/turner_check.py STEP [HASH ...]   (every STEP-th page; no hash: every cached book)
Prints per book: views, views drawn from a fresh copy, views different (any → exit 1)"""
import glob, os, shutil, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_crop as bc, pymupdf, numpy as np

C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
V1000 = [(0, 0, 0), (0.35, 0, 0), (0, 3.5, -12.0), (0.25, 3.5, -12.0), (-0.35, 0, 0), (1.2, 0, 0), (0, -20.0, 30.0), (0, 0, -60.0),
         (0, 40.0, 0), (-2.5, 0, 0), (0.5, 0, 0), (3.0, 0, 0), (-5.0, 0, 0), (0.45, 0, 0), (1.2, -15.0, 25.0), (0, 0, 0)]
V500 = [(0.6, 0, 0), (0, 0, 0), (0.8, 0, 0), (-1.0, 0, 0), (0, 0, -50.0), (0.2, 0, 0), (2.0, 0, 0), (-0.6, 0, 0), (0, 0, 0)]

def check(path, step):
    d = pymupdf.open(path); tot = fresh = bad = 0
    for i in range(0, d.page_count, step):
        if d[i].rotation: continue
        for px, views in ((1000, V1000), (500, V500)):
            tu = bc.Turner(d, i)
            for v in views:
                t = bc.turned(d, i, *v); a, _ = bc.gray(t[0], px); t.close()
                b, _ = bc.gray(tu.page(*v), px); tot += 1; fresh += tu.fresh is not None
                if not np.array_equal(a, b): bad += 1; print('  DIFFERENT p.', i + 1, px, 'px, view', v, int((a != b).sum()), 'pixels', flush=True)
            tu.close()
    n = d.page_count; d.close()
    return n, tot, fresh, bad

def main():
    step = int(sys.argv[1]); hs = sys.argv[2:] or sorted(os.path.basename(f)[:12] for f in glob.glob(C + '*.pdf') if len(os.path.basename(f)) == 16)
    bad_all = 0
    for h in hs:
        t0 = time.time(); src = C + h.split('.')[0] + '.pdf'; tmp = None
        if h.endswith('.split'):                       # as plan() splits a book of spreads
            d = pymupdf.open(src); gut = bc.spread_gutters(d); d.close()
            tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'split.pdf'); shutil.copyfile(src, path)
            dd = pymupdf.open(path); bc.split_pages(dd, gut); dd.save(path, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); dd.close()
        else: path = src
        try: n, tot, fresh, bad = check(path, step)
        finally:
            if tmp: shutil.rmtree(tmp)
        bad_all += bad
        print(f'{h}: {n} pages, every {step}: {tot} views, {fresh} from a fresh copy, {bad} different ({time.time() - t0:.0f} s)', flush=True)
    sys.exit(1 if bad_all else 0)

if __name__ == '__main__': main()

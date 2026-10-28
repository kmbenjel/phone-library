"""fl2.py BOOK PAGE VARIANT… — fl.py plus what fix B5 is about: the lines outside the text block, and the parts lying within
3 pt of the allowed area's edges (band-edge slivers), on the first look of ONE page under each code variant (2026-10-28)."""
import sys, os, importlib
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
h, pg = sys.argv[1], int(sys.argv[2]); path = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
r1 = lambda b: [round(x, 1) for x in b[:4]]
for v in sys.argv[3:]:
    bc = importlib.import_module('bc_' + v)
    r = bc.analyse_pages(path, {}, only={pg - 1})[pg - 1]
    t = r.get('text') or r.get('box'); al = r.get('allowed')
    outl = [r1(b) for b in r.get('lines') or []
            if t and not (b[0] >= t[0] - 1 and b[2] <= t[2] + 1 and b[1] >= t[1] - 1 and b[3] <= t[3] + 1)]
    print(f'{v}: skew {r.get("skew")} text {r1(t) if t else None} box {r1(r["box"]) if r.get("box") else None} allowed {r1(al) if al else None}')
    print(f'     lines outside the text ({len(outl)}): {outl[:6]}  blots {[r1(b) for b in r.get("blots") or []][:3]}', flush=True)

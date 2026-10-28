"""fl.py BOOK PAGE VARIANT… — the first look (analyse_pages) of ONE page under each code variant (code/bc_<v>.py), no stamps
(the book has none). Prints the tilt fields. For 26j's failures: which of O, Q3, H, G changed the page's first look."""
import sys, os, importlib, json
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
h, pg = sys.argv[1], int(sys.argv[2]); path = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
KEYS = ('kind', 'tilt_by_proj', 'tilt_by_base', 'tilt_by_tracks', 'base_robust', 'skew', 'unsure_tilt', 'text')
for v in sys.argv[3:]:
    bc = importlib.import_module('bc_' + v)
    r = bc.analyse_pages(path, {}, only={pg - 1})[pg - 1]
    print(v, json.dumps({k: r.get(k) for k in KEYS if r.get(k) is not None}, ensure_ascii=False), flush=True)

"""fl.py BOOK PAGE VARIANT… — the first look (analyse_pages) of ONE page under each code variant (code/bc_<v>.py): its turn,
text block, box, allowed area, blots and lines. For fixes L and B (2026-10-28)."""
import sys, os, importlib, json
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
h, pg = sys.argv[1], int(sys.argv[2]); path = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
r1 = lambda v: [round(x, 1) for x in v] if isinstance(v, list) and v and not isinstance(v[0], list) else v
for v in sys.argv[3:]:
    bc = importlib.import_module('bc_' + v)
    r = bc.analyse_pages(path, {}, only={pg - 1})[pg - 1]
    print(v, json.dumps({k: r1(r.get(k)) for k in ('skew', 'loop_confirmed', 'tilt_by_tracks', 'text', 'box', 'allowed') if r.get(k) is not None}, ensure_ascii=False))
    print('   blots', [r1(b) for b in r.get('blots') or []][:4], 'lines(n)', len(r.get('lines') or []), 'edge', [r1(b) for b in r.get('edge') or []][:3], flush=True)

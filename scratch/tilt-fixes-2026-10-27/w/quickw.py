"""quickw.py BOOK PAGES V… — decide (0.95) on the cached first look, then verify only the given pages with each version"""
import sys, os, copy, pickle, time, importlib
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D + '/code')
Q = '/tmp/claude-1000/-home-k-projects-phone-library/45cf1df4-524b-4ab8-a6ae-dc204a1aaf10/scratchpad/bench'
C = '/home/k/.cache/phone-library/crop-regress/'
h = sys.argv[1]; pg = [int(x) for x in sys.argv[2].split(',')]; vers = sys.argv[3:] or ['r', 'w']
st, pages0 = pickle.load(open(f'{Q}/{h}.pages.pkl', 'rb'))
for v in vers:
    bc = importlib.import_module('bc_' + v); t = time.time()
    pages = copy.deepcopy(pages0)
    if v != 'g2':                                     # (fixes P and Q change the first look of the pages by_proj turned)
        idx = {g - 1 for g in pg if pages0[g - 1].get('tilt_by_proj') is not None}
        if idx:
            new_ = bc.analyse_pages(C + h + '.pdf', st, only=idx)
            for i in idx: pages[i] = new_[i]
    rec = bc.decide(pages, 0.95); rec['stamp_pages'] = len(st)
    rec = bc.verify(C + h + '.pdf', rec, only={g - 1 for g in pg})
    for g in pg:
        p = rec['pages'][g - 1]
        print(v, h, 'p.', g, 'skew', p.get('skew'), {k: p.get(k) for k in ('two_angles', 'lines_lean', 'tilt_by_proj', 'tilt_by_base', 'level_by_base', 'level_by_proj', 'unsure_tilt', 'tilt_disputed', 'untreated_tilt', 'turned_in_check', 'proj_sheet_line') if p.get(k) is not None})
    print(v, f'{time.time() - t:.0f}s', flush=True)

"""fbp.py BOOK [VERSION …] — fix P (the projection read again without a sheet's line) on ONE first look of the whole book:
the first look of g2 (= book_crop 20d30c2020) cached as <book>.pages.pkl; version p's first look = the same, its pages with
tilt_by_proj looked at again by bc_p (only by_proj differs); then plan()'s loop (decide + verify at the width quantiles) for
each version, the owner's turns as crop_regress passes them. g2 must reproduce the 26g recipe (b32a237bbf: guard G touches
no page of these books) → FAITHFUL"""
import sys, os, json, glob, copy, pickle, time, importlib
S = os.path.dirname(os.path.abspath(__file__)); C = '/home/k/.cache/phone-library/crop-regress/'
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import crop_batch as cb
sys.path.insert(0, f'{S}/code')
def load(n): return importlib.import_module('bc_' + n)
h = sys.argv[1]; vers = sys.argv[2:] or ['g2', 'p']; path = C + h + '.pdf'
J = int(os.environ.get('J', 2))
PH = {'2b47002d18ab': 'التاريخ/الموسوعة الشاملة في تاريخ الحروب الصليبية - سهيل زكار/الموسوعة الشاملة (38).pdf'}
while not cb.room(own=cb.own_bytes()): time.sleep(30)
pk = f'{S}/{h}.pages.pkl'
if not os.path.exists(pk):
    bc = load('g2'); t = time.time(); st = bc.stamps_of(path, J); pages = bc.analyse_pages(path, st, jobs=J)
    pickle.dump((st, pages), open(pk, 'wb')); print(h, 'first look', f'{time.time() - t:.0f}s', flush=True)
st, pages0 = pickle.load(open(pk, 'rb'))
OT = cb.owner_turns(PH[h]) if h in PH else {}
print(h, 'owner turns', OT, flush=True)
for v in vers:
    while not cb.room(own=cb.own_bytes()): time.sleep(30)
    bc = load(v); t = time.time(); pages = copy.deepcopy(pages0)
    if v != 'g2':                                     # the pages by_proj turned: their first look again with this version
        idx = sorted(i for i, p in enumerate(pages) if p.get('tilt_by_proj') is not None)
        new = bc.analyse_pages(path, st, only=set(idx))      # (with «only» it returns {page index: record})
        for i in idx: pages[i] = new[i]
        ch = [i + 1 for i in idx if pages[i] != pages0[i]]
        print(h, v, 'first look again on', len(idx), 'pages; changed', ch, flush=True)
    tried = []
    for wq in (0.95, 0.98, 1.0):
        rec = bc.decide(copy.deepcopy(pages), wq); rec['stamp_pages'] = len(st)
        if rec.get('decision') == 'level': tried.append((wq, 'level (decide)', [])); break
        if rec.get('decision') != 'crop': tried.append((wq, rec.get('decision'), [])); continue
        rec = bc.verify(path, rec, jobs=J, owner_turns=OT)
        tried.append((wq, rec.get('decision'), rec.get('whole') or []))
        if rec.get('decision') == 'crop': rec['width_quantile'] = wq; rec = bc.frames(rec); break
    json.dump(rec, open(f'{S}/{h}.{v}.json', 'w'), ensure_ascii=False)
    print(h, v, f'{time.time() - t:.0f}s', [(w, d, len(wh), wh[:50]) for w, d, wh in tried], flush=True)
    if v == 'g2':
        R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[0]))
        bad = [i + 1 for i, (a, b) in enumerate(zip(rec['pages'], R['pages']))
               if (a.get('crop'), a.get('skew'), a.get('show')) != (b.get('crop'), b.get('skew'), b.get('show'))]
        print(h, v, 'FAITHFUL' if not bad and rec.get('decision') == R.get('decision') else f'NOT FAITHFUL: {rec.get("decision")} vs {R.get("decision")}, pages {bad[:30]}', flush=True)

"""quickd.py BOOK — decide() alone (no second look) of base and o on the cached first look: every page whose box/crop/folio/
ornament/stain flags differ"""
import sys, os, pickle, copy, importlib
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, '/home/k/projects/phone-library/scripts'); sys.path.insert(0, f'{S}/code')
h = sys.argv[1]; F = pickle.load(open(f'{S}/{h}.pages.pkl', 'rb')); pages = F[('pages', h + '.pdf')]
A = importlib.import_module('bc_base').decide(copy.deepcopy(pages), 0.95); B = importlib.import_module('bc_o').decide(copy.deepcopy(pages), 0.95)
print(h, A.get('decision'), B.get('decision'), A.get('size'), B.get('size'))
for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
    d = {k: (p.get(k), q.get(k)) for k in ('crop', 'folio', 'ornament', 'folio_specks', 'stain_kept', 'dodged', 'anchored_x', 'anchored_y', 'own_centre', 'text') if p.get(k) != q.get(k)}
    if d: print(' p.', i + 1, d)

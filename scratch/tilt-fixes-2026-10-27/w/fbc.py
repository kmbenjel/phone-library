"""fbc.py BOOK PAGES V1 V2 … — the second look (verify) of chosen pages only, by each version, on one first look: g2's
cached <book>.pages.pkl (made with bc_g2 when missing), the chosen pages looked at again by V1 (fix Q's first look: the
versions share it), the book's box decided once at the 95 % width; the owner's turns as crop_regress passes them.
→ <book>.<version>.only.json and one line per page that differs between the versions"""
import sys, os, json, copy, pickle, time, importlib, hashlib, unicodedata, csv
S = os.path.dirname(os.path.abspath(__file__)); C = '/home/k/.cache/phone-library/crop-regress/'
ROOT = '/home/k/projects/phone-library'
sys.path.insert(0, ROOT + '/scripts')
import crop_batch as cb
sys.path.insert(0, f'{S}/code'); sys.path.insert(0, '/tmp/claude-1000/-home-k-projects-phone-library/fcd8d325-9813-40ca-94ce-bd6c86424307/scratchpad/w/code')
def load(n): return importlib.import_module('bc_' + n)
PK = {'00597fea27cf': '/tmp/claude-1000/-home-k-projects-phone-library/b7f753c2-6527-4c3d-9dcb-f4e918ed0046/scratchpad/bench/bench/00597fea27cf.pages.pkl',
      '2b47002d18ab': '/tmp/claude-1000/-home-k-projects-phone-library/37b40576-c90e-4994-a417-028a295f8c53/scratchpad/bench/2b47002d18ab.pages.pkl',
      '35fbe344b8c6': '/tmp/claude-1000/-home-k-projects-phone-library/45cf1df4-524b-4ab8-a6ae-dc204a1aaf10/scratchpad/bench/35fbe344b8c6.pages.pkl',
      '9da5c530d977': '/tmp/claude-1000/-home-k-projects-phone-library/45cf1df4-524b-4ab8-a6ae-dc204a1aaf10/scratchpad/bench/9da5c530d977.pages.pkl'}
h, sel, vers = sys.argv[1], sys.argv[2], sys.argv[3:]; path = C + h + '.pdf'
N = lambda s: unicodedata.normalize('NFC', s)
PH = {}
for r in csv.reader(open(ROOT + '/data/improve/crop-regression.tsv', encoding='utf-8'), delimiter='\t'):
    if r and not r[0].startswith('#'): PH.setdefault(hashlib.md5(N(r[0]).encode()).hexdigest()[:12], r[0])
while not cb.room(own=cb.own_bytes()): time.sleep(30)
pk = PK.get(h, f'{S}/{h}.pages.pkl')
if not os.path.exists(pk):
    g2 = load('g2'); t = time.time(); st = g2.stamps_of(path, 1); pages = g2.analyse_pages(path, st, jobs=1)
    pickle.dump((st, pages), open(pk, 'wb')); print(h, 'first look', f'{time.time() - t:.0f}s', flush=True)
st, pages0 = pickle.load(open(pk, 'rb'))
OT = cb.owner_turns(PH[h]) if h in PH else {}
idx = sorted(int(x) - 1 for x in sel.split(','))
t = time.time(); new = load(vers[0]).analyse_pages(path, st, only=set(idx))
pages = copy.deepcopy(pages0)
for i in idx: pages[i] = new[i]
rec0 = load(vers[0]).decide(copy.deepcopy(pages), 0.95); rec0['stamp_pages'] = len(st)
print(h, 'first look of', len(idx), 'pages', f'{time.time() - t:.0f}s', rec0.get('decision'), flush=True)
out = {}
for v in vers:
    t = time.time(); rec = load(v).verify(path, copy.deepcopy(rec0), jobs=1, only=set(idx), owner_turns=OT)
    json.dump(rec, open(f'{S}/{h}.{v}.only.json', 'w'), ensure_ascii=False); out[v] = rec
    print(h, v, f'{time.time() - t:.0f}s', flush=True)
K = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
FL = ('tilt_by_proj', 'tilt_by_base', 'level_by_base', 'level_by_proj', 'unsure_tilt', 'tilt_disputed', 'turned_in_check',
      'after_tilt', 'after_tilt_image', 'two_angles', 'turn_by_tracks', 'level_by_tracks', 'level_by_print', 'curved',
      'level_by_lines', 'tilt_by_columns', 'level_by_columns')
a, b = out[vers[0]], out[vers[-1]]
for i in idx:
    p, q = a['pages'][i], b['pages'][i]
    same = all(p.get(k) == q.get(k) for k in K)
    print(f'  p. {i + 1} {"same" if same else "DIFF"}: {vers[0]} {p.get("skew")} {dict((k, p[k]) for k in FL if p.get(k) is not None)}'
          + ('' if same else f' | {vers[-1]} {q.get("skew")} {dict((k, q[k]) for k in FL if q.get(k) is not None)}'), flush=True)

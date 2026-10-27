"""fbo.py BOOK [VERSION …] — fix O (a repeated ornament is print; no futile dodge) on ONE first look of the whole book: the
book copied here from the regression cache, book_crop.plan() of each version (code/bc_<version>.py) run as crop_regress runs
it (the owner's turns passed), but stamps_of and analyse_pages answered from one cached first look made by the base version
(fix O changes only decide(): the first look is the same). → <book>.<version>.json. Compare with cmpo.py (base must equal
regression 26i's recipe, 3205efa17f = FAITHFUL)"""
import sys, os, json, pickle, time, importlib, hashlib, unicodedata, csv, shutil
S = os.path.dirname(os.path.abspath(__file__)); C = '/home/k/.cache/phone-library/crop-regress/'
ROOT = '/home/k/projects/phone-library'
sys.path.insert(0, ROOT + '/scripts')
import crop_batch as cb
sys.path.insert(0, f'{S}/code')
h = sys.argv[1]; vers = sys.argv[2:] or ['base', 'o']
J = int(os.environ.get('J', 2))
N = lambda s: unicodedata.normalize('NFC', s)
PH = {}                                               # the book's phone path (its owner's turns), as crop_regress hashes it
for r in csv.reader(open(ROOT + '/data/improve/crop-regression.tsv', encoding='utf-8'), delimiter='\t'):
    if r and not r[0].startswith('#'): PH.setdefault(hashlib.md5(N(r[0]).encode()).hexdigest()[:12], r[0])
os.makedirs(f'{S}/books', exist_ok=True)
path = f'{S}/books/{h}.pdf'
if not os.path.exists(path): shutil.copyfile(C + h + '.pdf', path)
OT = cb.owner_turns(PH[h]) if h in PH else {}
print(h, 'owner turns', OT, flush=True)
pk = f'{S}/{h}.pages.pkl'
FIRST = pickle.load(open(pk, 'rb')) if os.path.exists(pk) else {}
for v in vers:
    while not cb.room(own=cb.own_bytes()): time.sleep(30)
    bc = importlib.import_module('bc_' + v); t = time.time()
    st0, an0 = bc.stamps_of, bc.analyse_pages
    def stamps_of(p, jobs=1, _f=st0):
        k = ('stamps', os.path.basename(p))
        if k not in FIRST: FIRST[k] = _f(p, jobs); pickle.dump(FIRST, open(pk, 'wb'))
        return FIRST[k]
    def analyse_pages(p, stamps=None, only=None, jobs=1, _f=an0):
        if only is not None: return _f(p, stamps, only=only, jobs=jobs)      # the workers' chunks (_analyse_chunk)
        k = ('pages', os.path.basename(p))
        if k not in FIRST: FIRST[k] = _f(p, stamps, jobs=jobs); pickle.dump(FIRST, open(pk, 'wb')); print(h, 'first look', flush=True)
        import copy; pages = copy.deepcopy(FIRST[k])
        if v != 'base' and os.environ.get('RELOOK'):      # a version that changes the first look of the projection pages
            k2 = ('relook', v, os.path.basename(p))      # (Q3): those pages looked at again by it
            if k2 not in FIRST:
                idx = sorted(i for i, q in enumerate(pages) if q.get('tilt_by_proj') is not None)
                from concurrent.futures import ProcessPoolExecutor
                new = {}
                with ProcessPoolExecutor(J) as ex:
                    for part in ex.map(bc._analyse_chunk, [(p, stamps, idx[k::J]) for k in range(J)]): new.update(part)
                FIRST[k2] = {i: new[i] for i in idx}; pickle.dump(FIRST, open(pk, 'wb'))
                print(h, v, 'first look again on', len(idx), 'pages; changed', sum(1 for i in idx if new[i] != pages[i]), flush=True)
            for i, q in FIRST[k2].items(): pages[i] = copy.deepcopy(q)
        return pages
    bc.stamps_of, bc.analyse_pages = stamps_of, analyse_pages
    rec = bc.plan(path, J, owner_turns=OT)
    json.dump(rec, open(f'{S}/{h}.{v}.json', 'w'), ensure_ascii=False)
    print(h, v, f'{time.time() - t:.0f}s', rec.get('decision'), flush=True)

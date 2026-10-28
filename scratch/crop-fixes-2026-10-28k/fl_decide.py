"""fl_decide.py BOOK VARIANT… — each variant's first look of the whole book (analyse_pages, cached in out/<book>.<v>.pages.pkl),
then decide() at 0.95: its decision, and the first-look pages that differ from the first variant's (the keys that differ)."""
import sys, os, json, time, importlib, pickle, copy
S = os.path.dirname(os.path.abspath(__file__)); ROOT = '/home/k/projects/phone-library'
sys.path.insert(0, S + '/code'); sys.path.insert(1, ROOT + '/scripts')
import crop_batch as cb
h = sys.argv[1]; path = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
os.makedirs(S + '/out', exist_ok=True); first = {}
for v in sys.argv[2:]:
    bc = importlib.import_module('bc_' + v); pk = f'{S}/out/{h}.{v}.pages.pkl'
    if os.path.exists(pk): pages, stamps = pickle.load(open(pk, 'rb'))
    else:
        while not cb.room(own=0): time.sleep(30)
        jobs = max(1, cb.governed(3)); t = time.time()
        stamps = bc.stamps_of(path, jobs); pages = bc.analyse_pages(path, stamps, jobs=jobs)
        pickle.dump((pages, stamps), open(pk, 'wb')); print(v, f'first look {time.time() - t:.0f}s', flush=True)
    first[v] = pages
    for wq in (0.95, 0.98):
        rec = bc.decide(copy.deepcopy(pages), wq)
        print(v, 'decide', wq, '→', str(rec.get('decision'))[:200], '| clean', rec.get('clean_margins'), 'size', rec.get('size'), flush=True)
v0 = sys.argv[2]
for v in sys.argv[3:]:
    diff = [(i + 1, sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))) for i, (a, b) in enumerate(zip(first[v0], first[v])) if a != b]
    print(v0, 'vs', v, len(diff), 'first-look pages differ:')
    for x in diff: print('   p.', x[0], x[1])

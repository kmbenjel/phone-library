"""bplan.py BOOK VARIANT… — book_crop.plan() of one regression book under each code variant (code/bc_<v>.py), as
crop_regress runs it (the owner's turns passed, the governor's worker count, a book only with room) → out/<book>.<v>.json.
Each width attempt (0.95, 0.98, 1.0) logged with what the second look decided. Resumable: a variant already written is
skipped. For regression 27l's faults (2026-10-28): what fixes L and B change in a book."""
import sys, os, json, time, importlib, hashlib, unicodedata, csv
S = os.path.dirname(os.path.abspath(__file__)); ROOT = '/home/k/projects/phone-library'
sys.path.insert(0, S + '/code'); sys.path.insert(1, ROOT + '/scripts')
import crop_batch as cb
N = lambda s: unicodedata.normalize('NFC', s)
h = sys.argv[1]; path = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
PH = {}
for r in csv.reader(open(ROOT + '/data/improve/crop-regression.tsv', encoding='utf-8'), delimiter='\t'):
    if r and not r[0].startswith('#'): PH.setdefault(hashlib.md5(N(r[0]).encode()).hexdigest()[:12], r[0])
OT = cb.owner_turns(PH[h]) if h in PH else {}
os.makedirs(S + '/out', exist_ok=True)
for v in sys.argv[2:]:
    out = f'{S}/out/{h}.{v}.json'
    if os.path.exists(out): print(h, v, 'already done', flush=True); continue
    while True:
        jobs = max(1, cb.governed(int(os.environ.get('JOBS', 3))))
        if cb.room(own=cb.own_bytes() if jobs == 1 else 0): break
        time.sleep(30)
    bc = importlib.import_module('bc_' + v); t = time.time(); tries = []
    v0 = bc.verify
    def verify(p, rec, *a, _v=v0, **k):
        r = _v(p, rec, *a, **k)
        if k.get('only') is None and not k.get('tilt_only'):
            tries.append(r.get('decision'))
            print(f'   {v} width attempt {len(tries)}: {str(r.get("decision"))[:160]} | whole {r.get("whole")} size {r.get("size")}', flush=True)
        return r
    bc.verify = verify
    rec = bc.plan(path, jobs, owner_turns=OT)
    json.dump(rec, open(out, 'w'), ensure_ascii=False)
    print(h, v, f'{time.time() - t:.0f}s jobs {jobs}', rec.get('decision'), 'wq', rec.get('width_quantile'), 'size', rec.get('size'),
          'clean_margins', rec.get('clean_margins'), flush=True)

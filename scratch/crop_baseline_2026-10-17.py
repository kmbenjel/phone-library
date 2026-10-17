"""One-off (2026-10-17): the current crop method (book_crop.plan) on the books the owner marked (data/crop/owner-marked-2026-10-14.tsv),
from their original bytes (crop_regress.local_copy) → ~/.cache/phone-library/crop-baseline/<sheet id>.json, to see why each
marked page went wrong before the method is changed. Resumable (a finished book is skipped); then the regression set's run."""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'scripts')); os.chdir(ROOT)
import book_crop as bc, crop_regress as cr
OUT = os.path.expanduser('~/.cache/phone-library/crop-baseline'); os.makedirs(OUT, exist_ok=True)
for l in open('data/crop/owner-marked-2026-10-14.tsv', encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    n, rep, p, why = l.rstrip('\n').split('\t')[:4]
    dst = os.path.join(OUT, n + '.json')
    if os.path.exists(dst): continue
    try:
        pdf = cr.local_copy(p); t = time.time(); rec = bc.plan(pdf, 6)
        json.dump(rec, open(dst, 'w'), ensure_ascii=False)
        print(time.strftime('%F %T'), n, rec.get('decision'), f'{time.time() - t:.0f}s', rec.get('n'), 'pages', flush=True)
    except BaseException as e: print(time.strftime('%F %T'), 'ERR', n, repr(e)[:200], flush=True)

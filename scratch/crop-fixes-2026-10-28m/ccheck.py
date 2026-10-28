"""ccheck.py BOOK VARIANT — the regression's case rows of one book (crop_regress.check, as the regression runs them) on a
bench recipe out/<book>.<variant>.json, and the whole-book tilt check (residual / untreated). PASS/FAIL per row."""
import sys, os, json, csv, hashlib, unicodedata
ROOT = '/home/k/projects/phone-library'; S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT + '/scripts')
import crop_regress as cr
N = lambda s: unicodedata.normalize('NFC', s)
h, v = sys.argv[1], sys.argv[2]
rec = json.load(open(f'{S}/out/{h}.{v}.json')); pdf = os.path.expanduser(f'~/.cache/phone-library/crop-regress/{h}.pdf')
rows = []                                            # (the regression's rows, then the staged ones of case-rows.tsv)
for f in (ROOT + '/data/improve/crop-regression.tsv', S + '/case-rows.tsv'):
    rows += [r for r in csv.reader(open(f, encoding='utf-8'), delimiter='\t')
             if r and not r[0].startswith('#') and hashlib.md5(N(r[0]).encode()).hexdigest()[:12] == h and r not in rows]
fails = 0; keep_flat = set()
for r in rows:
    ok, why = cr.check(r, rec, pdf); fails += not ok
    if r[2] == 'turn' and r[3] == 'no': keep_flat.add(int(r[1]))
    print('PASS' if ok else 'FAIL', 'p.', r[1], r[2], r[3], '—', why)
rt = rec.get('residual_tilt') or []; ut = [x for x in rec.get('untreated_tilt') or [] if x not in keep_flat]
fails += bool(rt or ut)
print('PASS' if not (rt or ut) else 'FAIL', 'whole book: still tilted', rt[:12], '| tilted, not turned', ut[:12], '| two angles', rec.get('two_angles'))
print(f'{h} {v}: {len(rows)} rows, {fails} failures; decision {rec.get("decision")} wq {rec.get("width_quantile")} size {rec.get("size")} clean {rec.get("clean_margins")}')

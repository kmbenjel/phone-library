"""One-off (2026-10-08): finish the crop revert (212) in ONE lane.
In batches 212-x03..x05 the two lanes raced on «نسخ مستبعدة/__المستبدل/<section>» folders (one created what the other
removed as empty): 92 originals stayed cropped in place, their whole-page copies waiting in «نسخ محسنة للاستبدال».
4 more could not be uncropped (MuPDF refused set_cropbox; fix_pdf.uncrop now copies the MediaBox value instead).
Steps: 219 deletes 12 obsolete cropped copies (checked one by one against the change log and a full phone listing) →
the 92 waiting copies substituted (size checked against the listing) → the 4 redone through revert_crops.py →
plan 218 retried. Usage: python3 scratch/redo_revert_212.py LISTING MISSFILE"""
import csv, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fix_at_scale as fx
from revert_crops import WHY
IMP = fx.IMP
listing, missfile = sys.argv[1], sys.argv[2]
ph = {}
for l in open(listing, encoding='utf-8'):
    p, s = l.rstrip('\n').rsplit('\t', 1); ph[p] = int(s)
miss = [p for p in open(missfile, encoding='utf-8').read().split('\n') if p]
env = dict(os.environ, ALLOW_PROTECTED='1', NETPACE='0')
run = lambda cmd: subprocess.run(cmd, env=env).returncode

fx.wait_phone()
if not any(r[5:6] == ['219-delete-orphan-crop-copies'] for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t')):
    run(['python3', 'scripts/delete_files.py', 'plans/219-delete-orphan-crop-copies.tsv', '219-delete-orphan-crop-copies'])

copies = {}
for b in ('x01', 'x02', 'x03', 'x04', 'x05', 'x06', 'x07', 'y01', 'y02', 'y03', 'y04', 'y05', 'y06', 'y07'):
    for p, n in fx.copies_of(f'212-{b}-copies').items():
        if p in miss: copies[p] = n
ok = {p: n for p, n in copies.items() if ph.get(IMP + p) == n and p in ph}
bad = sorted(set(copies) - set(ok))
print('waiting copies', len(copies), 'size-checked', len(ok), 'not usable', len(bad), flush=True)
for p in bad: print('  NOT USABLE', p, copies[p], ph.get(IMP + p), p in ph, flush=True)
idx = {p: int(s) for p, s in csv.reader(open('data/phone/index-now.tsv', encoding='utf-8'), delimiter='\t') if s.isdigit()}
if ok:
    print('212-r01 substituted', fx.substitute('212-r01', ok, idx, WHY), flush=True)

rest = [p for p in miss if p not in ok]
with open('lists/212-redo.tsv', 'w', encoding='utf-8') as w:
    for p in rest: w.write(f'{p}\tuncrop\n')
print('redo through revert_crops.py:', len(rest), flush=True)
run(['python3', 'scripts/revert_crops.py', 'lists/212-redo.tsv', '--prefix', '212-r2-'])

if not any(r[5:6] == ['218-sheets-230-232'] for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t')):
    run(['python3', 'scripts/apply_plan.py', 'plans/218-sheets-230-232.tsv'])
    run(['python3', 'scripts/index_update.py', '218-sheets-230-232'])
print('done', flush=True)

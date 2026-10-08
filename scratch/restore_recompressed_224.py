"""One-off (2026-10-08): put back the 19 files recompressed (lossy) by plans 140 and 125 — their original files, fetched from
archive.org by exact size (data/queue/224-restore-recompressed.tsv → «نسخ محسنة للاستبدال», fetch_queue.py verified size,
%PDF, upload size), substituted with the three logged steps. Usage: python3 scratch/restore_recompressed_224.py"""
import csv, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fix_at_scale as fx
WHY = ('lossy recompressed copy (plan 140) set aside: its original file takes its place again (owner 2026-10-07)',
       'the original file again (archive.org, exact original size), replacing the recompressed copy',
       'recompressed copy replaced by the original file (owner 2026-10-07: undo the page changes)')
Q = 'data/queue/224-restore-recompressed.tsv'
fx.wait_phone()
subprocess.run(['python3', 'scripts/fetch_queue.py', Q, '224-restore-recompressed'], env=dict(os.environ, NETPACE='0', NET_MB='0'))   # owner: full speed until he says otherwise
done = set(open('data/queue/224-restore-recompressed.done', encoding='utf-8').read().split('\n')) if os.path.exists('data/queue/224-restore-recompressed.done') else set()
copies = {}
for url, size, target, why in csv.reader(open(Q, encoding='utf-8'), delimiter='\t'):
    if target in done: copies[target[len('Books/' + fx.IMP):]] = int(size)
print('fetched and uploaded', len(copies), 'of 19', flush=True)
idx = {p: int(s) for p, s in csv.reader(open('data/phone/index-now.tsv', encoding='utf-8'), delimiter='\t') if s.isdigit()}
if copies: print('substituted', fx.substitute('224-restore-originals', copies, idx, WHY), flush=True)

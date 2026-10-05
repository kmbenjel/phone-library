"""One-off helper (2026-10-05): download every file of a fetch_queue TSV to a staging folder (aria2c, 12 files × 8
connections, resumable), check exact size + %PDF + %%EOF, and render the first pages of each book's first file so the
title pages can be read before naming. Writes <stage>/manifest.tsv (url, size, target, reason, local path, status).
Usage: python3 scratch/stage_queue.py QUEUE.tsv STAGE_DIR"""
import csv, hashlib, os, subprocess, sys, shutil
q, stage = sys.argv[1], sys.argv[2]
os.makedirs(stage, exist_ok=True)
rows = [r for r in csv.reader(open(q), delimiter='\t') if r and not r[0].startswith('#')]
loc = lambda r: os.path.join(stage, hashlib.md5(r[2].encode()).hexdigest() + '.pdf')
have = lambda r: os.path.exists(loc(r)) and os.path.getsize(loc(r)) == int(r[1])
need = sum(int(r[1]) for r in rows if not have(r))           # only what is still missing
if shutil.disk_usage(stage).free - need < 8e9: sys.exit(f'not enough disk: need {need/1e9:.1f} GB + 8 GB free')
with open(os.path.join(stage, 'aria.txt'), 'w') as w:
    for r in rows:
        p = loc(r)
        if os.path.exists(p) and os.path.getsize(p) == int(r[1]) and not os.path.exists(p + '.aria2'): continue
        w.write(f'{r[0]}\n  out={os.path.basename(p)}\n')
subprocess.run(['aria2c', '-q', '-j12', '-x8', '-s8', '-k1M', '--continue=true', '--max-tries=5', '--retry-wait=10',
                '--auto-file-renaming=false', '--allow-overwrite=true', '-U', 'personal-library/1.0', '-d', stage, '-i', os.path.join(stage, 'aria.txt')])
def check(p, size):
    if not os.path.exists(p): return 'missing'
    n = os.path.getsize(p)
    if n != size: return f'size {n}≠{size}'
    with open(p, 'rb') as f:
        if f.read(4) != b'%PDF': return 'not %PDF'
        f.seek(max(0, n - 8192))
        if b'%%EOF' not in f.read(): return 'no %%EOF'
    return 'ok'
with open(os.path.join(stage, 'manifest.tsv'), 'w') as w:
    for r in rows:
        st = check(loc(r), int(r[1])); w.write('\t'.join(r[:4] + [loc(r), st]) + '\n')
        if st != 'ok': print(st, r[2][-90:])
print('staged', sum(check(loc(r), int(r[1])) == 'ok' for r in rows), 'of', len(rows))

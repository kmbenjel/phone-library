"""Exact MD5 of every phone file, computed by the phone itself (Apache FtpServer `MD5` command, ~70 MB/s on the
device, nothing transferred). Same-size files first (the duplicate candidates), then the rest. Resumable: a path
already hashed with the same size is skipped. One FTP connection.
Usage: python3 scripts/phone_md5.py [index.tsv]   → data/phone/md5.tsv (path, size, md5)"""
import collections, csv, ftplib, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from phone_host import HOST, PORT
IDX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data/phone/index-now.tsv')
OUT = os.path.join(ROOT, 'data/phone/md5.tsv')

rows = [(p, int(s)) for p, s in csv.reader(open(IDX, encoding='utf-8'), delimiter='\t') if s.isdigit()]
done = {}
if os.path.exists(OUT):
    for r in csv.reader(open(OUT, encoding='utf-8'), delimiter='\t'):
        if len(r) == 3: done[r[0]] = int(r[1])
n_by_size = collections.Counter(s for _, s in rows)
todo = [(p, s) for p, s in rows if done.get(p) != s]
todo.sort(key=lambda r: (n_by_size[r[1]] == 1, r[0]))

def connect():
    f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=600); f.login(); return f

f = connect(); t0 = time.time(); ok = 0
with open(OUT, 'a', newline='', encoding='utf-8') as o:
    w = csv.writer(o, delimiter='\t')
    for i, (p, s) in enumerate(todo):
        for attempt in range(3):
            try:
                resp = f.sendcmd('MD5 /Books/' + p)
                w.writerow([p, s, resp.split()[-1].lower()]); ok += 1; break
            except ftplib.error_perm as e:
                print('FAIL', p, e); break
            except (ftplib.error_temp, OSError, EOFError) as e:
                print('retry', p, e); time.sleep(5); f = connect()
        if i % 200 == 0:
            o.flush(); print(f'{i}/{len(todo)}  {time.time() - t0:.0f}s', flush=True)
print('hashed', ok, 'of', len(todo))

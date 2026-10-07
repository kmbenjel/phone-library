"""Produce improved copies for the owner to judge (never touching the originals):
download each listed phone file (paced), apply scripts/fix_pdf.py operations, check it (opens, page count, %PDF),
upload it to Books/نسخ محسنة للاستبدال/<same relative path> (paced), log each upload (action add, plan name).
List format (TSV): path<TAB>ops   ops = comma list of crop | split | recompress
MAX_KEPT=0.9: a crop still showing more than 90 % of the median page is not uploaded (logged in data/improve/noop.tsv).
Usage: PYTHONPATH=~/.local/share/phone-library-tools/site /usr/bin/python3 scripts/improve_copies.py list.tsv PLAN"""
import csv, ftplib, json, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from phone_host import HOST, PORT
from netpace import Pacer
J = lambda p: os.path.join(ROOT, p)
DEST = 'نسخ محسنة للاستبدال'
TMP = J(f'data/improve-tmp/{os.getpid()}'); os.makedirs(TMP, exist_ok=True)   # per run: several runs may overlap
rows = [r for r in csv.reader(open(sys.argv[1], encoding='utf-8'), delimiter='\t') if r and not r[0].startswith('#')]
plan = sys.argv[2]
pacer = Pacer()
def connect():
    f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=300); f.login(); return f
def mkdirs(f, path):
    cur = ''
    for part in path.split('/'):
        cur = f'{cur}/{part}' if cur else part
        try: f.mkd('/Books/' + cur)
        except ftplib.error_perm: pass
f = connect(); log = open(J('data/changes/changes.tsv'), 'a', newline='', encoding='utf-8'); w = csv.writer(log, delimiter='\t')
done = {r[3] for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t') if len(r) > 5 and r[5] == plan}
MAX_KEPT = float(os.environ.get('MAX_KEPT', 1.0))   # crops showing more than this share of the page are not uploaded
NOOP_F = J('data/improve/noop.tsv'); os.makedirs(os.path.dirname(NOOP_F), exist_ok=True)
noop = {l.split('\t')[0] for l in open(NOOP_F, encoding='utf-8')} if os.path.exists(NOOP_F) else set()
done |= {'Books/' + DEST + '/' + p for p in noop}
for path, ops in rows:
    dst = f'{DEST}/{path}'
    if 'Books/' + dst in done: continue
    src, out = os.path.join(TMP, 'in.pdf'), os.path.join(TMP, 'out.pdf')
    try:
        with open(src, 'wb') as o:
            f.retrbinary('RETR /Books/' + path, lambda b: (o.write(b), pacer.wait(len(b))), blocksize=1 << 16)
        args = ['--' + x for x in ops.split(',') if x]
        r = subprocess.run([sys.executable, J('scripts/fix_pdf.py'), src, out, *args], capture_output=True, text=True, timeout=3600)
        if r.returncode: print('FIX FAIL', path, r.stderr[-300:]); continue
        res = json.loads(r.stdout.strip().splitlines()[-1])
        if open(out, 'rb').read(4) != b'%PDF': print('BAD OUTPUT', path); continue
        if 'crop' in ops.split(',') and 'split' not in ops:   # share of the page still shown (median page): a crop that
            import pymupdf                                 # keeps nearly everything changes nothing on the phone
            d = pymupdf.open(out); ks = sorted(p.cropbox.get_area() / p.mediabox.get_area() for p in d); d.close()
            res['kept'] = round(ks[len(ks) // 2], 3) if ks else 1.0
            if res['kept'] > MAX_KEPT:
                print('NOOP', path, ops, res, flush=True)
                with open(NOOP_F, 'a', encoding='utf-8') as n: n.write(f'{path}\t{ops}\t{res["kept"]}\n')
                continue
        mkdirs(f, os.path.dirname(dst))
        with open(out, 'rb') as i:
            f.storbinary('STOR /Books/' + dst, i, blocksize=1 << 16, callback=lambda b: pacer.wait(len(b)))
        f.voidcmd('TYPE I')
        if f.size('/Books/' + dst) != os.path.getsize(out):               # the upload arrived whole, or it is not logged
            print('UPLOAD SIZE MISMATCH', path, flush=True); continue
        w.writerow([time.strftime('%F %T'), 'add', '', 'Books/' + dst, f'improved copy ({ops}): {res}', plan]); log.flush()
        print('OK', path, ops, res, flush=True)
    except Exception as e:
        print('FAIL', path, e, flush=True); time.sleep(5)
        try: f = connect()
        except Exception: pass
    finally:
        for x in (src, out):
            if os.path.exists(x): os.remove(x)
print('done'); os.rmdir(TMP) if not os.listdir(TMP) else None

"""Keep the front pages (title page, copyright page, preface) of chosen phone files as small images for a visual
check — names and editions decided by reading the book itself. Each file is streamed from the phone (paced, see
netpace.py), pages 1..N rendered at 100 dpi gray (JPEG q55) into data/inspect/pages/<key>-<page>.jpg, then deleted.
<key> is the inspection key of (path, size), so pages already kept by inspect_ocr.py are reused.
Usage: python3 scripts/front_pages.py paths.txt [N=6]"""
import csv, ftplib, hashlib, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from phone_host import HOST, PORT
from netpace import Pacer
J = lambda p: os.path.join(ROOT, p)
PAGES, TMP = J('data/inspect/pages'), J('data/inspect/tmp-front')
os.makedirs(PAGES, exist_ok=True); os.makedirs(TMP, exist_ok=True)
paths = [l.rstrip('\n') for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6
size = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
key = lambda p: hashlib.md5(f'{p}\t{size[p]}'.encode()).hexdigest()[:16]
pacer = Pacer()
f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=300); f.login()
for i, p in enumerate(paths):
    if p not in size: print('gone', p); continue
    k = key(p)
    if os.path.exists(os.path.join(PAGES, f'{k}-1.jpg')): continue
    tmp = os.path.join(TMP, k + '.pdf')
    try:
        with open(tmp, 'wb') as o:
            f.retrbinary('RETR /Books/' + p, lambda b: (o.write(b), pacer.wait(len(b))), blocksize=1 << 16)
        subprocess.run(['pdftoppm', '-gray', '-jpeg', '-jpegopt', 'quality=55', '-r', '100', '-f', '1', '-l', str(N), tmp, os.path.join(TMP, k)], capture_output=True, timeout=300)
        for fn in os.listdir(TMP):
            if fn.startswith(k + '-') and fn.endswith('.jpg'):
                n = int(fn[len(k) + 1:-4])
                os.replace(os.path.join(TMP, fn), os.path.join(PAGES, f'{k}-{n}.jpg'))
    except Exception as e:
        print('FAIL', p, e); time.sleep(5)
        try: f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(HOST, PORT, timeout=300); f.login()
        except Exception: pass
    finally:
        if os.path.exists(tmp): os.remove(tmp)
    print(f'{i + 1}/{len(paths)} {pacer.status()}', flush=True)
print('done')

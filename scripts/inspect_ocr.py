"""OCR the front pages queued by inspect_files.py (data/inspect/ocr-queue/<key>-NNNN.jpg|png, 150 dpi gray) with
tesseract (ara+eng), N parallel single-thread workers. → data/inspect/ocr.jsonl {key, page, text}; each PNG is deleted
once read. Keeps polling while inspect_files.py runs (stops when the queue is empty and no inspect process is alive).
Front pages are kept small (≤1000 px, JPEG q55) in data/inspect/pages/<key>-N.jpg for visual checks.
Usage: /usr/bin/python3 scripts/inspect_ocr.py [workers]   (needs PIL: system python)"""
import json, os, re, subprocess, sys, threading, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q, OUT, PAGES = os.path.join(ROOT, 'data/inspect/ocr-queue'), os.path.join(ROOT, 'data/inspect/ocr.jsonl'), os.path.join(ROOT, 'data/inspect/pages')
os.makedirs(PAGES, exist_ok=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
env = dict(os.environ, OMP_THREAD_LIMIT='1')
lock, taken = threading.Lock(), set()

def inspect_alive():
    return subprocess.run(['pgrep', '-f', 'inspect_files.py'], capture_output=True).returncode == 0

def next_png():
    with lock:
        for f in sorted(os.listdir(Q)):
            if f.endswith(('.png', '.jpg')) and f not in taken:
                p = os.path.join(Q, f)
                if time.time() - os.path.getmtime(p) < 5: continue      # pdftoppm may still be writing
                taken.add(f); return f
    return None

def worker(out):
    idle = 0
    while True:
        f = next_png()
        if not f:
            idle += 1
            if idle > 30 and not inspect_alive(): return
            time.sleep(10); continue
        idle = 0
        p = os.path.join(Q, f)
        m = re.match(r'(.+)-(\d+)\.(?:png|jpg)$', f)
        try:
            txt = subprocess.run(['tesseract', p, '-', '-l', 'ara+eng', '--psm', '3'], capture_output=True, env=env,
                                 timeout=300).stdout.decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            txt = ''
        txt = re.sub(r'[ \t]+', ' ', re.sub(r'\n\s*\n+', '\n', txt)).strip()[:3000]
        with lock:
            out.write(json.dumps({'key': m.group(1), 'page': int(m.group(2)), 'text': txt}, ensure_ascii=False) + '\n'); out.flush()
        try:                                       # keep a readable copy of the front page for visual checks
            from PIL import Image
            im = Image.open(p); im.thumbnail((1000, 1000)); im.save(os.path.join(PAGES, f'{m.group(1)}-{int(m.group(2))}.jpg'), quality=55)
        except Exception:
            pass
        os.remove(p)

with open(OUT, 'a', encoding='utf-8') as out:
    ths = [threading.Thread(target=worker, args=(out,)) for _ in range(N)]
    for t in ths: t.start()
    for t in ths: t.join()
print('ocr queue empty')

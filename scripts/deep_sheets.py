"""Reading further into books whose first three pages did not give the publisher or the editor (owner 2026-10-11: «many
books in plan 318 have only two pieces of information for no clear reason»): for each reading number n, the book is
copied from the phone (under the shared lock), pages 2-9 and the last 3 are rendered small into one numbered sheet
→ data/names/deep/dNNNN.jpg (the imprint page, a back cover or a colophon usually holds what is missing); the copy is
deleted. Read by eye, then recorded with title_read_fix.py. Usage: python3 scripts/deep_sheets.py N [N…]"""
import csv, os, subprocess, sys, tempfile, unicodedata
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
OUT = J('data', 'names', 'deep')

def now_paths():
    path = {l.split('\t')[0]: l.rstrip('\n').split('\t')[2] for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8') if l.count('\t') >= 2}
    moved = {}
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 3 and r[1] == 'move': moved[r[2].removeprefix('Books/')] = r[3].removeprefix('Books/')
    idx = {unicodedata.normalize('NFC', l.split('\t')[0]): l.split('\t')[0] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8')}
    out = {}
    for n, p in path.items():
        for _ in range(30):                       # follow the logged moves only while the path is gone (a substituted
            if unicodedata.normalize('NFC', p) in idx or p not in moved: break     # copy came back to the same path)
            p = moved[p]
        out[n] = idx.get(unicodedata.normalize('NFC', p), '')
    return out

def sheet(pdf, n, out, h=620):
    pages = int([l for l in subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout.splitlines() if l.startswith('Pages')][0].split()[1])
    want = [p for p in range(2, min(pages, 9) + 1)] + [p for p in range(max(10, pages - 2), pages + 1)]
    ims = []
    with tempfile.TemporaryDirectory() as d:
        for p in want:
            base = os.path.join(d, f'p{p}')
            subprocess.run(['pdftoppm', '-gray', '-r', '45', '-f', str(p), '-l', str(p), '-png', '-singlefile', pdf, base], capture_output=True)
            if os.path.exists(base + '.png'):
                im = Image.open(base + '.png'); ims.append((p, im.resize((max(1, im.width * h // im.height), h))))
    per = 6
    rows = [ims[i:i + per] for i in range(0, len(ims), per)]
    W = max(sum(i.width + 8 for _, i in r) for r in rows); img = Image.new('L', (W, len(rows) * (h + 36) + 40), 255)
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
    except OSError: font = ImageFont.load_default()
    dr = ImageDraw.Draw(img); dr.text((4, 4), f'{n}  ({pages} p)', fill=0, font=font)
    for y, r in enumerate(rows):
        x = 0
        for p, im in r:
            img.paste(im, (x, 40 + y * (h + 36) + 30)); dr.text((x + 4, 40 + y * (h + 36)), f'p {p}', fill=0, font=font); x += im.width + 8
    img.save(out, quality=80)

def main(ns):
    os.makedirs(OUT, exist_ok=True)
    paths = now_paths()
    for n in ns:
        p = paths.get(n)
        if not p: print(n, 'not found on the phone index'); continue
        out = os.path.join(OUT, f'd{int(n):04d}.jpg')
        if os.path.exists(out): print(out); continue
        with tempfile.TemporaryDirectory(dir=J('data')) as d:
            local = os.path.join(d, 'b.pdf')
            r = subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', f'phone:Books/{p}', local], capture_output=True, text=True)
            if r.returncode or not os.path.exists(local): print(n, 'copy failed', r.stderr[-200:]); continue
            sheet(local, n, out)
        print(out, flush=True)

if __name__ == '__main__':
    main(sys.argv[1:])

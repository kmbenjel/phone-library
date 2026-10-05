"""One-off helper (2026-10-05): title-page sheets for a staged queue (scratch/stage_queue.py manifest): one strip per
book (its first volume file, pages 1-5 at low resolution), four books per PNG, numbered; plus books.tsv (n, folder, files).
Usage: python3 scratch/title_sheets.py STAGE_DIR OUT_DIR [dpi]"""
import csv, os, re, subprocess, sys, collections, glob
stage, out = sys.argv[1], sys.argv[2]; dpi = sys.argv[3] if len(sys.argv) > 3 else '28'
os.makedirs(out, exist_ok=True)
rows = [r for r in csv.reader(open(os.path.join(stage, 'manifest.tsv')), delimiter='\t') if r[5] == 'ok']
books = collections.OrderedDict()
for r in rows: books.setdefault(os.path.dirname(r[2]), []).append(r)
with open(os.path.join(out, 'books.tsv'), 'w') as w:
    for n, (b, fs) in enumerate(books.items()):
        fs.sort(key=lambda r: os.path.basename(r[2]))
        first = next((r for r in fs if not re.match(r'^00 ', os.path.basename(r[2]))), fs[0])
        w.write(f'{n}\t{b}\t{len(fs)}\t{os.path.basename(first[2])}\n')
        pre = os.path.join(out, f'p{n:03d}')
        subprocess.run(['pdftoppm', '-r', dpi, '-f', '1', '-l', '5', '-gray', first[4], pre], capture_output=True)
        pages = sorted(glob.glob(pre + '-*.pgm'))
        if pages:
            subprocess.run(['montage', *pages, '-tile', '5x1', '-geometry', '+2+2', '-title', str(n), os.path.join(out, f's{n:03d}.png')], capture_output=True)
            for p in pages: os.remove(p)
strips = sorted(glob.glob(os.path.join(out, 's*.png')))
for i in range(0, len(strips), 4):
    subprocess.run(['convert', *strips[i:i + 4], '-append', os.path.join(out, f'sheet{i // 4:02d}.png')])
print(len(books), 'books,', (len(strips) + 3) // 4, 'sheets')

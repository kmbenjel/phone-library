"""Drop the pages that put the file's numbering out of step with the printed one (owner 2026-10-18, decisions 45 and 714:
«هذه قاعدة، عند وجود صفحة فارغة أو الغلاف الخارجي وذلك يخالف بين الترقيمين تحذف الصفحة»; «أصلح الأمر بحيث يتوافق الترقيم
ولا يضيع شيء»): a blank page, or the outer cover, before the book's own pages.
REVERSIBLE: the pages are removed by an incremental update appended to the file — every byte of the original stays at its
start (undo = truncate to the logged original size, MD5 checked). A page given as blank must be blank (no ink on its
image at 40 dpi); a cover is dropped only with --cover. Uploaded beside the book as «<name>.redo», checked on the phone
(size + MD5), the old file deleted and the new one renamed into its place, checked again (as crop_redo.py does); logged in
data/changes/changes.tsv (action «pages»), index-now.tsv size updated.
Usage: python3 scripts/drop_pages.py LOCAL.pdf "PHONE PATH under Books/" PAGES BATCH [--cover] [--dry]
       PAGES: 1-based, e.g. 1 or 1-5 or 1,3"""
import csv, os, shutil, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import crop_batch as cb
import book_crop  # noqa: F401  (sets up pymupdf's path)
import numpy as np, pymupdf

def pages_of(spec):
    out = set()
    for part in spec.split(','):
        a, _, b = part.partition('-'); out |= set(range(int(a), int(b or a) + 1))
    return sorted(out)

def ink(page):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(40 / 72, 40 / 72), colorspace=pymupdf.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].astype(int)
    h, w = a.shape; core = a[int(.05 * h):int(.95 * h), int(.05 * w):int(.95 * w)]
    return float((core < 128).mean())

def main(local, path, spec, batch, cover=False, dry=False):
    drop = pages_of(spec); n0 = os.path.getsize(local); m0 = cb.md5_file(local)
    with cb.Phone() as ph: now = ph.md5(path)
    if now != m0: raise SystemExit(f'the local copy is not the phone file (md5 {m0} ≠ {now})')
    doc = pymupdf.open(local); k = doc.page_count
    for p in drop:
        e = ink(doc[p - 1])
        if e > 0.001 and not cover: raise SystemExit(f'page {p} is not blank (ink {e:.2%}); a cover needs --cover')
        print(f'page {p}: ink {e:.3%}')
    new = local + '.new.pdf'; shutil.copyfile(local, new)
    d = pymupdf.open(new); d.delete_pages([p - 1 for p in drop]); d.save(new, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP); d.close()
    with open(new, 'rb') as f, open(local, 'rb') as g:
        if f.read(n0) != g.read(): raise SystemExit('the new file does not start with the original bytes')
    d = pymupdf.open(new)
    if d.page_count != k - len(drop): raise SystemExit(f'{d.page_count} pages, expected {k - len(drop)}')
    keep = [i for i in range(k) if i + 1 not in drop]
    if [doc[i].xref for i in keep] != [d[j].xref for j in range(d.page_count)]: raise SystemExit('the kept pages are not the same objects')
    n1 = os.path.getsize(new); m1 = cb.md5_file(new)
    print(f'{k} → {d.page_count} pages, {n0} → {n1} B')
    if dry: return
    tmp = path + '.redo'
    with cb.Phone() as ph:
        if ph.md5(path) != m0: raise SystemExit('the phone file changed meanwhile')
        ph.put(tmp, new)
        if ph.size(tmp) != n1 or ph.md5(tmp) != m1: raise SystemExit('upload not verified (the old file is untouched)')
        ph.f.delete('Books/' + path); ph.f.rename('Books/' + tmp, 'Books/' + path)
        if ph.md5(path) != m1: raise SystemExit('RENAMED FILE NOT VERIFIED — check ' + path)
    with open(cb.LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter='\t').writerow([time.strftime('%F %T'), 'pages', 'Books/' + path, 'Books/' + path,
            f'dropped page(s) {spec} of {k} ({"cover" if cover else "blank"}) so the file\'s numbering follows the printed one; '
            f'original {n0} B md5 {m0}; appended {n1 - n0} B → md5 {m1} (undo: truncate to {n0})', batch])
    cb.set_index_size(path, n1); os.remove(new)
    print('DONE', path)

if __name__ == '__main__':
    a = sys.argv[1:]; cover = '--cover' in a; dry = '--dry' in a
    a = [x for x in a if x not in ('--cover', '--dry')]
    main(a[0], a[1], a[2], a[3], cover, dry)

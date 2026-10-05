"""Size, cropping and readability problems, from data/inspect/files.jsonl (owner's aims: correct or republish, save
storage, read better on the phone). One row per problem → data/phone/quality.tsv; summary → reports/overnight/02-quality.md.
Problems (thresholds chosen for reading a scanned book on a phone screen, ~1080 px wide):
  broken        not a PDF / no pages
  bloated       ≥ 350 KB per page for a text scan (gray/bitonal content stored as colour or at very high resolution);
                expected after a sound recompression is shown (200-dpi gray JPEG ≈ 110 KB/p, 300-dpi bitonal ≈ 35 KB/p)
  colour-text   colour images on most pages of a book whose pages are text (wastes space, no gain in reading)
  low-res       median image width < 900 px for a full page (small letters blur when zoomed) or < 150 ppi bitonal
  margins       content box leaves > 18 % blank on a side (or > 30 % left+right) → on a phone the text is small;
                fix: lossless CropBox to the content (+2 % padding)
  dark-borders  scanner edges: dark bands at the page border → crop
  spreads       landscape pages holding two book pages → split into single pages
  mixed-sizes   page sizes vary widely inside one file (> 15 % in width) → inconsistent zoom while reading
Usage: python3 scripts/quality_report.py index.tsv"""
import collections, csv, json, os, re, statistics, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)

def problems(d):
    out = []
    if not str(d.get('magic', '')).startswith('%PDF'): return [('broken', 'not a PDF: starts with ' + repr(d.get('magic')), 0)]
    if not d.get('pages'): return [('broken', 'PDF without readable pages (truncated or damaged)', 0)]
    pages, size, im = d['pages'], d['size'], d.get('images') or {}
    bpp = d.get('bytes_per_page', 0)
    col = im.get('color', {}); n_img = im.get('n', 0) or 1
    rgb_share = (col.get('rgb', 0) + col.get('cmyk', 0) + col.get('icc', 0)) / n_img
    textual = d.get('text_mid_chars', 0) > 200 or im.get('bpc1_share', 0) > 0.5 or rgb_share < 0.5
    if bpp >= 350_000 and pages >= 20:
        target = 110_000 if im.get('bpc1_share', 0) < 0.5 else 35_000
        out.append(('bloated', f'{bpp // 1000} KB/page ({size / 1e6:.0f} MB, {pages} p, {im.get("ppi_median")} ppi, '
                    f'{"colour" if rgb_share > 0.5 else "gray/bw"}); ≈{target * pages / 1e6:.0f} MB after recompression', size - target * pages))
    if rgb_share > 0.8 and pages >= 50 and bpp > 150_000:
        out.append(('colour-text', f'{rgb_share:.0%} colour page images, {bpp // 1000} KB/page', 0))
    pxw = None
    if im.get('px_median') and d.get('page_sizes'):
        w, h = (float(x) for x in re.match(r'(\d+)x(\d+)', next(iter(d['page_sizes']))).groups())
        if h > 0: pxw = (im['px_median'] * w / h) ** 0.5
    if pxw and pxw < 900 and im.get('per_page', 0) >= 0.9:
        out.append(('low-res', f'page images ≈{pxw:.0f} px wide ({im.get("ppi_median")} ppi)', 0))
    elif im.get('bpc1_share', 0) > 0.8 and (im.get('ppi_median') or 300) < 150:
        out.append(('low-res', f'bitonal at {im.get("ppi_median")} ppi', 0))
    m = [x for x in d.get('margins', []) if not x.get('blank')]
    if m:
        l, r, t, b = (statistics.median(x[k] for x in m) for k in ('l', 'r', 't', 'b'))
        if l + r > 0.30 or max(l, r) > 0.20:                       # text uses < 70 % of the width: worth cropping
            out.append(('margins', f'blank margins L{l:.0%} R{r:.0%} T{t:.0%} B{b:.0%} → text uses {(1 - l - r):.0%} of the width', 0))
        dark = max(max(x.get('edge_dark_rows', 0), x.get('edge_dark_cols', 0)) for x in m)
        if dark >= 0.35:
            out.append(('dark-borders', f'dark scanner edges (band density {dark:.0%})', 0))
    ps = d.get('page_sizes') or {}
    if ps:
        dims = []
        for k, c in ps.items():
            mm = re.match(r'(\d+)x(\d+)(r(\d+))?', k)
            w, h = int(mm.group(1)), int(mm.group(2))
            if mm.group(4) in ('90', '270'): w, h = h, w
            if w > 50 and h > 50: dims += [(w, h)] * c
        if not dims: return out
        land = sum(1 for w, h in dims if w > h * 1.15) / len(dims)
        if land > 0.5 and pages >= 10:
            out.append(('spreads', f'{land:.0%} of pages are landscape (two book pages per PDF page)', 0))
        ws = sorted(w for w, h in dims)
        if len(ws) > 10 and ws[int(len(ws) * 0.9)] > 1.15 * ws[int(len(ws) * 0.1)]:
            out.append(('mixed-sizes', f'page widths vary {ws[int(len(ws) * 0.1)]}–{ws[int(len(ws) * 0.9)]} pt (10th–90th percentile)', 0))
    return out

def main(index):
    idx = {p: int(s) for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')}
    rows, per, saving, n = [], collections.Counter(), 0, 0
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d['path'] not in idx or idx[d['path']] != d['size']: continue
        n += 1
        for kind, why, save in problems(d):
            rows.append((kind, d['path'], d['size'], why)); per[kind] += 1; saving += save
    rows.sort(key=lambda r: (r[0], -r[2]))
    with open(J('data/phone/quality.tsv'), 'w', encoding='utf-8') as w:
        w.write('problem\tpath\tbytes\tdetail\n')
        for r in rows: w.write('\t'.join(map(str, r)) + '\n')
    print('inspected', n, dict(per), f'possible saving ≈ {saving / 1e9:.1f} GB')

if __name__ == '__main__':
    main(sys.argv[1])

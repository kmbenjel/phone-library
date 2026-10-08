"""Are two phone files the same scan? (duplicate-edition pass, owner's standing permission 2026-10-08: keep the best of the
copies of one edition.) Downloads both (the shared phone lock), and compares page by page:
  * the page count and page sizes;
  * every page's images, by the MD5 of their raw (still compressed) streams — identical streams = the same scanned pixels;
  * the text layer (pages with text), bookmarks (outline entries), metadata title/author.
Verdict «same scan» only when every page's images are identical; otherwise «different» with the first differing page.
The extra bookmarks/text/metadata tell which copy to keep. Usage:
  python3 scripts/same_scan.py "<phone path A>" "<phone path B>" [A B …]   (paths relative to Books/)
  python3 scripts/same_scan.py --sets "A1|A2|…" "B1|…"   (copies split differently: pages of each set missing from the other)"""
import hashlib, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.expanduser('~/.local/share/phone-library-tools/site'))
import pymupdf

def fetch(path, dst):
    subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', '--retries', '3', f'phone:Books/{path}', dst], check=True)

def profile(f):
    doc = pymupdf.open(f)
    pages = []
    for p in doc:
        imgs = [hashlib.md5(doc.xref_stream_raw(x[0]) or b'').hexdigest() for x in p.get_images(full=True)]
        pages.append({'imgs': imgs, 'size': (round(p.mediabox.width), round(p.mediabox.height)), 'text': len(p.get_text('text').strip())})
    out = {'pages': pages, 'outline': len(doc.get_toc()),
           'meta': {k: v for k, v in (doc.metadata or {}).items() if v and k in ('title', 'author')}, 'bytes': os.path.getsize(f)}
    doc.close()
    return out

def compare(a, b):
    with tempfile.TemporaryDirectory() as t:
        fa, fb = os.path.join(t, 'a.pdf'), os.path.join(t, 'b.pdf')
        fetch(a, fa); fetch(b, fb)
        pa, pb = profile(fa), profile(fb)
    r = {'a': a, 'b': b, 'pages': [len(pa['pages']), len(pb['pages'])], 'outline': [pa['outline'], pb['outline']],
         'text_pages': [sum(1 for x in pa['pages'] if x['text']), sum(1 for x in pb['pages'] if x['text'])],
         'meta': [pa['meta'], pb['meta']], 'bytes': [pa['bytes'], pb['bytes']]}
    diff = None
    if len(pa['pages']) != len(pb['pages']): diff = 'page count'
    else:
        for i, (x, y) in enumerate(zip(pa['pages'], pb['pages'])):
            if not x['imgs'] or x['imgs'] != y['imgs']: diff = f'page {i + 1} images'; break
            if x['size'] != y['size']: diff = f'page {i + 1} size'; break
    r['verdict'] = 'same scan' if diff is None else f'different ({diff})'
    return r

def compare_sets(A, B):
    """two copies split differently (one file vs three volumes): every page's images as one key; which pages of each set
    are missing from the other (both empty = the same scan; one side empty = that side is contained in the other)"""
    prof = {}
    with tempfile.TemporaryDirectory() as t:
        for n, p in enumerate(A + B):
            f = os.path.join(t, f'{n}.pdf'); fetch(p, f); prof[p] = profile(f); os.remove(f)
    keys = lambda S: [(p, i + 1, tuple(x['imgs'])) for p in S for i, x in enumerate(prof[p]['pages'])]
    ka, kb = keys(A), keys(B)
    sa, sb = {k for *_, k in ka if k}, {k for *_, k in kb if k}
    only = lambda K, other: [(p.rsplit('/', 1)[-1], i) for p, i, k in K if not k or k not in other]
    oa, ob = only(ka, sb), only(kb, sa)
    return {'A': A, 'B': B, 'pages': [len(ka), len(kb)], 'outline': [sum(prof[p]['outline'] for p in A), sum(prof[p]['outline'] for p in B)],
            'text_pages': [sum(1 for p in A for x in prof[p]['pages'] if x['text']), sum(1 for p in B for x in prof[p]['pages'] if x['text'])],
            'bytes': [sum(prof[p]['bytes'] for p in A), sum(prof[p]['bytes'] for p in B)],
            'only_in_A': oa[:40], 'only_in_A_count': len(oa), 'only_in_B': ob[:40], 'only_in_B_count': len(ob),
            'verdict': 'same scan' if not oa and not ob else 'B contained in A' if not ob else 'A contained in B' if not oa else 'different'}

def signature(page):
    """the page's text block, drawn 48×72 (blurred, normalised): two scans of one printed page give nearly the same
    signature whatever the scanner, resolution or margins; None for a blank or dark page"""
    import numpy as np
    from scipy import ndimage
    z = 240 / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].astype(float)
    paper = np.percentile(a, 90)
    if paper < 100: return None
    m = a < paper - 60
    h, w = m.shape; by, bx = max(1, h // 30), max(1, w // 30)
    m[:by] = m[-by:] = False; m[:, :bx] = m[:, -bx:] = False          # scanner edges
    ys, xs = np.nonzero(m)
    if len(ys) < 50: return None
    y0, y1 = (int(v) for v in np.percentile(ys, [0.5, 99.5])); x0, x1 = (int(v) for v in np.percentile(xs, [0.5, 99.5]))
    if y1 - y0 < 5 or x1 - x0 < 5: return None                # the text block, specks and stray marks left out
    sub = a[y0:y1 + 1, x0:x1 + 1]
    s = ndimage.gaussian_filter(ndimage.zoom(sub, (72 / sub.shape[0], 48 / sub.shape[1]), order=1), 1.0)[:72, :48]
    if s.shape != (72, 48): return None
    v = (s - s.mean()).ravel(); n = np.linalg.norm(v)
    return v / n if n else None

def signatures(f):
    import numpy as np
    doc = pymupdf.open(f); sig = [signature(p) for p in doc]; doc.close()
    return sig

def align(SA, SB, T=0.75):
    """order-keeping alignment of two page sequences (Needleman–Wunsch on similarity − T): matched pairs, unmatched pages"""
    import numpy as np
    ia = [i for i, s in enumerate(SA) if s is not None]; ib = [j for j, s in enumerate(SB) if s is not None]
    if not ia or not ib: return [], ia, ib, None
    sim = np.array([SA[i] for i in ia]) @ np.array([SB[j] for j in ib]).T
    n, m = sim.shape; D = np.zeros((n + 1, m + 1)); bt = np.zeros((n + 1, m + 1), np.int8)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d, u, l = D[i - 1, j - 1] + sim[i - 1, j - 1] - T, D[i - 1, j], D[i, j - 1]
            if d >= u and d >= l: D[i, j], bt[i, j] = d, 0
            elif u >= l: D[i, j], bt[i, j] = u, 1
            else: D[i, j], bt[i, j] = l, 2
    i, j, pairs = n, m, []
    while i and j:
        if bt[i, j] == 0: pairs.append((ia[i - 1], ib[j - 1], round(float(sim[i - 1, j - 1]), 3))); i -= 1; j -= 1
        elif bt[i, j] == 1: i -= 1
        else: j -= 1
    pairs.reverse()
    ma, mb = {p[0] for p in pairs}, {p[1] for p in pairs}
    return pairs, [x for x in ia if x not in ma], [x for x in ib if x not in mb], sim

def compare_visual(A, B, keep=None):
    """same printing, different scans? Signatures of every page; each file of A paired with the file of B it resembles most,
    aligned page by page. Reports per pair: matched pages (similarity), pages of each side without a counterpart (blank
    pages are listed apart). keep=dir saves the local copies there (to look at the unmatched pages)."""
    import numpy as np
    sig, npages = {}, {}
    with tempfile.TemporaryDirectory() as t:
        for n, p in enumerate(A + B):
            f = os.path.join(keep or t, f'{"A" if p in A else "B"}{n:02d}.pdf')
            if not os.path.exists(f): fetch(p, f)
            sig[p] = signatures(f); npages[p] = len(sig[p])
    def quick(a, b):                                     # how much a resembles b: median of each page's best match
        SA = [s for s in sig[a] if s is not None]; SB = [s for s in sig[b] if s is not None]
        if not SA or not SB: return 0
        return float(np.median((np.array(SA) @ np.array(SB).T).max(1)))
    out = []
    usedB = set()
    for a in A:
        b = max(B, key=lambda b: quick(a, b))
        pairs, ua, ub, _ = align(sig[a], sig[b])
        usedB.add(b)
        out.append({'a': a, 'b': b, 'pages': [npages[a], npages[b]], 'matched': len(pairs),
                    'sim_median': round(float(np.median([p[2] for p in pairs])), 3) if pairs else None,
                    'sim_min': min((p[2] for p in pairs), default=None),
                    'only_a': [i + 1 for i in ua], 'only_b': [j + 1 for j in ub],
                    'blank_a': [i + 1 for i, s in enumerate(sig[a]) if s is None], 'blank_b': [j + 1 for j, s in enumerate(sig[b]) if s is None]})
    return {'pairs': out, 'B_unpaired': [b for b in B if b not in usedB]}

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--visual':        # same_scan.py --visual "A1|A2|…" "B1|…" [keep_dir]
        r = compare_visual(args[1].split('|'), args[2].split('|'), args[3] if len(args) > 3 else None)
        for x in r['pairs']: print(json.dumps(x, ensure_ascii=False), flush=True)
        print(json.dumps({'B_unpaired': r['B_unpaired']}, ensure_ascii=False)); sys.exit()
    if args and args[0] == '--sets':          # same_scan.py --sets "A1|A2|…" "B1|B2|…"
        print(json.dumps(compare_sets(args[1].split('|'), args[2].split('|')), ensure_ascii=False)); sys.exit()
    for a, b in zip(args[0::2], args[1::2]):
        print(json.dumps(compare(a, b), ensure_ascii=False), flush=True)

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

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--sets':          # same_scan.py --sets "A1|A2|…" "B1|B2|…"
        print(json.dumps(compare_sets(args[1].split('|'), args[2].split('|')), ensure_ascii=False)); sys.exit()
    for a, b in zip(args[0::2], args[1::2]):
        print(json.dumps(compare(a, b), ensure_ascii=False), flush=True)

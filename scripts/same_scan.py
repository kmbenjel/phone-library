"""Are two phone files the same scan? (duplicate-edition pass, owner's standing permission 2026-10-08: keep the best of the
copies of one edition.) Downloads both (the shared phone lock), and compares page by page:
  * the page count and page sizes;
  * every page's images, by the MD5 of their raw (still compressed) streams — identical streams = the same scanned pixels;
  * the text layer (pages with text), bookmarks (outline entries), metadata title/author.
Verdict «same scan» only when every page's images are identical; otherwise «different» with the first differing page.
The extra bookmarks/text/metadata tell which copy to keep. Usage:
  python3 scripts/same_scan.py "<phone path A>" "<phone path B>" [A B …]   (paths relative to Books/)"""
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

if __name__ == '__main__':
    args = sys.argv[1:]
    for a, b in zip(args[0::2], args[1::2]):
        print(json.dumps(compare(a, b), ensure_ascii=False), flush=True)

"""Join the parts of one volume into one file, losslessly (owner 2026-10-20 on تاريخ الطبري: «ولم ليست المقدمة مع الجزء
الأول»): a preface, introduction or plates file that Waqfeya split off goes back in front of its volume. Pages are copied
as they are (pymupdf insert_pdf: the same image streams, nothing re-encoded); a page the next part repeats (its own scan of
the same title page) can be left out with «file.pdf:2-z». Checks: every image stream of the kept pages is in the result
(raw stream digests), page count = the sum. Usage:
  python3 scripts/join_parts.py OUT.pdf PART1.pdf[:pages] PART2.pdf[:pages] …   (pages 1-based: «1-z», «2-z», «1-5»)"""
import hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import book_crop  # noqa: F401  (sets up pymupdf's path)
import pymupdf

def span(spec, n):
    a, _, b = (spec or '1-z').partition('-')
    a = int(a); b = n if b in ('z', '') and '-' in (spec or '1-z') else int(b or a) if b != 'z' else n
    return a - 1, b - 1

def digests(doc, pages):
    out = []
    for p in pages:
        for img in doc[p].get_images(full=True):
            out.append(hashlib.md5(doc.xref_stream_raw(img[0])).hexdigest())
    return out

def main(out, parts):
    res = pymupdf.open(); want = []; total = 0
    for part in parts:
        path, _, spec = part.rpartition(':') if ':' in os.path.basename(part) else (part, '', '')
        d = pymupdf.open(path); a, b = span(spec, d.page_count)
        res.insert_pdf(d, from_page=a, to_page=b)
        want += digests(d, range(a, b + 1)); total += b - a + 1
    res.save(out, garbage=1, deflate=False)
    chk = pymupdf.open(out)
    got = digests(chk, range(chk.page_count))
    assert chk.page_count == total, (chk.page_count, total)
    assert sorted(got) == sorted(want), 'image streams differ'
    print(f'{out}: {total} pages, {len(got)} image streams unchanged, {os.path.getsize(out):,} bytes')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])

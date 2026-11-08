"""Re-render a PDF whose fonts are not embedded (a Word file printed to PDF: its pages draw as empty boxes on the phone)
from its own text layer (owner 2026-10-18, decision 416 «يعاد إخراجه من طبقة النص» approved): page for page, line for line
at the same place, size and weight, in an embedded Arabic font (Noto Naskh Arabic). The words are the file's own (its
ToUnicode text: presentation forms → letters, the «ﷲ» ligature, the justification tatweel dropped, brackets of a
right-to-left line mirrored back); the page count and the page numbers stay. Lines are set right-aligned at their own
right edge, centred when they stood centred. The old file is kept aside by the caller.
Usage: python3 scripts/rerender_text.py IN.pdf OUT.pdf"""
import os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_crop  # noqa: F401  (sets up pymupdf's path)
import pymupdf

FONTS = '/usr/share/fonts/truetype/noto'
CSS = ("@font-face {font-family: n; src: url(NotoNaskhArabic-Regular.ttf);} "
       "@font-face {font-family: n; font-weight: bold; src: url(NotoNaskhArabic-Bold.ttf);} "
       "p {font-family: n; margin: 0; line-height: 1.15; white-space: nowrap;}")
MIRROR = str.maketrans('()[]{}<>«»', ')(][}{><»«')
ARABIC = re.compile(r'[؀-ۿﭐ-﷿ﹰ-﻿]')

def clean(t):
    t = t.replace('ﷲ', 'لله')                     # the «ﷲ» ligature after an alif: ا + ﷲ = الله
    t = unicodedata.normalize('NFKC', t).replace('ـ', '')
    return re.sub(r' +([ً-ْ])', r'\1', t)    # a vowel mark set apart by the extraction

def lines_of(page):
    """the page's lines, each rebuilt from its glyphs' own places (Word cut justified words into pieces and stretched them
    with private kashida glyphs, so its runs of text are out of order): the glyphs of a row in visual order — right to
    left in an Arabic row — vowel marks after the letter they stand on, kashidas and tatweel dropped, brackets mirrored,
    runs of digits or Latin letters turned back"""
    chars = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                for c in sp['chars']:
                    ch = c['c']
                    if ch == '\uFDF2': ch = 'لله'
                    ch = ch.replace('\u2013', '-').replace('\u2014', '-')   # dashes the font lacks
                    if 0xE000 <= ord(ch[0]) <= 0xF8FF or ch == '\u0640': continue
                    r = pymupdf.Rect(c['bbox'])
                    if any(d['c'] == ch and abs((r & d['r']).get_area()) >= 0.6 * max(r.get_area(), 1e-6) for d in chars[-80:]): continue  # a shadow
                    chars.append(dict(c=ch, r=r, size=sp['size'], bold='Bold' in sp['font'] or sp['flags'] & 16))
    rows = []
    for c in sorted(chars, key=lambda c: (c['r'].y0 + c['r'].y1) / 2):
        cy = (c['r'].y0 + c['r'].y1) / 2
        if rows and abs(rows[-1]['cy'] - cy) <= 0.35 * c['size']: rows[-1]['c'].append(c)
        else: rows.append({'cy': cy, 'c': [c]})
    out = []
    for row in rows:
        cs = row['c']; rtl = any(ARABIC.search(c['c']) for c in cs)
        mark = lambda c: all(unicodedata.combining(x) for x in unicodedata.normalize('NFKC', c['c']))
        base = sorted((c for c in cs if not mark(c)), key=lambda c: -(c['r'].x0 + c['r'].x1) / 2 if rtl else (c['r'].x0 + c['r'].x1) / 2)
        if not base: continue
        letters = [c for c in base if c['c'].strip()]    # a space glyph lying over a letter (set there with a vowel mark) is
        base = [c for c in base if c['c'].strip() or not any(    # no gap between words
            d['r'].x0 + 0.2 < (c['r'].x0 + c['r'].x1) / 2 < d['r'].x1 - 0.2 for d in letters)]
        seq = [[c] for c in base]
        for m in (c for c in cs if mark(c)):
            mx = (m['r'].x0 + m['r'].x1) / 2
            k = min(range(len(base)), key=lambda j: abs((base[j]['r'].x0 + base[j]['r'].x1) / 2 - mx) if base[j]['c'].strip() else 1e9)
            seq[k].append(m)
        text = ''.join(unicodedata.normalize('NFKC', c['c']) for g in seq for c in g)
        if rtl:
            text = text.translate(MIRROR)
            text = re.sub(r'[0-9A-Za-z][0-9A-Za-z.,:/]*[0-9A-Za-z]|[0-9A-Za-z]', lambda m: m.group(0)[::-1], text)
        text = re.sub(r'\s+([.،؛:؟!)\]»])', r'\1', re.sub(r'([(\[«])\s+', r'\1', re.sub(r'\s+', ' ', text))).strip()
        if not text: continue
        x0 = min(c['r'].x0 for c in cs); x1 = max(c['r'].x1 for c in cs)
        y0 = min(c['r'].y0 for c in cs); y1 = max(c['r'].y1 for c in cs)
        out.append(dict(text=text, rect=(x0, y0, x1, y1), size=max(c['size'] for c in cs), bold=any(c['bold'] for c in cs), rtl=rtl))
    return out

def main(src, dst):
    doc = pymupdf.open(src); new = pymupdf.open(); arch = pymupdf.Archive(FONTS)
    for page in doc:
        w, h = page.rect.width, page.rect.height; p = new.new_page(width=w, height=h)
        ls = lines_of(page)
        if not ls: continue
        left = min(l['rect'][0] for l in ls if l['rtl'] or True); right = max(l['rect'][2] for l in ls)
        for l in ls:
            x0, y0, x1, y1 = l['rect']; cx = (x0 + x1) / 2
            centred = abs(cx - w / 2) <= 0.03 * w and (x1 - x0) <= 0.8 * (right - left)
            align = 'center' if centred else ('right' if l['rtl'] else 'left')
            r = pymupdf.Rect(left - 4, y0 - 0.25 * l['size'], right + 4, y1 + 0.35 * l['size'])
            if align == 'right': r.x1 = x1 + 4
            elif align == 'left': r.x0 = x0 - 4
            html = (f'<p dir="{"rtl" if l["rtl"] else "ltr"}" style="font-size:{l["size"]:.1f}px;text-align:{align};'
                    f'font-weight:{"bold" if l["bold"] else "normal"}">{l["text"]}</p>')
            html = html.replace('&', '&amp;') if '&' in l['text'] else html
            rc = p.insert_htmlbox(r, html, css=CSS, archive=arch, scale_low=0.5)
            if rc[0] < 0: print('did not fit:', page.number + 1, l['text'][:50])
    new.set_metadata({'title': clean(doc.metadata.get('title') or '') if not (doc.metadata.get('title') or '').startswith('<') else '',
                      'producer': 'rerender_text.py (from the text layer of the original)'})
    new.subset_fonts(); new.save(dst, garbage=4, deflate=True)
    print(doc.page_count, 'pages →', dst, os.path.getsize(dst), 'B')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

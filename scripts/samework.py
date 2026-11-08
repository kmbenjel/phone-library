"""Is this work already on the phone, under another name? (2026-10-09: queues 274/280 uploaded المحن، الغنية، الرسالة الوافية
and تفسير ابن أبي زمنين although the phone had them — their names differed from the Waqfeya titles, and only exact sizes were
checked.) The same rule as Rule B of scripts/compare_waqfeya.py: the same opening words, in order (the first min(4, both)
words, particles and name words skipped), by an author agreeing on the surname/nisba.
Use: on_phone(title, author) → list of catalog books (cat/folder) holding the work; [] when none."""
import json, os, re
from textnorm import norm, author_tokens
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART = {norm(w) for w in ('في', 'من', 'على', 'عن', 'الى', 'إلى', 'مع', 'ومعه', 'ويليه', 'وبهامشه', 'كتاب', 'أو', 'او', 'بين', 'المسمى',
                          'ابن', 'أبي', 'أبو', 'بن')}
_books = None

def open_words(title):
    t = re.split(r'\s+-\s+(?:ط|ت)[\s.:]|\s+-\s+|\s+=\s+|،|:|\(', title)[0]
    return [w for w in norm(t).split() if len(w) > 2 and w not in PART]

def surname(author):
    return author_tokens(re.split(r'[؛;،,]', author or '')[0])

def _load():
    global _books
    if _books is None:
        cat = json.load(open(os.path.join(ROOT, 'data/catalog.json'), encoding='utf-8'))
        _books = [(b['cat'] + '/' + b['folder'], open_words(b['title']), author_tokens(b.get('author', '')),
                   set(norm(b['folder']).split())) for b in cat['books']]
    return _books

def on_phone(title, author):
    R, am = open_words(title), surname(author)
    if not R or not am: return []
    out = []
    for key, P, pa, words in _load():
        n = min(4, len(R), len(P))
        same_title = (n >= 2 and R[:n] == P[:n]) or (len(R) == 1 and P[:1] == R and
                                                     all(w in am or w[1:] in am or w in ('لابي', 'لابن') for w in P[1:]))
        if same_title and ((pa & am) or (not pa and any(t in words or ('ل' + t) in words for t in am))):
            out.append(key)
    return out

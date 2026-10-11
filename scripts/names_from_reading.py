"""Names from the title-page readings (data/names/title-read.tsv) under AGENTS.md §4 (scripts/name_compose.py):
«<title> - <author> - ت <editor> - <publisher> <city> <year>», no parentheses or commas; a thesis or a manuscript says so at the
end; a translator is «ترجمة X»; «part» (one volume of a set) stays a folder: «<folder>/NN - <title> - <label>.pdf».
Usage: python3 scripts/names_from_reading.py [N…]   (prints old → new for the readings N, or all)"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from name_compose import compose, B
from textnorm import norm

_COVER = {}
def cover_text(n):
    """page 1 of book n (its main cover, as a rule): the text layer, else the stored OCR (data/inspect/ocr.jsonl)"""
    if not _COVER:
        import json
        J = lambda *p: os.path.join(ROOT, *p)
        path = {l.split('\t')[0]: l.rstrip('\n').split('\t')[2] for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8')}
        key, text = {}, {}
        for l in open(J('data', 'inspect', 'files.jsonl'), encoding='utf-8'):
            d = json.loads(l)
            if d.get('key'): key[d['path']] = d['key']
            if d.get('text_first'): text[d['path']] = d['text_first'].split('\x0c')[0]
        ocr = {}
        if os.path.exists(J('data', 'inspect', 'ocr.jsonl')):
            for l in open(J('data', 'inspect', 'ocr.jsonl'), encoding='utf-8'):
                d = json.loads(l)
                if str(d.get('page')) == '1': ocr[d['key']] = d.get('text', '')
        for k, pth in path.items():
            _COVER[k] = (text.get(pth) or '') + ' ' + (ocr.get(key.get(pth), '') or '')
    t = _COVER.get(str(n), '')
    return t.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789'))

def year_of(y, n=None, on_cover=False, useful=False):
    """the year (owner 2026-10-10/11): his convention — a year when it has a special useful meaning («السنة يمكن إضافتها
    حين يكون لذلك معنى خاص نافع») — PLUS, added to it, every year printed on the main cover («when year mentioned in the
    main cover, mention it»; not a limit: «I didn't say only when»). Useful here: an old print (≤ 1950 / ≤ 1370 هـ), a
    journal offprint (the year names the issue) — `useful`; then as printed: «1428 هـ 2007»"""
    y = (y or '').replace('?', '').strip()
    g = re.search(r'\b(1[5-9]\d\d|20\d\d)\b', y)
    h = re.search(r'\b(\d{3,4})\s*هـ', y)
    hy, gy = (h.group(1) if h else ''), (g.group(1) if g and not (h and g.group(1) == h.group(1)) else '')
    cov = cover_text(n) if n is not None else ''
    on = [x for x in (hy, gy) if x and re.search(r'(?<!\d)' + x + r'(?!\d)', cov)]
    if on_cover and (hy or gy): on = [x for x in (hy, gy) if x]          # «[cover-year]»: seen on the cover by eye
    if on: return ' '.join(f'{x} هـ' if x == hy else x for x in on)
    if useful and (hy or gy): return ' '.join(f'{x} هـ' if x == hy else x for x in (hy, gy) if x)
    if gy: return gy if int(gy) <= 1950 else ''
    return f'{hy} هـ' if hy and int(hy) <= 1370 else ''

ROLE_WORD = re.compile(r'وقف على|بعناية|عناية|اعتن|عني|عنى|صحح|تصحيح|علق|تعليق|جمع|رتب|ترتيب|تنسيق|نسق|إعداد|أعد|ضبط|راجع|مراجعة|قرأ|خرج|تخريج|'
                       r'شرح|نشر|نسخ|اختصر|اختصار|إشراف|أشرف|قدم له|تقديم|اختار|انتقى|فهرس')
TAHQIQ = re.compile(r'حقق|تحقيق|محقق')

ROLE_HEAD = re.compile(r'^و?(بعناية|عناية|اعتن|عني|عنى|صحح|تصحيح|علق|تعليق|جمع|رتب|ترتيب|تنسيق|نسق|إعداد|أعد|ضبط|راجع|مراجعة|قرأ|خرج|تخريج|'
                       r'شرحه|شرح و|نشر|نسخه|اختصر|اختصار|إشراف|أشرف|قدم|تقديم|اختار|انتقى|اختيار|وقف على)')

def role_of(r):
    """the editor's printed role when it is not tahqiq: a «…» of the note that BEGINS with a role word («صححه وعلق عليه»،
    «تنسيق»، «اعتنى به»، «قدم لها»), at most 7 words, not a quoted title (not after «name»/«title»), followed by the
    editor's name or the note's only such quote; «تحقيق/حقق» in it → «ت». An editor field «role: name» wins."""
    ed, note = r.get('editor') or '', r.get('note') or ''
    if not ed: return 'ت'
    qs = [q for q in re.finditer(r'«([^»]{2,60})»\s*(\S+)?', note)
          if ROLE_HEAD.match(q.group(1).strip()) and len(q.group(1).split()) <= 7
          and not re.search(r"(name|title|said|gave|reads?)('s)?\W{0,12}$", note[max(0, q.start() - 25):q.start()])]
    if any(TAHQIQ.search(x) for x in re.findall(r'«([^»]{2,60})»', note)): return 'ت'      # «تحقيق ودراسة» anywhere
    for q in qs:
        txt, nxt = q.group(1).strip(), (q.group(2) or '').strip('،؛')
        if (nxt and nxt in ed) or ed.split()[0] in note[q.end():q.end() + 40]: return txt
        if len(qs) == 1 and not re.search(r'\b(بن|عبد|محمد|أحمد)\b', txt): return txt          # «صححه وعلق عليه» alone
    return 'ت'

OVERRIDE = os.path.join(ROOT, 'data', 'names', 'name-override.tsv')    # n → a name written by hand (owner's corrections)

def overrides():
    if not os.path.exists(OVERRIDE): return {}
    return {l.split('\t')[0]: l.rstrip('\n').split('\t')[1] for l in open(OVERRIDE, encoding='utf-8') if '\t' in l and not l.startswith('#')}

def name_of(r):
    o = overrides().get(r['n'])
    if o: return o
    return name_auto(r)

def name_auto(r):
    """publisher, city and year stay separate fields until name_compose renders them (no commas): «الناشر بالمدينة»"""
    t, au, ed, pub, city = r['title'], r['author'], r['editor'], r['publisher'], r['city']
    kind = r.get('kind', '')
    role = 'ترجمة' if kind == 'ترجمة' and ed else role_of(r)
    m = re.match(r'^([^:]{2,40}):\s*(.+)$', ed or '')          # «صححه وعلق عليه: فلان»
    if m and TAHQIQ.search(m.group(1)) and len(m.group(1).split()) == 1: role, ed = 'ت', m.group(2).strip()   # «حققها: فلان» → «ت فلان»; «تحقيق وتخريج» stays as printed
    elif m and (ROLE_WORD.search(m.group(1)) or TAHQIQ.search(m.group(1))): role, ed = m.group(1).strip(), m.group(2).strip()
    place = pub + (f'، {city}' if city else '')
    edition = (f'ت {ed}' + (f' - {place}' if place else '')) if ed else (f'ط {place}' if place else '')
    extra = [kind] if kind and kind not in ('نظم', 'متن', 'ترجمة') else []
    # the author is left out only when the title holds his whole name (not one word of it: «رحلة التجاني» keeps
    # «أبو محمد عبد الله التجاني» — owner: «تقصير كبير»)
    drop = au and norm(au).strip() and f' {norm(au)} ' in f' {norm(t)} '                   # whole words: «الجكني» is not in «الجكنية»
    return compose(t, '' if drop else au, edition, kinds_extra=extra, year=year_of(r.get('year'), r['n'], '[cover-year]' in (r.get('note') or ''), useful='مستل' in (r.get('kind') or '')), role=role)

if __name__ == '__main__':
    want = set(sys.argv[1:])
    for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'names', 'title-read.tsv'), encoding='utf-8'), delimiter='\t'):
        if want and r['n'] not in want: continue
        short = ''
        if r['n'] not in overrides():
            from names_plan_read import shortened
            short = '  SHORT — check against the cover' if shortened(r) else ''
        print(f"[{r['n']}] {r['verdict']:10} {r['book']}\n      → {name_of(r)}.pdf  [{B(name_of(r))} B]{short}")

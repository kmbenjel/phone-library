"""Edition card for every book of the catalog (owner, 2026-10-06: «الطبعة وسنة الطبع غير مذكورة»; accuracy above all).
For each phone book (data/catalog.json) gathers, with the source of every value:
  editor, publisher, edition number (الطبعة), year (hijri / gregorian), printed pages, volumes, author's death year,
  a one-line description.
Evidence is accepted only when it describes the phone's OWN edition:
  * Waqfeya record linked to the phone file by its exact size (provenance) — but if the phone name names an editor or a
    publisher that the record contradicts, the record is not used (→ review list);
  * the local official Shamela book card (data/shamela/book-cards.jsonl, dumped by tools/shamela-dump) — only for the same
    work (data/compare/shamela-matches.tsv) AND the same edition: the editor of the phone name matches the card's
    editor, or (no editor named on either side) the publisher matches;
  * title / imprint pages read by tesseract (data/editions/imprint-ocr.jsonl, scripts/imprint_ocr.py) — only a year
    printed next to «الطبعة» or the imprint line, read cleanly;
  * death year: Shamela's author record of the matched work.
Writes data/editions/edition-info.json (by catalog folder key «cat/folder») and data/editions/edition-review.tsv.
Usage: python3 scripts/edition_info.py"""
import csv, json, os, re, sqlite3, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
sys.path.insert(0, J('scripts'))
from textnorm import norm

AR = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')
STOP = set(norm(w) for w in '''بن ابن أبو ابو أبي ابي عبد الله محمد أحمد احمد علي الشيخ الدكتور د الأستاذ الاستاذ تحقيق ت ط
    دار مكتبة المكتبة مطبعة المطبعة مؤسسة شركة الكتب للنشر والنشر النشر والتوزيع التوزيع للطباعة الطباعة و في من
    القاهرة بيروت دمشق الرياض مصر لبنان وأولاده واولاده وشركاه'''.split())

def toks(s):
    return {w for w in norm(re.sub(r'[()،,.\-–/]', ' ', s or '')).split() if len(w) > 2 and w not in STOP}

def same_person(a, b):
    """two spellings of an editor's name: the family name (last distinctive word) of the shorter is in the longer, and
    together they share at least two distinctive words (or the shorter has only one)"""
    ta, tb = toks(a), toks(b)
    if not ta or not tb: return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    common = short & long_
    return len(common) >= min(2, len(short))

def same_publisher(a, b):
    ta, tb = toks(a), toks(b)
    return bool(ta) and bool(tb) and (ta <= tb or tb <= ta)

def phone_edition(folder):
    """editor / publisher named in the phone folder «… (ت X - Y)» or «(ط Y)»"""
    m = re.search(r'\((ت|ط)\s+([^()]*)\)\s*$', folder)
    if not m: return '', ''
    if m.group(1) == 'ط': return '', m.group(2).strip()
    parts = [p.strip() for p in m.group(2).split(' - ')]
    return parts[0], ' - '.join(parts[1:])

def parse_card(text):
    f = {}
    for line in re.split(r'[\r\n]+', text or ''):
        m = re.match(r'\s*([^:]{2,30}):\s*(.+)$', line)
        if m: f.setdefault(m.group(1).strip(), m.group(2).strip())
    ed = f.get('الطبعة', '')
    years = [int(y) for y in re.findall(r'\d{4}', ed.translate(AR))]
    hij = next((y for y in years if 1200 <= y <= 1460), None)
    gre = next((y for y in years if 1800 <= y <= 2030 and y != hij), None)
    no = re.match(r'\s*([^،,\d٠-٩(]+)', ed)
    pages = re.search(r'\d+', f.get('عدد الصفحات', '').translate(AR))
    vols = re.search(r'\d+', f.get('عدد الأجزاء', '').translate(AR))
    return {'editor': f.get('المحقق') or f.get('تحقيق') or f.get('حققه') or '', 'publisher': f.get('الناشر', ''),
            'edition_no': (no.group(1).strip() if no else '').strip(' -'), 'hijri': hij, 'gregorian': gre,
            'pages': int(pages.group()) if pages else None, 'volumes': int(vols.group()) if vols else None, 'raw_edition': ed}

def waq_year(s):
    ys = [int(y) for y in re.findall(r'\d{4}', (s or '').translate(AR))]
    return next((y for y in ys if 1200 <= y <= 1460), None), next((y for y in ys if 1800 <= y <= 2030), None)

NOISE = re.compile(r'دمج|للتسلسل|^سلسلة|^مدرسة|^\*?\s*هذا الكتاب ضمن|^المجلدات? من|يحتوي كل مجلد|^\d+$')
def waq_note(desc):
    """the useful lines of a Waqfeya cataloguer note (thesis origin, unique manuscript, unfinished work, «ومعه: …»);
    not volume-merging remarks, series names or lists of authors"""
    keep = []
    for line in re.split(r'<br\s*/?>|\n', desc or ''):
        line = re.sub(r'\s+', ' ', line).strip(' -*•\t')
        if len(line) < 12 or NOISE.search(line) or line.count('؛') >= 1: continue
        keep.append(line)
    return ' — '.join(keep)[:300]

MOVES = None
def sheet_key(key, file):
    """the book key a sheet was made for, carried along the renames logged since the sheets began (2026-10-06): the
    sheet's own file is followed, so a file moved out of a misnamed folder lands on its new book, not the old folder"""
    global MOVES
    if MOVES is None:
        strip = lambda p: p[6:] if p.startswith('Books/') else p
        MOVES = [(strip(r[2]), strip(r[3])) for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t')
                 if len(r) >= 4 and r[0] >= '2026-10-06' and r[1] == 'move' and 'substitute' not in (r[5] if len(r) > 5 else '')]
    cat, folder = key.split('/', 1)
    p = f'{cat}/{file}' if file == folder + '.pdf' else f'{key}/{file}'
    for a, b in MOVES:
        if p == a: p = b
        elif p.startswith(a + '/'): p = b + p[len(a):]
    parts = p.split('/')
    return f'{parts[0]}/{parts[1][:-4]}' if len(parts) == 2 else f'{parts[0]}/{parts[1]}'

def main():
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    wq = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn), encoding='utf-8'):
            d = json.loads(l); wq[d['_id']] = {**wq.get(d['_id'], {}), **d}
    cards = {}
    for l in open(J('data/shamela/book-cards.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d.get('id') and d.get('body_store'): cards[int(d['id'])] = parse_card(d['body_store'])
    db = sqlite3.connect(os.path.expanduser('~/.local/share/shamela/database/master.db'))
    death = {}
    for bid, ma in db.execute('select book_id, main_author from book'):
        r = db.execute('select death_number from author where author_id=?', (ma,)).fetchone()
        if r and r[0] and 0 < int(r[0]) < 1500: death[bid] = int(r[0])
    by_phone = collections.defaultdict(list)                       # catalog id → shamela ids of the same work
    for r in csv.DictReader(open(J('data/compare/shamela-matches.tsv'), encoding='utf-8'), delimiter='\t'):
        if r['match'] in ('exact', 'prefix+author', 'smart-tokens', 'prefix'):
            for i in (r['phone_book_ids'] or '').split():
                if i.isdigit(): by_phone[int(i)].append(int(r['shamela_id']))
    ocr = {}
    if os.path.exists(J('data/editions/imprint-ocr.jsonl')):
        for l in open(J('data/editions/imprint-ocr.jsonl'), encoding='utf-8'):
            d = json.loads(l); ocr[d['key']] = d
    seen = {}                                   # imprint pages read by eye (scripts/imprint_sheets.py → imprint-read.tsv)
    mapf, readf = J('data/editions/imprint-sheets/books.tsv'), J('data/editions/imprint-read.tsv')
    if os.path.exists(mapf) and os.path.exists(readf):
        nkey = {r[0]: sheet_key(r[1], r[2]) for r in csv.reader(open(mapf, encoding='utf-8'), delimiter='\t') if len(r) > 2}
        for r in csv.DictReader(open(readf, encoding='utf-8'), delimiter='\t'):
            if r['n'] in nkey: seen[nkey[r['n']]] = r
    textread = {}                               # imprint lines read from the PDF's own text layer (imprint_sheets.py)
    if os.path.exists(J('data/editions/imprint-text.tsv')):
        for r in csv.reader(open(J('data/editions/imprint-text.tsv'), encoding='utf-8'), delimiter='\t'):
            if len(r) >= 6: textread[r[0]] = {'hijri': r[3], 'gregorian': r[4], 'edition': r[5]}
    out, review, stats = {}, [], collections.Counter()
    for b in cat['books']:
        key = f"{b['cat']}/{b['folder']}"
        p_ed, p_pub = phone_edition(b['folder'])
        info = {}
        def put(field, value, source):
            if value and field not in info: info[field] = {'v': value, 's': source}
        # 1. Waqfeya record of the very file
        ws = [wq[x['id']] for x in b.get('waqfeya') or [] if x['id'] in wq]
        if len({(w.get('yearOfPublish') or '').strip() for w in ws}) > 1:
            review.append([key, 'waqfeya', 'several records with different years']); ws = []
        if ws:
            w = ws[0]
            conflict = (p_ed and w.get('researcher') and not same_person(p_ed, w['researcher'])) or \
                       (p_pub and w.get('publisher') and not p_ed and not same_publisher(p_pub, re.split(r'\s+-\s+', w['publisher'])[0]))
            if conflict:
                review.append([key, 'waqfeya', f"phone «{p_ed or p_pub}» vs record «{w.get('researcher') or w.get('publisher')}»"]); stats['waq conflict'] += 1
            else:
                h, g = waq_year(w.get('yearOfPublish'))
                put('hijri', h, 'الوقفية'); put('gregorian', g, 'الوقفية')
                cn = str(w.get('copyNumber') or '').strip()
                if cn and cn not in ('0', '-'): put('edition_no', cn, 'الوقفية')
                if str(w.get('pages') or '').isdigit() and int(w['pages']) > 0: put('pages', int(w['pages']), 'الوقفية')
                put('editor', (w.get('researcher') or '').strip(), 'الوقفية')
                put('publisher', (w.get('publisher') or '').strip(), 'الوقفية')
                note = waq_note(w.get('description'))
                if note: put('note', note, 'الوقفية')
                stats['waqfeya'] += 1
        # 2. Shamela card of the same work and edition
        for sid in by_phone.get(b['id'], []):
            if sid in death: put('death', death[sid], 'الشاملة')
            c = cards.get(sid)
            if not c: continue
            ok = (p_ed and c['editor'] and same_person(p_ed, c['editor'])) or \
                 (not p_ed and not c['editor'] and p_pub and c['publisher'] and same_publisher(p_pub, c['publisher']))
            if not ok: continue
            stats['shamela card'] += 1
            if 'hijri' in info and c['hijri'] and c['hijri'] != info['hijri']['v']:
                review.append([key, 'shamela', f"year {c['hijri']} (الشاملة: {c['raw_edition']}) vs {info['hijri']['v']} ({info['hijri']['s']})"])
                continue                                            # another printing of the same edition: keep the file's own
            put('hijri', c['hijri'], 'الشاملة'); put('gregorian', c['gregorian'], 'الشاملة')
            put('edition_no', c['edition_no'], 'الشاملة'); put('pages', c['pages'], 'الشاملة')
            put('editor', c['editor'], 'الشاملة'); put('publisher', c['publisher'], 'الشاملة'); put('volumes', c['volumes'], 'الشاملة')
        # 3. the imprint page read by eye (60-85 dpi render of the very file)
        v, src = (seen.get(key), 'صفحة الحقوق') if key in seen else (textread.get(key), 'صفحة الحقوق (نص)')
        if v:
            if 'hijri' in info and v['hijri'] and int(v['hijri']) != info['hijri']['v']:
                review.append([key, 'imprint', f"page {v['hijri']} vs {info['hijri']['v']} ({info['hijri']['s']})"])
            put('hijri', int(v['hijri']) if v['hijri'] else None, src); put('gregorian', int(v['gregorian']) if v['gregorian'] else None, src)
            put('edition_no', v['edition'], src)
        # 4. imprint OCR (tesseract), only clean reads
        o = ocr.get(key)
        if o and o.get('ok'):
            put('hijri', o.get('hijri'), 'صفحة العنوان'); put('gregorian', o.get('gregorian'), 'صفحة العنوان')
            put('edition_no', o.get('edition_no'), 'صفحة العنوان')
        if p_ed: put('editor', p_ed, 'اسم المجلد')
        if p_pub: put('publisher', p_pub, 'اسم المجلد')
        if info: out[key] = {k: v for k, v in info.items()}
        for k in info: stats['has ' + k] += 1
    os.makedirs(J('data/editions'), exist_ok=True)
    json.dump(out, open(J('data/editions/edition-info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(J('data/editions/edition-review.tsv'), 'w', encoding='utf-8') as w:
        w.write('book\tsource\tconflict\n')
        for r in review: w.write('\t'.join(r) + '\n')
    n = len(cat['books'])
    print(n, 'books;', ', '.join(f'{k}: {v} ({v / n:.0%})' for k, v in sorted(stats.items())), '; review', len(review))

if __name__ == '__main__':
    main()

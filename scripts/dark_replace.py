"""Books whose Waqfeya archive.org items went dark: verify the other uploads find_on_archive.py proposed, and queue the right
ones (owner, 2026-10-08: «حمّل هذه الكتب كلها بعد التدقيق وأخضعها لما يلزم من فحص وعناية»).

v2 (2026-10-09). The owner asked «تقارن بالعنوان والمؤلف فقط، هل هذا يكفي؟» — no: v1 accepted on title + author and 3 of its 8
uploads were wrong (a typed al-mostafa copy, a master's thesis about the book, part 1 of another edition). Now each
candidate item is READ, not downloaded: its first 8 page images (archive.org /page/nK_w1000.jpg) go through tesseract
(ara), and the record (details.jsonl + details2.jsonl: editor, publisher, year, volumes, pages, size) is compared with
what the pages say (the editor and publisher only on the first 4 pages — cover, title page, imprint):
  - the work: ≥ 60 % of the record title's distinctive words and, when the record names one, the author;
  - SKIPPED when the work is already on the phone under another name (scripts/samework.py: same opening words, same
    author's surname; 2026-10-09 four duplicates came in that way);
  - REFUSED: a thesis (رسالة ماجستير/دكتوراه، بحث مقدم لنيل، إشراف…) unless the record is one; a typed copy (al-mostafa,
    the Shamela, «مصفوف»); more PDFs than the record's volumes allow (a bundle: > 2 × volumes + 2); > 2 GB;
    the same sizes already on the phone;
  - THE EDITION: the record's editor (≥ 2 of the distinctive words of one of its names) or, for a record without an
    editor, its publisher or its size (all PDFs within 10 % of the record's MB) — read on the pages / from the files;
  - COMPLETE: as many PDFs as the record's volumes, or one PDF whose size is within 10 % of the record's; a page that
    says «الجزء الأول» on a one-PDF item smaller than that is a single part → refused.
Accepted only when all of these hold; the accepted PDFs are then downloaded and checked again (size, %PDF, pages) by
scripts/fetch_queue.py. Everything else goes to the review list WITH a contact sheet of the pages read
(~/.cache/phone-library/dark-sheets/<waqfeya id>__<item>.jpg) — read by eye, never uploaded automatically.
Names come from the record's own edition (the edition was proved): Books/<section>/<title> - <author> (ت <editor> -
<publisher>).pdf, or a folder with NN - <short title>.pdf for several PDFs.
Usage: python3 scripts/dark_replace.py candidates.json queue.tsv review.tsv [ids-to-skip.txt]"""
import csv, json, os, re, subprocess, sys, tempfile, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens, norm
from rename_plan import clean, fit, short_title
from samework import on_phone
J = lambda p: os.path.join(ROOT, p)
SHEETS = os.path.expanduser('~/.cache/phone-library/dark-sheets'); os.makedirs(SHEETS, exist_ok=True)
PAGES = os.path.expanduser('~/.cache/phone-library/dark-pages'); os.makedirs(PAGES, exist_ok=True)
STOP = {'كتاب', 'رساله', 'جزء', 'شرح', 'مختصر', 'في', 'علي', 'من', 'الي', 'عن', 'ومعه', 'ويليه', 'ط', 'ت', 'المسمي'}
NAME_STOP = {'محمد', 'احمد', 'عبد', 'الله', 'بن', 'ابن', 'ابو', 'ابي', 'علي', 'الدكتور', 'دكتور', 'الشيخ', 'د', 'الرحمن', 'العزيز'}
THESIS = re.compile(r'رساله (ماجستير|دكتوراه|علميه)|درجه (الماجستير|الدكتوراه|العالميه)|بحث مقدم|اطروحه|لنيل درجه|اعداد الطالب|اشراف الدكتور|اشراف الاستاذ')
TYPED = re.compile(r'shamela|الشامله|مصفوف', re.I)   # al-mostafa.com copies are fine (owner 2026-10-09: only its signature/URL, to be ignored)
FIRST_PART = re.compile(r'(الجزء|المجلد) (الاول|1)\b|\bج ?1\b')
UA = {'User-Agent': 'personal-library/1.0'}

def words(t): return [w for w in title_key(t).split() if len(w) > 2 and w not in STOP]
def nat(s): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]
def person(a):
    a = re.split(r'[؛;]', a or '')[0].strip()
    if '،' in a:
        last, first = [x.strip() for x in a.split('،', 1)]
        a = f'{first} {last}' if len(first) < 40 else last
    return a

def names(s):
    """the distinctive words of each name in an editor/publisher field («فلان - فلان»، «فلان وفلان»)"""
    out = []
    for part in re.split(r'\s+-\s+|،|;|؛|\s+و(?=[^\s]{3,})', s or ''):
        w = [x for x in norm(part).split() if len(x) > 2 and x not in NAME_STOP]
        if w: out.append(w)
    return out

def found(fields, text):
    """≥ 2 distinctive words of one name (1 if the name has only one) appear in the text"""
    for w in fields:
        k = sum(1 for x in w if x in text)
        if k >= min(2, len(w)): return True
    return False

def get_json(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception: time.sleep(4 * (i + 1))
    return {}

def page_images(ident, n=8, w=1000):
    """the item's first n page images (archive.org BookReader) — read without downloading the PDF"""
    out = []
    for k in range(n):
        f = os.path.join(PAGES, f'{ident}__n{k}.jpg')
        if not os.path.exists(f):
            r = subprocess.run(['curl', '-sfL', '--max-time', '90', '--limit-rate', '1M', '-o', f,
                                f'https://archive.org/download/{ident}/page/n{k}_w{w}.jpg'], capture_output=True)
            if r.returncode or not os.path.exists(f) or os.path.getsize(f) < 2000:
                if os.path.exists(f): os.remove(f)
                break
        if out and open(f, 'rb').read() == open(out[-1], 'rb').read(): break   # past the first file's end: the last page again
        out.append(f)
    return out

def ocr(paths):
    return '\n'.join(subprocess.run(['nice', 'tesseract', p, '-', '-l', 'ara'], capture_output=True, text=True).stdout for p in paths)

def sheet(paths, out):
    from PIL import Image
    ims = [Image.open(p).convert('L') for p in paths]; h = 420
    ims = [x.resize((max(1, int(x.width * h / x.height)), h)) for x in ims]
    s = Image.new('L', (sum(i.width + 6 for i in ims) or 10, h), 255); x = 0
    for im in ims: s.paste(im, (x, 0)); x += im.width + 6
    s.save(out, quality=70)

def load_records():
    recs = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn), encoding='utf-8'):
            d = json.loads(l)
            if d.get('nodetail'): continue
            recs.setdefault(d['_id'], d)
    return recs

def judge(wid, rec, d, have):
    """→ (accepted candidate or None, notes)"""
    title = re.split(r'\s+-\s+(?:ط|ت)[\s.:]', rec['waqfeya'])[0].strip()
    au = re.split(r'[؛;]', rec.get('author') or '')[0].strip()
    vols = int(re.sub(r'\D', '', str(d.get('numberOfVolumes') or rec.get('volumes') or '1')) or 1)
    mb = float(re.sub(r'[^\d.]', '', str(d.get('sizeInMB') or '')) or 0)
    editor, publisher = names(d.get('researcher')), names(d.get('publisher'))
    rec_thesis = bool(re.search(r'رسال|أطروح|ماجستير|دكتوراه', rec['waqfeya']))
    tw = words(title); aw = author_tokens(au)
    notes = []
    here = on_phone(title, rec.get('author') or '')           # the same work already on the phone under another name
    if here: return None, [f'already on the phone: {here[0]}' + (f' (+{len(here) - 1})' if len(here) > 1 else '')]
    for c in rec.get('candidates') or []:
        ident = c['id']; pdfs = sorted(c['pdfs'], key=lambda x: nat(x[0])); tot = sum(z for _, z in pdfs)
        if len(pdfs) > 2 * vols + 2: notes.append(f'{ident}: {len(pdfs)} PDFs for {vols} volumes (a bundle)'); continue
        if tot > 2e9: notes.append(f'{ident}: too large'); continue
        if all(z in have for _, z in pdfs): notes.append(f'{ident}: already on the phone (same sizes)'); continue
        imgs = page_images(ident)
        if not imgs: notes.append(f'{ident}: no page images'); continue
        front = norm(ocr(imgs[:4]))                       # cover, title page, imprint: the edition is read HERE only —
        text = norm(front + ' ' + ocr(imgs[4:]) + ' ' + c.get('title', ''))   # an introduction may name an earlier editor
        sheet(imgs, os.path.join(SHEETS, f'{wid}__{ident}.jpg'))
        got = [w for w in tw if w in text]; score = len(got) / max(1, len(tw))
        a_ok = not aw or any(t in text for t in aw)
        if score < 0.6 or not a_ok: notes.append(f'{ident}: title {len(got)}/{len(tw)}, author {"yes" if a_ok else "no"}'); continue
        if THESIS.search(text) and not rec_thesis: notes.append(f'{ident}: a thesis'); continue
        if TYPED.search(text): notes.append(f'{ident}: a typed copy'); continue
        size_ok = mb > 0 and abs(tot / 2**20 - mb) <= max(1.0, 0.10 * mb)
        ed_ok = found(editor, front) if editor else False      # 2026-10-09: «الرسالة الوافية» passed on its editor's name
        pub_ok = found(publisher, front) if publisher else False  # quoted in another editor's introduction
        same = ed_ok or (not editor and (pub_ok or size_ok))
        complete = len(pdfs) >= vols or (len(pdfs) == 1 and size_ok)
        if len(pdfs) == 1 and vols > 1 and FIRST_PART.search(text) and not size_ok: complete = False
        ev = f'title {len(got)}/{len(tw)}, author{" ✓" if aw else " —"}, editor {"✓" if ed_ok else ("✗" if editor else "—")}, ' \
             f'publisher {"✓" if pub_ok else ("✗" if publisher else "—")}, size {"✓" if size_ok else ("✗" if mb else "—")} ' \
             f'({tot / 2**20:.0f}/{mb:.0f} MB), {len(pdfs)} PDF / {vols} vol'
        if same and complete: return {'id': ident, 'pdfs': pdfs, 'evidence': ev}, notes
        notes.append(f'{ident}: {ev} — {"other edition?" if not same else "incomplete?"}')
    return None, notes

def main(cands_json, queue_tsv, review_tsv, skip=None):
    cands = json.load(open(cands_json, encoding='utf-8'))
    skip_ids = {l.strip() for l in open(skip, encoding='utf-8')} if skip else set()
    recs = load_records()
    cat = {r['waqfeya_id']: r['phone_category'] for r in csv.DictReader(open(J('data/compare/waqfeya-matches.tsv'), encoding='utf-8'), delimiter='\t')}
    have = {int(l.rstrip('\n').split('\t')[1]) for l in open(J('data/phone/index-now.tsv'), encoding='utf-8') if l.rstrip('\n').split('\t')[1].isdigit()}
    todo = [(w, r) for w, r in cands.items() if w not in skip_ids]
    with ThreadPoolExecutor(3) as ex:
        results = list(ex.map(lambda x: (x[0], x[1]) + judge(x[0], x[1], recs.get(x[0], {}), have), todo))
    q, review = [], []
    for wid, rec, acc, notes in results:
        d = recs.get(wid, {})
        if not acc:
            review.append([wid, rec['waqfeya'], person(rec.get('author')), ' | '.join(notes) or 'no candidate'])
            print(f'--  {rec["waqfeya"][:60]}: {"; ".join(notes)[:160] or "no candidate"}', flush=True); continue
        title = clean(re.split(r'\s+-\s+(?:ط|ت)[\s.:]', rec['waqfeya'])[0].strip())
        au = person(rec.get('author'))
        if au and norm(au) in norm(title): au = ''
        ed_n, pub = clean(d.get('researcher') or ''), clean(re.split(r'\s+-\s+', d.get('publisher') or '')[0])
        ed = (f'ت {ed_n}' + (f' - {pub}' if pub else '')) if ed_n else (f'ط {pub}' if pub else '')
        name = next((fit(clean(x), 190) for x in (f'{title} - {au} ({ed})' if au and ed else '', f'{title} ({ed})' if ed else '',
                                                    f'{title} - {au}' if au else '', title) if x and len(clean(x).encode()) <= 190), fit(title, 190))
        sec = cat.get(wid) or 'كتب عامة'
        why = f'«{rec["waqfeya"]}»: Waqfeya item dark; archive.org {acc["id"]} read (8 page images, OCR): {acc["evidence"]}'
        pdfs = acc['pdfs']
        if len(pdfs) == 1:
            f, z = pdfs[0]; q.append([f'https://archive.org/download/{acc["id"]}/{urllib.parse.quote(f)}', z, f'Books/{sec}/{name}.pdf', why])
        else:
            short = clean(short_title(title, au))
            for n, (f, z) in enumerate(pdfs, 1):
                q.append([f'https://archive.org/download/{acc["id"]}/{urllib.parse.quote(f)}', z, f'Books/{sec}/{name}/{n:02d} - {fit(short, 80)}.pdf', why])
        print(f'OK  {rec["waqfeya"][:60]} ← {acc["id"]}: {acc["evidence"]}', flush=True)
    with open(queue_tsv, 'w', encoding='utf-8', newline='') as f: csv.writer(f, delimiter='\t').writerows(q)
    with open(review_tsv, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t'); w.writerow(['waqfeya_id', 'name', 'author', 'why not added (sheets: ~/.cache/phone-library/dark-sheets/<id>__<item>.jpg)']); w.writerows(review)
    print(len(q), 'files queued;', len(review), 'books for review')

if __name__ == '__main__':
    main(*sys.argv[1:5])

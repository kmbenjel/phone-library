"""Compare the phone library with the whole Waqfeya catalog.
status per Waqfeya book: complete | partial (some volumes) | other-copy (same title, different files/edition) | missing
A matched file counts only if the phone book holding it carries the Waqfeya title (owner 2026-10-08: «كتب ناقصة المجلدات
(22)» held records whose link points to another book's file — صيام الصالحين → «مقاصد الصوم» …): such records are missing,
listed in data/review/waqfeya-link-mismatch.tsv. A partial book is complete when another phone folder of the same title holds
as many volumes (the same edition stored twice: الروض الأنف ت الوكيل).
Output: data/compare/waqfeya-matches.tsv"""
import csv, json, os, re, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, author_tokens, norm
from rename_plan import vol_from_orig
J = lambda p: os.path.join(ROOT, p)
def is_volume(f):
    n = f['name'].lower()
    return n.endswith('.pdf') and not n.endswith('_text.pdf') and f.get('format') != 'Text PDF' and f['size'] > 0
items = {}
for fn in ['data/archive/items.jsonl'] + sorted(os.path.relpath(p, ROOT) for p in __import__('glob').glob(os.path.join(ROOT, 'data/archive/files*.jsonl'))):
    for l in open(J(fn)):
        d = json.loads(l)
        if not d.get('error'): items[d['id']] = [f for f in d.get('files', []) if is_volume(f)]
books = {}
for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(J(fn)):
        d = json.loads(l); books[d['_id']] = {**books.get(d['_id'], {}), **d}
wmap = {}
for l in open(J('data/mappings/waqfeya-to-phone.tsv')):
    if l.startswith('#') or not l.strip(): continue
    k, _, v = l.rstrip('\n').partition('\t'); wmap[k.strip()] = v.strip()
def phone_cat(c):
    c = re.sub(r'^[\d.]+\s+', '', (c or '').strip()); return c, wmap.get(c)
# phone side
prov = defaultdict(set)          # waqfeya id -> set of (archive id, orig name) present on phone
prov_books = defaultdict(set)    # waqfeya id -> phone folders
for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t'):
    if r['waqfeya_id']:
        prov[r['waqfeya_id']].add((r['archive_id'], r['orig_name'])); prov_books[r['waqfeya_id']].add(r['path'].rsplit('/', 1)[0])
cat = json.load(open(J('data/catalog.json')))
cat_books_files = {b['cat'] + '/' + b['folder']: len(b.get('files', [])) for b in cat['books']}
keys = defaultdict(set); pauth = {}
word_to_books = defaultdict(set)
phone_full_tks = {}
phone_folder_words = {}
STOP0 = {norm(w) for w in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر', 'في', 'على', 'من', 'الى', 'إلى', 'عن', 'ومعه', 'ويليه', 'ط', 'ت',
                           'ديوان', 'مجموعة', 'مجموع', 'مؤلفات', 'رسائل', 'أعمال', 'الشيخ', 'الإمام', 'تحقيق', 'ودراسة', 'دراسة')}   # normalised (title_key's form)
def _w(t): return {w for w in title_key(t).split() if len(w) > 2 and w not in STOP0}
for b in cat['books']:
    pk = b['cat'] + '/' + b['folder']
    own = _w(b['title'] + ' ' + b['folder'])        # a Waqfeya name joins the phone book's titles only if it resembles them
    ts = {b['title']} | {w['name'] for w in b.get('waqfeya', []) if len(_w(w['name']) & own) >= max(1, 0.5 * min(len(_w(w['name'])), len(own) or 1))}
    for t in ts:
        k = title_key(t)
        if k: keys[k].add(pk)
    phone_full_tks[pk] = [title_key(t) for t in ts if t]
    pauth[pk] = author_tokens(b.get('author', ''))
    tk = title_key(b['title'])
    fk = title_key(b['folder'])
    phone_folder_words[pk] = set(fk.split())
    all_words = set(tk.split()) | set(fk.split())
    for w in all_words:
        if len(w) > 2 and w not in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر'):
            word_to_books[w].add(pk)
col_keywords = {'مجموع', 'مؤلفات', 'رسائل', 'أعمال', 'فتاوى', 'تراث', 'موسوعة', 'جامع', 'الجامع'}
STOP = {'كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر', 'في', 'على', 'من', 'الى', 'إلى', 'عن', 'ومعه', 'ويليه', 'ط', 'ت'}
def words(t): return {w for w in title_key(t).split() if len(w) > 2 and w not in STOP}
own_title = {b['cat'] + '/' + b['folder']: b['title'] + ' ' + b['folder'] for b in cat['books']}
def book_key(path):                                   # a phone file → its catalog book (folder, or the single file)
    parts = path.split('/')
    return '/'.join(parts[:2]) if len(parts) > 2 else path[:-4] if path.endswith('.pdf') else path
def same_book(wname, path):
    a, b = words(wname), words(own_title.get(book_key(path), path))
    return bool(a) and len(a & b) >= max(1, 0.5 * min(len(a), len(b) or 1))
PART = {norm(w) for w in ('في', 'من', 'على', 'عن', 'الى', 'إلى', 'مع', 'ومعه', 'ويليه', 'وبهامشه', 'كتاب', 'أو', 'او', 'بين', 'المسمى',
                           'ابن', 'أبي', 'أبو', 'بن')}   # «أمالي المحاملي رواية ابن …»: name words do not tell works apart
def open_words(name):                                 # a title's words in order: normalised, particles and short words out
    t = re.split(r'\s+-\s+(?:ط|ت)[\s.:]|\s+-\s+|\s+=\s+|،|:|\(', name)[0]
    return [w for w in norm(t).split() if len(w) > 2 and w not in PART]
def authorish(at):                                    # the author's words as a title may carry them («المحن لأبي العرب»)
    return set(at) | {'ل' + t for t in at} | {'لابي', 'لابن', 'للامام', 'للحافظ', 'للشيخ', 'ابي', 'ابن'}
phone_open = {b['cat'] + '/' + b['folder']: open_words(b['title']) for b in cat['books']}
name_words = {b['cat'] + '/' + b['folder']: set(norm(b['folder']).split()) | set(norm(b['title']).split()) for b in cat['books']}
prov_paths = defaultdict(set)
for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t'):
    if r['waqfeya_id']: prov_paths[r['waqfeya_id']].add(r['path'])
mismatch = []
rows = []
for wid, b in books.items():
    links = b.get('links') or []
    explicit_files = set()
    for lk in links:
        u = lk.get('url', '')
        m = re.findall(r'archive\.org/(?:details|download)/([^/?#\s]+)/([^/?#\s]+)', u)
        if m and m[0][1].lower().endswith('.pdf'):
            explicit_files.add((m[0][0], m[0][1]))

    ids = set(re.findall(r'archive\.org/(?:details|download)/([^/"?#\s]+)', json.dumps([b.get('thumbnail'), b.get('links'), b.get('archiveLink')], ensure_ascii=False)))
    if explicit_files:
        allv = explicit_files
    else:
        allv = {(i, f['name']) for i in ids for f in items.get(i, [])}

    vols = {x for x in allv if (vol_from_orig(x[1]) or (1, 'vol'))[1] == 'vol'}      # main volumes only (no cover/preface files)
    have = prov.get(wid, set()) & (vols or allv) or prov.get(wid, set())
    wcat, pcat = phone_cat((b.get('category') or {}).get('name'))
    if have and prov_paths.get(wid) and not any(same_book(b['name'], pp) for pp in prov_paths[wid]):
        mismatch.append([wid, b['name'], ' | '.join(sorted(prov_paths[wid]))[:600]])      # the link points to another book
        have = set()
    if have:
        where = sorted(prov_books[wid])
        folder_max_vols = max([cat_books_files.get(pf, 0) for pf in where] if where else [0])
        # If the book folder on the phone already contains all required volumes, it is complete
        if not vols or have >= vols or folder_max_vols >= len(vols):
            status = 'complete'
        else:
            status = 'partial'
            head = [w for w in title_key(b['name']).split() if len(w) > 2 and w not in STOP][:2]   # the title's first words
            other = [pk for pk, n in cat_books_files.items() if n >= len(vols) and pk not in where and head
                     and ' '.join(head) in ' '.join(w for w in title_key(own_title.get(pk, '')).split() if len(w) > 2 and w not in STOP)]
            if other:                                # the same edition stored twice → complete; another edition → other-copy
                ed = words(re.sub(r'.*?\((.*)\).*', r'\1', ' '.join(where))) if where else set()
                same_ed = [pk for pk in other if ed and len(ed & words(pk.rsplit('/', 1)[-1])) >= max(1, 0.5 * len(ed))]
                status = 'complete' if same_ed else 'other-copy'
                where = sorted(set(where) | set(same_ed or other))
    else:
        k = title_key(b['name']); at = author_tokens((b.get('author') or {}).get('name', ''))
        cand = keys.get(k, set())
        if cand and len(k.split()) <= 2 and at: cand = {c for c in cand if not pauth[c] or pauth[c] & at}
        
        if not cand:
            # Smart fallback: token matching + author verification
            kw = [w for w in k.split() if len(w) > 2 and w not in ('كتاب', 'رسالة', 'جزء', 'شرح', 'مختصر')]
            if len(kw) >= 2:
                candidates = word_to_books[kw[0]]
                for w in kw[1:]:
                    candidates = candidates & word_to_books[w]
                    if not candidates: break
                if candidates:
                    valid = set()
                    for cid in candidates:
                        cb_at = pauth[cid]
                        if not at or not cb_at or (at & cb_at):
                            valid.add(cid)
                    if valid:
                        cand = valid
                        
        if not cand and at:
            valid = set()
            for cid in pauth:
                cb_at = pauth[cid]
                if cb_at and (at & cb_at):
                    # Rule A: Attached books (exact phrase match)
                    tk_list = phone_full_tks[cid]
                    kw = k.split()
                    if len(kw) >= 2 or len(k) >= 5:
                        if any(f" {k} " in f" {t} " for t in tk_list):
                            valid.add(cid)
            if valid:
                cand = valid
                
        if not cand and at:
            # Rule B (2026-10-09, «conceptually present»): the same opening words, in order — the first min(4, both) words
            # of the record's title and of a phone book's title (particles skipped) — by the same author. Long Waqfeya
            # titles vs shorter phone names (الرسالة الوافية للداني، أخبار الراضي، مجرد أسماء الرواة عن مالك…). A different
            # work sharing a short opening fails at its third or fourth word (المعجم المفصل في العروض / في شواهد العربية;
            # تلخيص المتشابه / تالي تلخيص المتشابه); «مختصر» and «شرح» stay distinctive.
            R = open_words(b['name'])
            am = author_tokens(re.split(r'[؛;،,]', (b.get('author') or {}).get('name', ''))[0])   # the author's surname/nisba
            for cid, P in phone_open.items():
                n = min(4, len(R), len(P))
                if n >= 2 and R[:n] == P[:n] or (len(R) == 1 and P and P[0] == R[0] and all(w in authorish(am) for w in P[1:])):
                    # the author agrees on the surname or nisba, not on a first name (حرب بن إسماعيل الكرماني ≠ إسماعيل الشالنجي)
                    if (pauth[cid] & am) or (not pauth[cid] and any(t in name_words[cid] or ('ل' + t) in name_words[cid] for t in am)):
                        cand.add(cid)
        status, where = ('other-copy', sorted(cand)) if cand else ('missing', [])
    vols_on_phone = len(have) if have else (max([cat_books_files.get(pf, 0) for pf in where] if where else [0]))
    size_mb = sum(f['size'] for i in ids for f in items.get(i, []) if is_volume(f)) / 2**20
    missing_mb = sum(f['size'] for i in ids for f in items.get(i, []) if is_volume(f) and (i, f['name']) in vols - have) / 2**20 if status == 'partial' else (size_mb if status == 'missing' else 0)
    rows.append([wid, b['name'], (b.get('author') or {}).get('name', ''), wcat, pcat or '', (b.get('century') or {}).get('name', ''),
                 b.get('visitCounts', 0), len(vols), vols_on_phone, round(size_mb, 1), round(missing_mb, 1), status, ' | '.join(where),
                 'https://waqfeya.net/books/' + b.get('permalink', ''), ' '.join(sorted(ids)), 'known' if ids and all(i in items for i in ids) else 'unknown-files'])
with open(J('data/compare/waqfeya-matches.tsv'), 'w') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['waqfeya_id', 'name', 'author', 'waqfeya_category', 'phone_category', 'century', 'visits', 'volumes', 'volumes_on_phone', 'size_mb', 'missing_mb', 'status', 'phone_folders', 'url', 'archive_ids', 'files_known'])
    w.writerows(rows)
with open(J('data/review/waqfeya-link-mismatch.tsv'), 'w') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['waqfeya_id', 'waqfeya_name', 'phone files the record links (another book)']); w.writerows(mismatch)
from collections import Counter
print(Counter(r[11] for r in rows), '| link to another book:', len(mismatch))

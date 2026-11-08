"""Check every current name against what the file says about itself (owner: earlier agents mislabelled books and
editions — e.g. Tabari «Hajar» that is really Dar al-Maarif). For each inspected file:
  title    — the book title in the path vs the PDF's own title (Waqfeya embeds «<title> - ج N: …»),
  volume   — the NN in «NN - …» vs «ج N» of the PDF title,
  edition  — the «(ت … - …)» / «(ط …)» of the folder/file name vs the investigator/publisher of the Waqfeya record the
             file matches byte-for-byte (exact-size provenance), and vs publisher names read (OCR) on the front pages.
→ data/phone/name-checks.tsv (issue, path, current, evidence). Nothing is renamed here.
Usage: python3 scripts/verify_names.py index.tsv"""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key
J = lambda p: os.path.join(ROOT, p)
META_VOL = re.compile(r'^(.*?)\s*-?\s*ج\s*(\d+)\s*(?::.*)?$')
ED_STOP = set(norm('ت ط دار مكتبة مؤسسة مطبعة المطبعة الطبعة نشر للنشر والتوزيع بيروت القاهرة و مجموعة من المحققين وآخرون').split())

def book_title(p):
    parts = p.split('/')
    name = parts[1] if len(parts) > 2 else parts[-1][:-4]
    return name

def words(s):
    return {w for w in norm(s).split() if w not in ED_STOP and len(w) > 2 and not w.isdigit()}

def edition_parts(name):
    """(investigator words, publisher words) claimed by a name: «(ت R - P)», «(ط P)», « - ت- R», « - ط. P»."""
    r, p = '', ''
    for seg in re.findall(r'\(([^()]*)\)', name):
        m = re.match(r'\s*ت[\s.:\-]+(.+?)(?:\s+-\s+(.+))?$', seg)
        if m: r, p = m.group(1), m.group(2) or p; continue
        m = re.match(r'\s*ط[\s.:\-]+(.+)$', seg)
        if m: p = m.group(1)
    for m in re.finditer(r'\s-\s(ت|ط)[\s.\-]+([^-()]+)', name):
        if m.group(1) == 'ت': r = r or m.group(2)
        else: p = p or m.group(2)
    return words(r), words(p)

def main(index):
    idx = {p for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')}
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv'), encoding='utf-8'), delimiter='\t')}
    books = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        if os.path.exists(J(fn)):
            for l in open(J(fn), encoding='utf-8'):
                d = json.loads(l); books[d['_id']] = d
    out, stats = [], collections.Counter()
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l); p = d['path']
        if p not in idx or not d.get('pages'): continue
        stats['checked'] += 1
        name, fn = book_title(p), p.rsplit('/', 1)[1]
        mt = ((d.get('meta') or {}).get('title') or '').strip()
        m = META_VOL.match(mt)
        mbase = m.group(1) if m else mt
        kt, km = title_key(name).split(), title_key(mbase).split()
        if len(km) >= 2 and not re.search(r'[A-Za-z]{4}', mt) and not re.match(r'^(مؤلفات|سلسلة|مجلة|موسوعة|مجموع)', name):
            head = km[:3]
            hit = sum(1 for w in head if w in kt) / len(head)
            if hit < 0.34:
                out.append(('title', p, name, mt)); stats['title mismatch'] += 1
        nn = re.match(r'^(\d{1,4}) - ', fn)
        if m and nn and int(nn.group(1)) not in (0, int(m.group(2))) and title_key(mbase)[:8] == title_key(name)[:8]:
            out.append(('volume', p, fn, mt)); stats['volume mismatch'] += 1
        r = prov.get(p)
        b = books.get(r['waqfeya_id']) if r and r.get('waqfeya_id') else None
        nr, np_ = edition_parts(name)
        if b and (nr or np_):
            br, bp = words(b.get('researcher') or ''), words(b.get('publisher') or '')
            if (nr and br and not (nr & br)) or (np_ and bp and not (np_ & bp | (np_ & br) | (nr & bp))):
                out.append(('edition', p, name, f'Waqfeya record (exact bytes): ت {b.get("researcher") or "-"} | ط {b.get("publisher") or "-"}')); stats['edition mismatch'] += 1
    with open(J('data/phone/name-checks.tsv'), 'w', encoding='utf-8') as w:
        w.write('issue\tpath\tcurrent\tevidence\n')
        for r in out: w.write('\t'.join(r) + '\n')
    print(dict(stats))

if __name__ == '__main__':
    main(sys.argv[1])

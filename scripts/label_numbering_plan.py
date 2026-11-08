"""Number and label volumes from Waqfeya's own per-file download labels (the most reliable source):
  "مجلد 3" / "المجلد الثالث: الطهارة" / "الجزء الأول - القسم الثاني: …" / "المجلدان 1-2: كتاب الإيمان" /
  "المجلدات الأول والثاني والثالث: …" / "مقدمة الجزء الأول" / "مقدمة التحقيق" / "الواجهة".
Number = the (first) volume the label names; label text = what the label says beyond a bare volume number.
Only folders flagged by audit_numbering.py are touched; files without a Waqfeya label keep their names
unless they clash, in which case the folder goes to review.
Usage: python3 scripts/label_numbering_plan.py index.tsv plans/NNN.tsv"""
import csv, json, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import clean, fit, short_title
from build_catalog import split_folder
from audit_numbering import audit
from tail_numbering_plan import ORD
J = lambda p: os.path.join(ROOT, p)
ORD_RX = '|'.join(sorted(map(re.escape, ORD), key=len, reverse=True))

def parse(label):
    """-> (number or None, 'vol'|'front', text) ; None if the label names no volume and is not front matter."""
    t = re.sub(r'^\s*تحميل\s+', '', label).strip()
    head, _, tail = t.partition(':')
    head, tail = head.strip(), tail.strip()
    front = bool(re.match(r'^(مقدمة|المقدمة|تقديم|الواجهة|الغلاف|مقدمة التحقيق)', head)) or bool(re.match(r'^(مقدمة|المقدمة)', tail) and not re.search(r'\d|' + ORD_RX, tail))
    m = re.search(r'(?:مجلد|المجلد|المجلدان|المجلدات|الجزء|الجزءان|جزء|ج)\s*(\d{1,3})', head) or re.search(r'(?:^|\s)(\d{1,3})(?:\s*-\s*\d{1,3})?(?:\s|$)', head)
    num = int(m.group(1)) if m else None
    if num is None:
        o = re.search(ORD_RX, head)
        if o: num = ORD[o.group(0)]
    if num is None and not front: return None
    pm = re.fullmatch(r'(?:مجلد|المجلد|الجزء|جزء|ج)\s*\d{1,3}\s*\((.+)\)', head)
    if pm and not tail: head, tail = re.sub(r'\s*\(.+\)$', '', head), pm.group(1)
    bare = re.fullmatch(r'(?:مجلد|المجلد|الجزء|جزء|ج)\s*(?:\d{1,3}|' + ORD_RX + r')', head)
    text = tail if bare else (t if not front or num is None else t)
    if front and num is None: return (0, 'front', clean(t.replace(':', ' -')))
    return (num, 'front' if front else 'vol', clean(text.replace(':', ' -')) if text else '')

def main(index, out):
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    link = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn)):
            d = json.loads(l)
            for x in d.get('links') or []:
                m = re.search(r'archive\.org/download/([^/]+)/(.+?)\s*$', x.get('url', ''))
                if m: link[(m.group(1), m.group(2))] = x['title'].strip()
    flagged = set(f for v in audit(index).values() for f in v)
    files = defaultdict(list)
    for p, s in csv.reader(open(index), delimiter='\t'):
        if p.rsplit('/', 1)[0] in flagged: files[p.rsplit('/', 1)[0]].append(p.rsplit('/', 1)[1])
    moves, review, stats = [], [], Counter()
    for folder, names in sorted(files.items()):
        parsed = {}
        for n in names:
            r = prov.get(f'{folder}/{n}', {})
            if r.get('match', 'none') == 'none': continue
            lab = link.get((r.get('archive_id'), r.get('orig_name')))
            if lab and (x := parse(lab)):
                if x[1] == 'vol' and re.search(r'p\.pdf$', r.get('orig_name', ''), re.I):
                    x = (x[0], 'front', (x[2] + ' - المقدمة').strip(' -') if 'مقدمة' not in x[2] else x[2])
                parsed[n] = x
        if len(parsed) < 2 or len(parsed) < 0.5 * len(names): stats['not enough labels'] += 1; continue
        title, author, _ = split_folder(folder.split('/', 1)[1])
        short = clean(short_title(title, author))
        width = max(2, len(str(max(v[0] for v in parsed.values()))))
        plan = {}
        for n, (num, kind, text) in parsed.items():
            if kind == 'front' and not text: text = 'المقدمة' if num else 'الواجهة'
            plan[n] = f'{str(num).zfill(width)} - {short}' + (f' ({fit(text, 100)})' if text else '') + '.pdf'
        final = {n: plan.get(n, n) for n in names}
        if len(set(final.values())) < len(final):
            review.append((folder, 'Waqfeya labels give the same name twice')); stats['review'] += 1; continue
        for n, new in final.items():
            if new != n: moves.append((f'Books/{folder}/{n}', f'Books/{folder}/{new}', 'numbering: from Waqfeya per-file labels')); stats['renamed'] += 1
    # order: vacate a name before another file takes it
    srcs = {a for a, b, r in moves}; ordered = []; pending = list(moves)
    while pending:
        ready = [m for m in pending if m[1] not in srcs or m[1] in {x[0] for x in ordered}]
        if not ready: ordered += pending; break
        for m in ready: ordered.append(m); pending.remove(m)
    with open(out, 'w') as w:
        for a, b, r in ordered: w.write(f'{a}\t{b}\t{r}\n')
    with open(J('data/phone/numbering-review.tsv'), 'a') as w:
        for x, why in review: w.write(f'{x}\t{why}\n')
    print(dict(stats), '| moves:', len(moves))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

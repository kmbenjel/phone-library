"""Plan names for files still carrying raw archive.org names (`NN_<id>.pdf`, `NN_<id>p.pdf`, `<id>_<title>.pdf`):
label from the Waqfeya record that links the file (provenance waqfeya_id / archive_id+orig_name), per AGENTS.md §4.
Usage: python3 scripts/raw_names_plan.py index.tsv plans/NNN-raw-names.tsv   (unresolved → stdout as REVIEW)"""
import csv, json, os, re, sys, urllib.parse
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from label_numbering_plan import parse
from rename_plan import clean, fit, short_title
from build_catalog import split_folder
J = lambda p: os.path.join(ROOT, p)
LINK = re.compile(r'archive\.org/(?:details|download|stream)/([^/\s]+)/(.+?)\s*$')
RAW = re.compile(r'^(\d+)_([^/]*)\.pdf$', re.I)
# an archive.org item's own file names, letters then the volume (2026-10-18 deep check: 158 files in 38 sets, «trm01.pdf»,
# «trm01p.pdf» the preface of 01, «shmiradat0.pdf» the front) — the same treatment as «NN_ID.pdf» / «NN_IDp.pdf»
RAW2 = re.compile(r'^[A-Za-z][A-Za-z_-]*?(\d{1,3})([a-z]?)\.pdf$')
def raw(n):
    m = RAW.match(n)
    if m: return m.group(1), m.group(2)
    m = RAW2.match(n)
    return (m.group(1), m.group(2) or '0') if m else None

def main(index, out):
    now = [(p, int(s)) for p, s in csv.reader(open(index), delimiter='\t')]
    names = defaultdict(set)
    for p, s in now: names[p.rsplit('/', 1)[0]].add(p.rsplit('/', 1)[1])
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    links = {}   # (item, file) -> label ; by waqfeya id too
    byid = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn)):
            d = json.loads(l); byid[d['_id']] = d
            for x in d.get('links') or []:
                m = LINK.search(x.get('url', ''))
                if m: links[(m.group(1), urllib.parse.unquote(m.group(2)))] = (x['title'].strip(), d)
    rows, review = [], []
    taken = {f: set(v) for f, v in names.items()}
    for p, s in now:
        folder, n = p.rsplit('/', 1)
        m = raw(n)
        if not m or p.startswith('فهارس الويب/'): continue
        pr = prov.get(p, {})
        item, orig = pr.get('archive_id', ''), pr.get('orig_name', '') or n
        hit = links.get((item, orig)) or links.get((item, orig[:-4]))
        t, a, _ = split_folder(folder.split('/', 1)[1])
        short = clean(short_title(t, a))
        others = [o for o in names[folder] if not raw(o)]
        width = max([len(mm.group(1)) for o in names[folder] for mm in [re.match(r'^(\d{2,3})[ _-]', o)] if mm] or [2])
        multi = sum(1 for o in names[folder] if raw(o) and len(raw(o)[0]) <= 3) > 1 or any(re.match(r'^\d+ - ', o) for o in others)
        new = None
        vol, rest = m
        if len(vol) >= 4:                                   # "<archive id>_<title words>.pdf": the book itself
            new = f'{fit(clean(t), 180)}.pdf' if len(names[folder]) == 1 else None
            how = 'single book file, named after its folder title'
        elif hit:
            lab, d = hit; pp = parse(lab)
            if pp:
                num, kind, text = pp
                text = re.sub(r'^\((.+)\)$', r'\1', text or '')
                if rest.endswith('p') and kind == 'vol': kind, text = 'front', 'المقدمة'
                if kind == 'front' and not text: text = 'المقدمة' if num else 'الواجهة'
                new = (f'{num:0{width}d} - ' if multi or kind == 'vol' else '') + short + (f' ({fit(text, 90)})' if text else '') + '.pdf'
            how = f'Waqfeya label «{lab}»'
        if new is None:
            # fall back on the archive.org pattern itself (§4): 00_ = front, NN_ = volume NN, NN_IDp = preface of NN, NN_IDe = ?
            k = int(vol)
            if rest.endswith('p'): new = f'{k:0{width}d} - {short} (المقدمة).pdf'; how = 'archive.org pattern NN_IDp (preface)'
            elif re.fullmatch(r'\d+', rest): new = f'{k:0{width}d} - {short}' + (' (الواجهة)' if k == 0 else '') + '.pdf'; how = 'archive.org pattern NN_ID (Waqfeya label not found)'
            else: review.append((p, f'no label, unknown suffix «{rest}»')); continue
        if new in taken[folder]: review.append((p, f'clash: {new}')); continue
        taken[folder].add(new); taken[folder].discard(n)
        rows.append((f'Books/{p}', f'Books/{folder}/{new}', f'raw archive name → {how}'))
    with open(out, 'w') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    for p, why in review: print('REVIEW', p, '|', why)
    print('planned', len(rows), 'review', len(review))

if __name__ == '__main__':
    main(*sys.argv[1:3])

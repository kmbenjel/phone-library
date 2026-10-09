"""Audit the files I added from Waqfeya/archive.org (plans 021-replacements, 024-complete-volumes).

An archive.org item often bundles several books, so an addition is kept only if it belongs to the book:
  - the Waqfeya record links this very file, or
  - the file sits in the same item and follows the record's own file pattern (Waqfeya sometimes links volume 5
    twice and forgets 4: "gse04" next to linked "gse03/gse05"), or it is a preface ("NN_IDp" / "IDp") of a linked file.
Everything else is another book of the bundle and is listed for removal (only my own additions, never original files).
Two copies of the same source file in one folder: one is kept. Kept files are named from the Waqfeya label.
Usage: python3 scripts/additions_audit.py index.tsv plans/NNN-remove.tsv plans/NNN-names.tsv"""
import csv, json, os, re, sys, urllib.parse
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from label_numbering_plan import parse
from rename_plan import clean, fit, short_title
from build_catalog import split_folder
from textnorm import title_key
J = lambda p: os.path.join(ROOT, p)
PLANS = tuple(os.environ.get('AUDIT_PLANS', '021-replacements,024-complete-volumes').split(','))
LINK = re.compile(r'archive\.org/(?:details|download|stream)/([^/\s]+)/(.+?)\s*$')

def skeleton(n):
    b = re.sub(r'\.pdf$', '', n, flags=re.I)
    return re.sub(r'\d+', '#', b), [int(x) for x in re.findall(r'\d+', b)]

def near(fname, linked):
    """Same letter/digit pattern as a linked file of the record and every number within reach of it."""
    sk, nums = skeleton(fname)
    for l in linked:
        s2, n2 = skeleton(l)
        if s2 == sk and all(abs(a - b) <= 40 for a, b in zip(nums, n2)): return True
    return False

def preface_of(fname, linked):
    b = re.sub(r'\.pdf$', '', fname, flags=re.I)
    return b.endswith('p') and any(re.sub(r'\.pdf$', '', l, flags=re.I) == b[:-1] for l in linked)

def main(index, out_rm, out_mv):
    now = {'Books/' + p: int(s) for p, s in csv.reader(open(index), delimiter='\t')}
    recs = defaultdict(list)
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn)):
            d = json.loads(l); recs[d.get('name', '').strip()].append(d)
    adds = {}
    for x in csv.reader(open(J('data/changes/changes.tsv')), delimiter='\t'):
        if x and x[1] == 'add' and x[5] in PLANS and x[3] in now:
            m = re.search(r'«(.+?)»: (\S+)', x[4])
            if m: adds[x[3]] = (m.group(1).strip(), m.group(2))
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    orig_items = defaultdict(set)
    for q in now:
        if q not in adds and q[6:] in prov and prov[q[6:]].get('archive_id'): orig_items[q.rsplit('/', 1)[0]].add((prov[q[6:]]['archive_id'], prov[q[6:]]['orig_name']))
    by_size = defaultdict(list)
    for q, sz in now.items(): by_size[sz].append(q)
    rm, mv, stats = [], [], Counter()
    seen_src = {}
    for p in sorted(adds):
        rec, url = adds[p]
        m = re.search(r'archive\.org/download/([^/]+)/(.+)$', url)
        item, fname = m.group(1), urllib.parse.unquote(m.group(2))
        links = {}
        for d in recs.get(rec, []):
            for x in d.get('links') or []:
                lm = LINK.search(x.get('url', ''))
                if lm:
                    f2 = urllib.parse.unquote(lm.group(2))
                    links[(lm.group(1), f2 if f2.lower().endswith('.pdf') else f2 + '.pdf')] = x['title'].strip()
        folder, n = p.rsplit('/', 1)
        key = (folder, item, fname)
        if key in seen_src: rm.append((p, f'same source file added twice ({seen_src[key].rsplit("/", 1)[1]})')); stats['twice'] += 1; continue
        linked = [f for (i, f) in links if i == item]
        twin = [q for q in by_size.get(now[p], []) if q != p and q not in adds]
        if twin: rm.append((p, f'already in the library, same size to the byte: {twin[0].split("/", 2)[2]}')); stats['already there'] += 1; continue
        if (item, fname) in links: lab, how = links[(item, fname)], 'linked'
        elif preface_of(fname, linked): lab, how = None, 'preface'
        elif linked and near(fname, linked): lab, how = None, 'pattern'
        else:
            rm.append((p, f'not part of «{rec}»: another book of the bundled item {item}')); stats['foreign'] += 1; continue
        if folder.count('/') < 2:                 # a single book uploaded as a plain file in its section (Books/<section>): named already
            seen_src[key] = p; stats[how] += 1; continue
        t, a, _ = split_folder(folder.split('/', 2)[2])
        kr, kt = title_key(rec).split(), title_key(t).split()
        own = ' '.join(kr[:2]) in ' '.join(kt) or ' '.join(kt[:2]) in ' '.join(kr)   # the folder is this book or series
        if not own and not (orig_items[folder] & set(links)):          # unless the folder's own files come from this record
            rm.append((p, f'another book: the record «{rec}» is not the book of this folder')); stats['other book'] += 1; continue
        seen_src[key] = p
        stats[how] += 1
        short = clean(short_title(t, a)) if own else clean(re.sub(r'\s*-\s*(ت|ط)[:.].*$', '', rec))
        others = [q.rsplit('/', 1)[1] for q in now if q.rsplit('/', 1)[0] == folder]
        wc = Counter(len(mm.group(1)) for o in others for mm in [re.match(r'^(\d{2,3}) - ', o)] if mm)
        width = wc.most_common(1)[0][0] if wc else 2
        numbered = bool(wc)
        vol = re.match(r'^(\d{1,3})[_-]', fname)
        raw = bool(re.search(r'\([A-Za-z0-9_ -]*[A-Za-z0-9][A-Za-z0-9_ -]*\)\.pdf$', n))   # "(14915)", "(dtia)", "(09 - amuzani)"
        sm = re.match(r'^(\d{1,4})_\s*(.+)$', lab or '')
        new = n
        if sm:                                                               # series issue: "150_title - author"
            new = f'{int(sm.group(1)):0{max(width, 3)}d} - {fit(clean(sm.group(2)), 180)}.pdf'
        elif lab and (pr := parse(lab)):
            num, kind, text = pr
            text = re.sub(r'^\((.+)\)$', r'\1', text or '')
            if kind == 'front' and not text: text = 'المقدمة' if num else 'الواجهة'
            cur = re.match(r'^(\d+) - ', n)
            if raw or not cur or int(cur.group(1)) != num or (text and text not in n):
                new = (f'{num:0{width}d} - ' if numbered or kind == 'vol' else '') + short + (f' ({fit(text, 90)})' if text else '') + '.pdf'
        elif how == 'preface':
            new = (f'{int(vol.group(1)):0{width}d} - {short} (مقدمة الجزء).pdf' if vol else
                   f'{0:0{width}d} - {short} (المقدمة).pdf' if numbered else f'{short} (المقدمة).pdf')
        elif how == 'pattern':
            k = int(vol.group(1)) if vol else skeleton(fname)[1][-1]
            if not re.match(rf'^0*{k} - ', n): new = f'{k:0{width}d} - {short}.pdf'
        elif raw:                                                            # "تحميل الكتاب": the book itself
            lab2 = clean(re.sub(r'^(?:تحميل|تصفح)\s*', '', lab or '')).strip()
            new = (f'{int(vol.group(1)):0{width}d} - ' if vol and numbered else '') + fit(short if own else clean(rec), 180) + \
                  ('' if lab2 in ('', 'الكتاب') else f' ({fit(lab2, 90)})') + '.pdf'
        if new != n: mv.append((p, f'{folder}/{new}', f'name from the Waqfeya label ({how})'))
    # never two files with one name: a clash with a file that stays is flagged, not overwritten
    gone = {a for a, r in rm} | {a for a, b, r in mv}
    taken = Counter(q for q in now if q not in gone) + Counter(b for a, b, r in mv)
    clash = [(a, b) for a, b, r in mv if taken[b] > 1]
    for a, b in clash: print('CLASH', a.split('/', 2)[2][:80], '->', b.rsplit('/', 1)[1][:70])
    mv = [x for x in mv if taken[x[1]] == 1]
    with open(out_rm, 'w') as w:
        for a, r in rm: w.write(f'{a}\t{r}\n')
    with open(out_mv, 'w') as w:
        for a, b, r in mv: w.write(f'{a}\t{b}\t{r}\n')
    print(dict(stats), '| remove:', len(rm), '| rename:', len(mv), '| clashes left as they are:', len(clash))

if __name__ == '__main__':
    main(*sys.argv[1:4])

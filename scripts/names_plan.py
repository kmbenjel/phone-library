"""Names from the inside: plan folder and volume names for multi-file book folders (AGENTS.md §4).

Evidence, strongest first:
  1. the file's own PDF metadata title (Waqfeya uploads embed «<title> - ج N: <label>»; data/inspect/files.jsonl),
  2. the Waqfeya link label of the exact file (provenance by exact size → record links),
  3. the raw archive.org pattern NN_<id>[p].pdf (00 = front matter, NN = volume, p = preface of NN).
Folder name = the Waqfeya record (title - author (ت investigator - publisher)) when the current name is deficient
(cut, «- - ط», «ت-», «ط.», «؛» full author, no author). A folder is planned only as a whole: every file must get a
name, numbers must be unique (00 may repeat), names must not collide; otherwise the folder goes to review.
Re-run as inspection progresses (files not inspected yet use the Waqfeya label if any).
Usage: python3 scripts/names_plan.py index.tsv plans/NNN-names.tsv review.tsv [--only-raw]"""
import collections, csv, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key
from rename_plan import load, canonical_folder, clean, fit, short_title, split_wname, label_from_link, vol_from_orig, deficient, author_short, redundant
J = lambda p: os.path.join(ROOT, p)
META_VOL = re.compile(r'^(.*?)\s*-?\s*ج\s*(\d+)\s*(?::\s*(.*))?$')
RAW = re.compile(r'^(\d{1,3})[_-]\d+(?:-\d+)?(p?)[a-z]?\.pdf$', re.I)
BAD_FOLDER = re.compile(r'\s-\s*-\s|\s-\sو\s?ط\b|\s-\s*ط\.?\s*$|\sت-\s|\sط\.\s|؛|\s-\s*$|\s\S{1,2}$')
CONV = re.compile(r'^(\d{2,4}) - .+\.pdf$')

WEAK_END = {norm(w) for w in 'بن ابن أبي أبو عبد ذي ذو أهل دار شيخ الإمام الشيخ العلامة'.split()}
STOPS = {norm(w) for w in 'في من على عن إلى إلي بين مع رواية تأليف شرح بشرح وهو أو المسمى المسماة'.split()}

def short(title, author=''):
    """§4 short title: up to the first subtitle marker, else the first particle (from the 3rd word on), a «و…» word
    (from the 3rd word on) or a «لل…/لإ…/لأ…» word (from the 2nd); never ends on a dangling word (بن، أبي، عبد، أهل…);
    a one-word title gets « - author»."""
    t = re.split(r'\s+=\s+|\s+-\s+|\s+(?:ويليه|ومعه|وبهامشه|وبذيله|وذيله|المسمى|المسماة|الموسوم|الموسومة)\s|،\s*', title)[0].strip()
    w = t.split()
    for i in range(1, len(w) if len(w) > 5 else 0):                      # five words or fewer: keep whole
        n = norm(w[i])
        if (i >= 2 and (n in STOPS or (len(n) > 3 and n.startswith('و')))) or (len(n) > 3 and w[i].startswith(('لل', 'لإ', 'لأ'))):
            w = w[:i]; break
    w = w[:6]
    while len(w) > 1 and norm(w[-1]) in WEAK_END: w.pop()
    s = ' '.join(w)
    if len(w) == 1 and author and not redundant(author, s):
        s = f'{s} - {author}'
    return clean(s)

def meta_titles():
    m = {}
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d.get('pages'): m[d['path']] = (d.get('meta') or {}).get('title', '') or ''
    return m

def batch_records():
    """10-04 batch: folder title (as download_missing.py wrote it) → Waqfeya id."""
    r = {}
    for f in glob.glob(J('lists/2026-10-04-download_missing-*.tsv')):
        for row in csv.DictReader(open(f, encoding='utf-8'), delimiter='\t'):
            r[row['title'].replace('/', '-').replace(':', '-')] = row['waqfeya_id']
    return r

def main(index, out, review_out, only_raw=False):
    books, link_label, prov = load()
    meta, brec = meta_titles(), batch_records()
    idx = [p for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')]
    folders = collections.defaultdict(list)
    for p in idx:
        if p.count('/') == 2 and not p.startswith('فهارس الويب/'): folders[p.rsplit('/', 1)[0]].append(p)
    existing = set(folders)
    rows, review, stats = [], [], collections.Counter()
    targets = {}
    for folder, ps in sorted(folders.items()):
        if len(ps) < 2: continue
        cat, name = folder.split('/', 1)
        if re.match(r'^(مؤلفات|سلسلة|مجلة|موسوعة)', name): continue                 # collections: own rules
        if only_raw and not any(RAW.match(p.rsplit('/', 1)[1]) for p in ps): continue
        src = collections.Counter(prov[p]['waqfeya_id'] for p in ps if p in prov and prov[p].get('waqfeya_id'))
        wid = src.most_common(1)[0][0] if src else brec.get(name)
        b = books.get(wid) if wid else None
        if b and src and src.most_common(1)[0][1] < 0.6 * len(ps):
            review.append((folder, f'files trace to {len(src)} Waqfeya records ({dict(src.most_common(3))})')); stats['review: mixed'] += 1; continue
        # ---- folder name
        new_folder = folder
        if b and (BAD_FOLDER.search(name) or deficient(name) or ' - ' not in name):
            canon, title, a = canonical_folder(b)
            if title_key(canon)[:12] != title_key(name)[:12] and not title_key(b['name']).startswith(title_key(name)[:12]):
                review.append((folder, f'Waqfeya record «{b["name"]}» does not match the folder name')); stats['review: record/name'] += 1; continue
            new_folder = f'{cat}/{canon}'
        title = split_wname(b['name'])[0] if b else re.split(r'\s+-\s+', name)[0]
        a = author_short(((b or {}).get('author') or {}).get('name', '')) if b else ''
        stitle = short(title, a)
        # ---- files
        plan, problem = [], None
        for p in sorted(ps):
            fn = p.rsplit('/', 1)[1]
            mt = META_VOL.match(meta.get(p, '').strip())
            r = prov.get(p, {})
            lab_w = label_from_link(link_label.get((r.get('archive_id'), r.get('orig_name')), '')) if r else ''
            raw = RAW.match(fn)
            num, kind, lab = None, None, ''
            if mt and title_key(mt.group(1))[:10] == title_key(title)[:10]:
                num, kind, lab = int(mt.group(2)), 'vol', lab_w or clean(mt.group(3) or '')   # number from the file, label: Waqfeya's (cleaner)
                if raw and raw.group(2): kind, lab = 'pref', 'المقدمة'
            elif mt and 'مقدم' in mt.group(1):
                num, kind, lab = 0, 'front', clean(f'{mt.group(1)} {mt.group(2)}')
            elif raw:
                n = int(raw.group(1))
                v = vol_from_orig(r['orig_name']) if r.get('orig_name') else None
                if raw.group(2): num, kind, lab = n, 'pref', lab_w or 'المقدمة'
                elif n == 0: num, kind, lab = 0, 'front', lab_w or 'الواجهة'
                elif lab_w or v: num, kind, lab = n, 'vol', lab_w
                else: problem = f'raw name without label: {fn}'; break
            elif CONV.match(fn) and not deficient(fn[:-4]):
                plan.append((p, fn)); continue                                       # already conventional
            else:
                plan.append((p, fn)); continue                                       # no evidence: leave as is
            lab = re.sub(r'^\((.+)\)$', r'\1', lab or '')
            if kind == 'vol' and lab and re.fullmatch(r'(ال)?(جزء|مجلد|ج)\s*\d+', norm(lab)): lab = ''
            if kind == 'vol' and lab and title_key(lab)[:10] == title_key(title)[:10]: lab = ''
            plan.append((p, (num, kind, fit(clean(lab), 90))))
        if problem:
            review.append((folder, problem)); stats['review: raw unlabeled'] += 1; continue
        vols = [x[1][0] for x in plan if isinstance(x[1], tuple) and x[1][1] == 'vol']
        width = max(2, len(str(max(vols, default=1))))
        if len(vols) != len(set(vols)):
            dup = [n for n, c in collections.Counter(vols).items() if c > 1]
            review.append((folder, f'volume numbers repeat by the evidence: {dup[:6]}')); stats['review: repeated volume'] += 1; continue
        final = []
        for p, x in plan:
            if isinstance(x, str): final.append((p, x)); continue
            num, kind, lab = x
            lab = lab or ('الواجهة' if kind == 'front' else 'المقدمة' if kind == 'pref' else '')
            final.append((p, f'{num:0{width}d} - {stitle}' + (f' ({lab})' if lab else '') + '.pdf'))
        names = collections.Counter(n for _, n in final)
        if any(c > 1 for c in names.values()):
            review.append((folder, 'two files would get the same name: ' + ', '.join(n for n, c in names.items() if c > 1)[:200])); stats['review: name clash'] += 1; continue
        if new_folder != folder and (new_folder in existing or new_folder in targets):
            review.append((folder, f'target folder already exists: {new_folder} (same Waqfeya record twice → edition/scan duplicate)')); stats['review: folder exists'] += 1; continue
        targets[new_folder] = folder
        n0 = len(rows)
        for p, nfn in final:
            dst = f'{new_folder}/{nfn}'
            if dst != p: rows.append((f'Books/{p}', f'Books/{dst}', 'names from the file itself (PDF title «ج N: …») + Waqfeya record' if b else 'names from the file itself'))
        if len(rows) > n0: stats['folders'] += 1; stats['moves'] += len(rows) - n0
    with open(out, 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    with open(review_out, 'w', encoding='utf-8') as w:
        for f, why in review: w.write(f'{f}\t{why}\n')
    print(dict(stats))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], '--only-raw' in sys.argv)

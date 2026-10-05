"""Exact duplicates (same MD5, computed on the phone by phone_md5.py) → which copy to keep, which to delete.
Keep = the copy that (1) completes a multi-file folder (its siblings are not themselves duplicates), (2) sits in the
section Shamela/Waqfeya give the title, (3) follows the naming rules (author, edition, no raw/ASCII name, no «ت-»/«ط.»).
When the copies' names disagree on WHICH book it is, the file's own evidence decides (PDF title/author metadata and
first-pages text from data/inspect/files.jsonl + OCR); no evidence or a tie → review list, nothing deleted.
Usage: python3 scripts/exact_dups_plan.py index.tsv plans/NNN-exact-dups.tsv review.tsv
  plan rows: path<TAB>duplicate of: <kept path> | <why>   (input for delete_files.py)"""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm, title_key, author_tokens
J = lambda p: os.path.join(ROOT, p)

def load_evidence():
    ev, keys = {}, {}
    if os.path.exists(J('data/inspect/files.jsonl')):
        for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
            d = json.loads(l); m = d.get('meta', {})
            ev[d['path']] = ' '.join([m.get('title', ''), m.get('author', ''), m.get('subject', ''), d.get('text_first', '')[:1500]])
            keys[d.get('key')] = d['path']
    if os.path.exists(J('data/inspect/ocr.jsonl')):
        for l in open(J('data/inspect/ocr.jsonl'), encoding='utf-8'):
            d = json.loads(l); p = keys.get(d['key'])
            if p: ev[p] = ev.get(p, '') + ' ' + d['text'][:1500]
    return {p: set(norm(t).split()) for p, t in ev.items()}

def shamela_sections():
    smap = {}
    for l in open(J('data/mappings/shamela-to-phone.tsv'), encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        k, _, v = l.rstrip('\n').partition('\t'); smap[k] = v.strip()
    sec = collections.defaultdict(set)
    for r in csv.DictReader(open(J('data/shamela/books.tsv'), encoding='utf-8'), delimiter='\t'):
        if smap.get(r['category']): sec[title_key(r['title'])].add(smap[r['category']])
    return sec

def book_name(p):
    parts = p.split('/')
    return parts[1] if len(parts) > 2 else parts[-1][:-4]

def author_of(name):
    """Author words of «title - author (edition)»; segments that are editions («ت - X», «ط. Y», «ج 1») are not authors."""
    raw = [x.strip() for x in re.sub(r'\([^()]*\)', ' ', name).split(' - ')[1:]]
    segs = []
    for i, x in enumerate(raw):
        if i and raw[i - 1] in ('ت', 'ط', 'و ط', 'ت.', 'ط.'): continue          # «- ت - هيتو»: investigator, not author
        if x and not re.match(r'^(ت|ط|ج|و\s?ط)\b|^(ت|ط)[.\-]', x) and len(x) > 2: segs.append(x)
    return author_tokens(segs[-1]) if segs else set()

JUNK_META = re.compile(r'binder|\.pdf$|^[A-Za-z0-9 _\-.]+$|acdsee|microsoft|untitled|^\s*$', re.I)

ED_STOP = set('ط ت دار مكتبه مكتبة مؤسسه مطبعه المطبعه الطبعه طبعه نشر للنشر والتوزيع الكتب العلميه بيروت القاهره و'.split())

def edition_of(name):
    segs = re.findall(r'\(([^()]*)\)', name) + re.findall(r'\s-\s(?:ط|ت)[\s.\-]+([^-()]+)', name)
    return {w for w in norm(' '.join(segs)).split() if w not in ED_STOP and len(w) > 2 and not w.isdigit()}

def edition_conflict(a, b):
    ea, eb = edition_of(a), edition_of(b)
    return bool(ea and eb and not (ea & eb))

def same_work(a, b):
    ka, kb = title_key(a).split(), title_key(b).split()
    if not ka or not kb: return False
    aa, ab = author_of(a), author_of(b)
    if aa and ab and not (aa & ab): return False           # same title, different authors (الأوائل للطبراني ≠ للعسكري)
    n = min(len(ka), len(kb), 3)
    if ka[:n] == kb[:n] and (n >= 2 or len(ka) == len(kb)): return True
    sa, sb = set(ka), set(kb)
    return len(sa & sb) / max(1, max(len(sa), len(sb))) >= 0.6

def main(index, out, review_out):
    idx = {p: int(s) for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t') if s.isdigit()}
    md5 = {r[0]: r[2] for r in csv.reader(open(J('data/phone/md5.tsv'), encoding='utf-8'), delimiter='\t') if len(r) == 3 and r[0] in idx and int(r[1]) == idx[r[0]]}
    groups = collections.defaultdict(list)
    for p, h in md5.items(): groups[h].append(p)
    groups = [sorted(v) for v in groups.values() if len(v) > 1]
    dup_paths = {p for g in groups for p in g}
    folder_files = collections.defaultdict(list)
    for p in idx: folder_files[p.rsplit('/', 1)[0]].append(p)
    ev, sec = load_evidence(), shamela_sections()
    global META, MAUTH
    META, MAUTH = {}, {}
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d.get('pages'):
            META[d['path']] = ((d.get('meta') or {}).get('title') or '').strip()
            MAUTH[d['path']] = ((d.get('meta') or {}).get('author') or '').strip()

    def score(p):
        parts = p.split('/'); cat, fname = parts[0], parts[-1]; folder = p.rsplit('/', 1)[0]
        s, why = 0, []
        if len(parts) > 2:
            sib = [q for q in folder_files[folder] if q != p]
            uniq = [q for q in sib if q not in dup_paths]
            if uniq: s += 40; why.append(f'completes a folder of {len(sib) + 1} files')
            elif sib: s += 10
            else: s -= 5                                    # lone file in its own folder (single books are plain files)
        else:
            s += 5
        secs = sec.get(title_key(book_name(p)), set())
        if cat in secs: s += 25; why.append('Shamela section')
        name = book_name(p)
        if re.search(r'\s-\s', name) and '(' in name: s += 10
        if re.search(r'[A-Za-z]{4,}|^\d+_\d+', fname[:-4]) and not re.search(r'[ء-ي]', fname): s -= 30
        if re.search(r'\sت-\s|\sط\.\s|\.\.\.|،$|\s-\s*$', name): s -= 10
        if re.search(r'\s-\s*-\s|\s-\sو\s?ط\b|\s-\s*ط\.?\s*$|\s-\sت\s-\s|؛', name): s -= 15     # junk «- - ط», «- ت - X»
        if author_of(name): s += 5
        if re.match(r'^\d{2,3} - ', fname): s += 5                                              # numbered volume name
        if re.search(r'نسخة (ثانية|أخرى)|_alt', p): s -= 40
        return s, why

    rows, review, stats = [], [], collections.Counter()
    for g in groups:
        names = [book_name(p) for p in g]
        agree = all(same_work(names[0], n) for n in names[1:])
        if agree and any(edition_conflict(a, b) for a in names for b in names):
            review.append((g, 'same work, conflicting edition labels')); stats['review: edition labels'] += 1; continue
        if agree and len({p.rsplit('/', 1)[0] for p in g}) == 1:
            review.append((g, 'same folder, different file labels')); stats['review: same-folder labels'] += 1; continue
        if agree:
            best = max(g, key=lambda p: (score(p)[0], -len(p)))
            how = 'same work'
        else:
            # different books claim the same bytes: the file itself decides
            have = [p for p in g if ev.get(p)]
            mt = META.get(g[0], '')
            if mt and not JUNK_META.search(mt):
                km = title_key(re.split(r'\s+-\s+ج\s*\d|:', mt)[0]).split()[:3]
                def hit(p):
                    k = title_key(book_name(p)).split()
                    return sum(1 for w in km if w in k) / max(1, len(km))
                ranked = sorted(g, key=lambda p: (hit(p), score(p)[0]), reverse=True)
                good = [p for p in g if hit(p) >= 0.67]
                if len(good) > 1:                                  # several names fit the title: the author must decide
                    ma = author_tokens(MAUTH.get(g[0], ''))
                    if ma:
                        good = [p for p in good if author_of(book_name(p)) & ma] or good
                    names_ = [book_name(p) for p in good]
                    if not all(same_work(names_[0], n) for n in names_[1:]) or any(edition_conflict(a, b) for a in names_ for b in names_):
                        good = []
                if good and all(hit(p) < 0.34 for p in g if p not in good):
                    best = max(good, key=lambda p: (score(p)[0], -len(p)))
                    how = f'names disagree; the file\'s own title «{mt[:60]}» is «{book_name(best)[:60]}»'
                    stats['groups'] += 1
                    for p in g:
                        if p != best:
                            rows.append((f'Books/{p}', f'duplicate of: {best} | {how}')); stats['delete'] += 1; stats['bytes'] += idx[p]
                    continue
            if os.environ.get('AUTO_EVIDENCE') != '1':           # no informative title inside: decided by looking at the pages
                review.append((g, 'names disagree' + ('' if have else ', not inspected yet'))); stats['review: names disagree'] += 1; continue
            if not have:
                review.append((g, 'names disagree, file not inspected yet')); stats['review: no evidence'] += 1; continue
            words = set().union(*(ev[p] for p in have))
            def match(p):
                k = set(title_key(book_name(p)).split())
                return len(k & words) / max(1, len(k))
            ranked = sorted(g, key=lambda p: (match(p), score(p)[0]), reverse=True)
            if match(ranked[0]) < 0.6 or match(ranked[0]) - match(ranked[1]) < 0.25:
                review.append((g, 'names disagree; evidence ' + ', '.join(f'{match(p):.2f}' for p in g))); stats['review: unclear'] += 1; continue
            best = ranked[0]; how = f'names disagree; the file\'s own title page/metadata matches «{book_name(best)}» ({match(best):.2f})'
        stats['groups'] += 1
        for p in g:
            if p != best:
                rows.append((f'Books/{p}', f'duplicate of: {best} | {how}')); stats['delete'] += 1; stats['bytes'] += idx[p]
    with open(out, 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    with open(review_out, 'w', encoding='utf-8') as w:
        for g, why in review: w.write(why + '\t' + '\t'.join(g) + '\n')
    stats['GB'] = round(stats.pop('bytes', 0) / 1e9, 2)
    print(dict(stats))

if __name__ == '__main__':
    main(*sys.argv[1:4])

"""Fix numbering inside folders (run after renames). Two folder kinds:

INDEPENDENT (a collection or series of separate books, e.g. «سلسلة أعلام المسلمين», «مؤلفات عبد الله كنون»):
  the fake "01 - <folder> (<title>)" numbering is removed; each file is named by its own title, taken from the
  archive.org original file name when it is Arabic, else from the bracketed title. Real series numbers are kept
  only where the source numbers the issues (e.g. عالم المعرفة: 008.pdf -> "008 - <title>").
MULTI-VOLUME (one book): each file's number = the volume number in its archive.org source name when known,
  else its current number when unique. "99"/"999" (indexes) -> the real number from the source, else last volume + 1.
  Cover/preface without a number -> 00. A folder whose numbers still clash is left unchanged (review list).
Usage: python3 scripts/renumber_plan.py data/phone/index-<state>.tsv plans/NNN-numbering.tsv"""
import csv, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import norm
from rename_plan import COLLECTION, clean, fit
J = lambda p: os.path.join(ROOT, p)
AR = re.compile(r'[ء-ي]')
INDEP_NAME = re.compile(r'^(مؤلفات|سلسلة|آثار|المكتبة|رسائل|مجموع فيه|موسوعة رسائل|تحقيقات|المنظومات)')
PERIODICAL = re.compile(r'^مجلة')
SERIES_NUMBERED = {'سلسلة عالم المعرفة'}           # series whose issue numbers are part of the reference
FRONT = re.compile(r'\((?:الواجهة|المقدمة|مقدمة[^)]*|الغلاف)\)')
INDEX_LABEL = re.compile(r'فهارس|الفهارس')

def src_number(orig):
    """Volume number and kind from an archive.org source name, or None."""
    b = orig.rsplit('/', 1)[-1]
    for rx in (r'^(\d{1,3})_\d+(?:-\d+)?([a-oq-z]?)(p?)(?:[-_]\d+)?\.pdf$',   # 01_144241-1.pdf, 05_27200d.pdf, 01_16678p.pdf
               r'^(\d{1,3})-\d{1,3}_\d+()(p?)\.pdf$',                          # 01-02_44056.pdf
               r'^(\d{1,3})()(p?)\.pdf$',                                      # 75.pdf
               r'^[a-z][a-z_-]{1,15}?(\d{1,3})()(p?)\.pdf$'):                  # mfsiaitm36.pdf, thtn03.pdf, zka5.pdf
        m = re.match(rx, b, re.I)
        if m:
            n = int(m.group(1)); pre = bool(m.group(3))
            return n, ('front' if n == 0 or pre else 'vol')
    return None

def title_from_orig(orig):
    b = re.sub(r'\.pdf$', '', orig.rsplit('/', 1)[-1], flags=re.I)
    if len(AR.findall(b)) < 6: return ''
    b = re.sub(r'^\d+\s*[-_.]?\s*', '', b)
    b = re.sub(r'_المؤلف_\s*', ' - ', b).replace('_', ' ')
    return clean(b)

def title_from_bracket(fn, folder_name, author):
    m = re.match(r'^\d+ - .*?\((.+)\)(?:_alt)?\.pdf$', fn)
    if not m: return ''
    t = m.group(1)
    t = re.sub(r'^(?:[^()]*\((?:ع\s*)?\d+\)\s*-\s*)', '', t)        # "أعلام المسلمين (ع 001) - " / "عالم المعرفة (001) - "
    t = re.sub(r'\s*\((?:دار|ط)[^)]*$', '', t)                         # cut "(دار ..." at the end
    parts = [x.strip() for x in t.split(' - ')]
    aw = {w for w in norm(author + ' ' + folder_name).split() if len(w) > 2}
    while len(parts) > 1 and (not parts[-1] or {w for w in norm(parts[-1]).split() if len(w) > 2} <= aw or len(parts[-1]) < 3):
        parts.pop()                                                     # trailing (cut) author / publisher fragments
    return clean(' - '.join(parts))

def main(index, out):
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    files = defaultdict(list); size = {}
    for p, s in csv.reader(open(index), delimiter='\t'):
        if p.startswith('فهارس الويب/') or p.count('/') != 2: continue
        files[p.rsplit('/', 1)[0]].append(p.rsplit('/', 1)[1]); size[p] = int(s)
    moves, review, stats = [], [], Counter()
    for folder, names in sorted(files.items()):
        sec, name = folder.split('/', 1)
        numbered = [n for n in names if re.match(r'^\d+ - ', n)]
        c = Counter(re.match(r'^(\d+) - ', n).group(1) for n in numbered)
        all01 = len(names) >= 3 and c.get('01', 0) >= 0.6 * len(names)
        brackets = {m.group(1)[:25] for n in names for m in [re.match(r'^\d+ - .*?\((.+)\)', n)] if m}
        author = name.split(' - ', 1)[1] if ' - ' in name else ''
        plan = {}
        indep = (INDEP_NAME.match(name) or COLLECTION.match(name)) and not PERIODICAL.match(name) and all01 and len(brackets) >= 0.6 * len(names)
        if indep:
            series_num = any(name.startswith(s) for s in SERIES_NUMBERED)
            issue_titles = {}
            if name.startswith('سلسلة عالم المعرفة') and os.path.exists(J('data/archive/aalam_almaarifa-titles.tsv')):
                issue_titles = dict(l.rstrip('\n').split('\t', 1) for l in open(J('data/archive/aalam_almaarifa-titles.tsv')) if '\t' in l)
            for n in names:
                if FRONT.search(n) and not re.match(r'^\d+ - .*\(.+\(', n): continue
                r = prov.get(f'{folder}/{n}', {})
                t = title_from_orig(r.get('orig_name', '')) if r.get('match', 'none') != 'none' else ''
                t = t or title_from_bracket(n, name, author)
                if not t: review.append((f'{folder}/{n}', 'independent item: no title found')); continue
                num = ''
                if series_num:
                    sn = src_number(r.get('orig_name', '')) if r else None
                    mm = re.search(r'\((?:ع\s*)?(\d{2,3})\)', n)
                    num = f'{sn[0]:03d} - ' if sn else (f'{int(mm.group(1)):03d} - ' if mm else '')
                    if num and issue_titles.get(num[:3]): t = clean(issue_titles[num[:3]])
                plan[n] = fit(num + t, 190) + '.pdf'
            kind = 'independent items'
        else:
            vols = {}
            for n in names:
                r = prov.get(f'{folder}/{n}', {})
                sn = src_number(r.get('orig_name', '')) if r.get('match', 'none') != 'none' else None
                m = re.match(r'^(\d+) - ', n)
                cur = int(m.group(1)) if m else None
                vols[n] = (sn, cur)
            real = [sn[0] for sn, cur in vols.values() if sn and sn[1] == 'vol'] + \
                   [cur for sn, cur in vols.values() if not sn and cur not in (None, 0, 99, 999)]
            if len(real) < 2 and not any(cur in (99, 999) for sn, cur in vols.values()):
                continue                                                # single-volume or nothing to renumber
            last = max(real or [0]); width = max(2, len(str(last + 1)))
            used = Counter(); newnum = {}
            for n, (sn, cur) in vols.items():
                if sn: v = sn
                elif cur in (99, 999) or (cur is None and INDEX_LABEL.search(n)): v = ('idx', 'vol')
                elif cur is None and FRONT.search(n): v = (0, 'front')
                elif cur is None: v = None
                else: v = (cur, 'front' if cur == 0 or FRONT.search(n) else 'vol')
                newnum[n] = v
            nxt = last
            for n in sorted(newnum, key=lambda x: x):
                if newnum[n] and newnum[n][0] == 'idx':
                    nxt += 1; newnum[n] = (nxt, 'vol')
            width = max(2, len(str(nxt)))
            extra = {}                                                  # n -> extra label to keep names apart
            for n in list(newnum):                                     # Shamela exports inside a book folder: named by their own title
                m = re.search(r'\(\(?نسخة للشاملة من\s*-?\s*(.+?)\)*(?:_alt)?\.pdf$', n)
                if m and newnum[n] and newnum[n][1] == 'vol' and len(AR.findall(m.group(1))) >= 4:
                    plan_direct = f'{clean(m.group(1))} (نسخة الشاملة).pdf'; newnum[n] = ('direct', plan_direct)
            groups = defaultdict(list)
            for n, v in newnum.items():
                if v and v[1] == 'vol': groups[v[0]].append(n)
            unresolved = False
            for num_, ns_ in groups.items():
                if len(ns_) < 2: continue
                srcs = {n: prov.get(f'{folder}/{n}', {}).get('orig_name', '') for n in ns_}
                stems = {n: re.sub(r'\.pdf$', '', srcs[n].rsplit('/', 1)[-1], flags=re.I) for n in ns_}
                sz = {n: size.get(f'{folder}/{n}', 0) for n in ns_}
                base = {n: re.sub(r'[a-z]$', '', stems[n], flags=re.I) for n in ns_ if stems[n]}
                big = max(ns_, key=lambda n: sz[n])
                if all(stems[n] for n in ns_) and len(set(base.values())) == 1 and len(set(stems.values())) == len(ns_):
                    pre = [n for n in ns_ if stems[n].lower().endswith('p') and stems[n][:-1] in stems.values()]
                    for n in pre: newnum[n] = (num_, 'front')
                    rest_ = [n for n in ns_ if n not in pre]
                    if len(rest_) > 1:                                  # sub-parts a/b/d… of one volume
                        for i, n in enumerate(sorted(rest_, key=lambda n: stems[n])): extra[n] = 'أبجدهوزحطي'[i]
                elif all(sz[n] < 1.5 * 2**20 for n in ns_ if n != big) and sz[big] >= 3 * max(sz[n] for n in ns_ if n != big):
                    for n in ns_:
                        if n != big: newnum[n] = (num_, 'front')            # small companion file = preface / cover pages
                elif len(ns_) == 2 and any('alt' in n for n in ns_):
                    for n in ns_:
                        if 'alt' in n: extra[n] = 'نسخة أخرى'
                else:
                    unresolved = True
            if unresolved:
                review.append((folder, 'volume numbers still clash after using source names')); stats['clash left'] += 1; continue
            for n, v in newnum.items():
                if v is None: continue
                if v[0] == 'direct': plan[n] = v[1]; continue
                rest = re.sub(r'^\d+ - ', '', n)
                rest = re.sub(r'\s*\(alt\s*-[^)]*\)', '', rest)
                rest = re.sub(r'\(\s*\)\s*-\s*[^()]*\)', '', rest)       # "() - ابن تيمية)" leftovers
                rest = re.sub(r'_alt(?=\.pdf$)', '', rest)
                stem = clean(rest[:-4]) if rest.lower().endswith('.pdf') else clean(rest)
                has_label = re.search(r'\([^()]+\)$', stem)
                edition_only = re.search(r'\s*\((?:ت|ط)[ .][^()]*\)$', stem)
                if v[1] == 'front' and edition_only: stem = stem[:edition_only.start()]; has_label = None
                if v[1] == 'front' and v[0] > 0 and not has_label: stem += ' (المقدمة)'
                if v[1] == 'front' and v[0] == 0 and not has_label: stem += ' (الواجهة)'
                if n in extra:
                    stem = re.sub(r'\s*\([\u0621-\u064A]\)$', '', stem)          # an old one-letter part label
                    stem += f' ({extra[n]})'
                plan[n] = f'{str(v[0]).zfill(width)} - {stem}.pdf'
            kind = 'multi-volume'
        taken = Counter(plan.get(n, n) for n in names)
        if any(k > 1 for k in taken.values()):
            review.append((folder, f'{kind}: new names would clash')); stats['clash left'] += 1; continue
        for n, new in plan.items():
            if new != n:
                moves.append((f'Books/{folder}/{n}', f'Books/{folder}/{new}', f'numbering: {kind}')); stats[kind] += 1
    with open(out, 'w') as w:
        for a, b, r in moves: w.write(f'{a}\t{b}\t{r}\n')
    with open(J('data/phone/numbering-review.tsv'), 'w') as w:
        for x, why in review: w.write(f'{x}\t{why}\n')
    print(dict(stats), '| moves:', len(moves), '| review:', len(review))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

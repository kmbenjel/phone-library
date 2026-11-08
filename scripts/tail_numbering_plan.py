"""Second numbering pass for folders where every file is "01 - …" (after renumber_plan.py):
 R3 inner number:    "01 - X (الصوتي - 02 - كتاب المياه)" -> "02 - كتاب المياه";  "(03 (نسخة للشاملة من - جزء ابن ثرثال))" -> "03 - جزء ابن ثرثال (نسخة الشاملة)"
 R4 ordinal volumes: Waqfeya link label "الأول والثاني والثالث: …" -> volume 01 (first of the range)
 R2 separate works:  bracketed titles that are works, not companions (e.g. each Mu'allaqa) -> "<work>.pdf"
 R1 book + companions: largest file = the book "<title>.pdf"; the rest "<title> (<what it is>).pdf"
Folders it cannot decide are listed in data/phone/numbering-review.tsv.
Usage: python3 scripts/tail_numbering_plan.py index.tsv plans/NNN.tsv"""
import csv, json, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import clean, fit, short_title
from build_catalog import split_folder
J = lambda p: os.path.join(ROOT, p)
COMPANION = re.compile(r'نسخة|الشاملة|صوت|الصوتي|موقع|الرق المنشور|مخطوط|ترجمة|المقدمة|الواجهة|\balt\b|صفحة|شرح صوتي|pdf', re.I)
ORD = {'الأول': 1, 'الثاني': 2, 'الثالث': 3, 'الرابع': 4, 'الخامس': 5, 'السادس': 6, 'السابع': 7, 'الثامن': 8, 'التاسع': 9, 'العاشر': 10,
       'الحادي عشر': 11, 'الثاني عشر': 12, 'الثالث عشر': 13, 'الرابع عشر': 14, 'الخامس عشر': 15, 'السادس عشر': 16, 'السابع عشر': 17,
       'الثامن عشر': 18, 'التاسع عشر': 19}
_TENS = {'العشرون': 20, 'الثلاثون': 30, 'الأربعون': 40, 'الاربعون': 40, 'الخمسون': 50, 'الستون': 60, 'السبعون': 70, 'الثمانون': 80, 'التسعون': 90}
ORD.update(_TENS)
for _u, _v in (('الحادي', 1), ('الواحد', 1), ('الثاني', 2), ('الثالث', 3), ('الرابع', 4), ('الخامس', 5), ('السادس', 6), ('السابع', 7), ('الثامن', 8), ('التاسع', 9)):
    for _t, _tv in _TENS.items(): ORD[f'{_u} و{_t}'] = _tv + _v

def first_ordinal(label):
    hits = [(label.find(k), -len(k), v) for k, v in ORD.items() if k in label]   # earliest, then longest phrase
    return min(hits)[2] if hits else None

def companion_label(b):
    b = clean(re.sub(r'^\(|\)$', '', b))
    b = re.sub(r'نسخة للشاملة( من)?', 'نسخة الشاملة', b)
    b = re.sub(r'^alt\s*-?\s*\d*\s*-?\s*', 'نسخة أخرى ', b).strip(' -')
    return b or 'نسخة أخرى'

def main(index, out):
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    link = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn)):
            d = json.loads(l)
            for x in d.get('links') or []:
                m = re.search(r'archive\.org/download/([^/]+)/(.+?)\s*$', x.get('url', ''))
                if m: link[(m.group(1), m.group(2))] = x['title'].strip()
    files = defaultdict(list); size = {}
    for p, s in csv.reader(open(index), delimiter='\t'):
        if p.startswith('فهارس الويب/') or p.count('/') != 2: continue
        files[p.rsplit('/', 1)[0]].append(p.rsplit('/', 1)[1]); size[p] = int(s)
    moves, review, stats = [], [], Counter()
    for folder, names in sorted(files.items()):
        nums = Counter(m.group(1) for n in names for m in [re.match(r'^(\d+) - ', n)] if m)
        if not (len(names) >= 3 and nums.get('01', 0) >= 0.6 * len(names)): continue
        sec, fname = folder.split('/', 1)
        title, author, _ = split_folder(fname)
        title = clean(re.sub(r'\s+-\s+صفحة تجميعية$', '', title))
        br = {n: (m.group(1) if (m := re.match(r'^\d+ - .*?\((.+)\)(?:\s*\([أبجد]\))?(?:_alt)?\.pdf$', n)) else '') for n in names}
        plan = {}; rule = ''
        sz = lambda n: size.get(f'{folder}/{n}', 0)
        short = clean(short_title(title, author))
        full = {}
        for n in names:
            r = prov.get(f'{folder}/{n}', {})
            if r.get('match', 'none') != 'none':
                lab = re.sub(r'^تحميل\s+', '', link.get((r.get('archive_id'), r.get('orig_name')), ''))
                if lab and lab not in ('الكتاب', 'الواجهة', 'تحميل'): full[n] = clean(lab.replace(':', ' -'))
        ords0 = {}
        for n in names:
            r = prov.get(f'{folder}/{n}', {})
            lab = link.get((r.get('archive_id'), r.get('orig_name')), '') if r.get('match', 'none') != 'none' else ''
            o = first_ordinal(lab.split(':')[0]) if lab else None
            if o: ords0[n] = (o, clean(lab.split(':', 1)[1]) if ':' in lab else '')
        r4 = len(ords0) >= 0.6 * len(names) and len({v[0] for v in ords0.values()}) == len(ords0)
        if r4:
            w = max(2, len(str(max(v[0] for v in ords0.values()))))
            for n, (k, lab) in ords0.items():
                plan[n] = f'{str(k).zfill(w)} - {short}' + (f' ({fit(lab, 90)})' if lab else '') + '.pdf'
            for n in names:
                if n not in plan and re.search(r'\((?:المقدمة|الواجهة|مقدمة[^)]*)\)', n): plan[n] = f'00 - {short} (المقدمة).pdf'
            rule = 'R4 ordinal volumes'
        # 1. real volumes beyond 01 exist -> only the extra "01" files are fixed
        elif any(k not in ('00', '01') for k in nums):
            ones = sorted([n for n in names if n.startswith('01 - ')], key=sz, reverse=True)
            for n in ones[1:]:
                if re.search(r'\((?:المقدمة|مقدمة[^)]*)\)', n): continue          # the preface of volume 1: allowed
                if sz(n) < 1.5 * 2**20: plan[n] = f'00 - {short} ({fit(full.get(n, "الواجهة"), 90)}).pdf'
                else: review.append((f'{folder}/{n}', 'second large "01" in a multi-volume book')); stats['review'] += 1
            rule = 'M cover numbered 01'
        else:
            # 2. ordinal volumes from Waqfeya labels
            ords = {}
            for n in names:
                r = prov.get(f'{folder}/{n}', {})
                lab = link.get((r.get('archive_id'), r.get('orig_name')), '') if r.get('match', 'none') != 'none' else ''
                o = first_ordinal(lab.split(':')[0]) if lab else None
                if o: ords[n] = (o, clean(lab.split(':', 1)[1]) if ':' in lab else '')
            inner = {}
            for n, b in br.items():
                m = re.search(r'(?:^|- )(\d{1,3}) - ([^\d].+)$', b) or re.match(r'^(\d{1,3}) \(نسخة للشاملة من\s*-?\s*(.+?)\)*$', b)
                if m and len(re.findall(r'[\u0621-\u064A]', m.group(2))) >= 4 and int(m.group(1)) <= 3 * len(names):
                    inner[n] = (int(m.group(1)), clean(m.group(2).rstrip(')')), 'نسخة للشاملة' in b)
            if len(ords) >= 0.6 * len(names) and len({v[0] for v in ords.values()}) == len(ords):
                w = max(2, len(str(max(v[0] for v in ords.values()))))
                for n, (k, lab) in ords.items():
                    plan[n] = f'{str(k).zfill(w)} - {short}' + (f' ({fit(lab, 90)})' if lab else '') + '.pdf'
                rule = 'R4 ordinal volumes'
            elif len(inner) >= 0.6 * len(names) and len({v[0] for v in inner.values()}) == len(inner):
                w = max(2, len(str(max(v[0] for v in inner.values()))))
                for n, (k, t, sh) in inner.items():
                    plan[n] = f'{str(k).zfill(w)} - {t}' + (' (نسخة الشاملة)' if sh else '') + '.pdf'
                rule = 'R3 inner number'
            else:
                ranked = sorted(names, key=sz, reverse=True)
                main_, second = ranked[0], (ranked[1] if len(ranked) > 1 else None)
                lab = lambda n: (full[n] if n in full else companion_label(br[n]) if br[n] else ('نسخة أخرى' if 'alt' in n else ''))
                if second is None or sz(second) < 0.5 * sz(main_) or COMPANION.search(br[second] or second):
                    plan[main_] = f'{fit(title, 180)}' + (f' ({fit(lab(main_), 70)})' if br[main_] and not COMPANION.search(br[main_]) else '') + '.pdf'
                    for n in ranked[1:]: plan[n] = f'{fit(title, 150)} ({fit(lab(n) or "ملحق", 70)}).pdf'
                    rule = 'R1 book + companions'
                else:                                                   # several significant files: keep the title, label each
                    for n in names: plan[n] = f'{fit(title, 150)}' + (f' ({fit(lab(n), 80)})' if lab(n) else '') + '.pdf'
                    rule = 'R5 labelled parts'
        final = {n: plan.get(n, n) for n in names}
        if len(set(final.values())) < len(final):
            seen = Counter()
            for n in sorted(final):
                v = final[n]; seen[v] += 1
                if seen[v] > 1: final[n] = v[:-4] + f' ({seen[v]}).pdf'
        for n, new in final.items():
            if new != n: moves.append((f'Books/{folder}/{n}', f'Books/{folder}/{new}', f'numbering: {rule}')); stats[rule] += 1
    with open(out, 'w') as w:
        for a, b, r in moves: w.write(f'{a}\t{b}\t{r}\n')
    with open(J('data/phone/numbering-review.tsv'), 'a') as w:
        for x, why in review: w.write(f'{x}\t{why}\n')
    print(dict(stats), '| moves:', len(moves))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

"""One-off (2026-10-18, owner «أجر فحصا عميقا لأجل أي تحسينات أخرى وإصلاحات»): every phone path in index-now.tsv against
AGENTS.md §4 as it stands today + misplaced hamzas (الإقتضاب) checked against the spellings of the local Shamela's titles.
Writes data/review/deep-check-2026-10-18.tsv (issue, path) and prints the counts."""
import csv, os, re, collections, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
SPECIAL = ('فهارس الويب', 'نسخ محسنة للاستبدال', 'نسخ مستبعدة')
cats = {l.rstrip('\r\n').split('\t')[1].strip() for l in open(J('data/mappings/shamela-to-phone.tsv'), encoding='utf-8') if l.strip() and not l.startswith('#')}
rows = [(N(p), int(s)) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')]
issues = collections.defaultdict(list)
folders = collections.defaultdict(list)
for p, s in rows:
    parts = p.split('/')
    if parts[0] in SPECIAL: continue
    name = parts[-1]
    if parts[0] not in cats: issues['category not one of the 40'].append(p)
    if len(parts) >= 3: folders['/'.join(parts[:-1])].append(name)
    for x in parts:
        if len(x.encode()) > 240: issues['name > 240 bytes'].append(p); break
    if any(re.search(r'[\\:*?"<>|]|  |^ | $|^\.|\.$|_alt|نسخة ثانية', x) for x in parts): issues['forbidden char / space / dot'].append(p)
    if any(re.search(r'[()]', x) for x in parts): issues['parentheses (owner: none)'].append(p)
    if any(re.search(r'[،,]', x) for x in parts): issues['comma (owner: none)'].append(p)
    if any(re.search(r'(^|[ (])ط ?\d', x) for x in parts): issues['«ط» before a number (owner: no «ط»)'].append(p)
    if re.match(r'^\d+_[^/]*\.pdf$', name, re.I): issues['raw archive name'].append(p)
    if not name.lower().endswith('.pdf'): issues['not .pdf'].append(p)
    if s < 20480: issues['< 20 KB'].append(p)
    if re.search(r'(^| )99 - ', name): issues['99 for indexes'].append(p)
    if re.search(r'تحميل|اونلاين|pdf ', name): issues['uploader words in the name'].append(p)
for f, names in folders.items():
    nums = [m.group(1) for n in names if (m := re.match(r'^(\d+) - ', n))]
    if len(names) == 1 and f.count('/') == 1 and not re.match(r'^(مجلة|سلسلة|مؤلفات) ', f.split('/')[1]): issues['folder with one file (§4: a plain file)'].append(f)
    dup = [k for k, c in collections.Counter(nums).items() if c > 1 and k.strip('0') != '']
    if dup: issues['volume number repeated'].append(f + '  ← ' + ','.join(sorted(dup)[:5]))
# misplaced hamza: «الإ…» / «إ…» words whose Shamela spelling is with a plain alif (hamzat al-wasl), and the reverse is not
words = collections.Counter()
for p, _ in rows:
    if p.split('/')[0] in SPECIAL: continue
    for w in re.findall(r'[ء-ي]+', p): words[w] += 1
sham = collections.Counter()
for l in open(J('data/shamela/books.tsv'), encoding='utf-8'):
    for w in re.findall(r'[ء-ي]+', N(l)): sham[w] += 1
bad = {}
for w in words:
    for pre in ('الإ', 'والإ', 'بالإ', 'إ'):
        if w.startswith(pre) and len(w) >= len(pre) + 4:
            alt = w[:len(pre) - 1] + 'ا' + w[len(pre):]
            if sham[alt] >= 2 and sham[w] == 0: bad[w] = alt
for p, _ in rows:
    if p.split('/')[0] in SPECIAL: continue
    hit = [w for w in re.findall(r'[ء-ي]+', p) if w in bad]
    if hit: issues['hamza on a hamzat al-wasl: ' + ' / '.join(f'{w}→{bad[w]}' for w in sorted(set(hit)))].append(p)
os.makedirs(J('data/review'), exist_ok=True)
with open(J('data/review/deep-check-2026-10-18.tsv'), 'w', encoding='utf-8') as w:
    for k, v in sorted(issues.items(), key=lambda kv: -len(kv[1])):
        for p in v: w.write(f'{k}\t{p}\n')
agg = collections.Counter()
for k, v in issues.items(): agg[k.split(':')[0] if k.startswith('hamza') else k] += len(v)
for k, c in agg.most_common(): print(f'{c:6d}  {k}')
print('hamza words:', ', '.join(f'{w}→{a}' for w, a in sorted(bad.items())[:40]))

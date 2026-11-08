"""Name audit against AGENTS.md §4 as it stands (rewritten 2026-10-18 from the owner's deep check: the old one still held
the 200-byte limit and flagged single files in a category). Every phone path in an index:
  category not one of the 40 · name > 240 bytes · forbidden characters, double/edge spaces or dots, «_alt», «نسخة ثانية» ·
  parentheses · commas · «ط» before a number (the owner: none of the three) · raw archive names («NN_<id>.pdf»,
  «trm01.pdf») · the uploader's words («تحميل», «اونلاين», «pdf» inside a name) · not .pdf · < 20 KB · indexes numbered 99 ·
  a folder holding one file (§4: a plain file) · a volume number used by two plain volumes · a hamza written on a hamzat
  al-wasl («الإقتضاب»: the word's plain-alif form is in the local Shamela's titles, the hamza form never is).
Usage: python3 scripts/name_audit.py index.tsv [--list]   → data/phone/name-audit.tsv (issue, path, bytes)"""
import collections, csv, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from special_dirs import NOT_BOOKS
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
AR = re.compile(r'[ء-ي]+')
FRONT = re.compile(r'المقدمة|الواجهة|الفهارس|ملحق|صور المخطوط|مقدمة|تقديم')
# the verbal nouns of patterns VII, VIII and X (انفعال، افتعال، استفعال, and افتعال after ص ض ط / ز: اصطلاح، ازدياد) always
# begin with a hamzat al-wasl — «الإعتكاف», «الإرتياب», «للإقتداء» are errors whatever Shamela's titles hold (2026-10-19:
# 53 paths the Shamela-based check above had missed); pattern IV (إفعال: إتقان، إنفاق، إنتاج) does not match
_C = r'[^\sاأإآ]'
WASL = re.compile(r'(?<![ء-ي])(?:ال|وال|بال|فال|كال|لل|و|ف|ب)?إ(?:ست' + _C + _C + r'ا|' + _C + r'ت' + _C + r'ا|ن' + _C + _C
                  + r'ا|[صضط]ط' + _C + r'ا|زد' + _C + r'ا)')
PRESENTATION = re.compile(r'[ﭐ-﷿ﹰ-﻿]')     # copied from a PDF's text: not found by search, sorts apart

def audit(index):
    cats = {l.rstrip('\r\n').split('\t')[1].strip() for l in open(J('data/mappings/shamela-to-phone.tsv'), encoding='utf-8')
            if l.strip() and not l.startswith('#')}
    rows = [(N(p), int(s)) for p, s in csv.reader(open(index, encoding='utf-8'), delimiter='\t')]
    rows = [(p, s) for p, s in rows if p.split('/')[0] not in NOT_BOOKS]
    res, folders = collections.defaultdict(list), collections.defaultdict(list)
    for p, s in rows:
        parts = p.split('/'); n = parts[-1]
        add = lambda k: res[k].append((p, s))
        if parts[0] not in cats: add('category not one of the 40')
        if len(parts) >= 3: folders['/'.join(parts[:-1])].append((n, s))
        if any(len(x.encode()) > 240 for x in parts): add('name > 240 bytes')
        if any(re.search(r'[\\:*?"<>|]|  |^ | $|^\.|\.$|_alt|نسخة ثانية', x) for x in parts): add('forbidden chars/spaces/dots/_alt')
        if any('(' in x or ')' in x for x in parts): add('parentheses')
        if any(re.search(r'[،,]', x) for x in parts): add('comma')
        if any(re.search(r'(^|[ (])ط ?\d', x) for x in parts): add('«ط» before a number')
        if re.match(r'^(\d+_[^/]*|[A-Za-z][A-Za-z_-]*?\d{1,3}[a-z]?)\.pdf$', n, re.I): add('raw archive name')
        if re.search(r'تحميل|اونلاين|pdf ', n): add('uploader words')
        if not n.lower().endswith('.pdf'): add('not .pdf')
        if s < 20480: add('< 20 KB')
        if re.search(r'(^| )99 - ', n): add('indexes numbered 99')
    for f, files in folders.items():
        if len(files) == 1 and f.count('/') == 1 and not re.match(r'^(مجلة|سلسلة|مؤلفات) ', f.split('/')[1]):
            res['folder holding one file'].append((f + '/' + files[0][0], files[0][1]))
        by = collections.defaultdict(list)
        for n, s in files:
            m = re.match(r'^(\d+) - ', n)
            if m and m.group(1).strip('0') and not FRONT.search(n): by[m.group(1)].append((n, s))
        for k, v in by.items():
            if len(v) > 1: res['volume number used twice'] += [(f + '/' + n, s) for n, s in v]
    words = collections.Counter(w for p, _ in rows for w in AR.findall(p))
    sham = collections.Counter(w for l in open(J('data/shamela/books.tsv'), encoding='utf-8') for w in AR.findall(N(l)))
    bad = {}
    for w in words:
        for pre in ('الإ', 'والإ', 'بالإ', 'إ'):
            if w.startswith(pre) and len(w) >= len(pre) + 4:
                alt = w[:len(pre) - 1] + 'ا' + w[len(pre):]
                if sham[alt] >= 2 and sham[w] == 0: bad[w] = alt
    for p, s in rows:
        if any(w in bad for w in AR.findall(p)) or WASL.search(p): res['hamza on a hamzat al-wasl'].append((p, s))
        if PRESENTATION.search(p): res['Arabic presentation forms (ﺟﻬﺎﺩ for جهاد)'].append((p, s))
    return res, bad

if __name__ == '__main__':
    r, bad = audit(sys.argv[1])
    with open(J('data/phone/name-audit.tsv'), 'w', encoding='utf-8') as w:
        for k, v in sorted(r.items(), key=lambda kv: -len(kv[1])):
            print(f'{len(v):6d}  {k}')
            for p, s in v:
                w.write(f'{k}\t{p}\t{s}\n')
                if '--list' in sys.argv: print('        ', p, s)
    if bad: print('hamza words:', ', '.join(f'{a}→{b}' for a, b in sorted(bad.items())))

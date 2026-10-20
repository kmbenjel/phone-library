"""One-off audit (owner 2026-10-20: «لا يمكن أن تكون الجملة مقصوصة هكذا أبدا» … «انطلق»): names whose title is a truncation
of the book's full title (its reading, or the Waqfeya record of that very file) at a point the composer would never cut
(name_compose.cuts) — «أوضح المسالك إلى ألفية», «الصحاح تاج اللغة وصحاح». Prints path, current title, full title."""
import csv, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT); sys.path.insert(0, 'scripts')
from textnorm import norm
from name_compose import cuts, tidy, split_title
N = lambda s: unicodedata.normalize('NFC', s)
idx = [l.split('\t')[0] for l in open('data/phone/index-now.tsv', encoding='utf-8')]
mv = {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move': mv[N(r[2].removeprefix('Books/'))] = N(r[3].removeprefix('Books/'))
def cur(p):
    p = N(p); s = 0
    while p in mv and s < 60: p = mv[p]; s += 1
    return p
full = {}                                           # current path → full title
for r in csv.DictReader(open('data/phone/provenance.tsv', encoding='utf-8'), delimiter='\t'):
    w = (r.get('waqfeya_name') or '').strip()
    if w: full[cur(r['path'])] = re.split(r'\s+-\s+(?:ط\.|ت:|ت\s|طبعة)', w)[0].strip()
sheet = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open('data/names/sheets/books.tsv', encoding='utf-8')}
for r in csv.DictReader(open('data/names/title-read.tsv', encoding='utf-8'), delimiter='\t'):
    if r['n'] in sheet and r.get('title') and r['verdict'] in ('ok', 'other-book', 'other-edition'):
        full[cur(sheet[r['n']][2])] = r['title']
BOUND = re.compile(r'\s+-\s*|\s*\(|\s*=\s*|\s*،\s*|\s*:\s*|\s+(?:ويليه|ويليها|ويليهما|ومعه|ومعها|وبهامشه|وبذيله|وذيله|المسمى|المسماة|الموسوم|المعروف|وهو|وهي|أو)\s+')
def allowed_cut(F, nt):
    F = tidy(F); ok = set()
    for m in BOUND.finditer(F):                     # every boundary of the full title: a whole part ends there
        ok.add(norm(F[:m.start()]))
    parts = BOUND.split(F)
    pre = ''
    for i, part in enumerate(parts):                # inside each part, the composer's own cut points
        if not part: continue
        for c in cuts(part) + [part]:
            ok.add(norm((pre + ' ' + c).strip()))
        pre = (pre + ' ' + part).strip()
    return nt in ok

def title_of(seg):
    name = re.sub(r'\.pdf$', '', seg); name = re.sub(r'^\d+(?:-\d+)? - ', '', name)
    return re.split(r' - | \(', name)[0].strip()
seen = set()
for p in idx:
    P = N(p); F = full.get(P)
    if not F: continue
    segs = P.split('/')[1:]
    for seg in segs[-1:] + (segs[:-1] if len(segs) > 1 else []):
        T = title_of(seg)
        nt, nf = norm(T), norm(tidy(F))
        if len(nt) < 6 or not nf.startswith(nt) or len(nf) <= len(nt) + 1: continue
        if nf[len(nt)] != ' ' and not nf[len(nt):].startswith(' '): continue
        if allowed_cut(F, nt): continue
        key = (seg if seg == segs[-1] else '/'.join(P.split('/')[:segs.index(seg) + 2]))
        if key in seen: continue
        seen.add(key)
        print(f'{p}\t{T}\t{F}')
        break

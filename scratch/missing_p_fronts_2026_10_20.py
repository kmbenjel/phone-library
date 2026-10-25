"""One-off (owner 2026-10-20, doubts-001 rows 1–3: «لا بد أن يكون هناك غلاف»): the «…p.pdf» front parts (title page,
introduction) that an archive.org item holds beside a volume the phone has, but that never reached the phone. Downloads
them to argv[1], records per file: its item, size, pages, the set's current folder (provenance path followed through the
change log) and the fronts already in that folder → argv[1]/list.json for the eye check."""
import csv, json, os, re, subprocess, sys, unicodedata, urllib.parse, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
N = lambda s: unicodedata.normalize('NFC', s)
items = {}
for l in open('data/archive/files.jsonl'):
    d = json.loads(l); items[d['id']] = d.get('files') or []
mv = {}
for r in csv.reader(open('data/changes/changes.tsv', encoding='utf-8'), delimiter='\t'):
    if len(r) > 3 and r[1] == 'move': mv[N(r[2].removeprefix('Books/'))] = N(r[3].removeprefix('Books/'))
def cur(p):
    p = N(p); s = 0
    while p in mv and s < 60: p = mv[p]; s += 1
    return p
idx = {N(l.split('\t')[0]): int(l.split('\t')[1]) for l in open('data/phone/index-now.tsv', encoding='utf-8')}
sizes = set(idx.values())
have = collections.defaultdict(dict)
for r in csv.DictReader(open('data/phone/provenance.tsv', encoding='utf-8'), delimiter='\t'):
    if r.get('archive_id'): have[r['archive_id']][r['orig_name']] = r['path']
out = []
for aid, hv in have.items():
    for f in items.get(aid, []):
        n = f['name']
        if not re.search(r'p\.pdf$', n) or n.endswith('_text.pdf') or n in hv or (n[:-5] + '.pdf') not in hv: continue
        if int(f.get('size') or 0) in sizes: continue
        base = cur(hv[n[:-5] + '.pdf'])
        folder = os.path.dirname(base) if base.count('/') >= 2 else ''
        sibs = sorted(p for p in idx if folder and p.startswith(folder + '/') and p.count('/') == base.count('/'))
        dst = os.path.join(OUT, f'{aid}__{n}')
        if not os.path.exists(dst):
            subprocess.run(['aria2c', '-q', '-x4', '-s4', '--max-overall-download-limit=2M', '-d', OUT, '-o', os.path.basename(dst),
                            f'https://archive.org/download/{aid}/{urllib.parse.quote(n)}'], check=False)
        pages = subprocess.run(['pdfinfo', dst], capture_output=True, text=True).stdout
        m = re.search(r'Pages:\s+(\d+)', pages)
        out.append({'item': aid, 'file': n, 'size': int(f['size']), 'pages': int(m.group(1)) if m else None, 'local': dst,
                    'volume': base, 'in_index': base in idx, 'folder': folder, 'siblings': sibs})
json.dump(out, open(os.path.join(OUT, 'list.json'), 'w'), ensure_ascii=False, indent=1)
print(len(out), 'fronts;', sum(1 for o in out if o['pages']), 'downloaded;', sum(1 for o in out if not o['in_index']), 'volume path not found')

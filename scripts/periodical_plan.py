"""Periodicals: name files by the issues they contain and find missing issues in the source item(s).

For a periodical folder: every file's issue range comes from its name ("أعداد 26-51") or its archive.org source
name; the file is renamed "الأعداد 0026-0051 (السنة 2 - النصف الأول).pdf" so files sort by issue number and no
number repeats. Source files of the same archive.org item(s) that are not on the phone (by exact size) are listed
as missing, with their size, for download.
Usage: python3 scripts/periodical_plan.py index.tsv "<section>/<periodical folder>" plans/NNN.tsv"""
import csv, glob, json, os, re, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
AR_ORD = {1: 'الأول', 2: 'الثاني'}

def issue_range(text):
    t = text.replace('–', '-')
    m = re.search(r'(?:أعداد|الأعداد|العدد|عدد)\s*(\d{1,4})\s*-\s*(\d{1,4})', t) or re.search(r'(?<!\d)(\d{1,4})\s*-\s*(\d{1,4})(?!\d)', t)
    if m and int(m.group(1)) <= int(m.group(2)): return int(m.group(1)), int(m.group(2))
    m = re.search(r'(?:العدد|عدد)\s*(\d{1,4})', t)
    return (int(m.group(1)), int(m.group(1))) if m else None

def main(index, folder, out):
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv')), delimiter='\t')}
    here = [(p, int(s)) for p, s in csv.reader(open(index), delimiter='\t') if p.startswith(folder + '/')]
    items = {}
    for fn in ['data/archive/items.jsonl'] + glob.glob(J('data/archive/files*.jsonl')):
        for l in open(fn):
            d = json.loads(l)
            if not d.get('error'): items[d['id']] = d
    ids = sorted({prov[p]['archive_id'] for p, s in here if p in prov and prov[p]['archive_id']})
    print('files on phone:', len(here), '| source items:', ids)
    rows, unknown = [], []
    for p, s in sorted(here):
        n = p.rsplit('/', 1)[1]; r = prov.get(p, {})
        rng = issue_range(n) or issue_range(r.get('orig_name', ''))
        year = re.match(r'^(\d+) - ', n); half = re.search(r'نصف\s*(\d)', n)
        rows.append({'path': p, 'size': s, 'range': rng, 'year': int(year.group(1)) if year else None,
                     'half': int(half.group(1)) if half else None, 'orig': r.get('orig_name', ''), 'item': r.get('archive_id', '')})
    for x in rows:
        print(f"  {x['path'].rsplit('/', 1)[1][:58]:60s} {x['size']/2**20:7.1f}MB range={x['range']} year={x['year']} half={x['half']} src={x['orig'][:40]}")
    have = {s for p, s in here}
    missing = []
    for i in ids:
        for f in items.get(i, {}).get('files', []):
            if f['name'].lower().endswith('.pdf') and not f['name'].lower().endswith('_text.pdf') and f['size'] not in have:
                missing.append({'item': i, 'name': f['name'], 'size': f['size'], 'range': issue_range(f['name'])})
    print('source files not on phone:', len(missing), '| %.0f MB' % (sum(m['size'] for m in missing) / 2**20))
    for m in sorted(missing, key=lambda m: (m['range'] or (99999,))[0]): print(f"   - {m['item']}/{m['name'][:70]}  {m['size']/2**20:.1f}MB range={m['range']}")
    json.dump({'rows': rows, 'missing': missing}, open(J('data/phone/periodical-' + re.sub(r'\W+', '_', folder.split('/')[-1]) + '.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)

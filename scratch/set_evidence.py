"""One-off helper: for a Waqfeya record, match its archive.org item files to phone files by exact size and print
phone path | source file | the record's label for that file. Usage: python3 scratch/set_evidence.py WAQFEYA_ID [...]"""
import json, csv, sys, urllib.request, collections
recs = {}
for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(fn, encoding='utf-8'):
        d = json.loads(l); recs[d['_id']] = d
by_size = collections.defaultdict(list)
for p, s in csv.reader(open('data/phone/index-now.tsv', encoding='utf-8'), delimiter='\t'):
    if s.isdigit(): by_size[int(s)].append(p)
for wid in sys.argv[1:]:
    d = recs[wid]
    labels = collections.defaultdict(list)
    for x in d['links']:
        labels[x['url'].strip().rsplit('/', 1)[-1]].append(x.get('title', '').strip())
    items = {x['url'].strip().split('/download/')[1].split('/')[0] for x in d['links'] if '/download/' in x.get('url', '')}
    print('##', d['name'], '| vols', d.get('numberOfVolumes'), '|', d.get('researcher'), '|', d.get('publisher'))
    for it in sorted(items):
        m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{it}', timeout=60))
        print('  item', it, 'dark' if m.get('is_dark') else '')
        for f in sorted(m.get('files', []), key=lambda f: f['name']):
            n = f['name']
            if not n.lower().endswith('.pdf') or n.endswith('_text.pdf'): continue
            ph = by_size.get(int(f['size']), [])
            print(f"   {n:24} {int(f['size']):>10} | {' / '.join(labels.get(n, ['—']))[:70]:70} | {ph[0] if ph else 'NOT ON PHONE'}")

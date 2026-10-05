"""One-off: Waqfeya records that link one file under two volume titles leave the second volume undownloaded.
For each such record (phone status complete/partial/other-copy): the PDFs of its archive.org item(s) that the record
does not link and whose exact size is not on the phone → candidates for a missing volume (read before adding)."""
import json, csv, urllib.request, collections, sys
dups = json.load(open(sys.argv[1]))
sizes = {int(s) for p, s in csv.reader(open('data/phone/index-now.tsv', encoding='utf-8'), delimiter='\t') if s.isdigit()}
recs = {}
for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(fn, encoding='utf-8'):
        d = json.loads(l); recs[d['_id']] = d
out = []
for wid, st, name, dl in dups:
    d = recs[wid]
    links = [x['url'].strip() for x in d['links'] if 'archive.org/download/' in x.get('url', '')]
    items = collections.Counter(u.split('/download/')[1].split('/')[0] for u in links)
    linked = {u.rsplit('/', 1)[1] for u in links}
    for it in items:
        try: m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{it}', timeout=60))
        except Exception as e: print('ERR', it, e); continue
        if m.get('is_dark') or not m.get('files'): print('dark', it, name); continue
        cand = [(f['name'], int(f['size'])) for f in m['files'] if f['name'].lower().endswith('.pdf') and not f['name'].endswith('_text.pdf')
                and f['name'] not in linked and int(f['size']) not in sizes]
        on_phone = sum(1 for f in m['files'] if f['name'].lower().endswith('.pdf') and int(f.get('size') or 0) in sizes)
        print(f'{name[:50]} | {it} | on phone {on_phone} | unlinked & absent: {cand}')
        out.append({'wid': wid, 'name': name, 'item': it, 'cand': cand, 'dup': dl})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)

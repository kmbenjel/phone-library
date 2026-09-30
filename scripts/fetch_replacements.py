"""Download replacement PDFs from archive.org (via their Waqfeya records) and upload them to the phone.
Input: data/phone/downloads.json (from the replacement planning step). Each file: download -> check exact size + %PDF -> upload.
Every added file is logged in data/changes/changes.tsv (action 'add', with the source URL)."""
import csv, json, os, re, subprocess, sys, time, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import canonical_folder, vol_from_orig, clean, fit, short_title, author_short
from label_numbering_plan import parse
J = lambda p: os.path.join(ROOT, p)
books = {}
for fn in ('data/waqfeya/books.jsonl', 'data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
    for l in open(J(fn)):
        d = json.loads(l); books[d['_id']] = {**books.get(d['_id'], {}), **d}
link = {}
for b in books.values():
    for x in b.get('links') or []:
        m = re.search(r'archive\.org/download/([^/]+)/(.+?)\s*$', x.get('url', ''))
        if m: link[(m.group(1), urllib.parse.unquote(m.group(2)))] = x['title']
todo = json.load(open(J('data/phone/downloads.json')))
seen = set(); os.makedirs(J('downloads'), exist_ok=True)
log = csv.writer(open(J('data/changes/changes.tsv'), 'a', newline=''), delimiter='\t')
ok = bad = 0
for t in todo:
    wid = t['waqfeya_id']
    if wid in seen: continue
    seen.add(wid); b = books[wid]
    sec = t['folder'].split('/')[0]
    canon, title, a = canonical_folder(b)
    dest = t['folder'] if t['mode'] == 'missing volumes' else f'{sec}/{canon}'
    short = clean(short_title(title, a))
    files = sorted(t['download'], key=lambda f: f['name'])
    main_count = sum(1 for f in files if (vol_from_orig(f['name']) or (1, 'vol'))[1] == 'vol')
    for f in files:
        lab = link.get((f['item'], f['name']), '')
        pr = parse(lab) if lab else None
        v = vol_from_orig(f['name'])
        if main_count <= 1 and t['mode'] == 'whole book':
            name = fit(title, 180) + (' (الواجهة)' if v and v[1] == 'front' else '') + '.pdf'
        elif pr:
            text = pr[2] or ('الواجهة' if pr[1] == 'front' and not pr[0] else 'المقدمة' if pr[1] == 'front' else '')
            name = f'{pr[0]:02d} - {short}' + (f' ({fit(text, 90)})' if text else '') + '.pdf'
        elif v:
            name = f'{v[0]:02d} - {short}' + (' (الواجهة)' if v == (0, 'front') else ' (المقدمة)' if v[1] == 'front' else '') + '.pdf'
        else:
            name = f'{short} ({clean(re.sub(r"\.pdf$", "", f["name"], flags=re.I))}).pdf'
        url = f'https://archive.org/download/{urllib.parse.quote(f["item"])}/{urllib.parse.quote(f["name"])}'
        local = J(f'downloads/{f["item"]}__{re.sub(r"[^A-Za-z0-9._-]", "_", f["name"])}')
        if not (os.path.exists(local) and os.path.getsize(local) == f['size']):
            subprocess.run(['curl', '-sL', '--fail', '--retry', '3', '--max-time', '1800', '-A', 'personal-library/1.0', '-o', local, url])
        good = os.path.exists(local) and os.path.getsize(local) == f['size'] and open(local, 'rb').read(5) == b'%PDF-'
        if not good: print('BAD download', url); bad += 1; continue
        target = f'phone:Books/{dest}/{name}'
        r = subprocess.run(['rclone', 'copyto', local, target, '--inplace', '--ftp-concurrency', '1', '-q'], capture_output=True, text=True)
        if r.returncode: print('UPLOAD FAIL', target, r.stderr[-200:]); bad += 1; continue
        log.writerow([time.strftime('%F %T'), 'add', '', f'Books/{dest}/{name}', f'replacement from Waqfeya «{b["name"]}»: {url}', '021-replacements']); ok += 1
        print('added', dest.split('/', 1)[1][:50], '/', name[:60], flush=True)
print('uploaded:', ok, '| failed:', bad)

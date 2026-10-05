"""One-off: stage candidate copies of Jahili dawawin missing on the phone (al-Asad's list, 130), so each
file's title pages can be read before anything is named or uploaded. Writes downloads/stage-130/dawawin/<id>/<file> and
downloads/stage-130/dawawin/sheets/<n>.jpg (first 3 pages of each file, labelled)."""
import json, os, subprocess, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'downloads/stage-130/dawawin'); os.makedirs(OUT, exist_ok=True)
IDS = '''3496pdf_202001 AAlexandrina-158329 a2185n 4050pdf.1 4051pdf.2 20191018_20191018_0907 waqdwaween1 diwan-al-maraqash 3398pdf_202001
3903pdf_202001 DiwanOmyah AAlexandrina-111622 0406016000001 3397pdf_202001 3467pdf_202001 diwan-durayd-ibn-al-simma diwan-aswad 3283pdf_202001
20191019_20191019_1524 AAlexandrina-138625 diwan-amr-ibn-qamiat'''.split()
lines, manifest = [], []
for i in IDS:
    m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{i}', timeout=60))
    fs = [f for f in m.get('files', []) if f['name'].lower().endswith('.pdf') and not f['name'].lower().endswith('_text.pdf')]
    if i == 'waqdwaween1': fs = [f for f in fs if f['name'] == 'dairds.pdf']
    if len(fs) > 4: print('skip bundle', i, len(fs)); continue
    for f in fs:
        n = f['name']
        if True:
            url = f'https://archive.org/download/{i}/' + urllib.parse.quote(n)
            lines += [url, f'  dir={OUT}/{i}', f'  out={n}']
            manifest.append({'id': i, 'file': n, 'size': int(f.get('size') or 0), 'title': m['metadata'].get('title'), 'url': url})
open(os.path.join(OUT, 'aria.txt'), 'w').write('\n'.join(lines) + '\n')
json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
print(len(manifest), 'files', round(sum(x['size'] for x in manifest) / 1e6), 'MB')
subprocess.run(['aria2c', '-q', '-x8', '-s8', '-k1M', '-j12', '--continue=true', '--max-tries=5', '--retry-wait=10', '-i', os.path.join(OUT, 'aria.txt')])
bad = []
for x in manifest:
    p = os.path.join(OUT, x['id'], x['file'])
    if not os.path.exists(p) or os.path.getsize(p) != x['size']:
        r = subprocess.run(['curl', '-sfL', '--retry', '3', '-o', p, x['url']])
    x['ok'] = os.path.exists(p) and os.path.getsize(p) == x['size'] and open(p, 'rb').read(4) == b'%PDF'
    if not x['ok']: bad.append(x['id'] + '/' + x['file'])
json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
print('bad:', bad)

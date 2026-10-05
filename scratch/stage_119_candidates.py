"""One-off: stage curated archive.org copies of pre-700 Shamela books missing on the phone (119), so each
file's title pages can be read before anything is named or uploaded. Writes downloads/stage-119/<id>/<file> and
downloads/stage-119/sheets/<n>.jpg (first 3 pages of each file, labelled)."""
import json, os, subprocess, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'downloads/stage-119'); os.makedirs(OUT, exist_ok=True)
IDS = '''diwan-muawiya 3491pdf TheDiwanOfAbuDahbalAlGumahi ar107diwan88 ar102arab119 alfirdwsiy2018_gmail_3694 Pdf1389 4041pdf
bensaoud_gmail_20170731_1708 AAskZad-0184541 20260401_20260401_1010 20260223_20260223_0305 20230426 000234_201807 20240915_296
maadwalymn 4669pdf BBib-Alex-03521 fotouh-cham-waqidy 1983_20251202 1983_20251202_202512 20240301_20240301_1438 769Pdf
rain_bow2020_yahoo_20180824 elshandawily15098 so-alat-bn-chiba AhkamHabib 3546pdf_202001 20260606_20260606_1502 20220309_649
601Pdf_201812 asma2-moghtaline p.d.f4105 20260129_20260129_0333 20200613_20200613_0933 alfirdwsiy2018_gmail_3101 hm2410
ar118hist131 musnad-bilal-bin-rabah talib-al-ilm-0346c5c6-148a-4990-a5cf-61907ff88673 20201015_20201015_0234 alfirdwsiy2018_gmail_3770 hmmt00217
pdfarabic_109 20260124_20260124_0355 azm101010_gmail_20180426_1640 jarathim 4740pdf Zohd-abouHatem mfasaoy01 20260123_20260123_0414
alfirdwsiy2018_gmail_3768'''.split()
lines, manifest = [], []
for i in IDS:
    m = json.load(urllib.request.urlopen(f'https://archive.org/metadata/{i}', timeout=60))
    for f in m.get('files', []):
        n = f['name']
        if n.lower().endswith('.pdf') and not n.lower().endswith('_text.pdf'):
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

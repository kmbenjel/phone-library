"""One-off: stage the curated archive.org copies of pre-700 works whose Waqfeya items went dark (091), so each
file's title pages can be read before anything is named or uploaded. Writes downloads/stage-091/<id>/<file> and
downloads/stage-091/sheets/<n>.jpg (first 3 pages of each file, labelled)."""
import json, os, subprocess, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'downloads/stage-091'); os.makedirs(OUT, exist_ok=True)
IDS = '''osulsirakhsi Ghyathi spdf_1520 Heliopolis1957_gmail_392 QAHMAD_L_YAHOO_20170209 2910pdf_202001 ar102arab44
alfirdwsiy2018_gmail_0823_201808 timstims AAskZad-1107642 alfirdwsiy2018_gmail_3137 2692p.d.f2449 20260126_20260126_1024 Pdf2067
BBib-Alex-15859 1_20191212_20191212_0700 tafrigh_201804 ar103anda30 20200204_20200204_1424 Pdf3880552 hanafi_20160325_0217
fazael-hz-fatima olomnasb_ymail_20160923 AAskZad-0183725 Pdf2494 newselos 3816pdf 20260611_20260611_0215 alfirdwsiy2018_gmail_2679
20240425_20240425_1919 alfirdwsiy2018_gmail_3168 20230123_20230123_1139 Al_Zabb_Ann_Madhab_Malik Pdf1277 0999pdf_201912
20200130_20200130_1402 ar103anda163 nodrm alfirdwsiy2018_gmail_3184 20210728_20210728_1859 5227pdf634 20240317_20240317_2227
4099pdf 20250705_20250705_0126 Heliopolis1957_gmail_20180930_1213 3611pdf 20200129_20200129_0502 alfirdwsiy2018_gmail_1616
590Pdf sardar_202409 alfirdwsiy2018_gmail_0135 alfirdwsiy2018_gmail_0166_201808 20211210_20211210_1535'''.split()
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

"""Render the phone index: ONE self-contained HTML file (index + all reports as tabs), because Android browsers
(Brave, Chrome) do not follow links from a locally opened page to other local files.
Reports are embedded as inert text and shown in a frame (srcdoc) when their tab is tapped."""
import json, os, glob, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
os.makedirs(J('site'), exist_ok=True)
catalog = json.load(open(J('data/catalog.json'), encoding='utf-8'))
# edition card (scripts/edition_info.py): year, edition number, editor, publisher, pages, death year, description, sources
EI = J('data/editions/edition-info.json')
if os.path.exists(EI):
    info = json.load(open(EI, encoding='utf-8'))
    for b in catalog['books']:
        e = info.get(f"{b['cat']}/{b['folder']}")
        if e: b['ed'] = {k: [v['v'], v['s']] for k, v in e.items()}
# works contained in a book (scripts/contents.py): shown as «يضم», ✓ when the work is in Shamela (counted as present)
CF = J('data/editions/contents.json')
if os.path.exists(CF):
    inc = json.load(open(CF, encoding='utf-8'))
    for b in catalog['books']:
        it = inc.get(f"{b['cat']}/{b['folder']}")
        if it: b['inc'] = [[x['t'], x['a'], 1 if x['sh'] else 0] for x in it]
cat = json.dumps(catalog, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
reports, sources = [], []
WEB = os.environ.get('WEB') == '1'          # the online copy (benjelloun.dev/library): no change log (owner, 2026-10-05)
pages = [p for p in sorted(glob.glob(J('site/[0-9][0-9] - *.html'))) if not os.path.basename(p).startswith('00 ')]
if WEB: pages = [p for p in pages if 'سجل التغييرات' not in p]
# the old static «فهرس خزانة المنظومات العلمية» is replaced by report 06 (scripts/report_manzumat.py)
for i, p in enumerate(pages):
    title = os.path.basename(p)[5:-5] if os.path.basename(p)[:2].isdigit() else 'فهرس خزانة المنظومات العلمية'
    html = open(p, encoding='utf-8').read()
    html = re.sub(r'<div class="back">.*?</div>', '', html, count=1, flags=re.S)       # the old link back to another file
    html = html.replace('<head>', '<head><base target="_blank">', 1)
    reports.append({'title': title})
    sources.append(f'<script type="text/plain" id="src-r{i}">' + html.replace('</script', '<\\/script') + '</script>')
page = open(J('templates/index.html')).read().replace('__CATALOG__', cat).replace('__REPORTS__', json.dumps(reports, ensure_ascii=False)).replace('__REPORT_SOURCES__', '\n'.join(sources))
OUT = J('site-web/00 - الفهرس العام.html') if WEB else J('site/00 - الفهرس العام.html')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w').write(page)
print(os.path.relpath(OUT, ROOT), round(len(page.encode()) / 2**20, 2), 'MB, tabs:', ['الفهرس'] + [r['title'] for r in reports])

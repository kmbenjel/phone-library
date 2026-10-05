"""Render the phone index: ONE self-contained HTML file (index + all reports as tabs), because Android browsers
(Brave, Chrome) do not follow links from a locally opened page to other local files.
Reports are embedded as inert text and shown in a frame (srcdoc) when their tab is tapped."""
import json, os, glob, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
os.makedirs(J('site'), exist_ok=True)
cat = open(J('data/catalog.json')).read().replace('</', '<\\/')
reports, sources = [], []
pages = [p for p in sorted(glob.glob(J('site/[0-9][0-9] - *.html'))) if not os.path.basename(p).startswith('00 ')]
# the old static «فهرس خزانة المنظومات العلمية» is replaced by report 06 (scripts/report_manzumat.py)
for i, p in enumerate(pages):
    title = os.path.basename(p)[5:-5] if os.path.basename(p)[:2].isdigit() else 'فهرس خزانة المنظومات العلمية'
    html = open(p, encoding='utf-8').read()
    html = re.sub(r'<div class="back">.*?</div>', '', html, count=1, flags=re.S)       # the old link back to another file
    html = html.replace('<head>', '<head><base target="_blank">', 1)
    reports.append({'title': title})
    sources.append(f'<script type="text/plain" id="src-r{i}">' + html.replace('</script', '<\\/script') + '</script>')
page = open(J('templates/index.html')).read().replace('__CATALOG__', cat).replace('__REPORTS__', json.dumps(reports, ensure_ascii=False)).replace('__REPORT_SOURCES__', '\n'.join(sources))
open(J('site/00 - الفهرس العام.html'), 'w').write(page)
print('site/00 - الفهرس العام.html', round(len(page.encode()) / 2**20, 2), 'MB, tabs:', ['الفهرس'] + [r['title'] for r in reports])

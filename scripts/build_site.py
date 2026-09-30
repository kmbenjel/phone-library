"""Render site/ (HTML indexes + reports) from data/catalog.json and reports/*.html. Output goes to site/, then publish.py uploads it."""
import json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
os.makedirs(J('site'), exist_ok=True)
cat = open(J('data/catalog.json')).read().replace('</', '<\\/')
reports = [{'title': os.path.basename(p)[5:-5], 'href': os.path.basename(p)} for p in sorted(glob.glob(J('site/[0-9][0-9] - *.html'))) if not os.path.basename(p).startswith('00 ')]
reports.append({'title': 'فهرس خزانة المنظومات العلمية', 'href': 'فهرس خزانة المنظومات العلمية.html'})
html = open(J('templates/index.html')).read().replace('__CATALOG__', cat).replace('__REPORTS__', json.dumps(reports, ensure_ascii=False))
open(J('site/00 - الفهرس العام.html'), 'w').write(html)
print('site/00 - الفهرس العام.html', round(len(html.encode()) / 2**20, 2), 'MB')

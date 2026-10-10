"""Books whose name could not be read from the book itself (owner 2026-10-10: «when impossible to read by eye, report
in an html»). From data/names/title-read.tsv: verdict no-title-page / unreadable, or a note asking for a closer look
(«check», «not legible», «read the file», «read further», «dark cover», «read the inner title page»).
Each book: its current name, what was read, what is missing, and its first pages (small, embedded) → one self-contained
Arabic page site/names-unreadable.html (opened in Brave on the laptop).
Usage: python3 scripts/report_unreadable.py"""
import base64, csv, html, io, os, re
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
RETRY = re.compile(r'check|not legible|too faint|dark cover|read the inner|from a stylised|from a small print')
FILE = re.compile(r'read the file|read further|no title page|only a half-title|starts at f\.|begin at once|cover only')

def thumbs(key, n=3, h=300):
    out = []
    for pg in range(1, 5):
        p = J('data', 'inspect', 'pages', f'{key}-{pg}.jpg')
        if not os.path.exists(p) or len(out) >= n: continue
        try:
            im = Image.open(p).convert('L'); im = im.resize((max(1, im.width * h // im.height), h))
            b = io.BytesIO(); im.save(b, 'JPEG', quality=70)
            out.append('data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode())
        except OSError:
            pass
    return out

def main():
    keys = {l.split('\t')[0]: l.rstrip('\n').split('\t')[3] for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8')}
    rows = []
    for r in csv.DictReader(open(J('data', 'names', 'title-read.tsv'), encoding='utf-8'), delimiter='\t'):
        note = r.get('note') or ''
        if r['verdict'] in ('no-title-page', 'unreadable') or FILE.search(note): kind = 'file'
        elif RETRY.search(note): kind = 'retry'
        else: continue
        rows.append((kind, r))
    E = html.escape
    cards = []
    for kind, r in sorted(rows, key=lambda x: (x[0] != 'file', int(x[1]['n']))):
        imgs = ''.join(f'<img src="{s}" alt="">' for s in thumbs(keys.get(r['n'], '')))
        got = ' — '.join(x for x in (r['title'], r['author'], ('ت ' + r['editor']) if r['editor'] else '', r['publisher']) if x)
        tag = 'لا يجيب عنه ما بين يدي من صفحات' if kind == 'file' else 'سأعيد النظر بدقة أعلى'
        cards.append(f'''<article class="{kind}"><header><span class="n">{E(r["n"])}</span><span class="tag">{tag}</span></header>
<p class="cur">{E(r["book"])}</p><p><b>ما قُرئ:</b> {E(got) or '—'}</p><p><b>ما ينقص:</b> {E(r.get("note") or "")}</p>
<div class="pages">{imgs}</div></article>''')
    n_file = sum(1 for k, _ in rows if k == 'file'); n_retry = len(rows) - n_file
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>كتب تعذرت قراءتها</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--warn:#9a3412;--info:#1e4f8a}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--warn:#f0a070;--info:#8fb6e8}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--warn:#f0a070;--info:#8fb6e8}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:980px;margin:auto}} h1{{font-size:1.5rem;margin:.2em 0}} .lead{{color:var(--mut)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:14px 0}}
header{{display:flex;gap:10px;align-items:center}} .n{{font-weight:bold}} .tag{{font-size:.85rem;padding:1px 8px;border-radius:99px;border:1px solid currentColor}}
.file .tag{{color:var(--warn)}} .retry .tag{{color:var(--info)}} .cur{{color:var(--mut);margin:.3em 0}} p{{margin:.3em 0}}
.pages{{display:flex;gap:8px;overflow-x:auto;padding-top:6px}} .pages img{{height:300px;border:1px solid var(--line);border-radius:4px}}
</style></head><body><main><h1>كتب تعذرت قراءة اسمها من الكتاب نفسه</h1>
<p class="lead">من قراءة صفحات العنوان (data/names/title-read.tsv): {n_file} كتابا لا يجيب عنها ما بين يدي من صفحاتها الأولى (لا صفحة عنوان، مخطوط بلا عنوان…)، و{n_retry} كتابا سأعيد النظر فيها بدقة أعلى قبل الحكم. تُحدَّث هذه الصفحة كلما تقدمت القراءة.</p>
{''.join(cards)}</main></body></html>'''
    out = J('site', 'names-unreadable.html')
    open(out, 'w', encoding='utf-8').write(page)
    print(f'{len(rows)} books ({n_file} file, {n_retry} retry) → {out}')

if __name__ == '__main__':
    main()

"""Books whose name cannot be read from the book itself, reported ONE BY ONE as they are met (owner 2026-10-10: «when
impossible to read by eye, report in an html — one by one, appended, with a link to open a copy of it from here»).

  python3 scripts/report_unreadable.py copy N      → a local copy of reading-sheet book N in data/names/copies/ (the
                                                    laptop's own copy when its MD5 equals the phone file's, else fetched
                                                    from the phone under the shared lock); prints its path, so its
                                                    further pages can be read first (pdftoppm)
  python3 scripts/report_unreadable.py add N "why" → appends book N to data/names/unreadable.tsv (once) and rebuilds the
                                                    page site/names-unreadable.html: current name, what was read, why
                                                    it cannot be read, its first pages, a link to the local copy
  python3 scripts/report_unreadable.py              → rebuilds the page
The copies are not tracked by git (data/names/copies/ is ignored); the laptop library (~/Books) is only read."""
import base64, csv, hashlib, html, io, os, shutil, sys, time
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
J = lambda *p: os.path.join(ROOT, *p)
COPIES, LOG, OUT = J('data', 'names', 'copies'), J('data', 'names', 'unreadable.tsv'), J('site', 'names-unreadable.html')

def sheet_books():
    return {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8')}

def readings():
    return {r['n']: r for r in csv.DictReader(open(J('data', 'names', 'title-read.tsv'), encoding='utf-8'), delimiter='\t')}

def copy(n):
    from crop_batch import Phone, md5_file, LOCAL_MAP
    n_, book, path, key = sheet_books()[n]
    assert path, 'no file for book ' + n
    os.makedirs(COPIES, exist_ok=True)
    dst = os.path.join(COPIES, f'{n} - {os.path.basename(path)}')
    if os.path.exists(dst): return dst
    with Phone() as ph: want = ph.md5(path)
    local = dict(l.rstrip('\n').split('\t')[:2] for l in open(LOCAL_MAP, encoding='utf-8')) if os.path.exists(LOCAL_MAP) else {}
    lp = local.get(path)
    if lp and os.path.exists(lp) and md5_file(lp) == want:
        shutil.copyfile(lp, dst)                          # reading the laptop's copy; it is never changed
    else:
        with Phone() as ph: ph.get(path, dst + '.part')
        if md5_file(dst + '.part') != want: os.remove(dst + '.part'); raise SystemExit('download differs from the phone file')
        os.rename(dst + '.part', dst)
    return dst

def thumbs(key, n=3, h=300):
    out = []
    for pg in range(1, 6):
        p = J('data', 'inspect', 'pages', f'{key}-{pg}.jpg')
        if not os.path.exists(p) or len(out) >= n: continue
        try:
            im = Image.open(p).convert('L'); im = im.resize((max(1, im.width * h // im.height), h))
            b = io.BytesIO(); im.save(b, 'JPEG', quality=70)
            out.append('data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode())
        except OSError:
            pass
    return out

def add(n, why):
    rows = list(csv.reader(open(LOG, encoding='utf-8'), delimiter='\t')) if os.path.exists(LOG) else []
    if any(r and r[0] == n for r in rows): build(); return
    dst = copy(n)
    with open(LOG, 'a', encoding='utf-8', newline='') as w:
        csv.writer(w, delimiter='\t', lineterminator='\n').writerow([n, time.strftime('%F %T'), os.path.relpath(dst, ROOT), why])
    build()

def build():
    sb, rd = sheet_books(), readings()
    rows = list(csv.reader(open(LOG, encoding='utf-8'), delimiter='\t')) if os.path.exists(LOG) else []
    E, cards = html.escape, []
    for n, when, rel, why in rows:
        r, b = rd.get(n, {}), sb.get(n, ['', '', '', ''])
        got = ' — '.join(x for x in (r.get('title'), r.get('author'), ('ت ' + r['editor']) if r.get('editor') else '', r.get('publisher')) if x)
        link = '/copies/' + os.path.basename(rel)                   # served by scripts/review_server.py
        imgs = ''.join(f'<img src="{s}" alt="">' for s in thumbs(b[3]))
        cards.append(f'''<article><header><span class="n">{E(n)}</span><a class="open" href="{E(link)}" target="_blank">افتح نسخة من الكتاب</a>
<span class="when">{E(when)}</span></header><p class="cur">{E(b[1])}</p><p><b>ما قُرئ:</b> {E(got) or '—'}</p>
<p><b>لماذا تعذرت القراءة:</b> {E(why)}</p><div class="pages">{imgs}</div>
<div class="review" data-n="{E(n)}"><label><input type="checkbox" class="chk"> تم الفحص</label>
<textarea class="cmt" rows="2" placeholder="تعليقك: العنوان الصحيح، المؤلف، المحقق، الناشر، أو ما ينبغي فعله"></textarea><span class="st"></span></div></article>''')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>كتب تعذرت قراءتها</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--link:#1e4f8a}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--link:#8fb6e8}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--link:#8fb6e8}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:980px;margin:auto}} h1{{font-size:1.5rem;margin:.2em 0}} .lead,.cur,.when{{color:var(--mut)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:14px 0}}
header{{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}} .n{{font-weight:bold}} .open{{color:var(--link)}} .when{{font-size:.85rem;margin-inline-start:auto}}
p{{margin:.3em 0}} .review{{display:flex;gap:10px;align-items:flex-start;margin-top:8px;flex-wrap:wrap}}
.review textarea{{flex:1;min-width:240px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}}
.st{{font-size:.8rem;color:var(--mut)}} .warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}} .pages{{display:flex;gap:8px;overflow-x:auto;padding-top:6px}} .pages img{{height:300px;border:1px solid var(--line);border-radius:4px}}
</style></head><body><main><h1>كتب تعذرت قراءة اسمها من الكتاب نفسه</h1>
<p class="lead">تضاف الكتب واحدا واحدا أثناء القراءة، بعد محاولة قراءة صفحات أبعد بدقة كاملة. {len(rows)} كتابا حتى الآن.</p>
<p class="warn" id="noserver" hidden>لحفظ الفحص والتعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/ (scripts/review_server.py)</p>
{''.join(cards) or '<p>لا شيء بعد.</p>'}</main><script>
const R = 'unreadable';
const live = location.protocol.startsWith('http');
if (!live) document.getElementById('noserver').hidden = false;
async function load() {{
  if (!live) return;
  try {{ const d = await (await fetch('/api/comments?r=' + R)).json();
    document.querySelectorAll('.review').forEach(b => {{ const x = d[b.dataset.n]; if (!x) return;
      b.querySelector('.chk').checked = x.checked; b.querySelector('.cmt').value = x.comment; b.querySelector('.st').textContent = 'حُفظ ' + x.time; }});
  }} catch (e) {{ document.getElementById('noserver').hidden = false; }}
}}
function save(b) {{
  if (!live) return;
  const st = b.querySelector('.st'); st.textContent = '…';
  fetch('/api/comment', {{method: 'POST', headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{report: R, n: b.dataset.n, checked: b.querySelector('.chk').checked, comment: b.querySelector('.cmt').value}})}})
    .then(r => r.json()).then(j => st.textContent = 'حُفظ ' + j.time).catch(() => st.textContent = 'لم يُحفظ');
}}
document.querySelectorAll('.review').forEach(b => {{
  let t; b.querySelector('.chk').addEventListener('change', () => save(b));
  b.querySelector('.cmt').addEventListener('input', () => {{ clearTimeout(t); t = setTimeout(() => save(b), 800); }});
}});
load();
</script></body></html>'''
    open(OUT, 'w', encoding='utf-8').write(page)
    print(f'{len(rows)} books → {OUT}')

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'copy': print(copy(a[1]))
    elif a and a[0] == 'add': add(a[1], a[2] if len(a) > 2 else '')
    else: build()

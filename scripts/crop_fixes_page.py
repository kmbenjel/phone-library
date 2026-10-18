"""One review page for the corrected crop method (2026-10-18): every page the owner marked in crop-review-002/004 —
the scan, the old crop, the new crop (the latest test run: crop-minitest r4, else r3) — with his remark and the verdict.
Comments go to data/names/review-comments.jsonl (report «crop-fixes»). → site/crop-fixes.html (+ site/crop-fixes/)
Verdicts and rounds: data/crop/fixes-verdicts.tsv; a book the owner approved, or whose remark was settled, leaves the page
(data/names/review-closed.tsv, owner 2026-10-18); after a comment that needs work, the next round shows the new images
with his comment above and a fresh box (id «<hash>#<round>»). Images: the latest crop-minitest run that has the book.
Usage: python3 scripts/crop_fixes_page.py"""
import html, json, os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p); E = html.escape
S = os.path.expanduser('~/.cache/phone-library/crop-sheets'); M = os.path.expanduser('~/.cache/phone-library/crop-minitest')
def tsv(name, report=None):
    p = J(*name)
    if not os.path.exists(p): return []
    rows = [l.rstrip('\n').split('\t') for l in open(p, encoding='utf-8') if l.strip() and not l.startswith('#')][1:]
    return [r for r in rows if report is None or r[0] == report]
V = {r[0]: (r[1], r[3], int(r[2])) for r in tsv(('data', 'crop', 'fixes-verdicts.tsv'))}
CLOSED = {r[1] for r in tsv(('data', 'names', 'review-closed.tsv'), 'crop-fixes')}
SAID = {}                                              # the owner's latest comment per id
for l in open(J('data', 'names', 'review-comments.jsonl'), encoding='utf-8'):
    r = json.loads(l)
    if r.get('report') == 'crop-fixes': SAID[r['n']] = r.get('comment', '')
RUNS = sorted((d for d in os.listdir(M) if d[1:].isdigit()), key=lambda d: -int(d[1:])) if os.path.isdir(M) else []
STATE = {'ok': ('أُصلح', '#1b7f3b'), 'part': ('أُصلح جزئيا', '#9a6b00'), 'no': ('لم يُصلح بعد', '#b3261e')}
out = J('site', 'crop-fixes'); os.makedirs(out, exist_ok=True); cards = []; n_ok = 0
for l in open(J('data', 'crop', 'owner-marked-2026-10-14.tsv'), encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    h, rep, path, remark = l.rstrip('\n').split('\t')[:4]
    st, verdict, rnd = V.get(h, ('part', '', 1))
    rid = h if rnd == 1 else f'{h}#{rnd}'                # a new round after his comment: a fresh box, his words shown above
    if rid in CLOSED: continue
    run = next((r for r in RUNS if os.path.exists(os.path.join(M, r, h, 'map.json'))), None)
    mp = json.load(open(os.path.join(M, run, h, 'map.json')))['marked'] if run else {}
    figs = []
    for pg in sorted(mp, key=int):
        ims = []
        for lab, src in (('الجديد', os.path.join(M, run, h, f'p{mp[pg] + 1:04d}-after.jpg')), ('القديم', os.path.join(S, h, f'p{int(pg):04d}-after.jpg')),
                         ('المسح', os.path.join(S, h, f'p{int(pg):04d}-before.jpg'))):
            if not os.path.exists(src): continue
            dst = f'{h}-{pg}-{os.path.basename(src)[6:]}' if 'minitest' not in src else f'{h}-{pg}-new-{run}.jpg'
            shutil.copyfile(src, os.path.join(out, dst)); ims.append(f'<div><span>{lab}</span><img src="crop-fixes/{dst}" alt="{lab}" loading="lazy"></div>')
        figs.append(f'<figure><div class="trio">{"".join(ims)}</div><figcaption>ص {pg}</figcaption></figure>')
    n_ok += st == 'ok'; lbl, col = STATE[st]
    prev = SAID.get(h if rnd == 2 else f'{h}#{rnd - 1}', '') if rnd > 1 else ''
    cards.append(f'''<article><h2>{E(path)}</h2><p class="rm">ملاحظتك ({E(rep)}): «{E(remark)}»</p>
{f'<p class="rm">ملاحظتك على الصور السابقة: «{E(prev)}»</p>' if prev else ''}
<p class="vd"><b style="color:{col}">{lbl}</b> — {E(verdict)}</p>{"".join(figs)}
<div class="review" data-n="{E(rid)}"><label><input type="checkbox" class="chk"> تم الفحص</label>
<textarea class="cmt" rows="2" placeholder="ملاحظتك"></textarea><span class="st"></span></div></article>''')
page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>إصلاحات القص</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1300px;margin:auto}} h1{{font-size:1.5rem}} h2{{font-size:1.02rem;margin:.2em 0;word-break:break-word}} .lead,.rm,figcaption,.st{{color:var(--mut)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:16px 0}}
.trio{{display:flex;gap:14px;align-items:flex-end;overflow-x:auto}} .trio>div{{display:flex;flex-direction:column;align-items:center}}
.trio img{{height:460px;display:block;border:1px solid var(--line)}} .trio span{{font-weight:bold}}
.review{{display:flex;gap:10px;align-items:flex-start;margin-top:8px;flex-wrap:wrap}}
.review textarea{{flex:1;min-width:240px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}}
.warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>القص بعد التصحيح: الصفحات التي علّمتَ عليها</h1>
<p class="lead">لكل صفحة علّقتَ عليها في مراجعتي الدفعتين 002 و004: «الجديد» (الطريقة المصححة) ثم «القديم» ثم «المسح» الأصلي. {n_ok} من {len(cards)} كتابا معروضة هنا أُصلحت (وما وافقتَ عليه أو حُسم خرج من الصفحة)، والباقي مبيّن سببه. هذه الطريقة ستُعاد بها الكتب الـ1122 المقصوصة قديما بعد نجاح الاختبار الشامل؛ علّق على ما تراه، فيُصلح هو ومثيلاته قبل المضي أو أثناءه.</p>
<p class="warn" id="noserver" hidden>لحفظ التعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/crop-fixes.html</p>
{"".join(cards)}</main><script>
const R = 'crop-fixes', live = location.protocol.startsWith('http');
if (!live) document.getElementById('noserver').hidden = false;
async function load() {{ if (!live) return;
  try {{ const d = await (await fetch('/api/comments?r=' + R)).json();
    document.querySelectorAll('.review').forEach(b => {{ const x = d[b.dataset.n]; if (!x) return;
      b.querySelector('.chk').checked = x.checked; b.querySelector('.cmt').value = x.comment; b.querySelector('.st').textContent = 'حُفظ ' + x.time; }});
  }} catch (e) {{ document.getElementById('noserver').hidden = false; }} }}
function save(b) {{ if (!live) return; const st = b.querySelector('.st'); st.textContent = '…';
  fetch('/api/comment', {{method: 'POST', headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{report: R, n: b.dataset.n, checked: b.querySelector('.chk').checked, comment: b.querySelector('.cmt').value}})}})
    .then(r => r.json()).then(j => st.textContent = 'حُفظ ' + j.time).catch(() => st.textContent = 'لم يُحفظ'); }}
document.querySelectorAll('.review').forEach(b => {{ let t; b.querySelector('.chk').addEventListener('change', () => save(b));
  b.querySelector('.cmt').addEventListener('input', () => {{ clearTimeout(t); t = setTimeout(() => save(b), 800); }}); }});
load();
</script></body></html>'''
open(J('site', 'crop-fixes.html'), 'w', encoding='utf-8').write(page)
print(len(cards), 'books,', n_ok, 'fixed → site/crop-fixes.html')

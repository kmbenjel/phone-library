"""The files the agent is still unsure about, as one review page (owner 2026-10-20: «أرني ما بقي مشكلا في المتصفح وما أريد
فتحه في برايف أضع x»): a section per kind of doubt, per file its name, folder, why it is doubtful and its first pages;
a comment box per row — «x» opens the file in Brave (scripts/review_on_demand_x.py watches for it), anything else is a
comment for the agent (review_server.py → data/names/review-comments.jsonl, report = the list's name).
Input: data/review/<report>.tsv — optional «#T<TAB>page title<TAB>opening line» (Arabic; default «ما بقي مشكلا», «N ملفا»),
«#S<TAB>section id<TAB>section title (Arabic)» lines, then rows
«section id<TAB>phone path (relative to Books/)<TAB>why (Arabic)<TAB>page images (comma-separated paths)».
Rows closed after his comment (data/names/review-closed.tsv: report, row id) are not shown; they stay in the list, so the
later rows keep their numbers (his comments and the «x» watcher find a row by its number).
Usage: python3 scripts/doubts_page.py doubts-001   → site/doubts-001.html (+ site/doubts-001/ for the images)"""
import html, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(report):
    src = os.path.join(ROOT, 'data', 'review', f'{report}.tsv')
    sections, rows, head = {}, [], None
    for l in open(src, encoding='utf-8'):
        r = l.rstrip('\n').split('\t')
        if r[0] == '#S': sections[r[1]] = r[2]
        elif r[0] == '#T': head = (r + ['', ''])[1:3]
        elif r[0] and not r[0].startswith('#'): rows.append((r + ['', '', '', ''])[:4])
    cf = os.path.join(ROOT, 'data', 'names', 'review-closed.tsv')
    closed = {r[1] for r in (l.rstrip('\n').split('\t') for l in open(cf, encoding='utf-8')) if len(r) > 1 and r[0] == report} if os.path.exists(cf) else set()
    imgdir = os.path.join(ROOT, 'site', report)
    shutil.rmtree(imgdir, ignore_errors=True); os.makedirs(imgdir)
    E, out, last = html.escape, [], None
    for k, (sec, path, why, imgs) in enumerate(rows, 1):        # row ids = data line numbers, as review_on_demand_x reads them
        if str(k) in closed: continue                           # (a closed row still counts: the later rows keep their numbers)
        if sec != last:
            n = sum(r[0] == sec and str(i) not in closed for i, r in enumerate(rows, 1))
            out.append(f'<h2>{E(sections.get(sec, sec))} <span class="mut">({n})</span></h2>'); last = sec
        pics = []
        for i, p in enumerate([x for x in imgs.split(',') if x][:4], 1):
            dst = f'{k}-{i}{os.path.splitext(p)[1] or ".jpg"}'
            shutil.copyfile(os.path.join(ROOT, p) if not os.path.isabs(p) else p, os.path.join(imgdir, dst))
            pics.append(f'<a href="{E(report)}/{E(dst)}" target="_blank"><img loading="lazy" src="{E(report)}/{E(dst)}" alt=""></a>')   # (a click shows it full size)
        folder, name = os.path.split(path)
        out.append(f'''<article data-n="{k}"><div class="head"><span class="k">{k}</span><div><div class="name">{E(name)}</div>
<div class="mut">{E(folder)}</div><div class="why">{E(why)}</div></div></div>
<div class="pics">{"".join(pics) or '<span class="mut">لا صور محفوظة لهذا الملف — اكتب x لفتحه</span>'}</div>
<div class="review" data-n="{k}"><textarea class="cmt" rows="2" placeholder="x لفتحه في برايف، أو تعليقك"></textarea><span class="st"></span></div></article>''')
    title, intro = (head[0], head[1]) if head else ('ما بقي مشكلا', f'{sum(str(i) not in closed for i in range(1, len(rows) + 1))} ملفا.')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--acc:#9a3412}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--acc:#f0a070}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--acc:#f0a070}}
body{{background:var(--bg);color:var(--fg);font:16px/1.8 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1200px;margin:auto}} h1{{font-size:1.4rem}} h2{{font-size:1.15rem;margin-top:1.6em;border-bottom:2px solid var(--line)}}
.mut,.st,.k{{color:var(--mut)}} .k{{min-width:2.2em;font-weight:bold}} .name{{font-weight:bold;word-break:break-word}} .why{{color:var(--acc)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:12px 0}}
.head{{display:flex;gap:10px}} .pics{{display:flex;gap:6px;overflow-x:auto;margin:8px 0}} .pics img{{height:300px;border:1px solid var(--line);background:#fff}}
textarea{{width:100%;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px;box-sizing:border-box}}
.warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>{E(title)}</h1>
<p class="mut">{E(intro)} اكتب <b>x</b> في خانة أي ملف ليُفتح في برايف (يُجلب من الهاتف أولا، فانتظر لحظة)، أو اكتب ملاحظتك وأعمل بها.</p>
<p class="warn" id="noserver" hidden>لحفظ التعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/{E(report)}.html</p>
{"".join(out)}</main><script>
const R = '{report}', live = location.protocol.startsWith('http');
if (!live) document.getElementById('noserver').hidden = false;
async function load() {{ if (!live) return;
  try {{ const d = await (await fetch('/api/comments?r=' + R)).json();
    document.querySelectorAll('.review').forEach(b => {{ const x = d[b.dataset.n]; if (!x) return;
      b.querySelector('.cmt').value = x.comment; b.querySelector('.st').textContent = ' حُفظ ' + x.time; }});
  }} catch (e) {{ document.getElementById('noserver').hidden = false; }} }}
function save(b) {{ if (!live) return; const st = b.querySelector('.st'), t = b.querySelector('.cmt'); st.textContent = ' …';
  fetch('/api/comment', {{method: 'POST', headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{report: R, n: b.dataset.n, checked: false, comment: t.value}})}})
    .then(r => r.json()).then(j => st.textContent = ' حُفظ ' + j.time).catch(() => st.textContent = ' لم يُحفظ'); }}
document.querySelectorAll('.review').forEach(b => {{ let tm; const t = b.querySelector('.cmt');
  t.addEventListener('input', () => {{ clearTimeout(tm);
    if (t.value.trim().toLowerCase().startsWith('x')) save(b); else tm = setTimeout(() => save(b), 800); }}); }});
load();
</script></body></html>'''
    open(os.path.join(ROOT, 'site', f'{report}.html'), 'w', encoding='utf-8').write(page)
    print(f'{len(rows)} rows → site/{report}.html')

if __name__ == '__main__':
    main(sys.argv[1])

"""A rename/move plan as a review page (owner 2026-10-10: check and comment from the HTML): every row old → new, section
moves marked, a filter box, a comment per row and «I approve the plan» at the top (review_server.py; comments →
data/names/review-comments.jsonl, report «plan-NNN»; row ids = line numbers in the plan).
Usage: python3 scripts/plan_review_page.py plans/NNN-name.tsv   → site/plan-NNN.html"""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(plan):
    name = os.path.basename(plan).removesuffix('.tsv'); num = name.split('-')[0]
    rows = [l.rstrip('\n').split('\t') for l in open(plan, encoding='utf-8') if l.strip()]
    E, trs, moved = html.escape, [], 0
    for k, (a, b, why) in enumerate(rows, 1):
        ca, cb = a.split('/')[1], b.split('/')[1]
        oa, ob = a.split('/', 2)[2], b.split('/', 2)[2]
        sec = f'<span class="sec">{E(ca)} ← {E(cb)}</span>' if ca != cb else f'<span class="cat">{E(ca)}</span>'
        moved += ca != cb
        flag = ' other' if 'other-' in why else ''
        trs.append(f'''<tr class="row{' moved' if ca != cb else ''}{flag}" data-n="{k}"><td class="k">{k}</td><td>{sec}<div class="old">{E(oa)}</div>
<div class="new">{E(ob)}</div><div class="why">{E(why)}</div></td>
<td class="review" data-n="{k}"><textarea class="cmt" rows="2" placeholder="تعليق على هذا الصف"></textarea><span class="st"></span></td></tr>''')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>خطة {E(num)}</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--new:#14532d;--sec:#9a3412}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--new:#86efac;--sec:#f0a070}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--new:#86efac;--sec:#f0a070}}
body{{background:var(--bg);color:var(--fg);font:15px/1.6 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1300px;margin:auto}} h1{{font-size:1.4rem}} .lead,.why,.st,.k,.cat{{color:var(--mut)}}
table{{width:100%;border-collapse:collapse;background:var(--card)}} td{{border-top:1px solid var(--line);padding:8px;vertical-align:top}}
.old{{text-decoration:line-through;color:var(--mut)}} .new{{color:var(--new);font-weight:bold}} .sec{{color:var(--sec);font-weight:bold}}
.why{{font-size:.85rem;direction:ltr;text-align:right}} td.review{{width:28%}} textarea{{width:100%;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px}}
.bar{{position:sticky;top:0;background:var(--bg);padding:8px 0;display:flex;gap:14px;flex-wrap:wrap;align-items:center;z-index:1}}
input[type=search]{{font:inherit;padding:4px 8px;min-width:240px}} .warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>خطة {E(num)}: تسمية الكتب المفردة من صفحات عناوينها</h1>
<p class="lead">{len(rows)} كتابا؛ منها {moved} تنتقل إلى قسم آخر (بالبرتقالي). لم يُطبق شيء على الهاتف. علّق على أي صف، ثم علّم الموافقة إن رضيت بالباقي.</p>
<p class="warn" id="noserver" hidden>لحفظ التعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/plan-{E(num)}.html</p>
<div class="bar"><span class="review" data-n="approve"><label><input type="checkbox" class="chk"> أوافق على الخطة (مع ما علقت عليه)</label><span class="st"></span></span>
<input type="search" id="q" placeholder="تصفية: كلمة أو قسم"><label><input type="checkbox" id="onlymoved"> الأقسام المنقولة فقط</label>
<label><input type="checkbox" id="onlyother"> «كتاب آخر» فقط</label></div>
<table>{''.join(trs)}</table></main><script>
const R = 'plan-{num}', live = location.protocol.startsWith('http');
if (!live) document.getElementById('noserver').hidden = false;
async function load() {{ if (!live) return;
  try {{ const d = await (await fetch('/api/comments?r=' + R)).json();
    document.querySelectorAll('.review').forEach(b => {{ const x = d[b.dataset.n]; if (!x) return;
      const c = b.querySelector('.chk'); if (c) c.checked = x.checked; const t = b.querySelector('.cmt'); if (t) t.value = x.comment;
      b.querySelector('.st').textContent = ' حُفظ ' + x.time; }});
  }} catch (e) {{ document.getElementById('noserver').hidden = false; }} }}
function save(b) {{ if (!live) return; const st = b.querySelector('.st'); st.textContent = ' …';
  const c = b.querySelector('.chk'), t = b.querySelector('.cmt');
  fetch('/api/comment', {{method: 'POST', headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{report: R, n: b.dataset.n, checked: c ? c.checked : false, comment: t ? t.value : ''}})}})
    .then(r => r.json()).then(j => st.textContent = ' حُفظ ' + j.time).catch(() => st.textContent = ' لم يُحفظ'); }}
document.querySelectorAll('.review').forEach(b => {{ let tm; const c = b.querySelector('.chk'), t = b.querySelector('.cmt');
  if (c) c.addEventListener('change', () => save(b));
  if (t) t.addEventListener('input', () => {{ clearTimeout(tm); tm = setTimeout(() => save(b), 800); }}); }});
function filt() {{ const q = document.getElementById('q').value.trim(), m = document.getElementById('onlymoved').checked, o = document.getElementById('onlyother').checked;
  document.querySelectorAll('tr.row').forEach(r => {{ r.hidden = (q && !r.textContent.includes(q)) || (m && !r.classList.contains('moved')) || (o && !r.classList.contains('other')); }}); }}
['q', 'onlymoved', 'onlyother'].forEach(id => document.getElementById(id).addEventListener('input', filt));
load();
</script></body></html>'''
    out = os.path.join(ROOT, 'site', f'plan-{num}.html'); open(out, 'w', encoding='utf-8').write(page)
    print(f'{len(rows)} rows ({moved} section moves) → {out}')

if __name__ == '__main__':
    main(sys.argv[1])

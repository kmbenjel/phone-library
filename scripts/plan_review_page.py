"""A rename/move plan as a review page (owner 2026-10-10: check and comment from the HTML): every row old → new, section
moves marked, a filter box, a comment per row and «I approve the plan» at the top (review_server.py; comments →
data/names/review-comments.jsonl, report «plan-NNN»; row ids = line numbers in the plan).
A plan rebuilt after an earlier review shows, per row, the earlier proposal and the owner's comment on it
(--prev plans/MMM-x.tsv: rows matched by their source path; comments of report «plan-MMM»), «unchanged» or «changed».
Usage: python3 scripts/plan_review_page.py plans/NNN-name.tsv [--prev plans/MMM-name.tsv]   → site/plan-NNN.html"""
import html, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def previous(prev):
    """source path → (earlier proposal, owner's comment) from an earlier plan and its review"""
    if not prev: return {}, ''
    pn = os.path.basename(prev).split('-')[0]
    rows = [l.rstrip('\n').split('\t') for l in open(prev, encoding='utf-8') if l.strip()]
    com = {}
    log = os.path.join(ROOT, 'data', 'names', 'review-comments.jsonl')
    if os.path.exists(log):
        for l in open(log, encoding='utf-8'):
            d = json.loads(l)
            if d.get('report') == f'plan-{pn}': com[str(d.get('n'))] = d.get('comment', '').strip()
    out = {a: (b, com.get(str(k), '')) for k, (a, b, _) in enumerate(rows, 1)}
    seen = max([int(k) for k, v in com.items() if k.isdigit()] or [0])        # rows the owner reached
    return {a: v + (k <= seen,) for k, (a, v) in enumerate(out.items(), 1)}, pn

def main(plan, prev=None):
    name = os.path.basename(plan).removesuffix('.tsv'); num = name.split('-')[0]
    rows = [l.rstrip('\n').split('\t') for l in open(plan, encoding='utf-8') if l.strip()]
    E, trs, moved = html.escape, [], 0
    old, pn = previous(prev)
    n_seen = n_changed = 0
    for k, (a, b, why) in enumerate(rows, 1):
        ca, cb = a.split('/')[1], b.split('/')[1]
        oa, ob = a.split('/', 2)[2], b.split('/', 2)[2]
        sec = f'<span class="sec">{E(ca)} ← {E(cb)}</span>' if ca != cb else f'<span class="cat">{E(ca)}</span>'
        moved += ca != cb
        flag = ' other' if 'other-' in why else ''
        hist = ''
        if a in old:
            ob13, cm, seen = old[a]
            if seen:
                n_seen += 1; flag += ' seen'
                same = ob13 == b
                n_changed += not same; flag += '' if same else ' changed'
                hist = (f'<div class="hist">{"راجعته في الخطة " + E(pn)}: '
                        + ('لم يتغير' if same else f'تغيّر — كان: <span class="was">{E(ob13.split("/", 2)[2])}</span>')
                        + (f'<div class="cm">تعليقك: {E(cm)}</div>' if cm else '') + '</div>')
        trs.append(f'''<tr class="row{' moved' if ca != cb else ''}{flag}" data-n="{k}"><td class="k">{k}</td><td>{sec}<div class="old">{E(oa)}</div>
<div class="new">{E(ob)}</div>{hist}<div class="why">{E(why)}</div></td>
<td class="review" data-n="{k}"><textarea class="cmt" rows="2" placeholder="تعليق على هذا الصف"></textarea><span class="st"></span></td></tr>''')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>خطة {E(num)}</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--new:#14532d;--sec:#9a3412}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--new:#86efac;--sec:#f0a070}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--new:#86efac;--sec:#f0a070}}
body{{background:var(--bg);color:var(--fg);font:15px/1.6 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1300px;margin:auto}} h1{{font-size:1.4rem}} .lead,.why,.st,.k,.cat{{color:var(--mut)}}
table{{width:100%;border-collapse:collapse;background:var(--card)}} td{{border-top:1px solid var(--line);padding:8px;vertical-align:top}}
.old{{text-decoration:line-through;color:var(--mut)}} .hist{{font-size:.9rem;margin-top:4px}} .was{{color:var(--mut)}} .cm{{background:#fff3cd;color:#5c4400;padding:2px 6px;border-radius:4px;margin-top:2px}} .new{{color:var(--new);font-weight:bold}} .sec{{color:var(--sec);font-weight:bold}}
.why{{font-size:.85rem;direction:ltr;text-align:right}} td.review{{width:28%}} textarea{{width:100%;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px}}
.bar{{position:sticky;top:0;background:var(--bg);padding:8px 0;display:flex;gap:14px;flex-wrap:wrap;align-items:center;z-index:1}}
input[type=search]{{font:inherit;padding:4px 8px;min-width:240px}} .warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>خطة {E(num)}: تسمية الكتب المفردة من صفحات عناوينها</h1>
<p class="lead">القواعد بعد ملاحظاتك: المدينة بعد الناشر («مطبعة حجازي بالقاهرة»)، السنة إن كانت على الغلاف أو كانت الطبعة قديمة، الأسماء كاملة أو بالكنية واللقب المشهورين، الدور كما طُبع إن لم يكن تحقيقا («صححه وعلق عليه»، «تنسيق»، «قدم لها»)، لا «ويليه» ولا «في» من عندي. ما طلبتَ حذفه أو استبداله بالكتاب كاملا ليس في هذه الخطة.</p>
<p class="lead">{len(rows)} صفا؛ منها {moved} تنتقل إلى قسم آخر (بالبرتقالي). لم يُطبق شيء على الهاتف. {f"راجعتَ {n_seen} منها في الخطة {E(pn)}، تغيّر منها {n_changed} بعد ملاحظاتك؛ الباقي جديد عليك. " if pn else ""}علّق على أي صف، ثم علّم الموافقة إن رضيت بالباقي.</p>
<p class="warn" id="noserver" hidden>لحفظ التعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/plan-{E(num)}.html</p>
<div class="bar"><span class="review" data-n="approve"><label><input type="checkbox" class="chk"> أوافق على الخطة (مع ما علقت عليه)</label><span class="st"></span></span>
<input type="search" id="q" placeholder="تصفية: كلمة أو قسم"><label><input type="checkbox" id="onlymoved"> الأقسام المنقولة فقط</label>
<label><input type="checkbox" id="onlyother"> «كتاب آخر» فقط</label>
<label><input type="checkbox" id="onlychanged"> ما تغيّر بعد مراجعتك</label><label><input type="checkbox" id="onlynew"> ما لم تراجعه بعد</label></div>
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
function filt() {{ const g = id => document.getElementById(id).checked, q = document.getElementById('q').value.trim();
  document.querySelectorAll('tr.row').forEach(r => {{ const c = x => r.classList.contains(x);
    r.hidden = (q && !r.textContent.includes(q)) || (g('onlymoved') && !c('moved')) || (g('onlyother') && !c('other')) || (g('onlychanged') && !c('changed')) || (g('onlynew') && c('seen')); }}); }}
['q', 'onlymoved', 'onlyother', 'onlychanged', 'onlynew'].forEach(id => document.getElementById(id).addEventListener('input', filt));
load();
</script></body></html>'''
    out = os.path.join(ROOT, 'site', f'plan-{num}.html'); open(out, 'w', encoding='utf-8').write(page)
    print(f'{len(rows)} rows ({moved} section moves) → {out}')

if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[a.index('--prev') + 1] if '--prev' in a else None)

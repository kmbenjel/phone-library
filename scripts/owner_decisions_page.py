"""The owner's open decisions in one page (owner 2026-10-11: «where should I interfere now»): every row of
data/names/owner-actions.tsv that needs his word — copies to compare, page fixes, stray covers, removals, replacements —
with the book's current path, what was found, «أوافق» and a comment (review_server.py; report «decisions»).
Rows the agent can do alone (pieces to find, additions to look for) are listed after, for information.
The page is in Arabic (owner 2026-10-11): the «ar» column of owner-actions.tsv; write it for every new row.
Usage: python3 scripts/owner_decisions_page.py   → site/decisions.html"""
import csv, html, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
NEED = {'compare': 'نسختان من الكتاب: أيهما تبقى؟', 'fix': 'إصلاح لا يمس الصفحات', 'stray': 'ملف من صفحة واحدة',
        'remove': 'حذف بأمرك', 'replace': 'استبدال بنسخة أفضل', 'replace-whole': 'استبدال بالكتاب كاملا',
        'ask': 'سؤال لك', 'check-file': 'لا يفتح في Files', 'set': 'مجموعة ملفات', 'index': 'فهرس المخطوطات'}
INFO = {'piece': 'قطعة من كتاب أكبر: أبحث عن الكتاب كاملا', 'add': 'إضافة أبحث عنها',
        'dup': 'نسخة ثانية من الطبعة نفسها: تُنحّى إلى «نسخ مستبعدة» وتبقى الأجود'}
AR = {'compare': 'مقارنة', 'fix': 'إصلاح', 'stray': 'غلاف منفرد', 'remove': 'حذف', 'replace': 'استبدال',
      'replace-whole': 'الكتاب كاملا', 'ask': 'سؤال', 'check-file': 'فحص الملف', 'set': 'مجموعة', 'index': 'فهرس',
      'piece': 'قطعة', 'add': 'إضافة', 'dup': 'مكرر'}

def main():
    rows = [r for r in csv.DictReader((l for l in open(J('data', 'names', 'owner-actions.tsv'), encoding='utf-8')
                                       if not l.startswith('#')), delimiter='\t')]
    books = {l.split('\t')[0]: l.split('\t')[2].rstrip('\n') for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8') if l.count('\t') >= 2}
    moved = {}
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 3 and r[1] == 'move': moved[r[2].removeprefix('Books/')] = r[3].removeprefix('Books/')
    import unicodedata
    idx = {unicodedata.normalize('NFC', l.split('\t')[0]) for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8')}
    def now(n):
        p = books.get(n, '')
        for _ in range(30):
            if unicodedata.normalize('NFC', p) in idx or p not in moved: break
            p = moved[p]
        return p
    E = html.escape
    def card(i, r, ask):
        n = r['n']
        rid = f"{n}-{r['action']}"
        box = (f'<div class="review" data-n="{E(rid)}"><label><input type="checkbox" class="chk"> أوافق</label>'
               f'<textarea class="cmt" rows="2" placeholder="قرارك أو تعليقك"></textarea><span class="st"></span></div>') if ask else ''
        return (f'<article><div class="tag">{E(AR.get(r["action"], r["action"]))}</div><h2>الكتاب {E(n)}</h2>'
                f'<div class="path">{E(now(n))}</div><p>{E(r.get("ar") or r["what"])}</p>{box}</article>')
    need = [r for r in rows if r['action'] in NEED]
    info = [r for r in rows if r['action'] in INFO]
    order = list(NEED)
    need.sort(key=lambda r: (order.index(r['action']), int(re.sub(r'\D', '', r['n']) or 0)))
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>قراراتك المعلقة</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--tag:#9a3412}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--tag:#f0a070}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--tag:#f0a070}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1000px;margin:auto}} h1{{font-size:1.4rem}} h2{{font-size:1rem;margin:.1em 0}} .lead,.path,.st{{color:var(--mut)}}
.path{{font-size:.85rem;word-break:break-word}} .tag{{color:var(--tag);font-weight:bold;font-size:.9rem}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:12px 0}}
.review{{display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap}} .review textarea{{flex:1;min-width:240px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}}
.warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>قراراتك المعلقة</h1>
<p class="lead">{len(need)} أمرا ينتظر كلمتك (علّم «أوافق» أو اكتب قرارك)، ثم {len(info)} أمرا أقوم به وحدي للعلم. لا شيء يطبق على الهاتف قبل موافقتك.</p>
<p class="warn" id="noserver" hidden>لحفظ القرارات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/decisions.html</p>
{''.join(card(i, r, True) for i, r in enumerate(need))}
<h1>أقوم به وحدي</h1>{''.join(card(i, r, False) for i, r in enumerate(info))}
</main><script>
const R = 'decisions', live = location.protocol.startsWith('http');
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
    open(J('site', 'decisions.html'), 'w', encoding='utf-8').write(page)
    print(len(need), 'decisions,', len(info), 'for information → site/decisions.html')

if __name__ == '__main__':
    main()

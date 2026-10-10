"""One review page for a crop batch: for every book that has sample pages (~/.cache/phone-library/crop-sheets/<hash>/,
written by crop_batch.py), each telling page shown AFTER | line | BEFORE, why that page was chosen, the book's reasons
and text gain, and a check box + comment per book (owner 2026-10-10: before/after separated by a vertical line; check and
comment from the page). Served by scripts/review_server.py → http://127.0.0.1:8765/crop-review-<batch>.html; comments go
to data/names/review-comments.jsonl with report «crop-<batch>».
Usage: python3 scripts/crop_review_page.py BATCH   (e.g. 001: the books logged as crop-batch-001)"""
import csv, html, json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
SHEETS = os.path.expanduser('~/.cache/phone-library/crop-sheets')
WHY = {'skew': 'صفحة مائلة قُوِّمت', 'notes': 'حاشية في الهامش أُبقيت', 'note': 'حاشية في الهامش أُبقيت',
       'scaled': 'صفحة صُغِّرت لتساوي مقاس الكتاب', 'folio': 'صفحة قصيرة وُضعت حسب رقم صفحتها', 'mid': 'صفحة نص عادية (للهوامش)'}
REASON = [('tilted pages', 'صفحات مائلة'), ('off-centre', 'النص غير متوسط'), ('text sways', 'النص يتمايل بين الصفحات'),
          ('bands', 'أشرطة'), ('stains', 'بقع'), ('gain', 'تكبير النص')]

def main(batch):
    tag = f'crop-batch-{batch}'
    logged = {r[2].removeprefix('Books/'): r[4] for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t')
              if len(r) > 5 and r[1] == 'crop' and r[5].strip() == tag}
    outdir = J('site', f'crop-review-{batch}'); os.makedirs(outdir, exist_ok=True)
    E, cards = html.escape, []
    for h in sorted(os.listdir(SHEETS)):
        d = os.path.join(SHEETS, h)
        try: book = json.load(open(os.path.join(d, 'book.json'), encoding='utf-8'))
        except (OSError, ValueError): continue
        if book.get('path') not in logged: continue
        why = {}
        try: why = json.load(open(os.path.join(d, 'reasons.json'), encoding='utf-8'))
        except (OSError, ValueError): pass
        pairs = []
        for f in sorted(os.listdir(d)):
            if not f.endswith('-before.jpg'): continue
            pg = f[1:5]; aft = f.replace('-before', '-after')
            if not os.path.exists(os.path.join(d, aft)): continue
            for x in (f, aft): shutil.copyfile(os.path.join(d, x), os.path.join(outdir, f'{h}-{x}'))
            label = WHY.get(why.get(str(int(pg) - 1), why.get(str(int(pg)), '')), '')
            pairs.append(f'''<figure><div class="pair"><div><span>بعد</span><img src="crop-review-{batch}/{h}-{aft}" alt="بعد"></div>
<div class="sep"></div><div><span>قبل</span><img src="crop-review-{batch}/{h}-{f}" alt="قبل"></div></div>
<figcaption>ص {int(pg)}{(' — ' + label) if label else ''}</figcaption></figure>''')
        reasons = '، '.join(book.get('reasons') or [])
        for en, ar in REASON: reasons = reasons.replace(en, ar)
        gain = book.get('gain')
        cards.append(f'''<article><h2>{E(book["path"])}</h2><p class="meta">{E(reasons)}{f" — تكبير النص {round((gain - 1) * 100)}٪" if gain else ""}</p>
{''.join(pairs)}<div class="review" data-n="{E(h)}"><label><input type="checkbox" class="chk"> تم الفحص</label>
<textarea class="cmt" rows="2" placeholder="ملاحظتك على هذا الكتاب"></textarea><span class="st"></span></div></article>''')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>مراجعة القص {batch}</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--sep:#1f1d1a}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--sep:#ece8e1}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--sep:#ece8e1}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1200px;margin:auto}} h1{{font-size:1.5rem}} h2{{font-size:1.05rem;margin:.2em 0}} .meta,.lead,figcaption,.st{{color:var(--mut)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:16px 0}}
figure{{margin:10px 0}} .pair{{display:flex;gap:0;align-items:flex-end;overflow-x:auto}} .pair>div{{display:flex;flex-direction:column;align-items:center}}
.pair img{{height:520px;display:block}} .pair span{{font-weight:bold;padding:0 6px}} .sep{{width:2px;align-self:stretch;background:var(--sep);margin-top:1.7em}}
.review{{display:flex;gap:10px;align-items:flex-start;margin-top:8px;flex-wrap:wrap}}
.review textarea{{flex:1;min-width:240px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}}
.warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>مراجعة دفعة القص {batch}: قبل وبعد</h1>
<p class="lead">{len(cards)} كتابا من {len(logged)} حُفظت لها صفحات دالة: كل صفحة «بعد» ثم خط فاصل ثم «قبل». علّم «تم الفحص» واكتب ملاحظتك على كل كتاب؛ تُحفظ فورا.</p>
<p class="warn" id="noserver" hidden>لحفظ الفحص والتعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/crop-review-{batch}.html</p>
{''.join(cards)}</main><script>
const R = 'crop-{batch}', live = location.protocol.startsWith('http');
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
    out = J('site', f'crop-review-{batch}.html'); open(out, 'w', encoding='utf-8').write(page)
    print(f'{len(cards)} books → {out}')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '001')

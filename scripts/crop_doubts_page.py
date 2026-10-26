"""The owner's review page for a crop run (owner 2026-10-18: a review of the pages the method itself doubts, not samples —
«hope my remarks will be rare»): for every book with doubtful pages (~/.cache/phone-library/crop-sheets/<hash>/book.json,
written by crop_batch.analyse — also during crop_redo.py), those pages after | before, what was doubted in Arabic, a check
box and a comment (report «crop-doubts»; review_server.py). The pages the owner pointed at in an earlier review are shown
too, his words beside them (crop_batch.owner_pages: data/crop/owner-pages.tsv, owner-turns.tsv). Books he ticks, or answered, leave the page
(data/names/review-closed.tsv, report «crop-doubts»). Books without doubts are not shown: the count says how many.
Usage: python3 scripts/crop_doubts_page.py [BATCH …]   (the change-log batch names, e.g. crop-redo-001; default: all)"""
import csv, html, json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
SHEETS = os.path.expanduser('~/.cache/phone-library/crop-sheets')
WHY = {'tilt': 'ميل لم تحسمه المقاييس (اختلفت أو لم تُعالجه)', 'whole': 'صفحة بقيت كاملة لم تُقص',
       'stain': 'بقعة أُبقيت داخل الإطار حفاظا على توازن الهامشين', 'stamp': 'ختم غُطّي بلون الصفحة',
       'larger': 'صفحة عُرضت بإطار أكبر قليلا ليسع ما فيها', 'sheet': 'صفحة على سطح الماسح: مُلئ ما وراء حافتها بلونها',
       'cut': 'حرف أو رقم كاد الإطار يقطعه بعد تحريكه: أُدخل في الإطار', 'folio': 'رقم الصفحة قُرئ بقعةً فأعيد إلى النص'}

def main(batches):
    logged = {}
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 5 and r[1] == 'crop' and (not batches or r[5].strip() in batches): logged[r[2].removeprefix('Books/')] = r[5].strip()
    closed = set()
    if os.path.exists(J('data', 'names', 'review-closed.tsv')):
        closed = {l.split('\t')[1] for l in open(J('data', 'names', 'review-closed.tsv'), encoding='utf-8') if l.startswith('crop-doubts\t')}
    out = J('site', 'crop-doubts'); os.makedirs(out, exist_ok=True)
    E, cards, clean = html.escape, [], 0
    for h in sorted(os.listdir(SHEETS)) if os.path.isdir(SHEETS) else []:
        d = os.path.join(SHEETS, h)
        try: book = json.load(open(os.path.join(d, 'book.json'), encoding='utf-8'))
        except (OSError, ValueError): continue
        if book.get('path') not in logged or 'shown' not in book: continue
        if not book['shown']: clean += 1; continue
        if h in closed: continue
        figs = []; own = book.get('owner') or {}
        for i, why in book['shown']:
            b, a = f'p{i + 1:04d}-before.jpg', f'p{i + 1:04d}-after.jpg'
            if not (os.path.exists(os.path.join(d, a)) and os.path.exists(os.path.join(d, b))): continue
            for x in (a, b): shutil.copyfile(os.path.join(d, x), os.path.join(out, f'{h}-{x}'))
            cap = '؛ '.join('صفحة أشرتَ إليها من قبل: ' + own.get(str(i + 1), '') if w == 'owner' else WHY.get(w, w) for w in why.split('+'))
            figs.append(f'<figure><div class="pair"><div><span>بعد</span><img src="crop-doubts/{h}-{a}" alt="بعد" loading="lazy"></div>'
                        f'<div class="sep"></div><div><span>قبل</span><img src="crop-doubts/{h}-{b}" alt="قبل" loading="lazy"></div></div>'
                        f'<figcaption>ص {i + 1} — {E(cap)}</figcaption></figure>')
        n = {k: v for k, v in (book.get('doubts') or {}).items() if v}
        summ = '، '.join(f'{WHY[k].split(" (")[0]}: {v}' for k, v in n.items() if k in WHY)
        cards.append(f'<article><h2>{E(book["path"])}</h2><p class="meta">مواضع الشك في الكتاب كله — {E(summ)}</p>{"".join(figs)}'
                     f'<div class="review" data-n="{E(h)}"><label><input type="checkbox" class="chk"> سليم</label>'
                     f'<textarea class="cmt" rows="2" placeholder="ملاحظتك"></textarea><span class="st"></span></div></article>')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>مواضع الشك في القص</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--sep:#1f1d1a}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--sep:#ece8e1}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--sep:#ece8e1}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1200px;margin:auto}} h1{{font-size:1.4rem}} h2{{font-size:1.02rem;margin:.2em 0;word-break:break-word}} .meta,.lead,figcaption,.st{{color:var(--mut)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:16px 0}}
figure{{margin:10px 0}} .pair{{display:flex;align-items:flex-end;overflow-x:auto}} .pair>div{{display:flex;flex-direction:column;align-items:center}}
.pair img{{height:500px;display:block}} .pair span{{font-weight:bold;padding:0 6px}} .sep{{width:2px;align-self:stretch;background:var(--sep);margin-top:1.7em}}
.review{{display:flex;gap:10px;align-items:flex-start;margin-top:8px;flex-wrap:wrap}}
.review textarea{{flex:1;min-width:240px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}}
</style></head><body><main><h1>مواضع الشك في القص</h1>
<p class="lead">{len(cards)} كتابا فيها مواضع تشك فيها الطريقة نفسها أو صفحات أشرتَ إليها في مراجعة سابقة، معروضة وحدها (بعد | قبل). و{clean} كتابا لا شك فيها لم تُعرض. علّم «سليم» أو اكتب ملاحظتك؛ يخرج الكتاب من الصفحة بعدها.</p>
{"".join(cards)}</main><script>
const R='crop-doubts';
async function load(){{try{{const d=await (await fetch('/api/comments?r='+R)).json();document.querySelectorAll('.review').forEach(b=>{{const x=d[b.dataset.n];if(!x)return;b.querySelector('.chk').checked=x.checked;b.querySelector('.cmt').value=x.comment;b.querySelector('.st').textContent='حُفظ '+x.time;}});}}catch(e){{}}}}
function save(b){{const st=b.querySelector('.st');st.textContent='…';fetch('/api/comment',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{report:R,n:b.dataset.n,checked:b.querySelector('.chk').checked,comment:b.querySelector('.cmt').value}})}}).then(r=>r.json()).then(j=>st.textContent='حُفظ '+j.time).catch(()=>st.textContent='لم يُحفظ');}}
document.querySelectorAll('.review').forEach(b=>{{let t;b.querySelector('.chk').addEventListener('change',()=>save(b));b.querySelector('.cmt').addEventListener('input',()=>{{clearTimeout(t);t=setTimeout(()=>save(b),800);}});}});load();
</script></body></html>'''
    open(J('site', 'crop-doubts.html'), 'w', encoding='utf-8').write(page)
    print(len(cards), 'books with doubts,', clean, 'without → site/crop-doubts.html')

if __name__ == '__main__':
    main(set(sys.argv[1:]))

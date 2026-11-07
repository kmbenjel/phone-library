"""The owner's review page for a crop run (owner 2026-10-18: a review of the pages the method itself doubts, not samples —
«hope my remarks will be rare»): for every book with doubtful pages (~/.cache/phone-library/crop-sheets/<hash>/book.json,
written by crop_batch.analyse — also during crop_redo.py), those pages after | before, what was doubted in Arabic, a check
box and a comment (report «crop-doubts»; review_server.py). The pages the owner pointed at in an earlier review are shown
too, his words beside them (crop_batch.owner_pages: data/crop/owner-pages.tsv, owner-turns.tsv). Books he ticks, or answered, leave the page
(data/names/review-closed.tsv, report «crop-doubts»). Books without doubts are not shown: the count says how many.
Usage: python3 scripts/crop_doubts_page.py [BATCH …]   (the change-log batch names, e.g. crop-redo-001; default: all)"""
import csv, hashlib, html, json, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
SHEETS = os.path.expanduser('~/.cache/phone-library/crop-sheets')
WHY = {'frame': 'صفحة ذات إطار مطبوع: قُوِّمت بميل إطارها نفسه (أو تُركت لأن إطارها قائم) مهما قرأت سطورها — حكمك على المخصص ج 13',
       'tilt': 'ميل لم تحسمه المقاييس (اختلفت أو لم تُعالجه)', 'whole': 'صفحة بقيت كاملة لم تُقص',
       'stain': 'بقعة أُبقيت داخل الإطار حفاظا على توازن الهامشين', 'stamp': 'ختم غُطّي بلون الصفحة',
       'rim': 'حافة صوّرها الماسح خارج النص غُطّيت بلون الورق',
       'larger': 'صفحة عُرضت بإطار أكبر قليلا ليسع ما فيها', 'sheet': 'صفحة على سطح الماسح: مُلئ ما وراء حافتها بلونها',
       'third': 'ميل واضح رأته المقاييس كلها: قُوِّمت الصفحة ولم يبق من قراءة الصورة إلا ثلثها أو أقل',
       'side': 'إطار أُزيح جانبا أكثر من ٢٪ ليسع عنوانا جانبيا أو حرفا عند حافة الورقة (النص غير متوسط تماما)',
       'edge': 'حروف عند حافة الورقة (في ظلها) أُدخلت في الإطار',
       'cut': 'حرف أو رقم كاد الإطار يقطعه بعد تحريكه: أُدخل في الإطار', 'folio': 'رقم الصفحة قُرئ بقعةً أو نُقَطًا متفرقة فأعيد إلى النص',
       'orn': 'زخرفة مطبوعة يكررها الكتاب (حلية آخر الفصل) كانت تُقرأ بقعة: أعيدت إلى النص، ولم يعد الإطار يتحرك ليتفاداها',
       'base': 'ميل لم تره المقاييس المعتادة ورأته سطور الصفحة نفسها (قاعدة كل سطر) ووافقها مقياس آخر: قُوِّمت حتى استوت سطورها',
       'two': 'سطور على زاويتين (صفحة ملتوية، أو سطور صُفّت كلٌّ وحده): لا يسويها تدوير واحد، فتُركت كما مُسحت',
       'tracks': 'تدوير أمال بعض السطور فرُدّ، ثم قُوِّمت الصفحة بالزاوية التي تتفق عليها سطورها (كل سطر مقيس وحده)'}

def main(batches):
    logged = {}                                       # path → (day, tag, recipe) of its latest crop: a card's id is «<hash>-<tag>»,
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):   # the crop's own md5
        if len(r) > 5 and r[1] == 'crop' and (not batches or r[5].strip() in batches):          # (2026-11-03: ids were
            m = r[4].rsplit('→ md5 ', 1)[1][:7] if '→ md5 ' in r[4] else r[0][2:10].replace('-', '')  # the path's hash alone)
            o = re.search(r'original \d+ B md5 (\w+)', r[4])
            logged[r[2].removeprefix('Books/')] = (r[0][:10], m, J('data', 'crop', 'recipes', o.group(1) + '.json') if o else None)
    # THE OWNER'S TICKS AND WORDS SURVIVE A REDO (owner 2026-11-07 «كثيرا من ملاحظاتي السابقة ألغيت»: every redo rewrites the
    # file, so the tag changed on 1,111 books and his 14 remarks of 10-31 and 11-06 went off the cards): a closed row names
    # the card («<hash>-<tag>», or the hash alone) and closes the book while its RECIPE is the one he saw — the row's
    # recipe=<md5> (review_close.py writes it), or, for the rows before 11-07 without it, a recipe git has not changed since
    # the row's day. A book whose recipe changed since comes back, his earlier words shown beside the new pages.
    closed = {}                                       # card or hash → (day, recipe md5 or None)
    if os.path.exists(J('data', 'names', 'review-closed.tsv')):
        for l in open(J('data', 'names', 'review-closed.tsv'), encoding='utf-8'):
            f = l.rstrip('\n').split('\t')
            if f[0] != 'crop-doubts' or len(f) < 3: continue
            rm = next((x[7:] for x in f[3:] if x.startswith('recipe=')), None)
            closed[f[1]] = (f[2], rm)
    changed = {}                                      # recipe file → the day git last changed it (one call for all)
    try:
        day = None
        for l in subprocess.run(['git', 'log', '--format=%%%cs', '--name-only', '--', 'data/crop/recipes'], cwd=ROOT,
                                capture_output=True, text=True).stdout.splitlines():
            if l.startswith('%'): day = l[1:]
            elif l.strip() and J(l.strip()) not in changed: changed[J(l.strip())] = day   # (the first = latest commit)
    except OSError: pass
    rmd5 = lambda f: hashlib.md5(open(f, 'rb').read()).hexdigest() if f and os.path.exists(f) else None
    def is_closed(h, key, day, rf):
        c = last.get(key)                             # (his words on THIS card, not yet answered: the card stays)
        if c and not c.get('checked') and c.get('comment', '').strip() and key not in closed: return False
        for k in (key, h) + tuple(k for k in closed if k.startswith(h + '-') and k != key):
            if k not in closed: continue
            cday, crm = closed[k]
            if k == key: return True
            if crm: return crm == rmd5(rf)
            if rf and changed.get(rf, '0000') <= cday: return True
        return False
    hist, last = {}, {}                               # hash → his remarks on the book's older cards [(time, card, checked, words)]
    try:
        for l in open(J('data', 'names', 'review-comments.jsonl'), encoding='utf-8'):
            try: c = json.loads(l)
            except ValueError: continue
            if c.get('report') == 'crop-doubts': last[str(c.get('n'))] = c
        for n, c in last.items():
            hist.setdefault(n.split('-')[0], []).append((c.get('time', ''), n, c.get('checked'), c.get('comment', '')))
            if c.get('checked') and n not in closed: closed[n] = (str(c.get('time', ''))[:10], None)   # his tick closes the card
    except OSError: pass
    out = J('site', 'crop-doubts'); os.makedirs(out, exist_ok=True)
    E, cards, clean = html.escape, [], 0
    for h in sorted(os.listdir(SHEETS)) if os.path.isdir(SHEETS) else []:
        d = os.path.join(SHEETS, h)
        try: book = json.load(open(os.path.join(d, 'book.json'), encoding='utf-8'))
        except (OSError, ValueError): continue
        if book.get('path') not in logged or 'shown' not in book: continue
        if not book['shown']: clean += 1; continue
        day, tag, rf = logged[book['path']]; key = f'{h}-{tag}'
        if is_closed(h, key, day, rf): continue
        prev = sorted((x for x in hist.get(h, []) if x[1] != key), reverse=True)
        pv = '؛ '.join(f'يوم {E(t[:10])}: ' + ('علّمته «سليم»' if ch and not w.strip() else '«' + E(w.strip()) + '»' + (' وعلّمته «سليم»' if ch else ''))
                      for t, _, ch, w in prev)
        pv = f'<p class="prev">ملاحظاتك على قصّ أقدم لهذا الكتاب (تغيّر القص بعدها): {pv}</p>' if pv else ''
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
        two = book.get('two') or []                   # (every page left as scanned for its two angles, named — owner 2026-10-27)
        tw = f'<p class="meta">صفحات تُركت كما مُسحت لأن سطورها على زاويتين: ص {"، ".join(map(str, two))}</p>' if two else ''
        rims = book.get('rims') or []                 # (every page with a rim painted out, named — pilot audit 2026-10-31)
        tw += f'<p class="meta">صفحات غُطّيت فيها حافة بلون الورق: ص {"، ".join(map(str, rims))}</p>' if rims else ''
        cards.append(f'<article><h2>{E(book["path"])}</h2><p class="meta">مواضع الشك في الكتاب كله — {E(summ)}</p>{tw}{pv}{"".join(figs)}'
                     f'<div class="review" data-n="{E(key)}"><label><input type="checkbox" class="chk"> سليم</label>'
                     f'<textarea class="cmt" rows="2" placeholder="ملاحظتك"></textarea><span class="st"></span></div></article>')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>مواضع الشك في القص</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--sep:#1f1d1a}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--sep:#ece8e1}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--sep:#ece8e1}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1200px;margin:auto}} h1{{font-size:1.4rem}} h2{{font-size:1.02rem;margin:.2em 0;word-break:break-word}} .meta,.lead,figcaption,.st{{color:var(--mut)}}
.prev{{color:#8a4b00;background:#fff6e5;border-radius:6px;padding:4px 8px}} @media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) .prev{{color:#f0c27a;background:#2a2112}}}}
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

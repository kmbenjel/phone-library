"""One review page for the corrected crop method (2026-10-18): every page the owner marked in crop-review-002/004 —
the scan, the old crop, the new crop (the latest test run: crop-minitest r4, else r3) — with his remark and the verdict.
Comments go to data/names/review-comments.jsonl (report «crop-fixes»). → site/crop-fixes.html (+ site/crop-fixes/)"""
import html, json, os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p); E = html.escape
S = os.path.expanduser('~/.cache/phone-library/crop-sheets'); M = os.path.expanduser('~/.cache/phone-library/crop-minitest')
V = {  # sheet id → (state, verdict in Arabic): ok = fixed, part = partly, no = not yet
 '00597fea27cf': ('ok', 'وُسّطت الصفحة: كان خط شارد فوق الرأس يجذب الإطار.'),
 '064846139175': ('part', 'زال الشريط الأسود ووُسّط الجدول؛ بقي تقوّس السطور لأن الورقة مقوسة في التصوير، ولا يصلحه التدوير.'),
 '29b9db6c6baa': ('ok', 'وُسّط النص وحُدّد الإطار؛ خطوط الماسح على الجانبين خارجه.'),
 '35fbe344b8c6': ('part', 'ص 18: أُزيل الطابع فصارت بتكبير سائر الصفحات. ص 44: بقي خط داكن صغير في الزاوية العليا.'),
 '52072388499d': ('ok', 'وُسّطت: نقاط شاردة في الحاشية كانت تجعل الكتاب «زوجيا وفرديا» فتُزاح صفحاته.'),
 '5b214426d112': ('ok', 'الإطار كله وسط الصفحة (الصورة من مستخرج الاختبار؛ أُصلح الكتاب كاملا بعدها أيضا).'),
 '68600214e7de': ('ok', 'ص 18: أُزيل الطابع. ص 236: زال الشريط الداكن فوق الرأس ووُسّط النص.'),
 '8ec1fd8095ad': ('ok', 'الغلاف وحده، بلا سطح الماسح.'),
 '9da5c530d977': ('ok', 'الغلاف وحده يملأ الصفحة.'),
 'd2e6995099bc': ('part', 'الغلاف الملتف (ظهر + كعب + وجه في صفحة واحدة عريضة) يُقسم الآن صفحتين؛ الصورة «الجديد» هنا قبل هذا الإصلاح.'),
 'd319e06e78d0': ('ok', 'زالت خطوط الجانب ووُسّط النص.'),
 'e27411fc9a16': ('ok', 'لم تعد تُدار (ص 88)، وطابع «المشكاة» خارج الإطار.'),
 'f134344a7421': ('ok', 'ص 69 بتكبير سائر الصفحات: خطوط التلف لم تعد «حاشية».'),
 'fbf39d55c6f7': ('ok', 'قُسمت كل ورقة مزدوجة صفحتين (اليمنى أولا) دون مساس بالمسح، ثم قُصّت. ويُبحث عن نسخة أفضل تصويرا.'),
 '0e655bcab0be': ('ok', 'بالتكبير الكامل ووسط الصفحة: كانت شرطات حافة الورقة تُعدّ حاشية.'),
 '1120ebd46313': ('no', 'لم يُحلّ: الكتاب يخرج في الاختبار «تقويما فقط» بلا قص، وأمر الختم في ص 9 باق.'),
 '16b15400af27': ('ok', 'كان رائعا وبقي كذلك.'),
 '1ab3b838b6d1': ('ok', 'ص 294 أكبر ووسط، وص 441 زال خط الحافة ووُسّطت.'),
 '1d12000b2925': ('ok', 'بتكبير سائر الصفحات: عيب الطباعة على اليسار لم يعد يوسّع الإطار.'),
 '2a8c4bfeff47': ('ok', 'قُوّمت صفحة العمودين (ص 42).'),
 '2af978d37d97': ('ok', 'قُوّمت ص 250 (ميلها نحو 4–6°، فوق حد البحث القديم).'),
 '2b47002d18ab': ('ok', 'ص 421 زالت خطوط الحافة، وص 426 زال الشريط العلوي ووُسّطت.'),
 '3103a9db389b': ('ok', 'صفحة العنوان وسط الصفحة.'),
 '43b1158bc5be': ('no', 'لم يُحلّ بعد: الصفحة مصورة بانحراف، فالسطور مستوية وحافتها مائلة؛ يلزمها «إمالة معاكسة» (تحويل بلا فقد) — التالي.'),
 '4a0fc25a3d64': ('part', 'ص 400 مستوية بالقياس؛ تموّج السطور في طبعة كلكتة الحجرية لا يصلحه التدوير.'),
 '51cfa6854fda': ('no', 'لم يُحلّ بعد: الشعار الأسود داخل عمود النص، ولا أفرّقه بعدُ عن المطبوع بأمان.'),
 '54dce4c59b22': ('ok', 'صورة المخطوط كاملة مع تعليقها ورقم الصفحة (كانت تُقطع).'),
 '55d35c02e3e0': ('ok', 'وُسّطت، ولم يعد خط عيب الطباعة يُعتدّ به.'),
 '816413b0e765': ('no', 'الأصل نفسه مقطوع الحواف: لا يصلحه القص؛ يُبحث عن نسخة أفضل.'),
 '83dfc7786870': ('ok', 'لم تعد ص 138 تُدار: الإطار المطبوع مستو، والصورة المائلة داخله كما هي.'),
 'ae39a500653d': ('ok', 'آخر ما راجعتَه؛ الصفحات بالطريقة الجديدة.'),
}
STATE = {'ok': ('أُصلح', '#1b7f3b'), 'part': ('أُصلح جزئيا', '#9a6b00'), 'no': ('لم يُصلح بعد', '#b3261e')}
out = J('site', 'crop-fixes'); os.makedirs(out, exist_ok=True); cards = []; n_ok = 0
for l in open(J('data', 'crop', 'owner-marked-2026-10-14.tsv'), encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    h, rep, path, remark = l.rstrip('\n').split('\t')[:4]
    run = next((r for r in ('r4', 'r3') if os.path.exists(os.path.join(M, r, h, 'map.json'))), None)
    mp = json.load(open(os.path.join(M, run, h, 'map.json')))['marked'] if run else {}
    figs = []
    for pg in sorted(mp, key=int):
        ims = []
        for lab, src in (('الجديد', os.path.join(M, run, h, f'p{mp[pg] + 1:04d}-after.jpg')), ('القديم', os.path.join(S, h, f'p{int(pg):04d}-after.jpg')),
                         ('المسح', os.path.join(S, h, f'p{int(pg):04d}-before.jpg'))):
            if not os.path.exists(src): continue
            dst = f'{h}-{pg}-{os.path.basename(src)[6:]}' if 'minitest' not in src else f'{h}-{pg}-new.jpg'
            shutil.copyfile(src, os.path.join(out, dst)); ims.append(f'<div><span>{lab}</span><img src="crop-fixes/{dst}" alt="{lab}" loading="lazy"></div>')
        figs.append(f'<figure><div class="trio">{"".join(ims)}</div><figcaption>ص {pg}</figcaption></figure>')
    st, verdict = V.get(h, ('part', ''))
    n_ok += st == 'ok'; lbl, col = STATE[st]
    cards.append(f'''<article><h2>{E(path)}</h2><p class="rm">ملاحظتك ({E(rep)}): «{E(remark)}»</p>
<p class="vd"><b style="color:{col}">{lbl}</b> — {E(verdict)}</p>{"".join(figs)}
<div class="review" data-n="{E(h)}"><label><input type="checkbox" class="chk"> تم الفحص</label>
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
<p class="lead">لكل صفحة علّقتَ عليها في مراجعتي الدفعتين 002 و004: «الجديد» (الطريقة المصححة) ثم «القديم» ثم «المسح» الأصلي. {n_ok} من {len(cards)} كتابا أُصلحت، والباقي مبيّن سببه. هذه الطريقة ستُعاد بها الكتب الـ1122 المقصوصة قديما بعد نجاح الاختبار الشامل؛ علّق على ما تراه، فيُصلح هو ومثيلاته قبل المضي أو أثناءه.</p>
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

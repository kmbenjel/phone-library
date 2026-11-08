"""Review page for an OCR-cleaning sample (scripts/ocr_clean.py → data/improve/ocr/report.json): per book, two telling
pages shown AFTER | line | BEFORE (the line flush between the pages, owner 2026-10-10), the sizes, the OCR read before
and after, links that open the original and the cleaned copy, and «تم الفحص» + a comment (served by review_server.py;
comments → data/names/review-comments.jsonl, report «ocr-<name>»).
Usage: python3 scripts/ocr_review_page.py NAME   → site/ocr-review-NAME.html (+ site/ocr-review-NAME/ images)"""
import html, json, os, subprocess, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)

def pair(orig, final, page, out, h=560):
    ims = []
    for f in (final, orig):
        base = out + ('-a' if f == final else '-b')
        subprocess.run(['pdftoppm', '-gray', '-r', '60', '-cropbox', '-f', str(page), '-l', str(page), '-png', '-singlefile', f, base],
                       check=True, stderr=subprocess.DEVNULL)
        im = Image.open(base + '.png').convert('L'); os.remove(base + '.png')
        ims.append(im.resize((max(1, im.width * h // im.height), h)))
    img = Image.new('L', (ims[0].width + ims[1].width + 2, h), 255)
    img.paste(ims[0], (0, 0)); img.paste(ims[1], (ims[0].width + 2, 0))
    ImageDraw.Draw(img).line([(ims[0].width, 0), (ims[0].width, h)], fill=0, width=2)
    img.save(out + '.jpg', quality=82)

def main(name):
    rep = json.load(open(J('data', 'improve', 'ocr', 'report.json'), encoding='utf-8'))
    outdir = J('site', f'ocr-review-{name}'); os.makedirs(outdir, exist_ok=True)
    E, cards = html.escape, []
    for key, r in rep.items():
        if not r.get('done'): continue
        d = J('data', 'improve', 'ocr', key)
        pages = r['sample_pages']; show = [pages[1], pages[len(pages) // 2 + 1]] if len(pages) > 3 else pages[:2]
        figs = ''
        for p in show:
            pair(os.path.join(d, 'orig.pdf'), os.path.join(d, 'final.pdf'), p, os.path.join(outdir, f'{key}-{p}'))
            figs += f'<figure><img src="ocr-review-{name}/{key}-{p}.jpg" alt=""><figcaption>ص {p} — بعد | قبل</figcaption></figure>'
        o, f = r['ocr_orig'], r['ocr_final']
        verdict = 'أوضح للقراءة الآلية' if f['good_words'] > o['good_words'] * 1.05 else ('مثلها' if f['good_words'] >= o['good_words'] * 0.95 else 'أضعف — يحتاج نظرا')
        cards.append(f'''<article><h2>{E(r["path"])}</h2>
<p class="meta">{r["pages"]} صفحة؛ الحجم {r["size_orig"] // 1000} ← {r["size_final"] // 1000} ك.ب؛ صفحات قُوِّمت {r["turned"]}؛ صفحات صور بقيت رمادية {r["grey_pages"]}؛
القراءة الآلية (6 صفحات): الثقة {o["conf"]} ← {f["conf"]}، الكلمات المقروءة {o["good_words"]} ← {f["good_words"]} ({verdict})</p>
<p><a href="/ocr/{key}/orig.pdf" target="_blank">افتح الأصل</a> · <a href="/ocr/{key}/final.pdf" target="_blank">افتح النسخة المعالجة (فيها طبقة نص قابلة للبحث)</a></p>
<div class="figs">{figs}</div>
<div class="review" data-n="{key}"><label><input type="checkbox" class="chk"> تم الفحص</label>
<textarea class="cmt" rows="2" placeholder="ملاحظتك على هذا الكتاب"></textarea><span class="st"></span></div></article>''')
    page = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>عينة المعالجة بالتعرف الضوئي</title><style>
:root{{--bg:#fbfaf7;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e4dfd6;--link:#1e4f8a}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--link:#8fb6e8}}}}
:root[data-theme="dark"]{{--bg:#161513;--fg:#ece8e1;--mut:#a39c91;--card:#1f1d1a;--line:#34312c;--link:#8fb6e8}}
body{{background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Naskh Arabic","Amiri",serif;margin:0;padding:16px}}
main{{max-width:1200px;margin:auto}} h1{{font-size:1.5rem}} h2{{font-size:1.05rem;margin:.2em 0}} .meta,.lead,figcaption,.st{{color:var(--mut)}} a{{color:var(--link)}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:16px 0}}
.figs{{display:flex;gap:16px;overflow-x:auto}} figure{{margin:6px 0}} figure img{{height:560px;border:1px solid var(--line)}}
.review{{display:flex;gap:10px;align-items:flex-start;margin-top:8px;flex-wrap:wrap}}
.review textarea{{flex:1;min-width:240px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}}
.warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:8px}}
</style></head><body><main><h1>عينة المعالجة: أبيض وأسود، تقويم، تكبير، وطبقة نص</h1>
<p class="lead">{len(cards)} كتب. لكل كتاب صفحتان: «بعد» ثم الخط ثم «قبل». الأصل محفوظ، ولا شيء على الهاتف بعد. صفحات الصور (الغلاف واللوحات) تبقى رمادية.</p>
<p class="warn" id="noserver" hidden>لحفظ الفحص والتعليقات افتح الصفحة من الخادم المحلي: http://127.0.0.1:8765/ocr-review-{name}.html</p>
{''.join(cards)}</main><script>
const R = 'ocr-{name}', live = location.protocol.startsWith('http');
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
    out = J('site', f'ocr-review-{name}.html'); open(out, 'w', encoding='utf-8').write(page)
    print(f'{len(cards)} books → {out}')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '001')

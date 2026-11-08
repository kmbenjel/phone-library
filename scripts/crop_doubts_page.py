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

# WHAT HE PASSED BEFORE IS NOT ASKED AGAIN (owner 2026-11-07: «show the really doubtful pages, they are a few; tolerate based
# on my previous tolerating»). His 24 crop-doubts cards (10-31 … 11-07, ~130 pages seen): ticked or «الباقي سليم/جيد» on
# every kind — two, stain, tilt, base, folio, stamp, rim, tracks, edge, third, whole, sheet, and «larger» up to ×1.18
# (59305303ab81 ص 3); his remarks fell on a first page shown ×1.42 (170f ص 1), a first page cut (الفن ص 1), a box grown to
# hold a smudge (خزانة 01 ص 236), a frame read by its lines (المخصص 13 → the frame rule). So a book he never ticked shows
# only: pages he pointed at before (owner), «larger» beyond ×1.2 (beyond ×1.1 on a first, second or last page), and the
# frame rule's turns (new, never passed by him). Each such page is first reviewed by me (data/crop/self-review.tsv:
# hash12, page, sig, right | wrong | unsure, note); «right» pages leave the page, the rest stay with my note.
def doubtful(i, w, P, ruled_ok=False):
    """ruled_ok: the page's only owner entries are rulings (turn / leave / whole / window) that check_owner_rulings finds in
    today's recipe — checked by the machine, not asked again (audit rule 2)"""
    ks = w.split('+'); e = (P[i].get('enlarged') or 0) if i < len(P) else 0
    if 'owner' in ks and not ruled_ok: return 'owner'
    if 'larger' in ks and (e > 1.2 or ((i < 2 or i == len(P) - 1) and e > 1.1)): return 'larger'
    if 'frame' in ks: return 'frame'
    return None

def sig(P, i):
    """the page's recipe entry, hashed: a verdict on a page holds while this is unchanged"""
    return hashlib.md5(json.dumps(P[i] if i < len(P) else None, sort_keys=True).encode()).hexdigest()[:10]

def self_review():
    out = {}
    f = J('data', 'crop', 'self-review.tsv')
    if os.path.exists(f):
        for l in open(f, encoding='utf-8'):
            x = l.rstrip('\n').split('\t')
            if len(x) >= 4 and not l.startswith('#'): out[(x[0], int(x[1]), x[2])] = (x[3], x[4] if len(x) > 4 else '')
    return out

_old = {}
def moved(rf, when, P):
    """pages whose crop box moved > 2 pt, turn > 0.1°, or cut ↔ whole, between git's recipe as of WHEN and P"""
    if not rf: return set()
    rel = os.path.relpath(rf, ROOT)
    if (rel, when) not in _old:
        c = subprocess.run(['git', 'rev-list', '-1', f'--before={when}', 'HEAD', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        try: _old[rel, when] = json.loads(subprocess.run(['git', 'show', f'{c}:{rel}'], cwd=ROOT, capture_output=True, text=True).stdout)['pages'] if c else None
        except ValueError: _old[rel, when] = None
    O = _old[rel, when]
    if O is None: return set(range(len(P)))           # (no recipe of that hour: every page counts as moved)
    bx = lambda d: d.get('crop') or d.get('show') or [0] * 4
    mv = {i for i, (a, b) in enumerate(zip(O, P)) if ('crop' in a) != ('crop' in b) or abs((a.get('skew') or 0) - (b.get('skew') or 0)) > 0.1
          or abs((a.get('shear') or 0) - (b.get('shear') or 0)) > 0.1
          or max(abs(x - y) for x, y in zip(bx(a), bx(b))) > 2}
    return mv | set(range(len(O), len(P)))

# NEWS FOR HIM ON THE PAGE ITSELF (owner 2026-11-07: «you don't keep me updated, I don't read [the terminal] constantly …
# remarks would be on brave»): data/crop/review-news.tsv (time, Arabic text — what was done, what waits for him), newest
# first, and every remark of his that was acted on with what was done (review-closed.tsv), shown above the cards.
def news_html(E):
    rows = []
    f = J('data', 'crop', 'review-news.tsv')
    if os.path.exists(f):
        for l in open(f, encoding='utf-8'):
            x = l.rstrip('\n').split('\t', 1)
            if len(x) == 2 and not l.startswith('#'): rows.append(x)
    rows.sort(reverse=True)
    acted = []
    if os.path.exists(J('data', 'names', 'review-closed.tsv')):
        for l in open(J('data', 'names', 'review-closed.tsv'), encoding='utf-8'):
            x = l.rstrip('\n').split('\t')
            if len(x) > 3 and x[0] == 'crop-doubts' and '«' in x[3] and not x[3].startswith(('REOPEN', 'owner ticked')):
                acted.append((x[2], x[1], x[3]))
    acted.sort(reverse=True)
    if not rows and not acted: return ''
    h = '<section class="news"><h2>آخر ما جرى (يُحدَّث مع كل عمل)</h2><ul>' + ''.join(
        f'<li><b>{E(t)}</b> — {E(w)}</li>' for t, w in rows[:30]) + '</ul>'
    if acted:
        h += '<details><summary>ملاحظاتك وما فُعل بها</summary><ul>' + ''.join(
            f'<li><b>{E(d)}</b> {E(n.split("-")[0])}: {E(w)}</li>' for d, n, w in acted[:40]) + '</ul></details>'
    return h + '</section>'

def main(batches):
    logged = {}                                       # path → (day, tag, recipe) of its latest crop: a card's id is «<hash>-<tag>»,
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):   # the crop's own md5
        if len(r) > 5 and r[1] == 'crop' and (not batches or r[5].strip() in batches):          # (2026-11-03: ids were
            m = r[4].rsplit('→ md5 ', 1)[1][:7] if '→ md5 ' in r[4] else r[0][2:10].replace('-', '')  # the path's hash alone)
            o = re.search(r'original \d+ B md5 (\w+)', r[4])
            logged[r[2].removeprefix('Books/')] = (r[0][:10], m, J('data', 'crop', 'recipes', o.group(1) + '.json') if o else None)
    # THE OWNER'S TICKS HOLD PAGE BY PAGE (owner 2026-11-07 «it asks about so many books that should be already ok», «go» on
    # the audit's rules): a book he ticked (or whose remark was acted on: a row of data/names/review-closed.tsv) stays off the
    # page unless one of its pages MOVED since — more than 2 pt, 0.1°, or cut ↔ whole, the recipe of that hour (git) against
    # today's — and then only the moved pages that the method doubts are shown. A row «REOPEN» cancels the closes before it.
    refs, reopen = {}, {}                             # hash → latest tick/close time; hash → time of a REOPEN row
    if os.path.exists(J('data', 'names', 'review-closed.tsv')):
        for l in open(J('data', 'names', 'review-closed.tsv'), encoding='utf-8'):
            f = l.rstrip('\n').split('\t')
            if f[0] != 'crop-doubts' or len(f) < 3: continue
            h = f[1].split('-')[0]                    # (in file order: a REOPEN drops the closes above it, a later close counts)
            if len(f) > 3 and f[3].startswith('REOPEN'): refs.pop(h, None); reopen[h] = f[2] + ' 00:00'
            else: refs[h] = max(refs.get(h, ''), f[2] + ' 23:59')
    hist, words = {}, {}                              # hash → his remarks [(time, card, checked, words)]; hash → time of his latest words
    try:
        last = {}
        for l in open(J('data', 'names', 'review-comments.jsonl'), encoding='utf-8'):
            try: c = json.loads(l)
            except ValueError: continue
            if c.get('report') == 'crop-doubts': last[str(c.get('n'))] = c
        for n, c in last.items():
            h, t = n.split('-')[0], str(c.get('time', ''))
            hist.setdefault(h, []).append((t, n, c.get('checked'), c.get('comment', '')))
            if c.get('checked') and t > reopen.get(h, ''): refs[h] = max(refs.get(h, ''), t)
            elif c.get('comment', '').strip(): words[h] = max(words.get(h, ''), t)
    except OSError: pass
    review = self_review()
    sys.path.insert(0, J('scripts')); import check_owner_rulings as cor, unicodedata
    nfc = lambda x: unicodedata.normalize('NFC', x)
    rul = {}                                          # (path, page) → all its rulings OK?
    for st, _, path, n, *_ in cor.check(): rul[nfc(path), n] = rul.get((nfc(path), n), True) and st == 'OK'
    words_pages = {(nfc(f[0]), int(f[1])) for f in cor.rows('owner-pages.tsv')}
    out = J('site', 'crop-doubts'); os.makedirs(out, exist_ok=True)
    E, cards, clean, held, passed, cand_rows = html.escape, [], 0, 0, 0, []
    for h in sorted(os.listdir(SHEETS)) if os.path.isdir(SHEETS) else []:
        d = os.path.join(SHEETS, h)
        try: book = json.load(open(os.path.join(d, 'book.json'), encoding='utf-8'))
        except (OSError, ValueError): continue
        if book.get('path') not in logged or 'shown' not in book: continue
        if not book['shown']: clean += 1; continue
        day, tag, rf = logged[book['path']]; key = f'{h}-{tag}'
        P = (json.load(open(rf, encoding='utf-8')).get('pages') or []) if rf and os.path.exists(rf) else []
        ref = refs.get(h); open_words = words.get(h, '') > (ref or '')
        shown = [(i, w) for i, w in book['shown'] if os.path.exists(os.path.join(d, f'p{i + 1:04d}-after.jpg'))]
        if open_words:                                # (his words not yet acted on: the whole card, as before)
            pick = [(i, w, 'words') for i, w in shown]
        elif ref:                                     # (ticked: only what moved since)
            mv = moved(rf, ref, P)
            pick = [(i, w, 'moved') for i, w in shown if i in mv]
            if not pick: held += 1; continue
        else:
            pk = nfc(book['path'])
            pick = [(i, w, why) for i, w in shown for why in [doubtful(i, w, P, rul.get((pk, i + 1)) is True and (pk, i + 1) not in words_pages)] if why]
        for i, w, why in pick: cand_rows.append((h, i + 1, w, why, sig(P, i), book['path']))
        pick = [(i, w, why) for i, w, why in pick if why == 'words' or review.get((h, i + 1, sig(P, i)), ('',))[0] != 'right']
        if not pick: passed += 1; continue
        prev = sorted((x for x in hist.get(h, []) if x[1] != key), reverse=True)
        pv = '؛ '.join(f'يوم {E(t[:10])}: ' + ('علّمته «سليم»' if ch and not w.strip() else '«' + E(w.strip()) + '»' + (' وعلّمته «سليم»' if ch else ''))
                      for t, _, ch, w in prev)
        pv = f'<p class="prev">ملاحظاتك على قصّ أقدم لهذا الكتاب: {pv}</p>' if pv else ''
        figs = []; own = book.get('owner') or {}
        for i, why, sel in pick:
            b, a = f'p{i + 1:04d}-before.jpg', f'p{i + 1:04d}-after.jpg'
            if not (os.path.exists(os.path.join(d, a)) and os.path.exists(os.path.join(d, b))): continue
            for x in (a, b): shutil.copyfile(os.path.join(d, x), os.path.join(out, f'{h}-{x}'))
            cap = '؛ '.join(('نافذة وضعتُها بحكمي (لم تُشر إليها): ' if own.get(str(i + 1), '').startswith('«my judgment') else 'صفحة أشرتَ إليها من قبل: ')
                            + own.get(str(i + 1), '') if w == 'owner' else WHY.get(w, w) for w in why.split('+'))
            if sel == 'moved': cap = 'تغيّر قصّها منذ علّمتَ الكتاب «سليما» — ' + cap
            note = review.get((h, i + 1, sig(P, i)), ('', ''))[1]
            if note: cap += (' — سؤالي إليك: ' if review.get((h, i + 1, sig(P, i)), ('',))[0] == 'unsure' else ' — رأيي: ') + note
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
.news{{background:var(--card);border:2px solid #8a4b00;border-radius:10px;padding:10px 14px;margin:12px 0}} .news h2{{margin:.2em 0}} .news li{{margin:.25em 0}}
</style></head><body><main><h1>مواضع الشك في القص</h1>{news_html(E)}
<p class="lead">{len(cards)} كتابا فيها صفحات لم تُجز مثلها من قبل، أو أشرتَ إليها، أو تغيّر قصّها منذ علّمتها «سليما» — معروضة وحدها (بعد | قبل). ولم تُعرض: {held} كتابا علّمتها ولم يتحرك فيها شيء، و{passed} كتابا شكوكها من جنس ما أجزتَه من قبل (أو راجعتُها فوجدتها سليمة)، و{clean} كتابا لا شك فيها. علّم «سليم» أو اكتب ملاحظتك؛ يخرج الكتاب من الصفحة بعدها.</p>
{"".join(cards)}</main><script>
const R='crop-doubts';
async function load(){{try{{const d=await (await fetch('/api/comments?r='+R)).json();document.querySelectorAll('.review').forEach(b=>{{const x=d[b.dataset.n];if(!x)return;b.querySelector('.chk').checked=x.checked;b.querySelector('.cmt').value=x.comment;b.querySelector('.st').textContent='حُفظ '+x.time;}});}}catch(e){{}}}}
function save(b){{const st=b.querySelector('.st');st.textContent='…';fetch('/api/comment',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{report:R,n:b.dataset.n,checked:b.querySelector('.chk').checked,comment:b.querySelector('.cmt').value}})}}).then(r=>r.json()).then(j=>st.textContent='حُفظ '+j.time).catch(()=>st.textContent='لم يُحفظ');}}
document.querySelectorAll('.review').forEach(b=>{{let t;b.querySelector('.chk').addEventListener('change',()=>save(b));b.querySelector('.cmt').addEventListener('input',()=>{{clearTimeout(t);t=setTimeout(()=>save(b),800);}});}});load();
</script></body></html>'''
    open(J('site', 'crop-doubts.html'), 'w', encoding='utf-8').write(page)
    with open(J('data', 'crop', 'doubt-candidates.tsv'), 'w', encoding='utf-8') as f:    # (for my own review: self-review.tsv)
        f.write('# hash12\tpage\tkinds\twhy shown\tsig\tpath\n' + ''.join('\t'.join(map(str, r)) + '\n' for r in cand_rows))
    print(len(cards), 'books shown,', held, 'ticked and unmoved,', passed, 'passed (his tolerance / my review),', clean,
          'without doubts →', 'site/crop-doubts.html;', len(cand_rows), 'candidate pages → data/crop/doubt-candidates.tsv')

if __name__ == '__main__':
    main(set(sys.argv[1:]))

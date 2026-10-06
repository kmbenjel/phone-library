"""Report 09 «النسخ المحسنة»: the books whose scans had defects at the source (wide blank margins, dark scanner edges,
two book pages on one PDF page, bloated colour scans, damaged or cut files) and whose phone copies were fixed
(owner, 2026-10-06: describe them well, so the improved copies can later be published).
Everything comes from the logs, nothing is guessed:
  * data/changes/changes.tsv — each improved copy («improved copy (crop|split|recompress): {pages_in, pages_out,
    cropped, bytes_out, kept}» or a repair reason), then its substitution (copy → the original's place), then every
    later rename / move / deletion, replayed in order so each fix is followed to the file's current path;
  * data/phone/quality.tsv — the defects measured in the original (margins %, dark edges, spreads, KB per page);
  * data/phone/substituted.tsv — the original's size; data/phone/provenance.tsv — the original's archive.org file
    (matched by that size) and data/catalog.json — the Waqfeya record of the book; data/editions/edition-info.json —
    editor, publisher, year.
Per book: what was wrong, what was done (lossless CropBox crop / page split, or lossy recompression), pages, sizes,
source, and a ready description for publishing the improved copy. Old prints (≤ 1370 هـ / 1950 م) with a known source
and a fully fixed set are listed first as candidates. Also writes data/fixed/fixed-copies.tsv (one row per file).
Usage: python3 scripts/report_fixed.py"""
import ast, collections, csv, html, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, RawHTML, gb
J = lambda p: os.path.join(ROOT, p)
FIXDIR, ASIDE = 'نسخ محسنة للاستبدال/', 'نسخ مستبعدة/'
strip = lambda p: p[6:] if p.startswith('Books/') else p
FIXNAME = {'crop': 'قص الهوامش', 'split': 'فصل الصفحات المزدوجة', 'recompress': 'إعادة ضغط', 'repair': 'إصلاح ملف تالف أو ناقص'}
PROB = {'margins': 'هوامش بيضاء واسعة', 'dark-borders': 'حواف سوداء من الماسح', 'spreads': 'صفحتان في صفحة',
        'bloated': 'حجم مفرط', 'low-res': 'دقة منخفضة', 'mixed-sizes': 'مقاسات صفحات مختلطة', 'colour-text': 'نص ملوّن مصوّر'}

def replay():
    """→ {current path: record} for every fixed file still on the phone, and the copies still waiting"""
    copies, fixed, prev = {}, {}, {}
    for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) < 6: continue
        t, act, a, b, why, plan = r[0], r[1], strip(r[2]), strip(r[3]), r[4], r[5]
        if act == 'add' and b.startswith(FIXDIR):
            m = re.match(r'improved copy \(([^)]*)\): (\{.*\})', why)
            if m:
                try: st = ast.literal_eval(m.group(2))
                except (ValueError, SyntaxError): st = {}
                copies[b] = {'fixes': m.group(1).split(','), 'stats': st, 'why': '', 'made': t[:10], 'copy_plan': plan}
            else:
                copies[b] = {'fixes': ['repair'], 'stats': {}, 'why': why, 'made': t[:10], 'copy_plan': plan}
            continue
        if act == 'move':
            if a.startswith(FIXDIR) and not b.startswith((FIXDIR, ASIDE)):           # the copy takes the original's place
                rec = dict(copies.pop(a, {'fixes': ['?'], 'stats': {}, 'why': '', 'made': t[:10], 'copy_plan': ''}))
                rec.update({'orig': a[len(FIXDIR):], 'done': t[:10], 'plan': plan})
                if b in prev:                                                         # fixed twice: keep both steps
                    old = prev.pop(b); rec['fixes'] = sorted(set(old['fixes']) | set(rec['fixes'])); rec['earlier'] = old
                fixed[b] = rec; continue
            if b.startswith(ASIDE + '__المستبدل/') and a in fixed:                   # a fixed file replaced again
                prev[a] = fixed.pop(a); continue
            if a in copies: copies[b] = copies.pop(a); continue
            moved = [(a, fixed.pop(a))] if a in fixed else [(k, fixed.pop(k)) for k in [k for k in fixed if k.startswith(a + '/')]]
            for k, rec in moved: fixed[b + k[len(a):]] = rec
            continue
        if act == 'delete':
            fixed.pop(a, None); copies.pop(a, None)
    return fixed, copies

def main():
    idx = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
    fixed, copies = replay()
    fixed = {p: r for p, r in fixed.items() if p in idx and not p.startswith((FIXDIR, ASIDE, 'فهارس الويب/'))}
    waiting = [p for p in idx if p.startswith(FIXDIR)]
    quality = collections.defaultdict(dict)
    for r in csv.reader(open(J('data/phone/quality.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) >= 4 and r[0] in PROB: quality[r[1]][r[0]] = r[3]
    orig_size = {r['path']: int(r['original_size']) for r in csv.DictReader(open(J('data/phone/substituted.tsv'), encoding='utf-8'), delimiter='\t')}
    prov = {r['path']: r for r in csv.DictReader(open(J('data/phone/provenance.tsv'), encoding='utf-8'), delimiter='\t')}
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    info = json.load(open(J('data/editions/edition-info.json'), encoding='utf-8')) if os.path.exists(J('data/editions/edition-info.json')) else {}
    book_of = {}
    for b in cat['books']:
        for f, s in b['files']:                    # a one-file book is a plain file, or a folder holding a same-named file
            book_of[f"{b['cat']}/{b['folder']}/{f}"] = b
            if len(b['files']) == 1: book_of.setdefault(f"{b['cat']}/{f}", b)
    # ---- per file rows -----------------------------------------------------------------------------------------
    rows = []
    for p, rec in fixed.items():
        st, q = rec['stats'], quality.get(rec['orig'], {})
        pv = prov.get(p, {})
        rows.append({'path': p, 'rec': rec, 'q': q, 'book': book_of.get(p), 'size': idx[p], 'orig_size': orig_size.get(p),
                     'pages_in': st.get('pages_in'), 'pages_out': st.get('pages_out'), 'kept': st.get('kept'),
                     'archive': pv.get('archive_id', ''), 'afile': pv.get('orig_name', '')})
    os.makedirs(J('data/fixed'), exist_ok=True)
    with open(J('data/fixed/fixed-copies.tsv'), 'w', encoding='utf-8') as w:
        w.write('path\tbook\tfixes\tdefects\tpages_in\tpages_out\tarea_kept\toriginal_size\tsize\tarchive_id\tarchive_file\tfixed_on\tplan\n')
        for x in sorted(rows, key=lambda x: x['path']):
            b = x['book']
            w.write('\t'.join(str(v if v is not None else '') for v in [
                x['path'], f"{b['cat']}/{b['folder']}" if b else '', ','.join(x['rec']['fixes']), '; '.join(f'{k}: {v}' for k, v in x['q'].items()),
                x['pages_in'], x['pages_out'], x['kept'], x['orig_size'], x['size'], x['archive'], x['afile'], x['rec']['done'], x['rec']['plan']]) + '\n')
    # ---- per book ------------------------------------------------------------------------------------------------
    books = collections.OrderedDict()
    for x in sorted(rows, key=lambda x: x['path']):
        b = x['book']; key = f"{b['cat']}/{b['folder']}" if b else x['path']
        books.setdefault(key, {'b': b, 'files': []})['files'].append(x)
    entries = []
    for key, g in books.items():
        b, fs = g['b'], g['files']
        e = info.get(key, {})
        v = lambda f: (e.get(f) or {}).get('v')
        fixes = collections.Counter(f for x in fs for f in x['rec']['fixes'])
        defects = collections.Counter(k for x in fs for k in x['q'])
        kept = [x['kept'] for x in fs if isinstance(x['kept'], (int, float))]
        pin = sum(x['pages_in'] or 0 for x in fs); pout = sum(x['pages_out'] or 0 for x in fs)
        so = sum(x['orig_size'] or x['size'] for x in fs); sn = sum(x['size'] for x in fs)
        items = sorted({x['archive'] for x in fs if x['archive']})
        waq = (b or {}).get('waqfeya') or []
        h, gy = v('hijri'), v('gregorian')
        year = ' / '.join(s for s in (f'{h} هـ' if h else '', f'{gy} م' if gy else '') if s)
        old = bool((h and int(h) <= 1370) or (gy and int(gy) <= 1950))
        total = len(b['files']) if b else len(fs)
        lossless = 'recompress' not in fixes
        margin = [re.search(r'text uses (\d+)% of the width', x['q'].get('margins', '')) for x in fs]
        width = [int(m.group(1)) for m in margin if m]
        entries.append({'key': key, 'title': (b or {}).get('folder') or os.path.basename(key)[:-4], 'cat': key.split('/')[0],
                        'n': len(fs), 'total': total, 'fixes': fixes, 'defects': defects, 'kept': sum(kept) / len(kept) if kept else None,
                        'width': sum(width) / len(width) if width else None, 'pin': pin, 'pout': pout, 'so': so, 'sn': sn,
                        'items': items, 'waq': waq, 'year': year, 'old': old, 'lossless': lossless,
                        'editor': v('editor') or '', 'publisher': v('publisher') or '', 'done': max(x['rec']['done'] for x in fs),
                        'files': fs})
    # ---- report --------------------------------------------------------------------------------------------------
    R = Report('النسخ المحسنة', 'كتب كان في تصويرها الأصلي عيوب (هوامش واسعة، حواف سوداء، صفحتان في صفحة، حجم مفرط، ملفات تالفة) وأُصلحت نسخها في المكتبة')
    nf = len(rows); nb = len(entries)
    lossless_n = sum(1 for x in rows if 'recompress' not in x['rec']['fixes'])
    split_pages = sum((x['pages_out'] or 0) - (x['pages_in'] or 0) for x in rows if 'split' in x['rec']['fixes'])
    cand = [e for e in entries if e['old'] and (e['items'] or e['waq']) and e['n'] == e['total']]
    R.kpis([('كتابًا أُصلحت', f'{nb:,}'), ('ملفًا مُصلحًا', f'{nf:,}'), ('إصلاح بلا فقد (قص/فصل)', f'{lossless_n:,}'),
            ('صفحة فُصلت من صفحات مزدوجة', f'{split_pages:,}'), ('مصدر الأصل معروف', f"{sum(1 for e in entries if e['items'] or e['waq']):,} كتابًا"),
            ('مرشّحة للنشر أولًا', f'{len(cand):,} كتابًا')])
    R.note('طريقة الإصلاح: «قص الهوامش» و«فصل الصفحات» بلا فقد — لا يُعاد ترميز الصور، وإنما يُضبط إطار العرض (CropBox) لكل صفحة '
           'على حدود النص مع هامش 3٪، فتبقى صورة الماسح الأصلية كاملة داخل الملف، ويظهر النص أكبر على شاشة الهاتف. والصفحة المزدوجة '
           'تُعرض صفحتين (اليمنى أولًا). أما «إعادة الضغط» فبفقد: صور رمادية JPEG بجودة 60 ودقة لا تتجاوز 200 نقطة في البوصة، '
           'ولم تُستعمل إلا لمسوح ملونة متضخمة لنص أسود، ولا تُستعمل مع الطبعات الملونة المقصودة. كل ملف فُحص بعد الإصلاح '
           '(عدد الصفحات، الفتح) ثم حلّ محل الأصل، وحُذف الأصل.')
    R.note('للنشر لاحقًا: الأَولى الطبعات القديمة (1370 هـ / 1950 م فما قبل) التي عُرف مصدر أصلها وأُصلحت مجلداتها كلها؛ '
           'ولكل كتاب وصفٌ جاهز للنسخ (زر «وصف النشر») يذكر الأصل ورابطه وما أُصلح. حقوق الطبع يُتحقق منها قبل نشر أي طبعة حديثة. '
           'والقائمة الكاملة لكل ملف في data/fixed/fixed-copies.tsv.')
    def desc(e):
        src = ' ؛ '.join([f'archive.org/details/{i}' for i in e['items']] + [w['url'] for w in e['waq'][:1]])
        what = '، '.join(FIXNAME.get(k, k) for k in e['fixes'])
        bad = '، '.join(PROB.get(k, k) for k in e['defects'])
        ed = ' - '.join(s for s in (e['editor'] and f"تحقيق {e['editor']}", e['publisher'], e['year']) if s)
        t = (f"{e['title']} — نسخة محسّنة للقراءة على الشاشات. "
             + (f"الطبعة: {ed}. " if ed else '')
             + (f"عيوب التصوير الأصلي: {bad}. " if bad else '')
             + f"ما أُصلح: {what}" + (' دون إعادة ضغط الصور (الصورة الأصلية محفوظة كاملة في الملف)' if e['lossless'] else '') + '. '
             + f"الملفات: {e['n']}" + (f" من {e['total']}" if e['n'] != e['total'] else '') + f"، الصفحات: {e['pout'] or e['pin']}. "
             + (f"الأصل: {src}" if src else 'الأصل: غير معروف المصدر'))
        return t
    def card(e):
        """one book: a compact card on phones (the table had seven columns)"""
        link = (f"https://archive.org/details/{e['items'][0]}" if e['items'] else (e['waq'][0]['url'] if e['waq'] else None))
        x = html.escape
        title = f'<a href="{x(link, quote=True)}">{x(e["title"])}</a>' if link else x(e['title'])
        bad = '، '.join(PROB.get(k, k) + (f" ({v})" if v > 1 else '') for k, v in e['defects'].most_common())
        what = '، '.join(FIXNAME.get(k, k) + (f" ({v})" if v > 1 else '') for k, v in e['fixes'].most_common())
        gain = []
        if e['width']: gain.append(f"كان النص يشغل {e['width']:.0f}٪ من عرض الصفحة")
        if e['kept'] is not None and 'crop' in e['fixes']: gain.append(f"قُصّ {100 * (1 - e['kept']):.0f}٪ من مساحتها")
        if 'split' in e['fixes'] and e['pout'] > e['pin']: gain.append(f"{e['pin']:,} صفحة ← {e['pout']:,}")
        if 'recompress' in e['fixes'] and e['so']: gain.append(f"{gb(e['so'])} ← {gb(e['sn'])}")
        meta = ' · '.join(s for s in (e['year'], f"{e['n']} من {e['total']} ملفات" if e['total'] > 1 else '', 'بلا فقد' if e['lossless'] else 'أُعيد ضغطه') if s)
        src = 'المصدر: ' + ('، '.join(f'<a href="https://archive.org/details/{x(i)}">archive.org/{x(i)}</a>' for i in e['items'][:3])
                            + (f' · <a href="{x(e["waq"][0]["url"], quote=True)}">الوقفية</a>' if e['waq'] else '')) if (e['items'] or e['waq']) else 'المصدر: غير معروف'
        R.m.append(f"| {e['title']} | {e['year'] or '—'} | {e['n']}/{e['total']} | {bad or '—'} | {what} | {'؛ '.join(gain) or '—'} | {', '.join(e['items'][:2])} |")
        return (f'<div class="fx"><div class="t">{title}</div><div class="m">{x(meta)}</div>'
                + (f'<div><span class="k">العيب:</span> {x(bad)}</div>' if bad else '')
                + f'<div><span class="k">الإصلاح:</span> {x(what)}' + (f' — {x("؛ ".join(gain))}' if gain else '') + '</div>'
                + f'<div class="m">{src} <button type="button" class="cp" data-d="{x(desc(e), quote=True)}">وصف النشر</button></div></div>')
    MDHEAD = ['| الكتاب | سنة الطبع | الملفات | عيوب الأصل | الإصلاح | الأثر | archive.org |', '|---|---|---|---|---|---|---|']
    if cand:
        R.h2('مرشّحة للنشر أولًا: طبعات قديمة، مصدرها معروف، أُصلحت كلها')
        cand.sort(key=lambda e: (-len(e['defects']), e['kept'] if e['kept'] is not None else 1))
        R.m += MDHEAD
        R.h.append('<div class="fxs">' + ''.join(card(e) for e in cand) + '</div>')
    R.h2('كل الكتب المصلحة، حسب القسم')
    by_cat = collections.defaultdict(list)
    for e in entries: by_cat[e['cat']].append(e)
    for c in sorted(by_cat, key=lambda c: -len(by_cat[c])):
        es = sorted(by_cat[c], key=lambda e: e['title'])
        head = f"{c} — {len(es):,} كتابًا، {sum(e['n'] for e in es):,} ملفًا"
        R.m += ['', f'**{head}**', ''] + MDHEAD
        R.h.append(f'<details><summary>{html.escape(head)}</summary><div class="fxs">' + ''.join(card(e) for e in es) + '</div></details>')
    if waiting:
        R.h2('نسخ محسنة تنتظر الاستبدال')
        R.ul([p[len(FIXDIR):] for p in sorted(waiting)])
    R.h.append('''<style>.fx{border-bottom:1px solid var(--line);padding:7px 2px;font-size:.9rem;line-height:1.6}.fx .t{font-weight:700}.fx .m{color:var(--muted);font-size:.82rem}.fx .k{color:var(--muted)}button.cp{font:inherit;font-size:.78rem;border:1px solid var(--accent);color:var(--accent);background:transparent;border-radius:8px;padding:1px 8px;white-space:nowrap}</style>
<script>document.addEventListener('click',function(ev){var b=ev.target.closest('button.cp');if(!b)return;var t=b.dataset.d;
function ok(){var o=b.textContent;b.textContent='نُسخ ✓';setTimeout(function(){b.textContent=o},1800)}
function fb(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');ok()}catch(e){prompt('',t)}a.remove()}
if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(ok,fb);else fb()});</script>''')
    R.write('09 - النسخ المحسنة')
    print(f'09 - النسخ المحسنة | books {nb} files {nf} lossless {lossless_n} candidates {len(cand)} waiting {len(waiting)}')

if __name__ == '__main__':
    main()

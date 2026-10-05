"""Report 05: works present on the phone in more than one edition (طبعة) or more than one scan of the same edition —
with what is needed to decide later which copies to keep:
  per copy: edition (investigator / publisher / year from the Waqfeya record the files match byte-for-byte, else the
  name), section, volumes on the phone vs volumes of the edition (complete?), pages, size, scan quality read from the
  files (pixels across a page, colour, KB per page, blank margins, text layer), and the path;
  per work: scholars'/specialists' notes on the editions (data/editions/notes.json, sourced) and a suggestion;
  «same edition, other scan» groups: the copy that reads best at the least size is marked.
Nothing is deleted on the basis of this report: the owner decides.
Writes site/05 + reports/05 and data/editions/groups.json."""
import collections, html, json, os, re, statistics, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, RawHTML, gb
from textnorm import norm, title_key, author_tokens
J = lambda p: os.path.join(ROOT, p)

cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
INDEX = {l.split('\t', 1)[0] for l in open(J('data/phone/index-now.tsv'), encoding='utf-8')}
notes = json.load(open(J('data/editions/notes.json'), encoding='utf-8')) if os.path.exists(J('data/editions/notes.json')) else {}
insp = {}
if os.path.exists(J('data/inspect/files.jsonl')):
    for l in open(J('data/inspect/files.jsonl'), encoding='utf-8'):
        d = json.loads(l); insp[d['path']] = d

ED_STOP = set(norm('ت ط دار مكتبة مؤسسة مطبعة المطبعة الطبعة طبعة نشر للنشر والتوزيع بيروت القاهرة تصوير مصورة و مجموعة من المحققين وآخرون الإسلامية العربية').split())

def work_key(b):
    raw = b.get('title') or b['folder']
    if not re.search(r'[\u0600-\u06FF]', raw):                       # other languages: their own words
        return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', raw.lower()).split()[:4]), set()
    w = title_key(raw).split()
    k = ' '.join(w[:4])
    sec = re.search(r'قسم [^-()]+', b['folder'])                        # parts of one work (خريدة القصر) are not editions
    if sec: k += ' | ' + norm(sec.group(0)).strip()
    return k, author_tokens(b.get('author') or '')

def ed_tokens(e):
    w = lambda s: {x for x in norm(s).split() if x not in ED_STOP and len(x) > 2 and not x.isdigit()}
    return w(e['researcher']), w(e['publisher'] + ' ' + (e['edition'] if not e['researcher'] and not e['publisher'] else ''))

def same_edition(a, b):
    ra, pa = ed_tokens(a); rb, pb = ed_tokens(b)
    if ra and rb: return bool(ra & rb)                                   # investigators decide when both are known
    return bool((ra | pa) & (rb | pb))

def quality(paths):
    ds = [insp[p] for p in paths if p in insp and insp[p].get('pages')]
    if not ds: return None
    pages = sum(d['pages'] for d in ds); size = sum(d['size'] for d in ds)
    pxw, cols, marg, text = [], collections.Counter(), [], 0
    for d in ds:
        im = d.get('images') or {}
        if im.get('px_median') and d.get('page_sizes'):
            m = re.match(r'(\d+)x(\d+)', next(iter(d['page_sizes'])))
            if m and int(m.group(2)) > 0: pxw.append((im['px_median'] * int(m.group(1)) / int(m.group(2))) ** 0.5)
        for k, v in (im.get('color') or {}).items(): cols['ملون' if k in ('rgb', 'cmyk', 'icc', 'index') else ('أبيض وأسود' if im.get('bpc1_share', 0) > 0.5 else 'رمادي')] += v
        for x in d.get('margins', []):
            if not x.get('blank'): marg.append(1 - x['l'] - x['r'])
        text += d.get('text_mid_chars', 0) > 200
    return {'files': len(ds), 'pages': pages, 'kbpp': size // max(pages, 1) // 1000,
            'px': int(statistics.median(pxw)) if pxw else None, 'colour': cols.most_common(1)[0][0] if cols else '',
            'width_used': round(statistics.median(marg), 2) if marg else None, 'text': text == len(ds)}

def score(q, complete):
    """Readability first (pixels across the page, text using the width), then compactness, then completeness."""
    if not q: return -1
    s = min((q['px'] or 0) / 1400, 1.0) * 50 + (q['width_used'] or 0.7) * 20 + (10 if q['text'] else 0)
    s -= max(0, q['kbpp'] - 150) / 50                       # heavy pages cost storage without reading better
    s += 15 if complete else 0
    return round(s, 1)

def main():
    groups = collections.defaultdict(list)
    for b in cat['books']:
        if b['cat'] == 'فهارس الويب' or re.match(r'^(مؤلفات|سلسلة|مجلة)', b['folder']): continue
        k, a = work_key(b)
        if not k.strip(): continue
        groups[k].append((a, b))
    works = []
    for k, items in groups.items():
        # split one title key by clearly different authors (الأوائل للطبراني ≠ للعسكري)
        clusters = []
        for a, b in items:
            for c in clusters:
                if not a or not c['a'] or a & c['a']:
                    c['books'].append(b); c['a'] |= a; break
            else:
                clusters.append({'a': set(a), 'books': [b]})
        for c in clusters:
            if len(c['books']) > 1: works.append((k, c['books']))
    out, rows_md = [], []
    for k, books in works:
        eds = []
        for b in books:
            paths = [f"{b['cat']}/{b['folder']}/{f[0]}" if f"{b['cat']}/{b['folder']}/{f[0]}" in INDEX else f"{b['cat']}/{f[0]}" for f in b['files']]
            q = quality(paths)
            nv = re.sub(r'\D', '', str(b.get('numberOfVolumes') or ''))
            nvol = sum(1 for f in b['files'] if not re.search(r'^0+ - |\((الواجهة|المقدمة)\)', f[0]))
            complete = bool(nv) and nvol >= int(nv)
            ed = ' - '.join(x for x in [('ت ' + b['researcher']) if b.get('researcher') else '', ('ط ' + b['publisher']) if b.get('publisher') else '', b.get('yearOfPublish') or ''] if x) or b.get('edition') or ''
            eds.append({'folder': b['folder'], 'cat': b['cat'], 'edition': ed, 'researcher': b.get('researcher') or '', 'publisher': b.get('publisher') or '',
                        'files': len(b['files']), 'vols_edition': nv, 'complete': complete, 'bytes': b['bytes'], 'quality': q,
                        'score': score(q, complete), 'waqfeya': [w['url'] for w in b.get('waqfeya') or []]})
        clusters = []
        for e in eds:
            for c in clusters:
                if same_edition(e, c[0]): c.append(e); break
            else: clusters.append([e])
        for v in clusters:
            if len(v) > 1:
                best = max(v, key=lambda e: e['score'])
                for e in v: e['same_edition'] = True; e['best_scan'] = e is best
        auth = norm(books[0].get('author') or '') + ' ' + norm(' '.join(b['folder'] for b in books))
        note = next((n for n in (notes if isinstance(notes, list) else []) if (k == n['key'] or k.startswith(n['key'] + ' ')) and (not n['author'] or n['author'] in auth)), None)
        out.append({'work': k, 'title': books[0]['title'], 'author': books[0].get('author', ''), 'bytes': sum(e['bytes'] for e in eds), 'editions': eds, 'note': note})
    out.sort(key=lambda w: -w['bytes'])
    os.makedirs(J('data/editions'), exist_ok=True)
    json.dump(out, open(J('data/editions/groups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    R = Report('05 - الكتب متعددة الطبعات', 'كل كتاب على الهاتف بأكثر من طبعة أو بأكثر من تصوير للطبعة نفسها، مع ما يلزم لاتخاذ القرار لاحقًا')
    n_same = sum(1 for w in out for e in w['editions'] if e.get('same_edition'))
    R.kpis([('الكتب', len(out)), ('النسخ', sum(len(w['editions']) for w in out)), ('الحجم', gb(sum(w['bytes'] for w in out))),
            ('نسخ من الطبعة نفسها بتصوير آخر', n_same), ('عليها ملاحظات أهل العلم', sum(1 for w in out if w['note']))])
    R.note('لا يُحذف شيء بناءً على هذه الصفحة: الطبعات كلها باقية حتى تقرر. «الجودة» مقروءة من داخل الملفات: عرض الصفحة بالبكسل '
           '(فوق 1200 واضح على الهاتف)، اللون، الحجم لكل صفحة، ونسبة ما يشغله النص من عرض الصفحة. ★ = أفضل تصوير بين نسخ الطبعة الواحدة '
           '(الأوضح ثم الأخف ثم الأكمل).')
    for w in out:
        R.h3(f"{w['title']}" + (f" — {w['author']}" if w['author'] else '') + f"  ({len(w['editions'])} نسخ، {gb(w['bytes'])})")
        if w['note']:
            n = w['note']
            R.p(n.get('note', ''))
            if n.get('best'): R.p('الأولى بالاعتماد: ' + n['best'])
            if n.get('sources'): R.p('المصادر: ' + '؛ '.join(n['sources']))
        rows = []
        for e in sorted(w['editions'], key=lambda e: -e['score']):
            q = e['quality']
            qs = '—' if not q else f"{q['px'] or '?'} بكسل · {q['colour']} · {q['kbpp']} ك.ب/ص · النص {int((q['width_used'] or 0) * 100)}% من العرض" + (' · نص قابل للبحث' if q['text'] else '')
            mark = ('★ ' if e.get('best_scan') else '') + ('(نسخة أخرى من الطبعة نفسها) ' if e.get('same_edition') and not e.get('best_scan') else '')
            rows.append([mark + (e['edition'] or '—'), e['cat'], f"{e['files']}" + (f" / {e['vols_edition']}" if e['vols_edition'] else ''),
                         'كاملة' if e['complete'] else ('ناقصة' if e['vols_edition'] else '؟'), q['pages'] if q else '—', gb(e['bytes']), qs, e['folder']])
        R.table(['الطبعة', 'القسم', 'الملفات / مجلدات الطبعة', 'الاكتمال', 'الصفحات', 'الحجم', 'الجودة', 'المجلد على الهاتف'], rows)
    print(R.write('05 - الكتب متعددة الطبعات'))

if __name__ == '__main__':
    main()

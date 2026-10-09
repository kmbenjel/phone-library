"""Waqfeya records → fetch_queue.py lines (only the files each record links; AGENTS.md §3 rule 4, §4 names).

Usage: python3 scripts/waq_queue.py IDS.tsv OUT_QUEUE.tsv [--force | --complete]
  IDS.tsv: waqfeya_id[<TAB>category][<TAB>folder]   (blank = automatic: Shamela category of the title, else Waqfeya map)
Skips: records already complete on the phone (data/compare/waqfeya-matches.tsv), the same work by the same author already on
the phone under another name (scripts/samework.py; a same title by ANOTHER author no longer skips — 2026-10-08), files whose exact size is already in the phone index. Sizes come from archive.org <id>_files.xml
(cached in data/archive/files*.jsonl; new ones appended to data/archive/files6.jsonl).
Queue reason = «record name»: url  (the format scripts/additions_audit.py reads; run it with AUDIT_PLANS=<plan>)."""
import csv, glob, json, os, re, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rename_plan import clean, fit, short_title
from textnorm import title_key, norm
from samework import on_phone
J = lambda p: os.path.join(ROOT, p)

WMAP = {'كتب المجاميع': 'الجوامع', 'السلاسل': 'الجوامع', 'كتب علم النفس': 'علوم أخرى', 'كتب المنطق': 'المنطق',
        'فلسفة': 'علوم أخرى', 'كتب فهارس الحديث': 'التخريج والأطراف', 'كتب علوم القرآن': 'علوم القرآن وأصول التفسير',
        'كتب مباحث قرآنية عامة': 'علوم القرآن وأصول التفسير', 'كتب أصول التفسير': 'علوم القرآن وأصول التفسير',
        'كتب التجويد والقراءات': 'التجويد والقراءات', 'كتب التفاسير': 'التفسير', 'كتب الحديث الشريف وعلومه': 'علوم الحديث',
        'كتب مصطلح الحديث': 'علوم الحديث', 'كتب الجرح والتعديل': 'التراجم والطبقات', 'كتب الكتب الستة': 'كتب السنة',
        'كتب مسانيد الأئمة الأربعة': 'كتب السنة', 'كتب المسانيد الأخرى والجوامع': 'كتب السنة', 'باقي مجموعات الحديث': 'كتب السنة',
        'كتب التخريج والزوائد': 'التخريج والأطراف', 'كتب شروح الحديث': 'شروح الحديث', 'كتب العلل': 'العلل والسؤلات الحديثية',
        'كتب التوحيد والعقيدة': 'العقيدة', 'الشيعة والرافضة والباطنية والبهائية والقاديانية': 'الفرق والردود',
        'الفرق والأديان والردود': 'الفرق والردود', 'اليهود والنصارى والمستشرقون..': 'الفرق والردود',
        'كتب أصول الفقه وقواعده': 'أصول الفقه', 'كتب الفرائض': 'الفرائض والوصايا', 'كتب الأحوال الشخصية': 'مسائل فقهية',
        'كتب السياسة الشرعية والأحكام السلطانية': 'السياسة الشرعية والقضاء', 'كتب الفقه العام': 'الفقه العام',
        'كتب الفقه الحنفي': 'الفقه الحنفي', 'كتب الفقه المالكي': 'الفقه المالكي', 'كتب الفقه الشافعي': 'الفقه الشافعي',
        'كتب الفقه الحنبلي': 'الفقه الحنبلي', 'كتب فقه المذاهب الأخرى': 'الفقه العام', 'كتب الفتاوى': 'الفتاوى',
        'مكتبة الحج والعمرة والزيارة': 'مسائل فقهية', 'كتب فقه الحج والعمرة والزيارة..': 'مسائل فقهية',
        'كتب التزكية والأخلاق والآداب': 'الرقائق والآداب والأذكار', 'كتب الأذكار والشعائر': 'الرقائق والآداب والأذكار',
        'التصوف': 'الرقائق والآداب والأذكار', 'كتب السيرة النبوية': 'السيرة النبوية', 'كتب اللغة': 'كتب اللغة',
        'المعاجم اللغوية العربية': 'الغريب والمعاجم', 'كتب البلاغة': 'البلاغة', 'كتب النحو والصرف': 'النحو والصرف',
        'كتب العروض': 'العروض والقوافي', 'كتب الأدب': 'الأدب', 'دواوين الشعر': 'الشعر ودواوينه',
        'كتب الجغرافيا والرحلات': 'البلدان والرحلات', 'كتب التراجم والأعلام': 'التراجم والطبقات', 'كتب الأنساب': 'الأنساب',
        'كتب الثقافة الإسلامية العامة': 'كتب عامة', 'كتب الطب': 'الطب', 'فهارس المخطوطات': 'فهارس الكتب والأدلة',
        'كتب الأدلة والفهارس': 'فهارس الكتب والأدلة'}

def wcat(c):
    c = re.sub(r'^[\d.]+\s*', '', c or '').strip()
    if c in WMAP: return WMAP[c]
    if 'تاريخ' in c: return 'التاريخ'
    return ''

def load_files():
    fs = {}
    for fn in sorted(glob.glob(J('data/archive/files*.jsonl'))):
        for l in open(fn):
            try: d = json.loads(l)
            except ValueError: continue
            if d.get('files'): fs[d['id']] = {f['name']: int(f.get('size') or 0) for f in d['files']}
    return fs

def fetch_files(i):
    try:
        x = urllib.request.urlopen(f'https://archive.org/download/{i}/{i}_files.xml', timeout=60).read()
        return i, [{'name': f.get('name'), 'size': int((f.findtext('size') or 0))} for f in ET.fromstring(x).iter('file')]
    except Exception as e:
        return i, None

LINK = re.compile(r'archive\.org/(?:details|download|stream)/([^/\s]+)/(.+?)\s*$')

def person(a):
    a = re.split(r'[؛;]', a or '')[0].strip()
    if '،' in a:                                   # "العمران، علي بن محمد بن حسين" → "علي بن محمد بن حسين العمران"
        last, first = [x.strip() for x in a.split('،', 1)]
        a = f'{first} {last}' if len(first) < 40 else last
    return a

def book_title(name):
    t = re.sub(r'\s+-\s+(ط|ت)\s*[.:]?\s.*$', '', name).strip()
    return t

def main():
    ids_f, out = sys.argv[1], sys.argv[2]; force = '--force' in sys.argv
    complete = '--complete' in sys.argv          # finish a partial book: no record-level skips, keep the per-file size skip
    recs = {}
    for fn in ('data/waqfeya/details.jsonl', 'data/waqfeya/details2.jsonl'):
        for l in open(J(fn)):
            d = json.loads(l); recs.setdefault(d['_id'], d)
    status = {r['waqfeya_id']: r['status'] for r in csv.DictReader(open(J('data/compare/waqfeya-matches.tsv')), delimiter='\t')}
    sham = {}
    for r in csv.DictReader(open(J('data/shamela/books.tsv')), delimiter='\t'):
        sham.setdefault(title_key(r['title']), r['category'])
    cat_titles = {}
    for r in csv.DictReader(open(J('data/catalog.tsv')), delimiter='\t'):
        cat_titles.setdefault(title_key(r['title']), []).append(r['folder'])
    idx = sorted(glob.glob(J('data/phone/index-2026-*.tsv')))[-1]
    sizes = {int(s) for p, s in csv.reader(open(idx), delimiter='\t') if s.isdigit()}
    rows = [l.rstrip('\n').split('\t') for l in open(ids_f) if l.strip() and not l.startswith('#')]
    files = load_files()
    need = set()
    for r in rows:
        d = recs.get(r[0])
        for x in (d or {}).get('links') or []:
            m = LINK.search(x.get('url', ''))
            if m and m.group(1) not in files: need.add(m.group(1))
    if need:
        with ThreadPoolExecutor(16) as ex, open(J('data/archive/files6.jsonl'), 'a') as w:
            for i, fl in ex.map(fetch_files, sorted(need)):
                if fl is not None:
                    w.write(json.dumps({'id': i, 'files': fl}, ensure_ascii=False) + '\n')
                    files[i] = {f['name']: f['size'] for f in fl}
    lines, tot = [], 0
    for r in rows:
        d = recs.get(r[0])
        if not d: print('NO RECORD', r[0]); continue
        name = d['name'].strip(); t = clean(book_title(name)); tk = title_key(t)
        if status.get(r[0]) == 'complete' and not (force or complete): print('ON PHONE', name[:70]); continue
        pub = clean(re.split(r'\s+-\s+', d.get('publisher') or '')[0])
        inv = clean(d.get('investigator') or '')
        auth_full = (d.get('author') or {}).get('name', '')
        here = [] if (force or complete) else on_phone(t, auth_full)   # same work, same author's surname (scripts/samework.py)
        if here:
            print('ON PHONE AS', name[:60], '→', here[0][:80]); continue
        if not (force or complete) and tk in cat_titles and not on_phone(t, auth_full) and auth_full:
            print('SAME TITLE, OTHER AUTHOR (queued)', name[:50], '≠', cat_titles[tk][0][:70])   # 2026-10-08: الناسخ والمنسوخ
        cat = (r[1] if len(r) > 1 and r[1] else '') or sham.get(tk) or wcat(d.get('category', {}).get('name'))
        if not cat: print('NO CATEGORY', name[:70], d.get('category', {}).get('name')); continue
        auth = person(d.get('author', {}).get('name'))
        if auth in ('مجموعة من المؤلفين', 'كتاب سماوي'): auth = ''
        ed = f'ت {inv}' + (f' - {pub}' if pub else '') if inv else (f'ط {pub}' if pub else '')
        if auth and norm(auth) in norm(t): auth = ''
        folder = (r[2] if len(r) > 2 and r[2] else '')
        if not folder:
            for cand in (t + (f' - {auth}' if auth else '') + (f' ({ed})' if ed else ''), t + (f' - {auth}' if auth else ''), t):
                if len(clean(cand).encode()) <= 200: folder = clean(cand); break
            else: folder = fit(clean(t), 200)
        links = []
        for x in d.get('links') or []:
            m = LINK.search(x.get('url', ''))
            if not m: continue
            item, fn = m.group(1), urllib.parse.unquote(m.group(2)).strip()
            if not fn.lower().endswith('.pdf'): fn += '.pdf'
            sz = files.get(item, {}).get(fn)
            if not sz: print('  MISSING FILE', item, fn, '|', name[:50]); continue
            links.append((item, fn, sz, x['title'].strip()))
        if not links: print('NO FILES', name[:70]); continue
        vols = {}
        for item, fn, sz, lab in links:
            m = re.match(r'^(\d{1,3})(?:-(\d{1,3}))?_', fn)
            vols[fn] = int(m.group(1)) if m else None
        multi = len({v for v in vols.values() if v is not None and v > 0}) > 1
        width = max(2, len(str(max([v for v in vols.values() if v is not None] or [0]))))
        short = clean(short_title(t, auth))
        used = set(); seen = set()
        for item, fn, sz, lab in links:
            if (item, fn) in seen: continue
            seen.add((item, fn))
            if sz in sizes and not force: print('  SAME SIZE ON PHONE', fn, name[:50]); continue
            base = re.sub(r'\.pdf$', '', fn, flags=re.I)
            pref = bool(re.search(r'\d(p|ps)$', base)) or 'مقدم' in lab
            lab2 = re.sub(r'^\s*(تحميل|تصفح)\s*', '', lab)
            lab2 = re.sub(r'^\(\s*[\d\-\s]+\)\s*', '', lab2).strip()
            lab2 = clean(re.sub(r'\s*\*.*$', '', lab2))
            v = vols[fn]
            if multi and v is not None:
                if v == 0: label = 'الواجهة' if not pref else 'المقدمة'
                elif pref: label = 'مقدمة التحقيق' if not lab2 or lab2 in ('مقدمة التحقيق', 'المقدمة') else re.sub(r'\s*\((مقدمة التحقيق)\)', r' - \1', lab2)
                else: label = lab2 if lab2 and lab2 not in ('الكتاب',) and norm(lab2) != norm(t) else ''
                fname = f'{v:0{width}d} - {short}' + (f' ({fit(label, 110)})' if label else '') + '.pdf'
            else:
                if pref: fname = f'{fit(t, 150)} (مقدمة التحقيق).pdf'
                elif lab2 in ('', 'الكتاب', 'الكتاب كاملا') or norm(lab2) == norm(t): fname = f'{fit(t, 180)}.pdf'
                elif lab2 == 'الواجهة': fname = f'{fit(t, 150)} (الواجهة).pdf'
                else: fname = f'{fit(t, 100)} ({fit(lab2, 80)}).pdf'
            fname = clean(fname[:-4]) + '.pdf'
            k = 2
            while fname in used: fname = re.sub(r'( \(\d\))?\.pdf$', f' ({k}).pdf', fname); k += 1
            used.add(fname)
            url = f'https://archive.org/download/{item}/{urllib.parse.quote(fn)}'
            lines.append((url, sz, f'Books/{cat}/{folder}/{fname}', f'«{name}»: https://archive.org/download/{item}/{fn}'))
            tot += sz
    with open(out, 'w') as w:
        for x in lines: w.write('\t'.join(map(str, x)) + '\n')
    print(f'{len(lines)} files, {tot/1e9:.2f} GB → {out}')

if __name__ == '__main__':
    main()

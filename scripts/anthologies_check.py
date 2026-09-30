"""Which major poetry anthologies (جمهرات ومختارات، قديمًا وحديثًا) are missing from the phone, and are they on Waqfeya?
The list below is a starting canon (edit freely). Presence = title match in data/catalog.json (folder titles, Waqfeya
names of matched files); Waqfeya = best-visited record with title (+author hint) match, with size of its PDFs.
Usage: python3 scripts/anthologies_check.py  -> prints a table and writes data/compare/anthologies.tsv"""
import csv, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from textnorm import title_key, norm
J = lambda p: os.path.join(ROOT, p)

# (group, title variants separated by |, author hint)
CANON = [
 ('المعلقات وشروحها', 'شرح المعلقات السبع|شرح المعلقات السبع للزوزني|المعلقات السبع', 'الزوزني'),
 ('المعلقات وشروحها', 'شرح القصائد السبع الطوال الجاهليات', 'الأنباري'),
 ('المعلقات وشروحها', 'شرح القصائد العشر', 'التبريزي'),
 ('المعلقات وشروحها', 'شرح القصائد التسع المشهورات', 'النحاس'),
 ('الجمهرات والمختارات القديمة', 'المفضليات', 'الضبي'),
 ('الجمهرات والمختارات القديمة', 'الأصمعيات', 'الأصمعي'),
 ('الجمهرات والمختارات القديمة', 'جمهرة أشعار العرب', 'القرشي'),
 ('الجمهرات والمختارات القديمة', 'شعر الهذليين|ديوان الهذليين|شرح أشعار الهذليين', ''),
 ('الجمهرات والمختارات القديمة', 'منتهى الطلب من أشعار العرب', 'ميمون'),
 ('الجمهرات والمختارات القديمة', 'مختارات شعراء العرب', 'الشجري'),
 ('الجمهرات والمختارات القديمة', 'الاختيارين', 'الأخفش'),
 ('الحماسات وشروحها', 'ديوان الحماسة|الحماسة', 'تمام'),
 ('الحماسات وشروحها', 'شرح ديوان الحماسة', 'المرزوقي'),
 ('الحماسات وشروحها', 'شرح ديوان الحماسة', 'التبريزي'),
 ('الحماسات وشروحها', 'الوحشيات|الحماسة الصغرى', 'تمام'),
 ('الحماسات وشروحها', 'الحماسة', 'البحتري'),
 ('الحماسات وشروحها', 'الحماسة البصرية', 'البصري'),
 ('الحماسات وشروحها', 'الحماسة الشجرية', 'الشجري'),
 ('الحماسات وشروحها', 'الأشباه والنظائر من أشعار المتقدمين|حماسة الخالديين', 'الخالدي'),
 ('الحماسات وشروحها', 'الحماسة المغربية', 'الجراوي'),
 ('مختارات الشعراء وتراجمهم', 'الشعر والشعراء', 'قتيبة'),
 ('مختارات الشعراء وتراجمهم', 'طبقات فحول الشعراء', 'الجمحي'),
 ('مختارات الشعراء وتراجمهم', 'الأغاني', 'الأصفهاني'),
 ('مختارات الشعراء وتراجمهم', 'معجم الشعراء', 'المرزباني'),
 ('مختارات الشعراء وتراجمهم', 'يتيمة الدهر', 'الثعالبي'),
 ('مختارات الشعراء وتراجمهم', 'تتمة اليتيمة', 'الثعالبي'),
 ('مختارات الشعراء وتراجمهم', 'دمية القصر', 'الباخرزي'),
 ('مختارات الشعراء وتراجمهم', 'خريدة القصر', 'الأصفهاني'),
 ('مختارات الشعراء وتراجمهم', 'الذخيرة في محاسن أهل الجزيرة', 'بسام'),
 ('مختارات الشعراء وتراجمهم', 'قلائد العقيان', 'خاقان'),
 ('مختارات الشعراء وتراجمهم', 'ريحانة الألبا', 'الخفاجي'),
 ('مختارات الشعراء وتراجمهم', 'سلافة العصر', 'معصوم'),
 ('مختارات الشعراء وتراجمهم', 'نفحة الريحانة', 'المحبي'),
 ('المغرب والأندلس', 'النبوغ المغربي', 'كنون'),
 ('المغرب والأندلس', 'روضة الآس', 'المقري'),
 ('المغرب والأندلس', 'المغرب في حلى المغرب', 'سعيد'),
 ('المغرب والأندلس', 'نفح الطيب', 'المقري'),
 ('المغرب والأندلس', 'زاد المسافر', 'إدريس'),
 ('الحديث والمعاصر', 'مختارات البارودي', 'البارودي'),
 ('الحديث والمعاصر', 'مجاني الأدب', 'شيخو'),
 ('الحديث والمعاصر', 'شعراء النصرانية', 'شيخو'),
 ('الحديث والمعاصر', 'مختار الأغاني', 'منظور'),
 ('الحديث والمعاصر', 'روائع الشعر العربي|موسوعة روائع الشعر العربي', ''),
 ('الحديث والمعاصر', 'معجم البابطين', 'البابطين'),
 ('الحديث والمعاصر', 'ديوان الشعر العربي', 'أدونيس'),
]

def auth_ok(hint, *texts):
    if not hint: return True
    h = norm(hint).removeprefix('ال')
    return any(h in norm(t or '') for t in texts)

cat = json.load(open(J('data/catalog.json')))
wrows = list(csv.DictReader(open(J('data/compare/waqfeya-matches.tsv')), delimiter='\t'))
out = []
for group, titles, hint in CANON:
    found = None
    for t in titles.split('|'):
        k = title_key(t)
        for b in cat['books']:
            ks = {title_key(b['title'])} | {title_key(w['name']) for w in b.get('waqfeya', [])}
            if any(x == k or x.startswith(k + ' ') for x in ks) and (not b.get('author') or auth_ok(hint, b['folder'], b.get('author', ''), ' '.join(w['name'] for w in b.get('waqfeya', [])))):
                found = b; break
        if found: break
    best = None
    if not found:
        cands = [r for t in titles.split('|') for r in wrows
                 if (title_key(r['name']) == title_key(t) or title_key(r['name']).startswith(title_key(t) + ' ')) and auth_ok(hint, r['author'], r['name'])]
        if not cands:   # wider: every word of the title appears in the Waqfeya name (wording varies)
            cands = [r for t in titles.split('|') for r in wrows if set(norm(t).split()) <= set(norm(r['name']).split()) and auth_ok(hint, r['author'], r['name'])]
        cands = [r for r in cands if float(r['size_mb'] or 0) > 0] or cands
        best = max(cands, key=lambda r: int(r['visits'] or 0)) if cands else None
    out.append([group, titles.split('|')[0], hint, 'موجود' if found else 'غير موجود',
                (found['cat'] + ' / ' + found['folder']) if found else (best['name'] if best else '— ليس في الوقفية'),
                '' if found or not best else best['size_mb'], '' if found or not best else best['url']])
csv.writer(open(J('data/compare/anthologies.tsv'), 'w'), delimiter='\t').writerows(out)
for r in out:
    print(f'{r[3]:9s} | {r[0][:18]:18s} | {r[1]} ({r[2]}) | {r[4][:80]} {("| " + str(r[5]) + " MB") if r[5] else ""}')

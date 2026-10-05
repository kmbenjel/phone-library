"""Report 05: double-editioned books on phone (titles present in multiple editions/folders)."""
import html, json, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, RawHTML, pct
from textnorm import norm, title_key, author_tokens

J = lambda p: os.path.join(ROOT, p)

cat = json.load(open(J('data/catalog.json')))

def book_group_key(b):
    t = b.get('title', '').strip()
    fld = b.get('folder', '').strip()
    if '/' in fld:
        _, fld = fld.rsplit('/', 1)

    # Check if Arabic title
    has_arabic = bool(re.search(r'[\u0600-\u06FF]', t or fld))
    if not has_arabic:
        # English book: normalize latin title
        base = re.sub(r'\s*-\s*OpenStax.*', '', fld, flags=re.I)
        base = re.sub(r'\s*\b\d+e\b', '', base, flags=re.I).strip().lower()
        return ('en', base, '')
    
    # Arabic title
    tk = title_key(t)
    if not tk:
        tk = title_key(fld)
    
    # Author
    a = b.get('author', '').strip()
    if not a:
        m = re.match(r'^[^(]+ - ([^(]+)', fld)
        if m:
            cand_a = m.group(1).strip()
            if not cand_a.startswith(('ط.', 'ت ', 'ت.', 'ط ')):
                a = cand_a
    
    at = sorted(author_tokens(a))
    ak = at[0] if at else ''
    return ('ar', tk, ak)

groups = defaultdict(list)
for b in cat['books']:
    k = book_group_key(b)
    if k[1]:
        groups[k].append(b)

multis = {k: v for k, v in groups.items() if len(v) > 1}
total_titles = len(multis)
total_folders = sum(len(v) for v in multis.values())
total_files = sum(len(b.get('files', [])) for v in multis.values() for b in v)
total_mb = sum(
    sum(f.get('size', 0) if isinstance(f, dict) else f[1] for f in b.get('files', []))
    for v in multis.values() for b in v
) / 2**20

R = Report('الكتب متعددة الطبعات',
           f'فهرس تفصيلي بالكتب التي تتوفر منها أكثر من طبعة أو نسخة على الهاتف ({total_titles:,} عنوانًا في {total_folders:,} مجلدًا)')

R.kpis([
    ('العناوين المتكررة', f'{total_titles:,}'),
    ('المجلدات / الطبعات', f'{total_folders:,}'),
    ('إجمالي الملفات', f'{total_files:,}'),
    ('الحجم الإجمالي', f'{total_mb / 1024:,.1f} GB' if total_mb >= 1024 else f'{total_mb:,.0f} MB')
])

R.note('هذا الفهرس يجمع العناوين التي يمتلك الهاتف منها نسختين أو أكثر لنفس المؤلف (طبعات مختلفة، أو تحقيقات متعددة، أو تصويرات متباينة). '
       'يمكنك الاستفادة منه للمقارنة بين التحقيقات أو مراجعة الطبعات التي تفضل الاحتفاظ بها.')

# Table of Categories breakdown
by_cat = defaultdict(int)
for k, v in multis.items():
    for b in v:
        by_cat[b['cat']] += 1

trs_cat = []
for c, cnt in sorted(by_cat.items(), key=lambda x: -x[1]):
    trs_cat.append([c, cnt, pct(cnt, total_folders)])
R.h2('توزيع الطبعات المتعددة حسب الأقسام', 'cats')
R.table(['قسم الهاتف', 'عدد الطبعات / المجلدات', 'النسبة'], trs_cat, numeric=(1, 2))

# Detailed list sorted by number of editions descending, then title
R.h2('قائمة العناوين والطبعات المتوفرة', 'list')

trs = []
sorted_multis = sorted(multis.items(), key=lambda x: (-len(x[1]), x[1][0].get('title', '')))

for k, books in sorted_multis:
    first_b = books[0]
    title = first_b.get('title', k[1])
    author = first_b.get('author', '')
    if not author:
        f_clean = first_b['folder'].rsplit('/', 1)[-1]
        m = re.match(r'^[^(]+ - ([^(]+)', f_clean)
        if m and not m.group(1).strip().startswith(('ط.', 'ت ', 'ت.', 'ط ')):
            author = m.group(1).strip()
    
    header_label = title
    if author:
        header_label += f' — <span class="sub">{html.escape(author)}</span>'

    editions_info = []
    for b in books:
        n_files = len(b.get('files', []))
        sz_mb = sum(f.get('size', 0) if isinstance(f, dict) else f[1] for f in b.get('files', [])) / 2**20
        fld = html.escape(b['folder'])
        cat_name = html.escape(b['cat'])
        
        # Highlight commercial or renowned editions visually
        badge = ''
        if any(w in b['folder'] for w in ['العلمية', 'دار الكتب العلمية', 'دار الحديث', 'التوفيقية']):
            badge = ' <span class="bad" style="font-size:0.8rem; border:1px solid currentColor; border-radius:4px; padding:1px 4px;">طبعة تجارية</span>'
        elif any(w in b['folder'] for w in ['الرسالة', 'ابن عفان', 'هجر', 'المنهاج', 'الغرب الإسلامي', 'أم القرى', 'المجمع']):
            badge = ' <span class="good" style="font-size:0.8rem; border:1px solid currentColor; border-radius:4px; padding:1px 4px;">طبعة معتمدة</span>'

        editions_info.append(
            f'<li><b>[{cat_name}]</b> {fld}{badge} '
            f'<span class="sub" style="font-size:0.85rem;">({n_files} م · {sz_mb:.1f} MB)</span></li>'
        )
    
    ed_html = RawHTML(
        f'<div style="font-weight:bold; margin-bottom:4px;">{header_label}</div>'
        f'<ul style="margin:4px 0 8px; padding-inline-start:1.4em; line-height:1.7;">'
        + ''.join(editions_info)
        + '</ul>'
    )
    trs.append([RawHTML(f'<b>{html.escape(title)}</b>' + (f'<div class="sub">{html.escape(author)}</div>' if author else '')), len(books), ed_html])

R.table(['الكتاب والمؤلف', 'عدد الطبعات', 'بيان الطبعات والمجلدات على الهاتف'], trs, numeric=(1,))

print(R.write('05 - الكتب متعددة الطبعات'))

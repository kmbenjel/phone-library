"""Report 06: فهرس المنظومات وشروحها — the poems that carry the sciences (المتون المنظومة) and their commentaries.
Part 1 — the canon of each science (data/mappings/manzumat-canon.tsv): the poem itself on the phone (متن), every
commentary/gloss on the phone, and, when the poem or no commentary is on the phone, what Waqfeya offers (tick to
download, codes w:<id>).
Part 2 — every other poem on the phone (title words نظم/منظومة/ألفية/أرجوزة/لامية/نونية/… ), by section, with its
commentaries when the library has them.
Replaces the old static «فهرس خزانة المنظومات العلمية» (a snapshot of a blog list with obsolete sections)."""
import collections, csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, RawHTML, gb
from textnorm import norm
J = lambda p: os.path.join(ROOT, p)
WAQ = 'https://waqfeya.net/books/'
MARK = re.compile(r'(^|\s)(نظم|منظومه|منظومة|الفيه|ألفية|الفية|ارجوزه|أرجوزة|لاميه|لامية|نونيه|نونية|ميميه|ميمية|تائيه|تائية|داليه|دالية|رائيه|رائية|بائيه|بائية|همزيه|همزية|قصيده|قصيدة|مقصوره|مقصورة|مزدوجه|مزدوجة|الرجز)(\s|$)')
SHARH = re.compile(r'^(شرح|حاشيه|تعليق|فتح|التعليق|الشرح|اتحاف|اسعاف|منحه|نيل|توضيح|تيسير|تقريرات|الحواشي|ختم|الطره|طره)\b')
ABOUT = re.compile(r'(^|\s)(شرح|بشرح|حاشيه|طره|توشيح|احمرار|الاحمرار|ختم|دراسه|تقريرات|تعليق|تعليقات)(\s|$)')

def books():
    cat = json.load(open(J('data/catalog.json'), encoding='utf-8'))
    idx = {p for p in (l.split('\t', 1)[0] for l in open(J('data/phone/index-now.tsv'), encoding='utf-8'))}
    out = []
    for b in cat['books']:
        if b['cat'] in ('فهارس الويب', 'نسخ محسنة للاستبدال', 'نسخ مستبعدة'): continue
        name = b['folder']; t = norm(b.get('title') or name)
        out.append({'title': b.get('title') or name, 'n': t, 'nfull': norm(name), 'author': b.get('author', ''), 'cat': b['cat'],
                    'folder': name, 'files': len(b['files']), 'bytes': b['bytes'], 'edition': ' - '.join(x for x in [
                        ('ت ' + b['researcher']) if b.get('researcher') else '', ('ط ' + b['publisher']) if b.get('publisher') else ''] if x) or b.get('edition', '')})
    return out

def waqfeya():
    rows = []
    global PERMA
    PERMA = {}
    for l in open(J('data/waqfeya/books.jsonl'), encoding='utf-8'):
        d = json.loads(l); PERMA[d['_id']] = d.get('permalink', ''); rows.append((d['_id'], d.get('name', ''), norm(d.get('name', '')), (d.get('author') or {}).get('name', '') if isinstance(d.get('author'), dict) else '', d.get('slug') or ''))
    return rows

def main():
    B = books(); W = waqfeya()
    status = {r['waqfeya_id']: r['status'] for r in csv.DictReader(open(J('data/compare/waqfeya-matches.tsv'), encoding='utf-8'), delimiter='\t')}
    urls = {r['waqfeya_id']: r['url'] for r in csv.DictReader(open(J('data/compare/waqfeya-matches.tsv'), encoding='utf-8'), delimiter='\t')}
    canon = [l.rstrip('\n').split('\t') for l in open(J('data/mappings/manzumat-canon.tsv'), encoding='utf-8') if l.strip() and not l.startswith('#')]
    used = set()
    R = Report('06 - فهرس المنظومات وشروحها', 'المتون المنظومة في كل فن، وما على الهاتف من نصها وشروحها وحواشيها، وما ينقص منها')
    per_sci = collections.defaultdict(list)
    have_poem = have_sharh = 0
    for sci, poem, poet, keys, sh in canon:
        k = [norm(x) for x in keys.split('|') if x.strip()]
        s = [norm(x) for x in sh.split('|') if x.strip()]
        poems, sharhs = [], []
        for i, b in enumerate(B):
            hit_poem = any(x in b['n'] or x in b['nfull'] for x in k)
            on = hit_poem and any(('علي ' + x) in b['n'] for x in k)                  # «… على ألفية ابن مالك»
            hit_sharh = any(x in b['n'] for x in s) or (hit_poem and (SHARH.match(b['n']) or ABOUT.search(b['n']) or on))
            if hit_sharh: sharhs.append(b); used.add(i)
            elif hit_poem: poems.append(b); used.add(i)
        have_poem += bool(poems); have_sharh += bool(sharhs)
        offer = []
        if not poems or not sharhs:
            for wid, name, n, au, slug in W:
                if any(x in n for x in k + s) and status.get(wid) in (None, 'missing', 'partial'):
                    offer.append((wid, name))
        per_sci[sci].append((poem, poet, poems, sharhs, offer[:4]))
    R.kpis([('منظومات المتون المعتمدة', len(canon)), ('نصها على الهاتف', have_poem), ('لها شرح على الهاتف', have_sharh),
            ('منظومات أخرى على الهاتف', 0)])
    R.note('القسم الأول: أشهر المنظومات التي تُدرَّس في كل فن، ومعها ما على الهاتف من نصها (المتن) ومن شروحها وحواشيها. '
           'إذا نقص المتن أو لم يوجد له شرح، تُعرض الكتب المتاحة في الوقفية مع مربع اختيار للتحميل. القسم الثاني: سائر المنظومات على الهاتف.')
    for sci in sorted(per_sci):
        R.h2(sci)
        rows, picks = [], []
        for poem, poet, poems, sharhs, offer in per_sci[sci]:
            p_txt = RawHTML('<br>'.join(f'{b["folder"]} <span class="sub">({b["cat"]}، {gb(b["bytes"])})</span>' for b in poems) or '<span class="bad">ليس على الهاتف</span>')
            s_txt = RawHTML('<br>'.join(f'{b["folder"]} <span class="sub">({b["files"]} م، {gb(b["bytes"])})</span>' for b in sorted(sharhs, key=lambda b: -b['bytes'])) or '—')
            o_txt = RawHTML('<br>'.join(f'<a href="{urls.get(w) or WAQ + PERMA.get(w, "")}">{n}</a>' for w, n in offer) or '')
            rows.append([f'{poem} — {poet}', p_txt, f'{len(sharhs)}', s_txt, o_txt])
            picks.append((f'w:{offer[0][0]}', offer[0][1]) if offer else None)
        R.table(['المنظومة — الناظم', 'نص المنظومة على الهاتف', 'عدد الشروح', 'الشروح والحواشي على الهاتف', 'متاح في الوقفية'], rows, numeric=(2,), pick=picks)
    # part 2: all other poems on the phone
    others = collections.defaultdict(list)
    for i, b in enumerate(B):
        if i in used: continue
        if MARK.search(' ' + b['n'] + ' ') or MARK.search(' ' + norm(b['title']) + ' '):
            others[b['cat']].append(b)
    total_others = sum(len(v) for v in others.values())
    R.h[0] = R.h[0].replace('<b>0</b><span>منظومات أخرى على الهاتف', f'<b>{total_others}</b><span>منظومات أخرى على الهاتف')
    R.m = [x.replace('منظومات أخرى على الهاتف:** 0', f'منظومات أخرى على الهاتف:** {total_others}') for x in R.m]
    R.h2('سائر المنظومات على الهاتف (حسب القسم)')
    for cat in sorted(others, key=lambda c: -len(others[c])):
        v = sorted(others[cat], key=lambda b: b['title'])
        R.table(['المنظومة أو شرحها', 'المؤلف', 'الطبعة', 'الملفات', 'الحجم'],
                [[b['folder'], b['author'], b['edition'] or '—', b['files'], gb(b['bytes'])] for b in v],
                numeric=(3,), fold=f'{cat} ({len(v)})')
    print(R.write('06 - فهرس المنظومات وشروحها'), '| canon', len(canon), 'poem on phone', have_poem, 'with commentary', have_sharh, '| other poems', total_others)

if __name__ == '__main__':
    main()

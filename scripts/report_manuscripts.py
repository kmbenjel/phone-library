"""Report 10 «فهرس المخطوطات» (owner 2026-11-02, decisions row 86: «فهرس خاص بمخطوطات المكتبة ومصادرها»): every manuscript
in Books/, where the manuscript itself is kept and where our copy came from, and its printed edition in the library.
  * data/names/manuscripts.tsv — one row per file, by hand from the reading records: the holding library only as the book
    shows it (empty = not read yet, never guessed); a path there is followed through later moves in changes.tsv;
  * the copy's source: the first `add` row of the file in changes.tsv, else data/phone/provenance.tsv.
Files of one title are one row. «(من صور المخطوطات)» files are pictures in a printed edition's set: not listed.
Usage: python3 scripts/report_manuscripts.py"""
import collections, csv, os, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from report_lib import Report, gb
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
UNKNOWN = 'لم يُعرف بعد'

def main():
    idx = {}
    for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8'):
        p, s = l.rstrip('\n').split('\t')[:2]; idx[N(p)] = int(s)
    moved, added, back = {}, {}, collections.defaultdict(list)
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 3 and r[1] == 'move':
            a, b = N(r[2].removeprefix('Books/')), N(r[3].removeprefix('Books/')); moved[a] = b; back[b].append(a)
        elif len(r) > 3 and r[1] == 'add' and not r[2].startswith('phone:'): added[N(r[3].removeprefix('Books/'))] = r[2]
    def now(p):
        p = N(p)
        for _ in range(40):
            if p in idx or p not in moved: break
            p = moved[p]
        return p
    def origin(p):
        seen, todo = set(), [p]
        while todo:
            x = todo.pop()
            if x in seen: continue
            seen.add(x)
            if x in added: return added[x]
            todo += back.get(x, [])
        return ''
    prov = {N(r['path']): r for r in csv.DictReader(open(J('data', 'phone', 'provenance.tsv'), encoding='utf-8'), delimiter='\t')}
    works = collections.OrderedDict()
    for r in csv.DictReader((l for l in open(J('data', 'names', 'manuscripts.tsv'), encoding='utf-8') if not l.startswith('#')), delimiter='\t', quoting=csv.QUOTE_NONE):
        p = now(r['path'])
        if p not in idx: print('gone:', r['path'][:110]); continue
        url = origin(p)
        if not url and prov.get(p, {}).get('archive_id') and 'الرسالة' not in prov[p].get('archive_title', ''):      # (a size match on a magazine is chance)
            url = 'https://archive.org/details/' + prov[p]['archive_id']
        w = works.setdefault(r['title'], dict(r, section=p.split('/')[0], files=0, size=0, url=url))
        w['files'] += 1; w['size'] += idx[p]; w['url'] = w['url'] or url; w['holding'] = w['holding'] or r['holding']
        printed = now(r['printed']) if r['printed'] else ''
        w['printed'] = printed.rsplit('/', 1)[-1].removesuffix('.pdf') if printed in idx else ''
    rows = sorted(works.values(), key=lambda w: (w['section'], w['title']))
    held = collections.Counter((w['holding'].split('،')[0].split(' (')[0] if w['holding'] else UNKNOWN) for w in rows)
    R = Report('فهرس المخطوطات', 'مخطوطات المكتبة ومصادرها: أين يحفظ المخطوط، ومن أين جاءت نسختنا، وهل في المكتبة مطبوعه')
    R.kpis([('مخطوطا', f'{len(rows):,}'), ('ملفا', f'{sum(w["files"] for w in rows):,}'), ('الحجم', gb(sum(w['size'] for w in rows))),
            ('عُرفت خزانته', f'{len(rows) - held[UNKNOWN]:,}'), ('عُرف مصدر نسخته', f'{sum(1 for w in rows if w["url"]):,}'), ('له مطبوع في المكتبة', f'{sum(1 for w in rows if w["printed"]):,}')])
    R.note('الخزانة تثبت هنا كما تظهر في الكتاب نفسه (ختم، بطاقة، تملك)، وما لم يقرأ بعد لا يخمَّن. أكثر النسخ من رفع أبي يعلى البيضاوي (ملتقى أهل الحديث) على archive.org. '
           'ملفات «من صور المخطوطات» صور ضمن طبعات محققة، فليست هنا. وما كان بخط مغربي في إطار مطرد قرئ بالعين: ثمانية ملفات منها طبعات حجرية لا مخطوطات (خطة 392)، فأخرجت من هذا الفهرس.')
    R.h2('الخزائن')
    R.table(['الخزانة', 'مخطوطات'], [[k, v] for k, v in sorted(held.items(), key=lambda x: (x[0] == UNKNOWN, -x[1], x[0]))], numeric=(1,))
    R.h2('المخطوطات، حسب القسم')
    R.table(['العنوان', 'المؤلف', 'القسم', 'الخزانة', 'مصدر النسخة', 'المطبوع في المكتبة', 'ملاحظة'],
            [[w['title'] + (' (ملفان)' if w['files'] == 2 else f' ({w["files"]} ملفات)' if w['files'] > 2 else ''), w['author'], w['section'], w['holding'] or UNKNOWN,
              'archive.org' if w['url'] else UNKNOWN, w['printed'], w['note']] for w in rows],
            links={4: [w['url'] or None for w in rows]})
    R.write('10 - فهرس المخطوطات')
    print(len(rows), 'works,', sum(w['files'] for w in rows), 'files,', len(rows) - held[UNKNOWN], 'with a holding')

if __name__ == '__main__':
    main()

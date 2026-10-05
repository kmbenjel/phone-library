"""One-off (2026-10-05): final names for queue 144 (pre-700 Shamela works missing from the phone), from the title pages
read in downloads/stage-144/sheets and recorded in data/expansion/144-decisions.tsv (keep/drop, section, name).
Single-file books → plain files; multi-file books → numbered volume files (rules below, per book, from the file names
and the PDFs' embedded titles). Writes data/queue/144-final.tsv (file://) and lists what is held back."""
import csv, os, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
dec = {}
for r in csv.reader(open(J('data/expansion/144-decisions.tsv'), encoding='utf-8'), delimiter='\t'):
    if r and not r[0].startswith('#'): dec[int(r[0])] = r
books = [l.rstrip('\n').split('\t') for l in open(J('downloads/stage-144/sheets/books.frozen.tsv'), encoding='utf-8')]
man = [r for r in csv.reader(open(J('downloads/stage-144/manifest.tsv'), encoding='utf-8'), delimiter='\t') if len(r) > 5]
by = collections.defaultdict(list)
for r in man: by[os.path.dirname(r[2])].append(r)
AR = {'0': '٠'}

def short(name):
    t = re.sub(r'\s*\([^()]*\)$', '', name).split(' - ')[0]
    w = t.split()
    cut = next((i for i in range(2, len(w)) if w[i] in ('في', 'على', 'من', 'عن', 'إلى')), None)
    return ' '.join(w[:cut]) if cut else t

def multi(n, rows, s):
    """[(row, file name)] for the multi-file books kept; None = hold the book back"""
    f = lambda r: os.path.basename(r[2])
    rows = sorted(rows, key=f)
    if n == 2: return [(r, None) for r in rows if '۔لمحمد' not in f(r) and 'الکبیر' not in f(r)]          # the clean Cairo 1356 scan
    if n == 36: return [(max(rows, key=lambda r: int(r[1])), None)]                                    # two scans: the gray one
    if n == 206: return [(r, None) for r in rows if 'تخجيل' in f(r)]                                   # one book of a bundle
    if n == 33:                                                                                         # three editions
        ed = {'0242': 'ط قديمة', '0243': 'ط ابن زيدون', '0244': 'ت فوقية حسين محمود - دار الأنصار'}
        return [(r, f'__plain__الإبانة عن أصول الديانة - أبو الحسن الأشعري ({ed[f(r)[:4]]})') for r in rows]
    if n == 53:
        if len(rows) < 7 or any(r[5] != 'ok' for r in rows): return None                               # volume 3 not downloaded
    out = []
    for r in rows:
        b = f(r); ok = r[5] == 'ok'
        if not ok: return None
        if n in (157, 167):                                           # the book + a few pages of manuscript photos
            small = min(rows, key=lambda x: int(x[1]))
            out.append((r, f'{s} (صور المخطوطات).pdf' if r is small else f'{s}.pdf'))
            continue
        m = re.search(r'(?:_msga|tqaiaz|BSAER|Ruyani|_kbt|asmknh_|skmnkb_|shafiya_|hm0505-|mgmr)(\d+)(?:-(\d))?(p?)\.pdf$', b) \
            or re.search(r'(\d)\. ', b) or re.search(r'مسند الحارث بن محمد بن أبي أسامة([١-٥])', b) or re.match(r'(\d+)(p?)\.pdf$', b) or re.match(r'(\d\d)_\d+()()\.pdf$', b)
        if n == 13: v = '١٢٣٤٥'.index(m.group(1)) + 1; out.append((r, f'{v:02d} - {s}.pdf')); continue
        if n == 23: out.append((r, f'{s} (الدراسة).pdf' if 'intro' in b else f'{s}.pdf')); continue
        if n == 57:
            out.append((r, None)); continue
        if n == 203:
            if 'المقدمة' in b: out.append((r, f'00 - {s} (دراسة المحقق).pdf')); continue
            v = {'الأول': 1, 'الثاني': 2, 'الثالث': 3}[re.search(r'الجزء (\S+)', b).group(1)]
            lab = {1: 'الفاتحة - الأنفال', 2: 'التوبة - الأحزاب', 3: 'سبأ - الناس'}[v]
            out.append((r, f'{v:02d} - {s} ({lab}).pdf')); continue
        if n == 147:
            a, p = m.group(1), m.group(2)
            out.append((r, f'{s} (المجلد {a}' + (f' - القسم {p}' if p else '') + ').pdf')); continue
        if not m: raise SystemExit(f'book {n}: no volume number in {b}')
        v = int(m.group(1)); pref = m.group(3) if m.lastindex and m.lastindex >= 3 else ''
        if n == 21: pref = m.group(2)
        if v == 0: out.append((r, f'00 - {s} (الواجهة).pdf'))
        elif pref: out.append((r, f'{v:02d} - {s} (المقدمة).pdf'))
        else: out.append((r, f'{v:02d} - {s}.pdf'))
    if n == 57:                                                       # four volumes, in file-name order
        out = [(r, f'{i:02d} - {s}.pdf') for i, (r, _) in enumerate(out, 1)]
    if n == 147:                                                      # 12 files: volumes 1-5 in two parts, 6, 7
        out = [(r, f'{i:02d} - {nm}') for i, (r, nm) in enumerate(out, 1)]
    return out

def main():
    lines, held, dropped = [], [], 0
    for n, folder, cnt, first in books:
        n = int(n); d = dec[n]
        if d[1] != 'keep': dropped += 1; continue
        cat, name = d[2], d[3]
        rows = by[folder]; s = short(name)
        assert len((name + '.pdf').encode()) <= 200, name
        okrows = [r for r in rows if r[5] == 'ok']
        if len(rows) == 1 or n in (2, 36, 206):
            sel = multi(n, rows, s) if len(rows) > 1 else [(rows[0], None)]
            for r, _ in sel:
                if r[5] != 'ok': held.append(name); break
                lines.append((r, f'Books/{cat}/{name}.pdf'))
            continue
        sel = multi(n, rows, s)
        if sel is None: held.append(name); continue
        for r, fn in sel:
            if fn.startswith('__plain__'): lines.append((r, f'Books/{cat}/{fn[9:]}.pdf'))
            else: lines.append((r, f'Books/{cat}/{name}/{fn}'))
    seen = set()
    with open(J('data/queue/144-final.tsv'), 'w', encoding='utf-8') as w:
        for r, t in lines:
            assert t not in seen, t; seen.add(t)
            assert all(len(x.encode()) <= 200 for x in t.split('/')), t
            assert not re.search(r'[:*?"<>|\\]', t), t
            w.write('\t'.join([f'file://{os.path.abspath(r[4])}', r[1], t, r[3]]) + '\n')
    print(len(lines), 'files;', dropped, 'books dropped; held back:', held)

if __name__ == '__main__':
    main()

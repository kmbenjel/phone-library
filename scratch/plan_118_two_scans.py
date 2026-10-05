"""One-off (118): folders where two scans of the same book were numbered as parts («جزء 1 … جزء 6»). Files pair up
by identical page counts. In each pair the main copy = text layer and higher resolution; the other becomes a
companion «(… - نسخة أخرى)» (no number, AGENTS §4). Roles from the embedded titles («ج N : label», «- مقدمة»,
«- المدخل») or, failing that, page counts (largest = the book, 1 page = الواجهة, other small = المقدمة)."""
import csv, json, collections, re, sys
info = {}
for l in open('data/inspect/files.jsonl', encoding='utf-8'):
    d = json.loads(l); im = d.get('images') or {}
    info[d['path']] = dict(pages=d.get('pages'), ppi=im.get('ppi_median') or 0, text=d.get('text_first_chars') or 0, size=d['size'], title=(d.get('meta') or {}).get('title', ''))
idx = [p for p, s in csv.reader(open('data/phone/index-now.tsv', encoding='utf-8'), delimiter='\t')]
FOLDERS = [l.strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
def score(p):
    i = info[p]; ppi = i['ppi'] if i['ppi'] and i['ppi'] > 100 else 0
    return (i['text'] > 500, ppi, -i['size'])
plan = []
for d in FOLDERS:
    ps = [p for p in idx if p.rsplit('/', 1)[0] == d]
    title = re.split(r'\s+-\s+|\s+\(', d.split('/')[-1])[0].strip()
    groups = collections.defaultdict(list)
    for p in ps: groups[info[p]['pages']].append(p)
    big = sorted(groups, reverse=True)
    vols = [g for g in big if g > 60]
    if 'كتاب المتنبي' in d: vols = [max(vols)]                       # the 194-page file is «رسالة في الطريق إلى ثقافتنا», the book's introduction
    multi = len(vols) > 1
    for g in groups:
        a, b = sorted(groups[g], key=score, reverse=True)
        t = info[a]['title'] or info[b]['title']; t2 = info[b]['title'] if info[b]['title'] and not re.fullmatch(r'[\w\-.]*', info[b]['title']) else t
        m = re.search(r'ج\s*(\d+)\s*(?::\s*(.*))?$', t2) or re.search(r'ج\s*(\d+)\s*(?::\s*(.*))?$', t)
        if 'كتاب المتنبي' in d and g not in vols:
            main = f'{title} (رسالة في الطريق إلى ثقافتنا - المقدمة).pdf'; alt = f'{title} (رسالة في الطريق إلى ثقافتنا - نسخة أخرى).pdf'
        elif g > 60:
            n, lab = (int(m.group(1)), (m.group(2) or '').strip()) if m else (vols.index(g) + 1, '')
            lab = re.sub(r'\s*:\s*', ' - ', lab)
            main = f'{n:02d} - {title}' + (f' ({lab})' if lab else '') + '.pdf' if multi else f'{title}.pdf'
            alt = f'{title} (' + (f'ج {n} - ' if multi else '') + 'نسخة أخرى).pdf'
        else:
            role = 'المدخل' if 'المدخل' in t2 else 'المقدمة' if re.search(r'مقدم', t2) else 'الواجهة' if g <= 2 else 'المقدمة'
            main = f'{title} ({role}).pdf'; alt = f'{title} ({role} - نسخة أخرى).pdf'
            if multi and m: main = f'{int(m.group(1)):02d} - {title} ({role}).pdf'; alt = f'{title} (ج {int(m.group(1))} - {role} - نسخة أخرى).pdf'
            elif multi and role == 'الواجهة': main = f'00 - {title} ({role}).pdf'
        why = f'two scans of the same book had been numbered as parts; main copy = text layer {info[a]["text"]>500}, {info[a]["ppi"]} ppi, {info[a]["size"]/1e6:.1f} MB; the other ({info[b]["ppi"]} ppi, text {info[b]["text"]>500}, {info[b]["size"]/1e6:.1f} MB) kept as «نسخة أخرى» for the owner'
        plan.append((a, f'{d}/{main}', why)); plan.append((b, f'{d}/{alt}', why))
tg = collections.Counter(b for _, b, _ in plan)
bad = [b for b, c in tg.items() if c > 1]
if bad: print('CLASH', bad); sys.exit(1)
s1 = [('Books/' + a, 'Books/' + a.rsplit('/', 1)[0] + f'/__two_{i:04d}.pdf', 'step 1') for i, (a, b, c) in enumerate(plan)]
s2 = [('Books/' + a.rsplit('/', 1)[0] + f'/__two_{i:04d}.pdf', 'Books/' + b, c) for i, (a, b, c) in enumerate(plan)]
for n, rr in (('118a-two-scans-step1', s1), ('118b-two-scans-in-one-folder', s2)):
    with open(f'plans/{n}.tsv', 'w', encoding='utf-8') as w:
        for r in rr: w.write('\t'.join(r) + '\n')
for a, b, c in plan: print(a.rsplit('/', 1)[1][:50], '→', b.rsplit('/', 1)[1][:90])

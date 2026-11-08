"""The book cards («بطاقة الكتاب») and author biographies of the locally installed Shamela → data/shamela/cards.jsonl and
data/shamela/authors.jsonl (owner, 2026-10-08: «معلومات الشاملة في الفهرس يجب أن تكون أغنى وتعتمد على البطاقات»).
Shamela keeps them in Lucene indexes (database/store/book, store/author), read here with Shamela's own Lucene jars and
tools/shamela-dump/Dump (needs Java ≥ 21: Shamela's own JRE, or SHAMELA_JAVA). Also refreshes the raw dump
data/shamela/book-cards.jsonl that edition_info.py reads.
The indexes are copied first, so the app is never disturbed. Card lines «الحقل: القيمة» are parsed into fields:
  title (الكتاب / اسم الكتاب), author (المؤلف), editor (المحقق, تحقيق, دراسة وتحقيق …), publisher (الناشر, دار النشر),
  edition (الطبعة), year (عام النشر, سنة النشر), volumes (عدد الأجزاء), pages (عدد الصفحات), joined («ويليه …» lines),
  printed_pages (ترقيم الكتاب موافق للمطبوع), note (تنبيه), source (مصدر الكتاب / http links), card (the whole card), hint (نبذة)
Authors: {id, name, life, full (the full name line), bio}.
Usage: python3 scripts/export_shamela_cards.py"""
import glob, json, os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH = os.path.expanduser('~/.local/share/shamela')
JARS = sorted(glob.glob(f'{SH}/app/lucene/*/*.jar'))
AR = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

def java():
    cands = [os.environ.get('SHAMELA_JAVA', ''), f'{SH}/app/linux/64/jre/2/bin/java'] + \
            sorted(glob.glob(os.path.expanduser('~/.jdks/*/bin/java')), reverse=True) + sorted(glob.glob('/usr/lib/jvm/*/bin/java'), reverse=True)
    for j in cands:
        if not j or not os.path.exists(j): continue
        m = re.search(r'version "(\d+)', subprocess.run([j, '-version'], capture_output=True, text=True).stderr)
        if m and int(m.group(1)) >= 21: return j
    sys.exit('no Java ≥ 21 found (set SHAMELA_JAVA)')

def dump(index, out):
    """tools/shamela-dump/Dump (read-only, reflection: compiled once with any javac) on a copy of the index"""
    with tempfile.TemporaryDirectory() as tmp:
        cp = os.path.join(tmp, 'idx'); shutil.copytree(f'{SH}/database/store/{index}', cp)
        if os.path.exists(f'{cp}/write.lock'): os.remove(f'{cp}/write.lock')
        with open(out, 'w', encoding='utf-8') as w:
            subprocess.run([java(), '-cp', os.path.join(ROOT, 'tools/shamela-dump') + ':' + ':'.join(JARS), 'Dump', cp],
                           stdout=w, stderr=subprocess.DEVNULL, check=True)
    return [json.loads(l) for l in open(out, encoding='utf-8')]

FIELDS = [('title', r'الكتاب|اسم الكتاب'), ('author', r'المؤلف|تأليف|المؤلفون'),
          ('editor', r'المحقق|المحققون|تحقيق|دراسة وتحقيق|تحقيق ودراسة|تحقيق وتعليق|حققه وعلق عليه|حققه|اعتنى به|ضبطه|إعداد|جمع وترتيب'),
          ('publisher', r'الناشر|دار النشر'), ('edition', r'الطبعة'), ('year', r'عام النشر|سنة النشر'),
          ('volumes', r'عدد الأجزاء'), ('pages', r'عدد الصفحات'), ('note', r'\[?تنبيه\]?'), ('source', r'مصدر الكتاب'),
          ('commentator', r'الشارح'), ('origin_author', r'مؤلف الأصل'), ('thesis', r'رسالة|أصل الكتاب|أصل التحقيق')]

def parse(card):
    d = {}
    for line in card.split('\r'):
        line = line.strip()
        if not line: continue
        if line.startswith('ويليه') or line.startswith('ومعه') or line.startswith('وبهامشه') or line.startswith('وبذيله'):
            d.setdefault('joined', []).append(line); continue
        if 'موافق للمطبوع' in line: d['printed_pages'] = True; continue
        if line.startswith('http'): d.setdefault('source', line); continue
        m = re.match(r'^([^:]{2,30}):\s*(.+)$', line)
        if not m: continue
        k, v = m.group(1).strip(), m.group(2).strip()
        for f, rx in FIELDS:
            if re.fullmatch(rx, k):
                if f in d and f in ('editor', 'note'): d[f] += ' ؛ ' + v
                else: d.setdefault(f, v)
                break
    for f in ('volumes', 'pages'):
        if f in d:
            m = re.search(r'\d+', d[f].translate(AR))
            if m: d[f + '_n'] = int(m.group())
    return d

def main():
    os.makedirs(os.path.join(ROOT, 'data/shamela'), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        books, authors = dump('book', os.path.join(ROOT, 'data/shamela/book-cards.jsonl')), dump('author', f'{tmp}/a.jsonl')
    with open(os.path.join(ROOT, 'data/shamela/cards.jsonl'), 'w', encoding='utf-8') as w:
        for b in sorted(books, key=lambda x: int(x['id'])):
            card = b.get('body_store', '')
            d = {'id': int(b['id'])} | parse(card) | {'card': card.replace('\r', '\n').strip(), 'hint': b.get('hint', '').replace('\r', '\n').strip()}
            w.write(json.dumps(d, ensure_ascii=False) + '\n')
    with open(os.path.join(ROOT, 'data/shamela/authors.jsonl'), 'w', encoding='utf-8') as w:
        for a in sorted(authors, key=lambda x: int(x['id'])):
            lines = [x.strip() for x in a.get('body_store', '').split('\r')]
            nonempty = [x for x in lines if x]
            m = re.match(r'^(.*?)\s*\(([^)]*)\)\s*$', nonempty[0]) if nonempty else None
            name = (m.group(1) if m else (nonempty[0] if nonempty else '')).lstrip('• ')
            full = nonempty[1] if len(nonempty) > 1 and not nonempty[1].startswith('•') else ''
            # the name only: up to the first «:» / «.» (the line often goes on in prose), at most 16 words
            name, full = (' '.join(re.split(r'[:.]', x)[0].split()[:16]) for x in (name, full))
            d = {'id': int(a['id']), 'name': name, 'life': (m.group(2) if m else ''), 'full': full, 'bio': '\n'.join(nonempty[1:])}
            w.write(json.dumps(d, ensure_ascii=False) + '\n')
    print('cards', len(books), 'authors', len(authors))

if __name__ == '__main__':
    main()

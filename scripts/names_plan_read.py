"""A rename plan from the title-page readings (data/names/title-read.tsv, the latest row per book), under AGENTS.md §4:
a single book (verdict ok / other-book / other-edition) becomes a plain file in its section named from what its pages
print (names_from_reading.name_of); a section read as wrong («section» column) moves it there. Held back, listed in the
review file: «part» (one volume of a set: its folder and volume number need the set), unreadable / no title page, readings
whose note asks for a closer look («check», «not legible», «read further»), targets already taken, sections that are not
in the library. Sources are the phone's own bytes (raw paths from the index).
Usage: python3 scripts/names_plan_read.py plans/NNN-names-read.tsv data/names/plan-held.tsv"""
import csv, os, re, sys, unicodedata, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from names_from_reading import name_of, name_auto, overrides
import name_compose
from textnorm import norm
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)
def key(name):
    """what makes two names the same: textnorm.norm keeps Arabic letters and digits only, so every English name was «2»
    («Biology 2e» = «Chemistry 2e»: 9 OpenStax books held as taken, 2026-10-19) — a name without Arabic letters compares whole"""
    return norm(name) if re.search(r'[\u0621-\u064a]', name) else N(name).casefold()

DOUBT = re.compile(r'check|not legible|too faint|read further|read the file|read the inner|dark cover|stylised|small print')

def shortened(r):
    """did the 240-byte limit cut anything? (the same name composed without a limit is longer)"""
    lim = name_compose.LIMIT
    try:
        name_compose.LIMIT = 10_000
        import names_from_reading as m
        m.compose.__defaults__ = tuple(10_000 if x == lim else x for x in m.compose.__defaults__)
        full = name_auto(r)
    finally:
        name_compose.LIMIT = lim
        m.compose.__defaults__ = tuple(lim if x == 10_000 else x for x in m.compose.__defaults__)
    return full != name_auto(r)

def main(out, held_out):
    idx = [l.split('\t', 1)[0] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()]
    raw = {N(p): p for p in idx}
    sections = {N(p.split('/')[0]) for p in idx}
    plain = collections.defaultdict(set)
    for p in idx:
        parts = N(p).split('/')
        if len(parts) == 2: plain[parts[0]].add(key(parts[1].removesuffix('.pdf')))
    sheet = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(J('data', 'names', 'sheets', 'books.tsv'), encoding='utf-8')}
    last = {}
    for r in csv.DictReader(open(J('data', 'names', 'title-read.tsv'), encoding='utf-8'), delimiter='\t'): last[r['n']] = r
    act = {}
    if os.path.exists(J('data', 'names', 'owner-actions.tsv')):
        for r in csv.DictReader((l for l in open(J('data', 'names', 'owner-actions.tsv'), encoding='utf-8') if not l.startswith('#')), delimiter='\t'): act[r['n']] = r
    rows, held, c = [], [], collections.Counter()
    def hold(r, why): held.append((r['n'], r['book'], why)); c['held: ' + why] += 1
    for n, r in sorted(last.items(), key=lambda kv: int(kv[0])):
        if r['verdict'] not in ('ok', 'other-book', 'other-edition'): hold(r, r['verdict']); continue
        note = re.sub(r'read further\s*(\(|:|in\b|with\b)[^؛]*', '', r.get('note') or '')      # a further reading already done is not a doubt
        if DOUBT.search(note): hold(r, 'a closer look first'); continue
        # owner 2026-10-11 («why they didn't follow the rule»): missing information must be read from the file itself —
        # a reading without a publisher or an editor goes into a plan only after the file was read further
        # (deep_sheets.py: pages 2-9 and the last pages; the note then says «read further»)
        if r['verdict'] in ('ok', 'other-book', 'other-edition') and not r.get('publisher') \
                and 'مخطوط' not in (r.get('kind') or '') and 'read further' not in (r.get('note') or '') and n not in overrides():
            hold(r, 'publisher or editor missing: read the file further first (deep_sheets.py)'); continue
        a = act.get(n, {}).get('action', '')
        if a in ('remove', 'replace-whole', 'ask', 'stray', 'dup'): hold(r, f"owner: {a} — {act[n]['what'][:80]}"); continue
        src = N(sheet[n][2]) if n in sheet else ''
        if src not in raw: hold(r, 'the file is no longer at its path'); continue
        cat = src.split('/')[0]
        sec = N(r.get('section') or '').strip()
        if sec and sec not in sections: hold(r, f'section «{sec}» is not in the library'); continue
        dest_cat = sec or cat
        new = name_of(r) + '.pdf'
        if key(new.removesuffix('.pdf')) in plain[dest_cat]: hold(r, 'the name is taken in the section'); continue
        if len(src.split('/')) == 2 and src == f'{dest_cat}/{new}': c['already right'] += 1; continue
        plain[dest_cat].add(key(new.removesuffix('.pdf')))
        why = f"title page read (book {n}, {r['verdict']})" + (f'; section {cat} → {dest_cat}' if dest_cat != cat else '')
        if n not in overrides() and shortened(r): why += '; shortened (check against the cover)'
        rows.append((f'Books/{raw[src]}', f'Books/{dest_cat}/{new}', why))
        c['to rename' + (' + section' if dest_cat != cat else '') + (' (another book than its name)' if r['verdict'] != 'ok' else '')] += 1
    with open(out, 'w', encoding='utf-8') as w:
        for x in rows: w.write('\t'.join(x) + '\n')
    with open(held_out, 'w', encoding='utf-8') as w:
        w.write('n\tbook\twhy held\n')
        for x in held: w.write('\t'.join(x) + '\n')
    for k, v in sorted(c.items(), key=lambda kv: -kv[1]): print(f'{v:5}  {k}')

if __name__ == '__main__':
    main(*sys.argv[1:3])

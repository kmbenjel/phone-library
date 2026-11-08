"""After every crop redo: is each of the owner's rulings still in the book's current recipe? (owner 2026-11-07, rule 2 of the
review-page audit: «a page that went back is our fault to fix, not a new doubt for him»). Reads data/crop/owner-boxes.tsv
(whole | window X0 Y0), data/crop/owner-turns.tsv (turn by |tilt| / leave as scanned = 0) and the recipe of each book's
latest crop (changes.tsv → data/crop/recipes/<md5 of the original>.json). Prints one line per ruling: OK, WEAK (a turn smaller than
the tilt he saw), BROKEN with why, or UNCROPPED (a bench book never cropped on the phone);
exit 1 when any is broken. Usage: python3 scripts/check_owner_rulings.py [--broken]"""
import csv, json, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
nfc = lambda s: unicodedata.normalize('NFC', s)

def recipes():
    """path (NFC, without Books/) → its latest crop's recipe file"""
    out = {}
    for r in csv.reader(open(J('data', 'changes', 'changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 5 and r[1] == 'crop':
            o = re.search(r'original \d+ B md5 (\w+)', r[4])
            if o: out[nfc(r[2].removeprefix('Books/'))] = J('data', 'crop', 'recipes', o.group(1) + '.json')
    return out

def rows(name):
    for l in open(J('data', 'crop', name), encoding='utf-8'):
        if l.strip() and not l.startswith('#'):
            f = l.rstrip('\n').split('\t')
            if len(f) >= 3: yield f

def check():
    R, out = recipes(), []
    load = {}
    def page(path, n):
        rf = R.get(nfc(path))
        if not rf or not os.path.exists(rf): return None, 'UNCROPPED'
        if rf not in load: load[rf] = json.load(open(rf, encoding='utf-8'))
        P = load[rf]['pages']
        return (P[n - 1], None) if 0 < n <= len(P) else (None, f'page {n} not in the recipe ({len(P)} pages)')
    for f in rows('owner-boxes.tsv'):
        path, n, rule = f[0], int(f[1]), f[2].strip(); p, err = page(path, n)
        if err: out.append(('UNCROPPED' if err == 'UNCROPPED' else 'BROKEN', 'box', path, n, rule, err)); continue
        c = p.get('crop')
        if rule == 'whole':
            ok = not c; why = 'whole' if ok else f'cut to {c}'
        elif rule.startswith('sheet '):             # (the sheet's edges by hand, 2026-11-08: a fill, not a box — the slim
            # recipe keeps no fill; checked by the page's pixels after the crop, not here)
            out.append(('NOTE', 'box', path, n, rule, 'sheet fill: not in the recipe, check the page by eye')); continue
        elif rule.startswith('show '):              # (the reader's rect, 2026-11-07: kept as the page's crop to 0.1 pt)
            r = [float(v) for v in rule.split()[1:5]]
            ok = bool(c) and all(abs(a - b) <= 1 for a, b in zip(c, r)); why = f'crop {c}'
        else:
            x0, y0 = map(float, rule.split()[1:3])
            ok = bool(c) and abs(c[0] - x0) <= 1 and abs(c[1] - y0) <= 1; why = f'crop {c}'
        out.append(('OK' if ok else 'BROKEN', 'box', path, n, rule, why))
    for f in rows('owner-turns.tsv'):
        path, n, t = f[0], int(f[1]), abs(float(f[2])); p, err = page(path, n)
        if err: out.append(('UNCROPPED' if err == 'UNCROPPED' else 'BROKEN', 'turn', path, n, f[2], err)); continue
        s = abs(p.get('skew') or 0)             # (WEAK: turned, but by less than 2/3 of the tilt measured when he ruled — to look at)
        st = ('OK' if s <= 0.05 else 'BROKEN') if t == 0 else 'OK' if s >= 0.2 and abs(s - t) <= 0.3 else 'WEAK' if s >= 0.1 else 'BROKEN'
        out.append((st, 'turn', path, n, 'leave' if t == 0 else f'turn {t}', f'skew {p.get("skew")}'))
    return out

if __name__ == '__main__':
    res = check()
    for r in res:
        if r[0] in ('BROKEN', 'WEAK') or '--broken' not in sys.argv: print('\t'.join(map(str, r)))
    b = sum(1 for r in res if r[0] == 'BROKEN')
    print(f'{len(res)} rulings, {b} broken', file=sys.stderr)
    sys.exit(1 if b else 0)

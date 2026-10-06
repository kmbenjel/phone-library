"""Original sizes of the files whose fixed copies took their place (plans *substitute*: recompressed or cropped copies).
provenance.py matches phone files to their source by exact size; a substituted copy has a new size, so its link to the
Waqfeya record / archive.org file (the edition evidence) would be lost. This keeps it: for every current path that
received a copy, the size of the original it replaced, read from the last phone listing made before any substitution
(data/phone/index-2026-10-05-0950.tsv) and followed along every later rename/move in the change log.
→ data/phone/substituted.tsv (path, original_size, plan). Run after each substitution (refresh.sh does).
Usage: python3 scripts/substituted_sizes.py"""
import csv, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
SNAP = J('data/phone/index-2026-10-05-0950.tsv')          # before plan 125 (the first substitution, 10:50)
strip = lambda p: p[6:] if p.startswith('Books/') else p

def main():
    snap = {p: int(s) for p, s in csv.reader(open(SNAP, encoding='utf-8'), delimiter='\t') if s.isdigit()}
    log = [r for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t') if len(r) >= 6]
    i0 = next((i for i, r in enumerate(log) if r[0] >= '2026-10-05 09:50'), 0)
    cur = {p: p for p in snap}                                    # snapshot path → where it is now
    where = {p: p for p in snap}                                  # current name → snapshot path
    subs = {}                                                     # snapshot path → plan that put a copy in its place
    for r in log[i0:]:
        act, a, b, plan = r[1], strip(r[2]), strip(r[3]), r[5]
        if act != 'move': continue
        if 'substitute' in plan:
            if a.startswith('نسخ محسنة للاستبدال/') and b in where: subs[where[b]] = plan     # the copy takes the original's place
            continue                                              # the original going aside is not a rename of the book
        moved = [(a, where[a])] if a in where else \
                ([] if a.lower().endswith('.pdf') else [(k, v) for k, v in where.items() if k.startswith(a + '/')])
        for k, v in moved:
            new = b + k[len(a):]
            del where[k]; where[new] = v; cur[v] = new
    now = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
    rows = [(cur[v], snap[v], plan) for v, plan in subs.items() if cur[v] in now and now[cur[v]] != snap[v]]
    with open(J('data/phone/substituted.tsv'), 'w', encoding='utf-8') as w:
        w.write('path\toriginal_size\tplan\n')
        for r in sorted(rows): w.write('\t'.join(map(str, r)) + '\n')
    print(len(rows), 'substituted files with their original size')

if __name__ == '__main__':
    main()

"""Corrects fields of earlier readings (data/names/title-read.tsv) without retyping the whole row: each stdin line
«n | field=value | field=value …» appends a copy of book n's latest reading with those fields changed (a later row
supersedes; «note+=…» adds to the note). Fields: verdict title author editor publisher city year kind section note.
An editor may carry its printed role: «editor=صححه وعلق عليه: فلان» (names_from_reading.role_of).
Usage: python3 scripts/title_read_fix.py < fixes.txt"""
import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, 'data', 'names', 'title-read.tsv')
FIELDS = 'verdict title author editor publisher city year kind section note'.split()

def main():
    rows = list(csv.DictReader(open(F, encoding='utf-8'), delimiter='\t'))
    cols = list(rows[0].keys()) if rows else []
    last = {r['n']: r for r in rows}
    out = []
    for line in sys.stdin:
        parts = [p.strip() for p in line.rstrip('\n').split('|')]
        if not parts or not parts[0].isdigit(): continue
        n = parts[0]
        if n not in last: print('no reading for', n, file=sys.stderr); continue
        r = dict(last[n])
        for p in parts[1:]:
            if '=' not in p: continue
            k, v = p.split('=', 1); k = k.strip()
            if k.endswith('+'):
                k = k[:-1]; r[k] = ((r.get(k) or '') + '؛ ' + v.strip()).strip('؛ ')
            elif k in FIELDS: r[k] = v.strip()
            else: print('unknown field', k, file=sys.stderr)
        last[n] = r; out.append(r)
    with open(F, 'a', encoding='utf-8', newline='') as w:
        wr = csv.DictWriter(w, fieldnames=cols, delimiter='\t', lineterminator='\n')
        for r in out: wr.writerow({c: r.get(c, '') for c in cols})
    print(len(out), 'corrected')

if __name__ == '__main__':
    main()

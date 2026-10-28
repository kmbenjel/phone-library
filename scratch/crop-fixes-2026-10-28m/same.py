"""same.py A.json B.json — are two recipes of one book the same? Every page's fields compared (floats to 0.01): the count of
pages that differ and, for up to 12 of them, which fields — the faithfulness check of a regression recipe against the bench
recipe of the same code (2026-10-28: the applied book_crop must reproduce the bench exactly)."""
import sys, json

def norm(v):
    if isinstance(v, float): return round(v, 2)
    if isinstance(v, list): return [norm(x) for x in v]
    if isinstance(v, dict): return {k: norm(x) for k, x in v.items()}
    return v

A, B = (json.load(open(f)) for f in sys.argv[1:3])
book = sorted(k for k in set(A) | set(B) if k != 'pages' and norm(A.get(k)) != norm(B.get(k)))
diff = []
for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
    ks = sorted(k for k in set(p) | set(q) if norm(p.get(k)) != norm(q.get(k)))
    if ks: diff.append((i + 1, ks))
print(f'pages {len(A["pages"])} / {len(B["pages"])}; book-level fields that differ: {book}; pages that differ: {len(diff)}')
for pg, ks in diff[:12]: print(f'   p.{pg}: {ks}')

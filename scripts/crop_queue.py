"""The next crop batch of the library (owner 2026-10-10: after trial batch 001, «continue to the library»).

A batch = the next N scans (data/inspect/files.jsonl: ≥ 0.9 page images per page) not yet treated, the books that gain
most first — books of 40 pages or more before covers, front matter and short epistles; estimated gain = median over the
inspected pages of 1 / (1 − left − right margin) (the text is as much larger on the phone once the side margins go).
Books not inspected come last. Left out: the folders that are not books
(special_dirs.NOT_BOOKS), every file already in data/crop/done.tsv or logged as «crop» under any of its names (logged moves
followed back), and files already listed in two earlier batches (a file that fails twice is not tried again unattended).
Writes data/crop/batch-NNN.txt (the next free number) and prints its name; exit 1 when nothing is left.
Usage: python3 scripts/crop_queue.py [--size N]"""
import ast, csv, glob, json, os, re, statistics, sys, unicodedata
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from special_dirs import NOT_BOOKS
from crop_batch import moves, names_of, LOG, DONE
J = lambda *p: os.path.join(ROOT, *p)
N = lambda s: unicodedata.normalize('NFC', s)

def lit(v, default):
    if isinstance(v, str):
        try: return ast.literal_eval(v)
        except Exception: return default
    return v if v is not None else default

def main(size=300):
    idx = [l.rstrip('\n').split('\t')[0] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()]
    insp = {}
    for l in open(J('data', 'inspect', 'files.jsonl'), encoding='utf-8'):
        d = json.loads(l); insp[N(d['path'])] = d
    done = {l.split('\t')[0] for l in open(DONE, encoding='utf-8')} if os.path.exists(DONE) else set()
    done |= {r[2].removeprefix('Books/') for r in csv.reader(open(LOG, encoding='utf-8'), delimiter='\t') if len(r) > 2 and r[1] == 'crop'}
    # a file counts as «tried» in a batch only if that batch did not lose it to the phone being away: «STAGE FAIL … No
    # route to host / Connection refused / timed out» and «RETRY LATER (phone away)» are not attempts (2026-10-11: the
    # phone's FTP went down and moved address several times; 60 books were failing for that reason only)
    away = re.compile(r'^(?:STAGE FAIL|RETRY LATER \(phone away\)) (.+?\.pdf)\b.*(No route to host|Connection refused|timed out|Network is unreachable)', re.I)
    lost = Counter()
    for lg in glob.glob(J('logs', 'crop-batch-*.log')):
        for l in open(lg, encoding='utf-8', errors='replace'):
            m = away.match(l)
            if m: lost[m.group(1).removeprefix('Books/')] += 1
    listed = Counter()
    for b in sorted(glob.glob(J('data', 'crop', 'batch-*.txt'))):
        for l in open(b, encoding='utf-8'):
            if l.strip(): listed[l.strip().removeprefix('Books/')] += 1
    for k, v in lost.items(): listed[k] = max(0, listed[k] - v)
    _, back = moves()
    cand = []
    for p in idx:
        if p.split('/', 1)[0] in NOT_BOOKS or not p.lower().endswith('.pdf'): continue
        names = names_of(p, back)
        if any(n in done for n in names) or sum(listed[n] for n in names) >= 2: continue
        d = insp.get(N(p))
        if d:
            im = lit(d.get('images'), {}) or {}
            if (im.get('per_page') or 0) < 0.9: continue                 # born digital: nothing to crop
            g = [1 / max(0.3, 1 - m.get('l', 0) - m.get('r', 0)) for m in lit(d.get('margins'), []) or [] if isinstance(m, dict)]
            gain = statistics.median(g) if g else 1.0
            pages = int(d.get('pages') or 0)
            cand.append((0 if pages >= 40 else 1, -gain, p))            # covers, front matter, short epistles last
        else:
            cand.append((2, 0, p))                                     # not inspected yet: after the others
    cand.sort()
    if not cand: sys.exit(1)
    nums = [int(m.group(1)) for b in glob.glob(J('data', 'crop', 'batch-*.txt')) if (m := re.search(r'batch-(\d+)\.txt$', b))]
    name = f'batch-{max(nums, default=0) + 1:03d}'
    with open(J('data', 'crop', name + '.txt'), 'w', encoding='utf-8') as w:
        for _, _, p in cand[:size]: w.write(p + '\n')
    print(name)
    print(f'{min(size, len(cand))} files; {len(cand)} left before this batch; estimated gain of this batch '
          f'{-cand[0][1]:.2f}…{-cand[min(size, len(cand)) - 1][1]:.2f}', file=sys.stderr)

if __name__ == '__main__':
    main(int(sys.argv[sys.argv.index('--size') + 1]) if '--size' in sys.argv else 300)

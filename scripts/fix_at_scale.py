"""Lossless fixed copies at scale, substituted batch by batch (owner, 2026-10-05: make fixed copies and substitute them).
For the files of data/phone/quality.tsv with the chosen problems (default: margins, dark-borders → crop; spreads → split),
smallest first, in batches:
  1. scripts/improve_copies.py with MAX_KEPT=0.9: copy fixed and uploaded to «نسخ محسنة للاستبدال» only when it shows
     the text larger (a crop keeping > 90 % of the median page is not uploaded: data/improve/noop.tsv)
  2. substitution like plans 125/140/141: original → «نسخ مستبعدة/__المستبدل», copy → original path, original deleted
  3. data/phone/index-now.tsv kept current (index_update.py), one WORKLOG line per run
Never touches files already handled (substituted, judged no-op, or listed in an earlier batch), the special folders,
or the owner's protected local folders (phone only). Resumable: re-run the same command.
Usage: python3 scripts/fix_at_scale.py PREFIX [--batch 150] [--max-batches N] [--problems margins,dark-borders,spreads]
  PREFIX = plan number for this run, e.g. 142 → plans/142-b01a…, lists/142-b01.tsv"""
import argparse, csv, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
IMP, OUT = 'نسخ محسنة للاستبدال/', 'نسخ مستبعدة/__المستبدل/'
SPECIAL = ('نسخ محسنة للاستبدال', 'نسخ مستبعدة', 'فهارس الويب')
TOOLS = os.path.expanduser('~/.local/share/phone-library-tools/site')
OPS = {'margins': 'crop', 'dark-borders': 'crop', 'spreads': 'split'}

def sh(cmd, env=None, log=None):
    e = dict(os.environ, **(env or {}))
    with open(J(log), 'a') if log else open(os.devnull, 'w') as out:
        return subprocess.run(cmd, cwd=ROOT, env=e, stdout=out, stderr=subprocess.STDOUT).returncode

def handled():
    """paths that already have a fixed copy (made by any plan), were judged no-op, or are being recompressed — NOT
    merely listed: a batch that failed (phone offline) gives its files back to the pool"""
    h = set()
    for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 5 and r[1] == 'add' and r[3].startswith('Books/' + IMP): h.add(r[3][6 + len(IMP):])
    if os.path.exists(J('data/improve/noop.tsv')):
        h |= {l.split('\t')[0] for l in open(J('data/improve/noop.tsv'), encoding='utf-8')}
    for fn in ('lists/135-recompress.tsv', 'data/improve/139-measure.tsv'):
        if os.path.exists(J(fn)): h |= {r[0] for r in csv.reader(open(J(fn), encoding='utf-8'), delimiter='\t') if r}
    return h

def phone_up():
    import socket
    sys.path.insert(0, J('scripts'))
    from phone_host import CANDIDATES, PORT
    for h in CANDIDATES:
        try:
            socket.create_connection((h, PORT), timeout=3).close()
            subprocess.run(['rclone', 'config', 'update', 'phone', 'host', h], capture_output=True)
            return h
        except OSError: pass
    return None

def wait_phone():
    t = 0
    while not phone_up():
        if t % 30 == 0: print(time.strftime('%T'), 'phone offline: waiting', flush=True)
        time.sleep(60); t += 1

def candidates(problems):
    idx = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
    skip = handled(); ops = {}
    for r in csv.reader(open(J('data/phone/quality.tsv'), encoding='utf-8'), delimiter='\t'):
        if not r or r[0] not in problems or r[1] not in idx or r[1] in skip or r[1].startswith(SPECIAL): continue
        ops.setdefault(r[1], set()).add(OPS[r[0]])
    return sorted(((p, ','.join(sorted(o, key=['split', 'crop'].index))) for p, o in ops.items()), key=lambda x: idx[x[0]]), idx

def copies_of(plan):
    """path → bytes of the fixed copies a plan uploaded"""
    out = {}
    for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) > 5 and r[5] == plan and r[1] == 'add':
            m = re.search(r"'bytes_out': (\d+)", r[4])
            if m: out[r[3][6 + len(IMP):]] = int(m.group(1))
    return out

def substitute(name, copies, idx):
    """three-step substitution of the uploaded copies; returns how many"""
    a, b, c = [], [], []
    for p in copies:
        if p not in idx: continue
        a.append((f'Books/{p}', f'Books/{OUT}{p}', 'replaced by its lossless fixed copy (text shown larger on the phone)'))
        b.append((f'Books/{IMP}{p}', f'Books/{p}', 'lossless fixed copy takes the original\'s place'))
        c.append((f'Books/{OUT}{p}', 'replaced by its lossless fixed copy (owner 2026-10-05: substitute the improved copies)'))
    if not a: return 0
    for suffix, rows in (('a-substitute-fixed-step1', a), ('b-substitute-fixed', b), ('c-delete-replaced-originals', c)):
        with open(J(f'plans/{name}{suffix}.tsv'), 'w', encoding='utf-8') as w:
            for x in rows: w.write('\t'.join(x) + '\n')
    env = {'ALLOW_PROTECTED': '1'}
    log = f'logs/{name}.log'
    if sh(['python3', 'scripts/apply_plan.py', f'plans/{name}a-substitute-fixed-step1.tsv'], env, log): return -1
    if sh(['python3', 'scripts/apply_plan.py', f'plans/{name}b-substitute-fixed.tsv'], env, log): return -1
    sh(['python3', 'scripts/delete_files.py', f'plans/{name}c-delete-replaced-originals.tsv', f'{name}c-delete-replaced-originals'], env, log)
    sh(['python3', 'scripts/index_update.py', f'{name}a-substitute-fixed-step1', f'{name}b-substitute-fixed', f'{name}c-delete-replaced-originals'], None, log)
    now = {p for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')}
    add = J(f'data/improve/{name}-sizes.tsv')
    with open(add, 'w', encoding='utf-8') as w:
        for p, n in copies.items():
            if p not in now and p in idx: w.write(f'{p}\t{n}\n')
    sh(['python3', 'scripts/index_update.py', '--add', add], None, log)
    return len(a)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prefix'); ap.add_argument('--batch', type=int, default=150); ap.add_argument('--max-batches', type=int, default=999)
    ap.add_argument('--problems', default='margins,dark-borders,spreads')
    a = ap.parse_args()
    problems = set(a.problems.split(','))
    total = 0
    for k in range(1, a.max_batches + 1):
        name = f'{a.prefix}-b{k:02d}'
        lst = J(f'lists/{name}.tsv')
        if not os.path.exists(lst):
            rows, idx = candidates(problems)
            if not rows: break
            with open(lst, 'w', encoding='utf-8') as w:
                for p, o in rows[:a.batch]: w.write(f'{p}\t{o}\n')
        print(time.strftime('%T'), name, sum(1 for _ in open(lst)), 'files', flush=True)
        for attempt in range(3):                               # later passes pick up phone drops
            wait_phone()
            sh(['nice', '/usr/bin/python3', 'scripts/improve_copies.py', lst, f'{name}-copies'],
               {'PYTHONPATH': TOOLS, 'MAX_KEPT': '0.9', 'NETPACE': os.environ.get('NETPACE', '0')}, f'logs/{name}-copies.log')
            left = {r[0] for r in csv.reader(open(lst, encoding='utf-8'), delimiter='\t') if r} - handled()
            if not left: break
        wait_phone()                                           # never substitute while the phone is away
        idx = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
        done_subs = {r[2][6:] for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t')
                     if len(r) > 5 and r[5] == f'{name}a-substitute-fixed-step1'}
        copies = {p: n for p, n in copies_of(f'{name}-copies').items() if p not in done_subs}
        n = substitute(name, copies, idx)
        print(time.strftime('%T'), name, 'substituted', n, flush=True)
        if n < 0: print('substitution failed: see', f'logs/{name}.log'); break
        total += max(n, 0)
    with open(J('WORKLOG.md'), 'a', encoding='utf-8') as w:
        w.write(f'| {time.strftime("%F %H:%M")} | {a.prefix} (fix_at_scale.py): {total} lossless fixed copies substituted '
                f'(crops of wide margins / dark scanner edges showing ≤ 90 % of the page, split spreads); no-op crops not uploaded '
                f'(data/improve/noop.tsv). |\n')
    print('done', total)

if __name__ == '__main__':
    main()

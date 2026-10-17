"""Redo the crop of books cropped by an earlier version of scripts/book_crop.py (owner 2026-10-15, after his review of
crop-review-002/004: «you should be mature enough now to handle all this … Go ahead»). Per book (a phone path under Books/):
  1. the original bytes: the latest logged crop of the book (under any of its earlier names) gives the original size and
     MD5; the phone file must still be the cropped file that crop wrote (its logged MD5) — else the book is left alone; the
     laptop's copy when its MD5 is the original's, else the phone file truncated to the original size (a crop is an
     appended revision), checked against the original MD5;
  2. the method as it is now (crop_batch.analyse: book_crop.plan + apply, sample sheets for the review page);
  3. the new file = the original + the new revision, or the original alone when the method now leaves the book as it is
     (logged «crop undone»); uploaded beside the old one as «<name>.redo», checked on the phone (size + MD5), the old file
     deleted and the new one renamed into its place, checked again — a dropped connection never leaves a damaged book;
  4. logged in data/changes/changes.tsv (action «crop», reason «redo …»), the recipe kept, index-now.tsv size updated,
     data/crop/redo-done.tsv (resumable). The earlier sample sheets are kept in crop-sheets-v1/.
Usage: python3 scripts/crop_redo.py --list-all OUT.tsv          (every book cropped and not undone, current paths)
       python3 scripts/crop_redo.py LIST.tsv BATCH [--workers N]"""
import csv, hashlib, os, shutil, sys, time, ftplib
from concurrent.futures import ProcessPoolExecutor, as_completed
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import crop_batch as cb
J = lambda *p: os.path.join(ROOT, *p)
DONE = J('data', 'crop', 'redo-done.tsv')
LOCAL_MAP = os.path.expanduser('~/.cache/phone-library/local-map.tsv')

def crops():
    """{phone path at crop time: (original size, original md5, cropped md5)} — the latest crop row of each path; a path
    whose latest row is an undo maps to None"""
    out = {}
    for r in csv.reader(open(cb.LOG, encoding='utf-8'), delimiter='\t'):
        if len(r) > 4 and r[1] == 'crop':
            p = r[2].removeprefix('Books/'); why = r[4]
            if why.startswith('crop undone'): out[p] = None; continue
            if 'original ' not in why: continue
            try:
                n0 = int(why.split('original ')[1].split(' B')[0]); m0 = why.split('md5 ')[1].split(';')[0].strip()
                m1 = why.rsplit('→ md5 ', 1)[1].split()[0].strip() if '→ md5 ' in why else None
            except (IndexError, ValueError): continue
            out[p] = (n0, m0, m1)
    return out

def logged(path, table, back):
    for name in cb.names_of(path, back):
        if name in table: return table[name]
    return None

def list_all(out_tsv):
    table = crops(); fwd, back = cb.moves()
    idx = {l.split('\t')[0] for l in open(J('data', 'phone', 'index-now.tsv'), encoding='utf-8') if l.strip()}
    rows = []
    def follow(p):                                    # the logged moves, read once
        seen = set()
        while p in fwd and p not in seen: seen.add(p); p = fwd[p]
        return p
    for p, v in table.items():
        if not v: continue
        now = p if p in idx else follow(p)            # follow the moves only while the path is missing (an older file of the
        if now in idx: rows.append(now)               # same name may have moved away long before this book got it)
    rows = sorted(set(rows))
    open(out_tsv, 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print(len(rows), 'books cropped and not undone')

def stage(path, n0, m0, m1):
    """the original bytes in the staging folder (a copy: the worker writes beside it)"""
    work = os.path.join(cb.STAGE, hashlib.md5(path.encode()).hexdigest()[:12] + '.work.pdf')
    local = dict(l.rstrip('\n').split('\t')[:2] for l in open(LOCAL_MAP, encoding='utf-8')) if os.path.exists(LOCAL_MAP) else {}
    with cb.Phone() as ph: now = ph.md5(path)
    if m1 and now != m1: raise RuntimeError(f'the phone file is not the one the crop wrote (md5 {now} ≠ {m1})')
    lp = local.get(path)
    if lp and os.path.exists(lp) and os.path.getsize(lp) == n0 and cb.md5_file(lp) == m0:
        shutil.copyfile(lp, work); return work, now
    with cb.Phone() as ph: ph.get(path, work)
    with open(work, 'r+b') as f: f.truncate(n0)
    if cb.md5_file(work) != m0: os.remove(work); raise RuntimeError('the truncated phone file is not the original')
    return work, now

def finish(fu, meta, batch):
    path, n0, m0, m_old = meta
    try: r = fu.result()
    except Exception as e: print('ANALYSE FAIL', path, repr(e)[:200], flush=True); return
    src = r['src']; new = r.get('dst') or src
    def mark(result):
        with open(DONE, 'a', encoding='utf-8') as f: f.write(f'{path}\t{m0}\t{result}\n')
    touched = False
    try:
        n1 = os.path.getsize(new); m1 = cb.md5_file(new)
        with open(new, 'rb') as f:
            if f.read(n0) != open(src, 'rb').read(n0): raise RuntimeError('the new file does not start with the original bytes')
        if m1 == m_old: mark('same as before'); print('SAME', path[:80], flush=True); return
        tmp = path + '.redo'
        with cb.Phone() as ph:
            if ph.md5(path) != m_old: raise RuntimeError('the phone file changed meanwhile')
            touched = True
            ph.put(tmp, new)
            if ph.size(tmp) != n1 or ph.md5(tmp) != m1: raise RuntimeError('upload not verified (the old file is untouched)')
            ph.f.delete('Books/' + path)
            ph.f.rename('Books/' + tmp, 'Books/' + path)
            if ph.md5(path) != m1: raise RuntimeError('RENAMED FILE NOT VERIFIED — check ' + path)
        if r.get('dst'):
            import json
            json.dump(r['recipe'], open(os.path.join(cb.RECIPES, m0 + '.json'), 'w'), ensure_ascii=False)
            cb.log_change(path, f'book_crop {r["decision"]} (lossless), redo with the corrected method: gain {r["gain"]}, pages turned {r["turned"]}, '
                                f'shrunk to the book size {r["scaled"]}; original {n0} B md5 {m0}; appended {n1 - n0} B → md5 {m1}', batch)
            mark(f'redone {n0}->{n1}'); print('REDONE', path[:80], '| gain', r['gain'], '| turned', r['turned'], flush=True)
        else:
            cb.log_change(path, f'crop undone: back to the original ({n0} B md5 {m0}) — the corrected method leaves it as it is: {r["decision"][:120]}', batch)
            mark('original restored'); print('RESTORED', path[:80], '|', r['decision'][:80], flush=True)
        cb.set_index_size(path, n1)
    except Exception as e:
        if not touched and isinstance(e, OSError): print('RETRY LATER (phone away)', path, e, flush=True)
        else: mark(f'FAIL {e}'); print('FAIL', path, e, flush=True)
    finally:
        for p in {src, r.get('dst')}:
            if p and os.path.exists(p): os.remove(p)

def main(list_tsv, batch, workers=3):
    table = crops(); _, back = cb.moves()
    done = {l.split('\t')[0] for l in open(DONE, encoding='utf-8')} if os.path.exists(DONE) else set()
    paths = [l.strip() for l in open(list_tsv, encoding='utf-8') if l.strip() and not l.startswith('#') and l.strip() not in done]
    print(f'{len(paths)} books to redo', flush=True)
    v1 = cb.SHEETS + '-v1'; os.makedirs(v1, exist_ok=True)
    with ProcessPoolExecutor(workers) as ex:
        futs = {}
        for path in paths:
            if not cb.os.path.exists(cb.STAGE): os.makedirs(cb.STAGE, exist_ok=True)
            lg = logged(path, table, back)
            if not lg: print('NOT CROPPED', path, flush=True); continue
            n0, m0, m1 = lg
            try: work, now = stage(path, n0, m0, m1)
            except Exception as e:
                if isinstance(e, OSError): print('RETRY LATER (phone away)', path, e, flush=True)
                else:
                    with open(DONE, 'a', encoding='utf-8') as f: f.write(f'{path}\t{m0}\tSKIP {e}\n')
                    print('SKIP', path, e, flush=True)
                continue
            sh = os.path.join(cb.SHEETS, hashlib.md5(path.encode()).hexdigest()[:12])
            if os.path.isdir(sh) and not os.path.exists(os.path.join(v1, os.path.basename(sh))): shutil.move(sh, v1)
            futs[ex.submit(cb.analyse, path, work, 1)] = (path, n0, m0, now)
            while len(futs) >= workers * 2:
                for fu in as_completed(list(futs)): finish(fu, futs.pop(fu), batch); break
        for fu in as_completed(list(futs)): finish(fu, futs.pop(fu), batch)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--list-all': list_all(a[1])
    else: main(a[0], a[1], int(a[a.index('--workers') + 1]) if '--workers' in a else 3)

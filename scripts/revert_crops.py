"""Undo the page crops of plans 139/141/142 (owner, 2026-10-07: pages of unequal width, text not centred, natural margins
and a speck-widened page — «لا يضيع شيء من النص ولو تعليقة صغيرة في الهامش»). Every listed file is brought back to its
whole scanned page: fix_pdf.py --uncrop sets each page's CropBox to its MediaBox with an incremental save (the rest of
the file stays byte for byte; checked: same page count, same images, no page still cropped), uploaded to
«نسخ محسنة للاستبدال» (upload size checked), then substituted batch by batch with the three logged steps of
fix_at_scale.py (cropped file set aside → uncropped file in its place → set-aside file deleted). Split spreads stay split
(the two halves tile the page exactly: nothing is hidden); only their crop is undone. Resumable; waits while the phone is away.
Lanes (owner, 2026-10-07: «تزامن ذكي غير ضار»): run two instances on disjoint lists with their own --prefix; each skips
files any 212 plan has already substituted. Two FTP lanes stay within the phone's limit (≤ 3 sessions with apply_plan).
Usage: python3 scripts/revert_crops.py LIST [--batch 200] [--prefix 212-u]"""
import argparse, csv, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
sys.path.insert(0, J('scripts'))
import fix_at_scale as fx
WHY = ('the crop is undone (owner 2026-10-07): set aside while its whole-page copy takes its place',
       'the whole scanned page again: every CropBox = MediaBox (incremental save, images and text untouched)',
       'cropped copy replaced by its whole-page copy (owner 2026-10-07: undo the crops)')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('list'); ap.add_argument('--batch', type=int, default=200)
    ap.add_argument('--prefix', default='212-u'); a = ap.parse_args()
    import fcntl                                                   # one instance per lane, whoever starts it
    lock = open(f'/tmp/revert-{a.prefix}.lock', 'w')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('lane', a.prefix, 'already running'); return
    reverted = {r[2][6:] for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t')
                if len(r) > 5 and r[5].startswith('212-') and r[5].endswith('a-substitute-fixed-step1')}
    rows = [r for r in csv.reader(open(a.list, encoding='utf-8'), delimiter='\t') if r]     # stable offsets: resumable
    total = 0
    for k in range(0, len(rows), a.batch):
        name = f'{a.prefix}{k // a.batch + 1:02d}'
        lst = J(f'lists/{name}.tsv')
        if not os.path.exists(lst):
            with open(lst, 'w', encoding='utf-8') as w:
                for r in rows[k:k + a.batch]:
                    if r[0] not in reverted: w.write('\t'.join(r) + '\n')   # never redo a file another lane reverted
        want = {r[0] for r in csv.reader(open(lst, encoding='utf-8'), delimiter='\t') if r}
        done_subs = {r[2][6:] for r in csv.reader(open(J('data/changes/changes.tsv'), encoding='utf-8'), delimiter='\t')
                     if len(r) > 5 and r[5] == f'{name}a-substitute-fixed-step1'}
        if want <= done_subs: continue
        print(time.strftime('%T'), name, len(want), 'files', flush=True)
        for attempt in range(3):
            fx.wait_phone()
            fx.sh(['nice', '/usr/bin/python3', 'scripts/improve_copies.py', lst, f'{name}-copies'],
                  {'PYTHONPATH': fx.TOOLS}, f'logs/{name}-copies.log')
            if want <= set(fx.copies_of(f'{name}-copies')) | done_subs: break
        fx.wait_phone()
        idx = {p: int(s) for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t') if s.isdigit()}
        copies = {p: n for p, n in fx.copies_of(f'{name}-copies').items() if p not in done_subs and p in want}
        n = fx.substitute(name, copies, idx, WHY)
        print(time.strftime('%T'), name, 'substituted', n, flush=True)
        if n < 0: print('substitution failed: see', f'logs/{name}.log'); break
        total += n
    with open(J('WORKLOG.md'), 'a', encoding='utf-8') as w:
        w.write(f'- {time.strftime("%F %H:%M")} — revert_crops.py: {total} cropped files brought back to their whole scanned pages '
                f'(owner 2026-10-07).\n')
    print('done', total)

if __name__ == '__main__':
    main()

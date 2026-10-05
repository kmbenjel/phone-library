"""Make the laptop's ~/Books mirror the phone's names and sections (owner: the local library is a selection of the
phone library; names and sections follow the phone; the folders «أبو العلاء المعري» and «ابن الزبير الغرناطي» are
never touched).
Every local PDF whose MD5 equals a phone file's MD5 (data/phone/md5.tsv) takes that phone file's relative path.
Several local copies of the same bytes → one is kept (verified identical), the others are deleted.
Local-only files stay where they are (listed). Nothing is overwritten.
Usage: python3 scripts/local_sync_plan.py local-md5.txt out.tsv     (local-md5.txt = `md5sum` output run in ~/Books)
  out.tsv rows: action<TAB>from<TAB>to<TAB>reason   (action = move | delete)"""
import collections, csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
PROTECTED = ('أبو العلاء المعري/', 'ابن الزبير الغرناطي/')
LB = os.path.expanduser('~/Books')

def main(local_md5, out):
    idx = {p for p, s in csv.reader(open(J('data/phone/index-now.tsv'), encoding='utf-8'), delimiter='\t')}
    by_md5 = collections.defaultdict(list)
    for r in csv.reader(open(J('data/phone/md5.tsv'), encoding='utf-8'), delimiter='\t'):
        if len(r) == 3 and r[0] in idx: by_md5[r[2]].append(r[0])
    local = collections.defaultdict(list)
    for l in open(local_md5, encoding='utf-8'):
        h, p = l.rstrip('\n').split('  ', 1)
        p = p[2:] if p.startswith('./') else p
        if p.startswith(PROTECTED) or not p.lower().endswith('.pdf'): continue
        local[h].append(p)
    rows, stats, only = [], collections.Counter(), []
    taken = set()
    for h, ps in local.items():
        phone = sorted(by_md5.get(h, []))
        if phone:
            target = phone[0]                    # phone duplicates were removed; if several remain, take the first
            keep = target if target in ps else sorted(ps, key=len)[0]
            for p in ps:
                if p == keep: continue
                rows.append(('delete', p, '', f'byte-identical copy of {keep}')); stats['delete'] += 1
            if keep != target:
                if target in taken or os.path.exists(os.path.join(LB, target)):
                    stats['target exists'] += 1; continue
                rows.append(('move', keep, target, 'same bytes as the phone file → same name and section')); stats['move'] += 1
            taken.add(target); stats['mapped'] += 1
        else:
            keep = sorted(ps, key=len)[0]
            for p in ps:
                if p != keep: rows.append(('delete', p, '', f'byte-identical copy of {keep}')); stats['delete'] += 1
            only.append(keep); stats['local only'] += 1
    with open(out, 'w', encoding='utf-8') as w:
        for r in rows: w.write('\t'.join(r) + '\n')
    with open(J('data/local/local-only.tsv'), 'w', encoding='utf-8') as w:
        for p in sorted(only): w.write(p + '\n')
    print(dict(stats))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

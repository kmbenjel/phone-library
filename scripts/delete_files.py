"""Delete files on the phone (only with the owner's approval), log each deletion, remove folders left empty.
Input: TSV path<TAB>reason (paths relative to the FTP root, e.g. Books/...). Usage: python3 scripts/delete_files.py list.tsv plan-name"""
import csv, ftplib, os, posixpath, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from apply_plan import connect, listing, is_empty, note_del, protected, CACHE, LOG
rows = [r for r in csv.reader(open(sys.argv[1]), delimiter='\t') if r]
plan = sys.argv[2]; f = connect(); done = 0
with open(LOG, 'a', newline='') as lf:
    w = csv.writer(lf, delimiter='\t')
    for p, why in rows:
        if protected(p): print('REFUSED (index folder)', p); continue
        try:
            f.delete(p); note_del(p); done += 1
            w.writerow([time.strftime('%F %T'), 'delete', p, '', why, plan])
            d = posixpath.dirname(p)
            while d.count('/') >= 2 and is_empty(f, d):
                f.rmd(d); note_del(d); CACHE.pop(d, None); w.writerow([time.strftime('%F %T'), 'rmdir', d, '', 'empty after delete', plan]); d = posixpath.dirname(d)
        except ftplib.all_errors as e:
            print('FAIL', p, e); f = connect(); CACHE.clear()
        lf.flush()
print('deleted:', done, 'of', len(rows))

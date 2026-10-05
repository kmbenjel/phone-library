"""One-off (2026-10-05): which lossless fixed copies of plan 139 are worth substituting. A copy is fetched from
«نسخ محسنة للاستبدال», measured with pymupdf (share of each page still visible = CropBox/MediaBox; pages added by
splitting), then deleted locally. Worth it: a split (more pages than the original) or a crop keeping ≤ 90 % of the page
on the median page. Results → data/improve/139-measure.tsv (resumable). Needs PYTHONPATH with pymupdf.
Usage: python3 scratch/measure_139.py"""
import csv, os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: os.path.join(ROOT, p)
import pymupdf
OUT = J('data/improve/139-measure.tsv'); os.makedirs(os.path.dirname(OUT), exist_ok=True)
done = {r[0] for r in csv.reader(open(OUT, encoding='utf-8'), delimiter='\t')} if os.path.exists(OUT) else set()
rows = []
for l in open(J('logs/139-split-and-crop.log'), encoding='utf-8'):
    m = re.match(r"OK (.+\.pdf) (\S+) \{'pages_in': (\d+), 'pages_out': (\d+)", l.strip())
    if m and m.group(1) not in done: rows.append(m.groups())
w = open(OUT, 'a', encoding='utf-8', newline=''); cw = csv.writer(w, delimiter='\t')
tmp = os.path.join(tempfile.gettempdir(), 'measure139.pdf')
for path, ops, pin, pout in rows:
    pin, pout = int(pin), int(pout)
    if pout > pin:                                   # a split always helps: no need to download
        cw.writerow([path, ops, pin, pout, '', 'yes']); w.flush(); continue
    r = subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', 'phone:Books/نسخ محسنة للاستبدال/' + path, tmp, '-q'],
                       capture_output=True)
    if r.returncode or not os.path.exists(tmp): print('FETCH FAIL', path, flush=True); continue
    try:
        d = pymupdf.open(tmp)
        kept = sorted(p.cropbox.get_area() / p.mediabox.get_area() for p in d)
        med = kept[len(kept) // 2] if kept else 1
        cw.writerow([path, ops, pin, pout, f'{med:.3f}', 'yes' if med <= 0.90 else 'no']); w.flush()
        d.close()
    except Exception as e:
        print('MEASURE FAIL', path, e, flush=True)
    finally:
        if os.path.exists(tmp): os.remove(tmp)
print('measured', len(rows))

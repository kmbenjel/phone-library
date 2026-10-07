"""One-off (2026-10-07, owner: «how did you test the cropping?»): measure what the substituted crop copies really look like.
For each file: copy from the phone, read every page's CropBox against its MediaBox (pymupdf), then
  width spread  : widest crop / median crop width (1.00 = every page the same width; the owner saw pages «swaying»)
  odd pages     : share of pages whose crop is > 4 % wider or narrower than the median of their parity (odd/even)
  margin left   : the smallest blank kept between the content box (24-dpi render, as fix_pdf measures it) and the crop
                  edge, as % of page width (≈0 = text touches the edge)
  area kept     : median crop area / page area (≥ 0.85 = the crop changed little: probably not needed)
Writes data/fixed/crop-audit.tsv (append, resumable). Usage: PYTHONPATH=… python3 scratch/crop_audit.py LIST.txt"""
import csv, os, statistics, subprocess, sys, tempfile
import pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from fix_pdf import content_box
OUT = os.path.join(ROOT, 'data/fixed/crop-audit.tsv')

def audit(path):
    d = tempfile.mkdtemp(dir='/tmp'); f = os.path.join(d, 'f.pdf')
    try:
        r = subprocess.run(['flock', '/tmp/phone-ftp.lock', 'rclone', 'copyto', 'phone:Books/' + path, f, '-q'], capture_output=True)
        if r.returncode or not os.path.exists(f): return None
        doc = pymupdf.open(f)
        ws, rows, margins = [], [], []
        for i, p in enumerate(doc):
            cb, mb = p.cropbox, p.mediabox
            ws.append((i % 2, cb.width / mb.width)); rows.append(cb.width * cb.height / (mb.width * mb.height))
        step = max(1, len(doc) // 12)
        for i in range(0, len(doc), step):                     # ~12 pages: how much blank is left around the text
            p = doc[i]; box = content_box(p)
            if box: margins.append(min(box.x0, p.rect.width - box.x1) / p.rect.width)
        med = statistics.median(w for _, w in ws)
        par = {k: statistics.median([w for q, w in ws if q == k] or [med]) for k in (0, 1)}
        odd = sum(1 for q, w in ws if abs(w / par[q] - 1) > 0.04) / len(ws)
        return [path, len(doc), round(max(w for _, w in ws) / med, 3), round(odd, 3),
                round(min(margins), 3) if margins else '', round(statistics.median(rows), 3)]
    finally:
        subprocess.run(['rm', '-rf', d])

def main():
    done = {r[0] for r in csv.reader(open(OUT, encoding='utf-8'), delimiter='\t')} if os.path.exists(OUT) else set()
    todo = [l.rstrip('\n') for l in open(sys.argv[1], encoding='utf-8') if l.strip() and l.rstrip('\n') not in done]
    with open(OUT, 'a', encoding='utf-8') as w:
        for p in todo:
            try: r = audit(p)
            except Exception as e: r = [p, 'error', type(e).__name__, '', '', '']
            if r: w.write('\t'.join(map(str, r)) + '\n'); w.flush(); print('\t'.join(map(str, r))[-120:], flush=True)

if __name__ == '__main__':
    main()

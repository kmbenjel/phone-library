"""basesurvey.py [J] [SAMPLE_UNTURNED] — every page 26g turns (b32a237bbf recipes), plus a random sample of the text pages it
leaves: each line's baseline fitted to a fraction of a pixel (basefit.base_angles, 1,400 px, the page as scanned) → the
page's own tilt (median over its lines, the tilt the turn must undo: after = tilt − turn) → basesurvey.tsv
(book, page, turn, flags, tilt, lines, spread = IQR of the lines' angles, the lines' angles); resumable"""
import os, sys, json, glob, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from basefit import base_angles, bc, C
import numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
D = os.path.dirname(os.path.abspath(__file__)); OUT = f'{D}/basesurvey.tsv'
FL = ('tilt_by_proj', 'level_by_proj', 'image_third', 'level_by_lines', 'level_by_edge', 'tilt_by_edge', 'curved', 'owner_turn',
      'level_by_rules', 'tilt_by_rules', 'level_by_columns', 'reduced', 'turned_in_check', 'level_first', 'image_loose',
      'untreated_tilt', 'tilt_disputed', 'unsure_tilt', 'frame_level', 'proj_level_rule')

def one(arg):
    h, items = arg; out = []
    doc = pymupdf.open(C + h + '.pdf')
    for i, d, why, tb, paper in items:
        try:
            a, z = bc.gray(doc[i], 1400); L = base_angles(np.array(a), paper, tb, z)
        except Exception as e: L = []
        an = [v[1] for v in L]
        m = round(float(np.median(an)), 3) if an else None
        iqr = round(float(np.subtract(*np.percentile(an, [75, 25]))), 3) if len(an) >= 4 else None
        out.append('\t'.join([h, str(i + 1), str(d), ','.join(why), str(m), str(len(an)), str(iqr), json.dumps(an)]))
    doc.close(); return out

if __name__ == '__main__':
    J = int(sys.argv[1]) if len(sys.argv) > 1 else 2; S = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    done = set()
    if os.path.exists(OUT): done = {tuple(l.split('\t')[:2]) for l in open(OUT)}
    jobs = []; random.seed(5)
    for f in sorted(glob.glob(C + '*.b32a237bbf*.json')):
        h = os.path.basename(f)[:12]; R = json.load(open(f)); it = []
        for i, p in enumerate(R['pages']):
            tb = p.get('text') or p.get('core')
            if (h, str(i + 1)) in done or tb is None or p.get('kind') not in (None, 'text'): continue
            if p.get('skew') or (S and random.random() < S / 16000):
                it.append((i, p.get('skew') or 0.0, [k for k in FL if p.get(k) is not None], tb, p.get('paper') or 255))
        for k in range(0, len(it), 40): jobs.append((h, it[k:k + 40]))
    print(len(jobs), 'chunks', flush=True)
    with open(OUT, 'a') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs):
            for row in part: fo.write(row + '\n')
            fo.flush()

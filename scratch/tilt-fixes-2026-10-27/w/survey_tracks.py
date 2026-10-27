"""survey_tracks.py [J] [SAMPLE_UNTURNED] — every page 26g turns (b32a237bbf recipes) and a random sample of the text pages it
leaves: line_tracks at 1,000 px on the page as scanned (sheet, stamps and dot fields whitened, as verify's views) →
tracks.tsv (book, page, turn, flags, tracks [(y, angle, share, rms, n)]); resumable"""
import os, sys, json, glob, random
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
import numpy as np, pymupdf
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from track import line_tracks
C = '/home/k/.cache/phone-library/crop-regress/'; OUT = f'{D}/tracks.tsv'
FL = ('tilt_by_proj', 'level_by_proj', 'image_third', 'level_by_lines', 'level_by_edge', 'tilt_by_edge', 'curved', 'owner_turn',
      'level_by_rules', 'tilt_by_rules', 'level_by_columns', 'tilt_by_columns', 'reduced', 'turned_in_check', 'level_first',
      'image_loose', 'untreated_tilt', 'tilt_disputed', 'unsure_tilt', 'frame_level', 'proj_level_rule', 'lines_lean')

def one(arg):
    h, items = arg; out = []
    doc = pymupdf.open(C + h + '.pdf')
    for i, d, why, tb, paper, sheet, ex in items:
        try:
            page = doc[i]; a, z = bc.gray(page, 1000); a = np.array(a)
            if sheet: a = bc.whiten(a, z, sheet)
            for b in [bc.pad_box(b, page.rect.width) for b in ex[0]] + ex[1]:
                a[max(0, int(b[1] * z)):int(b[3] * z) + 1, max(0, int(b[0] * z)):int(b[2] * z) + 1] = 255
            T = line_tracks(a, paper, tb, z)
        except Exception as e: T = [['err', str(e)[:80]]]
        out.append('\t'.join([h, str(i + 1), str(d), ','.join(why), json.dumps(T)]))
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
            if p.get('skew') or p.get('lines_lean') or (S and random.random() < S / 16000):
                it.append((i, p.get('skew') or 0.0, [k for k in FL if p.get(k) is not None], tb, p.get('paper') or 255,
                           p.get('sheet'), (p.get('stamp') or [], p.get('dots') or [])))
        for k in range(0, len(it), 40): jobs.append((h, it[k:k + 40]))
    print(len(jobs), 'chunks', flush=True)
    with open(OUT, 'a') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs):
            for row in part: fo.write(row + '\n')
            fo.flush()
    print('done', flush=True)

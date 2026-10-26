"""turnsurvey.py [J] — every page 26g turns (b32a237bbf recipes): each line of its text block measured on its own (fast
line_leans, 1,400 px) as scanned and as turned → turnsurvey.tsv (book, page, turn, how it was turned, lines before, lines
after); resumable (pages already written are skipped)"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastleans import fast_line_leans, bc, C
import pymupdf
from concurrent.futures import ProcessPoolExecutor
D = os.path.dirname(os.path.abspath(__file__)); OUT = f'{D}/turnsurvey.tsv'
FL = ('tilt_by_proj', 'level_by_proj', 'image_third', 'level_by_lines', 'level_by_edge', 'tilt_by_edge', 'curved', 'owner_turn',
      'level_by_rules', 'tilt_by_rules', 'level_by_columns', 'reduced', 'turned_in_check', 'level_first', 'image_loose')

def one(arg):
    h, items = arg; out = []
    doc = pymupdf.open(C + h + '.pdf')
    for i, d, why, tb, paper in items:              # (the first look's text block for both views: a turn ≤ 2° moves its
        tu = bc.Turner(doc, i); L = []                #  corners less than line_leans' 2 % / 1 % margins)
        try:
            for k in (0.0, d):
                a14, z14 = bc.gray(tu.page(k), 1400)
                L.append(fast_line_leans(a14.copy(), paper, tb, z14))
        finally: tu.close()
        out.append('\t'.join([h, str(i + 1), str(d), ','.join(why), json.dumps(L[0]), json.dumps(L[1])]))
    doc.close(); return out

if __name__ == '__main__':
    J = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    done = set()
    if os.path.exists(OUT): done = {tuple(l.split('\t')[:2]) for l in open(OUT)}
    jobs = []
    for f in sorted(glob.glob(C + '*.b32a237bbf*.json')):
        h = os.path.basename(f)[:12]; R = json.load(open(f))
        it = [(i, p['skew'], [k for k in FL if p.get(k) is not None], p.get('text') or p.get('core') or p.get('box'), p.get('paper') or 255)
              for i, p in enumerate(R['pages']) if p.get('skew') and (h, str(i + 1)) not in done]
        for k in range(0, len(it), 25): jobs.append((h, it[k:k + 25]))
    print(len(jobs), 'chunks', flush=True)
    with open(OUT, 'a') as fo, ProcessPoolExecutor(J) as ex:
        for part in ex.map(one, jobs):
            for row in part: fo.write(row + '\n')
            fo.flush()

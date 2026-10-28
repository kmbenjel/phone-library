"""survey_w.py OUT.jsonl [-j J] — guard W (two_angles) on every page regression 26j turned (not by printed rules, not the
owner's), all 31 books: the lines followed across the page (line_tracks at 1,000 px, as verify's look: sheet, stamps and
dot fields whitened) as scanned and as turned, lines_read, and the verdict with a line «made worse» from 0.5° (now) and
from 0.35° (the band two_angles itself calls «takes the turn»). Where 0.35° refuses: the print's certificate, and the
median turn the guard falls back on (no line worse, four fifths within 0.2°, shear ≤ 0.2°). One JSON line per page;
resumable (pages already written are skipped). Code: code/bc_j.py = book_crop 9a43a0bc8c."""
import sys, os, json, glob
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import bc_j as bc
C = os.path.expanduser('~/.cache/phone-library/crop-regress')

def two_angles_t(L, T):
    if not L: return []
    w = [v for v in L if abs(v[2]) >= max(T, abs(v[1]) + 0.25) - 1e-6]
    agree = sum(1 for v in L if abs(v[2]) <= 0.35 + 1e-6)
    return w if len(w) >= 2 and (len(w) >= 0.2 * len(L) or agree < 0.8 * len(L)) else []

def work(args):
    pdf, rec_pages, idx = args
    import pymupdf
    doc = pymupdf.open(pdf); out = []
    for i in idx:
        pq = rec_pages[i]; tu = bc.Turner(doc, i)
        def view(d):
            q = {'skew': d}; page = tu.page(d, 0, 0); a, z = bc.gray(page, 1000)
            if pq.get('sheet'): a = bc.whiten(a, z, bc.fwd_box(doc, i, q, pq['sheet']))
            ex = [bc.pad_box(b, page.rect.width) for b in pq.get('stamp') or []] + (pq.get('dots') or [])
            fb = bc.fwd_boxes(doc, i, q, ex) if ex else None
            mk = bc.marks(a, z, page.rect.width, fb)
            if not mk.get('paper'): return mk, []
            b = a.copy()
            for x in fb or []: b[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
            return mk, bc.line_tracks(b, mk['paper'], mk.get('text'), z)
        d = pq['skew']; _, t0 = view(0); _, t1 = view(d)
        L = bc.lines_read(t0, t1, d); w50, w35 = two_angles_t(L, 0.5), two_angles_t(L, 0.35)
        r = {'pdf': os.path.basename(pdf)[:12], 'page': i + 1, 'skew': d, 'n': len(L) if L else 0,
             'w50': len(w50), 'w35': len(w35), 'by': [k for k in ('tilt_by_tracks', 'tilt_by_base', 'tilt_by_proj', 'turn_by_tracks',
             'level_by_print', 'base_found', 'image_third', 'tilt_by_edge', 'tilt_by_columns') if pq.get(k) is not None]}
        if w35 and not w50:
            cert, R = bc.print_turn(t0, t1, d); r['cert'] = bool(cert); r['L'] = L
            if not cert:
                m = round(round(float(np.median([v[1] for v in L])) / 0.025) * 0.025, 3); r['median'] = m; ok = False
                if abs(m) >= bc.SKEW_MIN:
                    m2, tm = view(m); L2 = bc.lines_read(t0, tm, m)
                    ok = bool(L2 and not two_angles_t(L2, 0.35) and sum(1 for v in L2 if abs(v[2]) <= 0.2 + 1e-6) >= 0.8 * len(L2)
                              and m2.get('xy') is not None and abs(bc.skew_of(m2['xy'], raw=True)[0]) <= 0.2 + 1e-6)
                r['median_ok'] = ok
        out.append(r); tu.close()
    doc.close(); return out

if __name__ == '__main__':
    outp = sys.argv[1]; J = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 3
    done = set()
    if os.path.exists(outp):
        for l in open(outp):
            try: x = json.loads(l); done.add((x['pdf'], x['page']))
            except ValueError: pass
    fo = open(outp, 'a')
    for f in sorted(glob.glob(f'{C}/*.9a43a0bc8c*.json')):
        h = os.path.basename(f)[:12]; rec = json.load(open(f)); pdf = f'{C}/{h}.pdf'
        idx = [i for i, p in enumerate(rec['pages']) if p.get('skew') and p.get('level_by_rules') is None
               and p.get('owner_turn') is None and (h, i + 1) not in done]
        if not idx or not os.path.exists(pdf): continue
        if rec.get('split'): print(h, 'split book: skipped (pages renumbered)', flush=True); continue
        with ProcessPoolExecutor(J) as ex:
            for part in ex.map(work, [(pdf, rec['pages'], idx[k::J]) for k in range(J)]):
                for r in part: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
                fo.flush()
        print(h, len(idx), 'pages', flush=True)

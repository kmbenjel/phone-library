"""twoang_page.py OUTDIR [-j J] — the pictures of the owner's review page crop-tilt-003: every page the method leaves as
scanned for its two angles (regression 27l, book_crop 6a1fad7b21: page flag two_angles = the turn refused). Per page two
pictures: 1 the page as scanned, every line it is judged by (line_tracks at 1,000 px with the survey's view: sheet, stamps,
dot fields whitened; lines_read: the same line read alike in both views) drawn at its own angle with its tilt; 2 the page
as the refused turn would have made it, the same lines at their angles after it. Green: within 0.35° of level; red: more.
Writes OUTDIR/<book>-<page>-1.jpg, -2.jpg and OUTDIR/rows.jsonl (resumable). Uses the current scripts/book_crop.py."""
import sys, os, json, glob, math
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
from concurrent.futures import ProcessPoolExecutor
C = os.path.expanduser('~/.cache/phone-library/crop-regress'); MD5 = '6a1fad7b21'

def draw(bc, a, z, tb, lines, title, out):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.fromarray(a).convert('RGB'); dr = ImageDraw.Draw(img); W = img.width
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    x0, x1 = tb[0] * z, tb[2] * z; xc = (x0 + x1) / 2
    for y, ang in lines:
        col = (0, 150, 0) if abs(ang) <= 0.35 + 1e-6 else (215, 0, 0)
        k = math.tan(math.radians(ang)); yc = y * z          # (line_tracks fits rows on columns, y down — as twoang_vis.py)
        dr.line([(x0, yc + k * (x0 - xc)), (x1, yc + k * (x1 - xc))], fill=col, width=3)
        lab = f'{abs(ang):.2f}°'; tx = x1 + 8 if x1 + 110 < W else max(2, x0 - 100)
        dr.text((tx, yc - 12), lab, fill=col, font=F)
    dr.text((14, 10), title, fill=(0, 0, 190), font=F)
    img = img.resize((900, img.height * 900 // W)); img.save(out, quality=82)

def work(args):
    h, items, outdir = args
    import book_crop as bc, pymupdf
    doc = pymupdf.open(f'{C}/{h}.pdf'); res = []
    for pg, pq in items:
        i = pg - 1; d = pq['two_angles']; tu = bc.Turner(doc, i)
        def view(t):
            q = {'skew': t}; page = tu.page(t, 0, 0); a, z = bc.gray(page, 1000)
            if pq.get('sheet'): a = bc.whiten(a, z, bc.fwd_box(doc, i, q, pq['sheet']))
            ex = [bc.pad_box(b, page.rect.width) for b in pq.get('stamp') or []] + (pq.get('dots') or [])
            fb = bc.fwd_boxes(doc, i, q, ex) if ex else None
            mk = bc.marks(a, z, page.rect.width, fb)
            if not mk.get('paper'): return a, z, mk, []
            b = a.copy()
            for x in fb or []: b[max(0, int(x[1] * z)):int(x[3] * z) + 1, max(0, int(x[0] * z)):int(x[2] * z) + 1] = 255
            return a, z, mk, bc.line_tracks(b, mk['paper'], mk.get('text'), z)
        a0, z0, m0, t0 = view(0); a1, z1, m1, t1 = view(d)
        L = bc.lines_read(t0, t1, d) or []
        y1 = [min((u for u in t1 if abs(u[0] - y) <= 6), key=lambda u: abs(u[0] - y), default=(y,))[0] for y, _, _ in L]
        n = f'{h}-{pg}'
        if L and m0.get('text') and m1.get('text'):
            draw(bc, a0, z0, m0['text'], [(y, b) for y, b, _ in L], f'p. {pg}: as scanned', f'{outdir}/{n}-1.jpg')
            draw(bc, a1, z1, m1['text'], [(yy, af) for yy, (_, _, af) in zip(y1, L)], f'p. {pg}: turned {d}°', f'{outdir}/{n}-2.jpg')
        res.append({'pdf': h, 'page': pg, 'turn': d, 'L': L, 'worse': len(bc.two_angles(L)), 'lean': pq.get('lines_lean')})
        tu.close()
    doc.close(); return res

if __name__ == '__main__':
    outdir = sys.argv[1]; J = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 2
    os.makedirs(outdir, exist_ok=True); rp = f'{outdir}/rows.jsonl'
    done = {(r['pdf'], r['page']) for r in map(json.loads, open(rp))} if os.path.exists(rp) else set()
    S = os.path.dirname(os.path.abspath(__file__))
    want = [r for r in map(json.loads, open(f'{S}/survey-w.jsonl'))
            if r['w35'] and not r['w50'] and not r.get('cert') and not r.get('median_ok')]
    jobs = {}
    for r in want:
        if (r['pdf'], r['page']) in done: continue
        rec = json.load(open(glob.glob(f"{C}/{r['pdf']}.{MD5}*.json")[0]))
        pq = rec['pages'][r['page'] - 1]
        if pq.get('two_angles') is None: print(r['pdf'], r['page'], 'NOT flagged two_angles in 27l', flush=True); continue
        jobs.setdefault(r['pdf'], []).append((r['page'], pq))
    fo = open(rp, 'a')
    with ProcessPoolExecutor(J) as ex:
        for part in ex.map(work, [(h, it, outdir) for h, it in jobs.items()]):
            for x in part: fo.write(json.dumps(x, ensure_ascii=False) + '\n')
            fo.flush(); print(part[0]['pdf'], len(part), 'pages', flush=True)

"""sel_sheets.py OLD NEW OUTDIR [BOOK …] [--min PT] [--px PX] — the pages of two regression runs (recipes in the regression
cache, by book_crop md5 prefix) whose box moved ≥ PT (default 3) on any side, whose move (q…cm shift) moved ≥ PT, or whose
scale / kind / enlargement changed — drawn as the reader sees them (book_crop.sheet «after»): the page before (new) | OLD |
NEW | the page after (new), so a page's place is judged against its neighbours. One JPEG per page (BOOK-pNNNN.jpg) and
index.tsv (book, page, cause, box move, q-move, scale/kind/enlarged changed). Rewritten 2026-10-28 (the 10-27 copy was lost
with the /tmp scratchpad)"""
import sys, os, json, glob, tempfile, textwrap
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
from crop_recipe_diff import C, cause
from PIL import Image, ImageDraw, ImageFont

def recipe(h, v):
    f = sorted(glob.glob(f'{C}{h}.{v}*.json'))
    return json.load(open(f[-1])) if f else None

def moved(p, q, lim):
    a, b = p.get('crop'), q.get('crop')
    mv = max(abs(x - y) for x, y in zip(a, b)) if a and b else (99.0 if a != b else 0.0)
    ma, mb = p.get('move') or [0, 0], q.get('move') or [0, 0]
    mm = max(abs(x - y) for x, y in zip(ma, mb)) if isinstance(ma, list) and isinstance(mb, list) else (99.0 if ma != mb else 0.0)
    other = [k for k in ('scale', 'kind', 'enlarged') if p.get(k) != q.get(k)]
    return (mv >= lim or mm >= lim or bool(other)), round(mv, 1), round(mm, 1), other

if __name__ == '__main__':
    args = sys.argv[1:]; lim, px = 3.0, 300
    for flag in ('--min', '--px'):
        if flag in args:
            k = args.index(flag); v = float(args[k + 1]); del args[k:k + 2]
            if flag == '--min': lim = v
            else: px = int(v)
    old, new, out, books = args[0][:10], args[1][:10], args[2], set(args[3:])
    os.makedirs(out, exist_ok=True)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    idx = open(os.path.join(out, 'index.tsv'), 'a')
    for f in sorted(glob.glob(f'{C}*.{old}*.json')):
        h = os.path.basename(f)[:12]
        if books and h not in books: continue
        A, B = recipe(h, old), recipe(h, new)
        if not B: continue
        sel = []
        for i, (p, q) in enumerate(zip(A['pages'], B['pages'])):
            ok, mv, mm, other = moved(p, q, lim)
            if ok: sel.append((i, mv, mm, other))
        if not sel: continue
        ch = [s[0] for s in sel]; n = len(B['pages'])
        nb = sorted({j for i in ch for j in (i - 1, i + 1) if 0 <= j < n})
        src = C + h + '.pdf'
        with tempfile.TemporaryDirectory() as td:
            ma = {m['page']: m for m in bc.sheet(src, A, os.path.join(td, 'a'), [(i, '') for i in ch], px=px)}
            mb = {m['page']: m for m in bc.sheet(src, B, os.path.join(td, 'b'), [(i, '') for i in sorted(set(ch) | set(nb))], px=px)}
            for i, mv, mm, other in sel:
                p, q = A['pages'][i], B['pages'][i]; c = cause(p, q) or 'OTHER'
                ims, tags = [], []
                if i >= 1 and i in mb: ims.append(Image.open(mb[i]['after'])); tags.append(f'p.{i} new')
                ims += [Image.open(ma[i + 1]['after']), Image.open(mb[i + 1]['after'])]; tags += [f'p.{i + 1} OLD', f'p.{i + 1} NEW']
                if i + 2 in mb: ims.append(Image.open(mb[i + 2]['after'])); tags.append(f'p.{i + 2} new')
                cap = (f'{h} p. {i + 1} [{c}] box {mv} pt' + (f' q-move {mm}' if mm else '') + (f' {"/".join(other)}' if other else '') +
                       f'  old skew {p.get("skew")} crop {p.get("crop")}  new skew {q.get("skew")} crop {q.get("crop")}' +
                       (f' scale {p.get("scale")}→{q.get("scale")}' if 'scale' in other else '') +
                       (f' enlarged {p.get("enlarged")}→{q.get("enlarged")}' if 'enlarged' in other else ''))
                lines = textwrap.wrap(cap, 160)[:3]; top = 6 + 16 * len(lines) + 16
                W = sum(im.width for im in ims) + 12 * (len(ims) - 1); H = max(im.height for im in ims) + top
                sh = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(sh); x = 0
                for im, t in zip(ims, tags):
                    sh.paste(im, (x, top)); d.text((x + 3, top - 15), t, fill='red' if ('OLD' in t or 'NEW' in t) else 'grey', font=font)
                    d.rectangle([x, top, x + im.width - 1, top + im.height - 1], outline='black'); x += im.width + 12
                for k, l in enumerate(lines): d.text((4, 3 + 16 * k), l, fill='black', font=font)
                sh.save(os.path.join(out, f'{h}-p{i + 1:04d}.jpg'), quality=82)
                idx.write(f'{h}\t{i + 1}\t{c}\t{mv}\t{mm}\t{",".join(other)}\n')
        idx.flush(); print(h, len(sel), 'pages drawn', flush=True)

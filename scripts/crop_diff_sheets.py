"""Every page whose turn, box, shown part, scale, move or kind changed between the regression recipes of two book_crop
versions, drawn as the reader sees it — old (left) | new (right), the cause and the after-turn readings in the caption — so
each change is checked by eye before anything reaches the phone (with crop_recipe_diff.py). One JPEG per page in OUTDIR.
Usage: crop_diff_sheets.py OLDMD5 NEWMD5 OUTDIR [BOOK …]"""
import glob, json, os, sys, tempfile, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_crop as bc
from crop_recipe_diff import C, KEYS, cause
from PIL import Image, ImageDraw, ImageFont

def main(old, new, out, only):
    os.makedirs(out, exist_ok=True)
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    except OSError: font = ImageFont.load_default()
    for f in sorted(glob.glob(C + f'*.{old}*.json')):
        h = os.path.basename(f)[:12]
        if only and h not in only: continue
        nf = sorted(glob.glob(C + f'{h}.{new}*.json'))
        if not nf: continue
        A, B = json.load(open(f)), json.load(open(nf[-1]))
        ch = [i for i, (p, q) in enumerate(zip(A['pages'], B['pages'])) if any(p.get(k) != q.get(k) for k in KEYS)]
        if not ch: continue
        src = C + h + '.pdf'
        with tempfile.TemporaryDirectory() as td:
            ma = {m['page']: m for m in bc.sheet(src, A, os.path.join(td, 'a'), [(i, '') for i in ch])}
            mb = {m['page']: m for m in bc.sheet(src, B, os.path.join(td, 'b'), [(i, '') for i in ch])}
            for i in ch:
                a, b = Image.open(ma[i + 1]['after']), Image.open(mb[i + 1]['after'])
                p, q = A['pages'][i], B['pages'][i]
                cap = (f'{h} p. {i + 1} [{cause(p, q) or "OTHER"}]  old: skew {p.get("skew")} crop {p.get("crop")}   new: skew {q.get("skew")} '
                       f'crop {q.get("crop")} enlarged {q.get("enlarged")}  after {q.get("after_tilt")}/{q.get("after_tilt_image")}')
                lines = textwrap.wrap(cap, 110)[:4]; top = 8 + 20 * len(lines)
                im = Image.new('RGB', (a.width + b.width + 30, max(a.height, b.height) + top), 'white')
                im.paste(a, (0, top)); im.paste(b, (a.width + 30, top))
                d = ImageDraw.Draw(im)
                for k, l in enumerate(lines): d.text((6, 4 + 20 * k), l, fill='black', font=font)
                im.save(os.path.join(out, f'{h}-p{i + 1:04d}.jpg'), quality=80)
        print(h, len(ch), 'pages drawn', flush=True)

if __name__ == '__main__':
    main(sys.argv[1][:10], sys.argv[2][:10], sys.argv[3], set(sys.argv[4:]))

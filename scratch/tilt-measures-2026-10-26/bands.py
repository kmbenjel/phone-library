"""bands.py BOOK PAGE OUT.jpg Y0:Y1 [Y0:Y1 …] [--turn D] [--md MD5] — bands of a page (pt on the page as shown, from its top),
each as scanned (above) and as the recipe turns it (below, or by D), at 1,400 px, with straight guide lines through each
band; a strip above each says which (beige: as scanned, blue: turned). For the owner's question pages"""
import glob, json, os, sys, tempfile, copy
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
from PIL import Image, ImageDraw, ImageFont
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
args = sys.argv[1:]; turn = None; md = 'b32a237bbf'
if '--turn' in args: k = args.index('--turn'); turn = float(args[k + 1]); del args[k:k + 2]
if '--md' in args: k = args.index('--md'); md = args[k + 1]; del args[k:k + 2]
h, pg, out = args[0], int(args[1]), args[2]; bands = [tuple(map(float, b.split(':'))) for b in args[3:]]
R = json.load(open(sorted(glob.glob(C + f'{h}.{md}*.json'))[-1])); p = R['pages'][pg - 1]
R0 = copy.deepcopy(R); R1 = copy.deepcopy(R)
for k in ('skew', 'move'): R0['pages'][pg - 1].pop(k, None)
if turn is not None: R1['pages'][pg - 1]['skew'] = turn
for k in ('crop', 'show'):                                   # the whole page, so both views show the same place
    for r in (R0, R1): r['pages'][pg - 1].pop(k, None)
ims = []
for r in (R0, R1):
    with tempfile.TemporaryDirectory() as td:
        m = bc.sheet(C + h + '.pdf', r, td, [(pg - 1, '')], px=1400)[0]
        im = Image.open(m['after']).convert('RGB'); im.load(); ims.append(im)
W, H = ims[0].size; z = H / p['h']
tb = p.get('core') or p.get('text') or [0, 0, p['w'], p['h']]   # (cropped to the text block's width, 4 % around it)
X0, X1 = max(0, int((tb[0] - 0.04 * p['w']) * z)), min(W, int((tb[2] + 0.04 * p['w']) * z))
tiles = []
for y0, y1 in bands:
    for n, im in enumerate(ims):
        b = im.crop((X0, int(y0 * z), X1, int(y1 * z))).copy(); d = ImageDraw.Draw(b); bh = b.size[1]
        for k in range(1, 8): d.line([(0, k * bh // 8), (X1 - X0, k * bh // 8)], fill=(220, 40, 40), width=1)
        lab = Image.new('RGB', (X1 - X0, 14), (200, 190, 170) if n == 0 else (120, 160, 210))   # beige: as scanned; blue: turned
        tiles += [lab, b]
    tiles.append(Image.new('RGB', (X1 - X0, 24), (255, 255, 255)))
sh = Image.new('RGB', (X1 - X0, sum(t.size[1] for t in tiles)), (255, 255, 255)); y = 0
for t in tiles: sh.paste(t, (0, y)); y += t.size[1]
sh.save(out, quality=88); print(out, sh.size, 'skew', p.get('skew'))

"""quick.py BOOK PAGE … — the first look of bc_q on chosen pages (the book's stamps from its recipe) next to 26g's recipe"""
import sys, json, glob, time
sys.path.insert(0, 'code')
import bc_q
C = '/home/k/.cache/phone-library/crop-regress/'
h = sys.argv[1]; pgs = [int(x) for x in sys.argv[2:]]
R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1]))
st = {i: p['stamp'] for i, p in enumerate(R['pages']) if p.get('stamp') and not p.get('colour_stamp')}
t = time.time(); new = bc_q.analyse_pages(C + h + '.pdf', st, only={g - 1 for g in pgs})
for g in pgs:
    o, n = R['pages'][g - 1], new[g - 1]
    print(f'{h} p. {g}: 26g proj {o.get("tilt_by_proj")} turn {o.get("skew")} | q proj {n.get("tilt_by_proj")} base {n.get("tilt_by_base")} turn {n.get("skew")} sheet-line {n.get("proj_sheet_line")}')
print(f'{time.time() - t:.1f} s')

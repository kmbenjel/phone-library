"""quickr.py BOOK PAGE … — bc_r's second look (verify) on chosen pages of 26g's recipe"""
import sys, json, glob, time, copy
sys.path.insert(0, 'code')
import bc_r
C = '/home/k/.cache/phone-library/crop-regress/'
h = sys.argv[1]; pgs = [int(x) for x in sys.argv[2:]]
R = json.load(open(sorted(glob.glob(C + h + '.b32a237bbf*.json'))[-1])); R0 = copy.deepcopy(R)
t = time.time(); rec = bc_r.verify(C + h + '.pdf', R, only={g - 1 for g in pgs})
for g in pgs:
    o, n = R0['pages'][g - 1], rec['pages'][g - 1]
    print(f'{h} p. {g}: 26g turn {o.get("skew")} | r turn {n.get("skew")} base {n.get("tilt_by_base")} → {n.get("level_by_base")} found {n.get("base_found")} flags', {k: n.get(k) for k in ('untreated_tilt', 'tilt_disputed', 'unsure_tilt', 'proj_level_rule') if n.get(k) is not None})
print(f'{time.time() - t:.1f} s')

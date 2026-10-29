"""ftest.py BOOK PAGE TURN — fix F's smoke test on ONE page: the second look (verify, only that page) of 27m's recipe under
code/bc_f.py, once without the owner's verdict and once with it ({PAGE: TURN}; 0 = «leave as scanned»): the page's turn, the
fields F sets, and the crop it ends with (2026-10-29)."""
import sys, json, glob, os, copy
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S + '/code'); sys.path.insert(1, '/home/k/projects/phone-library/scripts')
import bc_f as bc
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
h, pg, t = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
rec0 = json.load(open(sorted(glob.glob(f'{C}{h}.4fcdf11f58*.json'))[-1]))
for ot in ({}, {pg: t}):
    r = bc.verify(f'{C}{h}.pdf', copy.deepcopy(rec0), only={pg - 1}, owner_turns=ot)
    p = r['pages'][pg - 1]
    print(f'owner_turns {ot}: skew {p.get("skew")} owner_flat {p.get("owner_flat")} owner_turn {p.get("owner_turn")} two_angles {p.get("two_angles")} '
          f'crop {p.get("crop")} | lists: two_angles {pg in r["two_angles"]} untreated {pg in r["untreated_tilt"]} residual {pg in r["residual_tilt"]}')

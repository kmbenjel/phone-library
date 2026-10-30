"""ntest.py BOOK PAGE TURN VARIANT… — fix N's smoke test on ONE page: 27m's recipe with that page put back to the state the
second look starts from (the first look's turn TURN, the verdicts verify adds removed), verify (only that page) under each
code variant (crop-fixes-2026-10-28m/code or this folder's code): the turn kept and the fields that say why (2026-10-29)."""
import sys, json, glob, os, copy, importlib
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S + '/code'); sys.path.insert(1, S + '/../crop-fixes-2026-10-28m/code'); sys.path.insert(2, '/home/k/projects/phone-library/scripts')
C = os.path.expanduser('~/.cache/phone-library/crop-regress/')
h, pg, t = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
rec0 = json.load(open(sorted(glob.glob(f'{C}{h}.4fcdf11f58*.json'))[-1]))
P = rec0['pages'][pg - 1]
for k in ('two_angles', 'lines_lean', 'loop_fallback', 'level_by_proj', 'level_by_tracks', 'after_tilt', 'after_tilt_image',
          'unsure_tilt', 'turned_in_check', 'turn_by_tracks', 'tracks_near', 'owner_flat'): P.pop(k, None)
P['skew'] = t
for v in sys.argv[4:]:
    bc = importlib.import_module('bc_' + v)
    r = bc.verify(f'{C}{h}.pdf', copy.deepcopy(rec0), only={pg - 1}, owner_turns={})
    p = r['pages'][pg - 1]
    print(f'{v}: skew {p.get("skew")} tracks_near {p.get("tracks_near")} level_by_tracks {p.get("level_by_tracks")} level_by_proj {p.get("level_by_proj")} '
          f'loop_fallback {p.get("loop_fallback")} two_angles {p.get("two_angles")} unsure {p.get("unsure_tilt")} crop {p.get("crop")}')

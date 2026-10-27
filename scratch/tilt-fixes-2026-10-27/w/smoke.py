"""smoke.py — the committed-to-be book_crop on the smallest regression book (2a8c4bfeff47, 54 pages), as crop_regress
calls it (plan with the owner's turns), compared page by page with 26h's recipe"""
import sys, os, json, time
sys.path.insert(0, '/home/k/projects/phone-library/scripts')
import book_crop as bc
import crop_batch as cb
C = '/home/k/.cache/phone-library/crop-regress/'
h = sys.argv[1] if len(sys.argv) > 1 else '2a8c4bfeff47'
t = time.time()
ot = cb.owner_turns(h) if hasattr(cb, 'owner_turns') else None
rec = bc.plan(C + h + '.pdf', jobs=2, owner_turns=ot or None)
print(h, 'plan', round(time.time() - t), 's', rec.get('decision'), rec.get('size'))
old = json.load(open(C + h + '.20d30c2020.json'))
K = ('skew', 'crop', 'show', 'scale', 'move', 'kind')
for i, (p, q) in enumerate(zip(old['pages'], rec['pages'])):
    if any(p.get(k) != q.get(k) for k in K):
        print('  p.', i + 1, {k: (p.get(k), q.get(k)) for k in K if p.get(k) != q.get(k)},
              {k: q[k] for k in ('two_angles', 'turn_by_tracks', 'level_by_tracks', 'tilt_by_base', 'level_by_base', 'base_found',
                                  'level_by_print', 'proj_sheet_line') if q.get(k) is not None})
print('two_angles', rec.get('two_angles'))

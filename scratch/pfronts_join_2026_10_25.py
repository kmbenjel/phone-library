"""One-off (owner 2026-10-20 «لا بد أن يكون هناك غلاف» / «ولم ليست المقدمة مع الجزء الأول»): each «…p.pdf» front part of an
archive.org item that never reached the phone is joined with its volume (scripts/join_parts.py: page objects copied, image
streams unchanged), the volume's own pages that repeat the part's (title page, imprint, blanks — read by eye on the match
sheets) left out. Writes the joined files to argv[1]/joined/, plans/371-…-aside.tsv (each original volume set aside in
«نسخ مستبعدة/__المستبدل») and data/queue/372-….tsv (the joined file uploaded under the volume's own name)."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
S = sys.argv[1]
SPEC = {1: ['P', 'V:2-z'], 3: ['P', 'V:3-z'], 4: ['P', 'V:1-1', 'V:3-z'], 5: ['V:1-1', 'P', 'V:2-z'], 18: ['P', 'V:2-z'],
        21: ['P', 'V:3-z'], 22: ['V:1-2', 'P', 'V:3-z'], 23: ['V:1-1', 'P', 'V:3-z'], 25: ['P', 'V:3-z'], 26: ['P', 'V:5-z'],
        28: ['P', 'V:5-z'], 29: ['P', 'V:5-z'], 30: ['P', 'V:2-3', 'V:5-z'], 31: ['P', 'V:2-z'], 32: ['P', 'V:5-z']}
WHOLE = [6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 20, 24, 33]                 # the volume has no front of its own: part + volume
m = {x['i']: x for x in json.load(open(f'{S}/match.json'))}
t = {x['i']: x for x in json.load(open(f'{S}/targets.json'))}
os.makedirs(f'{S}/joined', exist_ok=True)
aside, queue = [], []
for i in sorted(list(SPEC) + WHOLE):
    x, part = m[i], t[i]['local']
    spec = SPEC.get(i, ['P', 'V:1-z'])
    args = [part + ':1-z' if s == 'P' else x['vol_local'] + ':' + s.split(':')[1] for s in spec]
    out = f'{S}/joined/{i}.pdf'
    r = subprocess.run(['python3', 'scripts/join_parts.py', out] + args, capture_output=True, text=True)
    if r.returncode: print('FAIL', i, r.stderr[-300:]); continue
    print(i, r.stdout.strip().split(': ', 1)[1])
    vol = x['volume']; item = t[i]['local'].split('/')[-1].split('__')
    why = (f"owner 2026-10-20 (doubts-001 rows 1–3, 7): the volume's front part {item[1]} (archive.org {item[0]}, beside the "
           f"volume's own file in that item) never reached the phone — joined in front, the volume's repeated pages left out "
           f"({' + '.join(spec)}); scripts/join_parts.py, image streams unchanged")
    aside.append(f'Books/{vol}\tBooks/نسخ مستبعدة/__المستبدل/{vol}\t{why} — the original set aside (queue 372 puts the joined file in its place)')
    queue.append(f'file://{out}\t{os.path.getsize(out)}\tBooks/{vol}\t{why}')
open('plans/371-volume-fronts-originals-aside.tsv', 'w', encoding='utf-8').write('\n'.join(aside) + '\n')
open('data/queue/372-volume-fronts-joined.tsv', 'w', encoding='utf-8').write('\n'.join(queue) + '\n')
print(len(queue), 'joined')

"""Prints one line per settled owner comment on the review pages (unchanged for 45 s: he types into a box that saves as he
goes) and when the phone's FTP port goes away or comes back for at least 3 minutes — for an agent to act on each comment
as it comes (owner 2026-10-18: «احذف ما علقت عليه … وبشكل مستمر»). Comments: data/names/review-comments.jsonl.
Usage: python3 scripts/watch_comments.py   (runs until stopped)"""
import json, os, socket, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, 'data', 'names', 'review-comments.jsonl')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
HOST = (open(os.path.join(ROOT, 'data', 'phone', 'current-address.txt')).read().strip()
        if os.path.exists(os.path.join(ROOT, 'data', 'phone', 'current-address.txt')) else '192.168.11.100')

seen, pend = {}, {}
for l in open(F, encoding='utf-8'):
    try: r = json.loads(l)
    except ValueError: continue
    seen[(r.get('report'), r.get('n'))] = (r.get('checked'), r.get('comment', ''))
pos = os.path.getsize(F); phone = since = None
while True:
    if os.path.getsize(F) > pos:
        with open(F, encoding='utf-8') as f:
            f.seek(pos); data = f.read(); pos = f.tell()
        for l in data.splitlines():
            try: r = json.loads(l)
            except ValueError: continue
            pend[(r.get('report'), r.get('n'))] = ((r.get('checked'), r.get('comment', '')), time.time())
    now = time.time()
    for k, (v, t) in list(pend.items()):
        if now - t >= 45:
            del pend[k]
            if seen.get(k) != v:
                seen[k] = v
                print(f'COMMENT {k[0]} {k[1]} checked={v[0]} «{v[1]}»', flush=True)
    s = socket.socket(); s.settimeout(3)
    up = s.connect_ex((HOST, 2221)) == 0; s.close()
    if up != phone:                                   # reported only when it lasts 3 minutes (brief drops are noise)
        if not since or since[0] != up: since = (up, now)
        if now - since[1] >= 180:
            if phone is not None: print('PHONE', 'up' if up else 'away', time.strftime('%H:%M'), flush=True)
            phone = up; since = None
    else: since = None
    time.sleep(15)

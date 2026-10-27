"""wsim3_eval.py W.jsonl [WSIM2.txt] — guard W's verdicts from the stored views, as it is (V0) and with printed rules left
out of its lines (V1: a line along which the ink runs unbroken — ≥ COV of its span, no gap over GAP pt — is a rule, not a
line of text), and V2 = V1 + scattered readings refused when over a quarter of the steps between consecutive lines exceed
0.3°. Prints the verdict counts per book, V0 vs wsim2's (must agree), and every page whose verdict changes"""
import sys, os, json, collections
sys.path.insert(0, os.path.expanduser("~/.local/share/phone-library-tools/site"))
sys.path.insert(0, '/tmp/claude-1000/-home-k-projects-phone-library/fcd8d325-9813-40ca-94ce-bd6c86424307/scratchpad/w/code')
import numpy as np
import bc_w2 as bc
COV, GAP = 0.9, 6.0
rule = lambda t: t[7] >= COV and t[8] <= GAP

def verdict(t0, t1, d, drop_rules=False, steps=False):
    if drop_rules: t0, t1 = [t for t in t0 if not rule(t)], [t for t in t1 if not rule(t)]
    L = bc.lines_read([tuple(t[:5]) for t in t0], [tuple(t[:5]) for t in t1], d)
    if L and steps:
        st = np.abs(np.diff([v[1] for v in L]))
        if (st > 0.3 + 1e-6).mean() > 0.25: L = None
    return L, bc.two_angles(L)

def print_certifies(t0, t1, d):
    """V5: the turn is the print's when the page's printed rules (read in both views, alike) all stand level once turned
    (≤ 0.15°) and its lines of text give no reading (lines_read on the text alone: None, or jumps at over a quarter of
    the steps) → (True/False, the rules [(y, before, after)])"""
    ok = lambda t: t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3
    R = []
    for t in t0:
        if not (ok(t) and rule(t)): continue
        m_ = [u for u in t1 if ok(u) and abs(u[0] - t[0]) <= 6]
        if not m_: continue
        u = min(m_, key=lambda u: abs(u[0] - t[0]))
        if abs(u[1] - (t[1] - d)) <= 0.15 + 1e-6: R.append((t[0], t[1], round(t[1] - d, 3)))
    if not R or any(abs(v[2]) > 0.15 + 1e-6 for v in R): return False, R
    LT = bc.lines_read([tuple(t[:5]) for t in t0 if not rule(t)], [tuple(t[:5]) for t in t1 if not rule(t)], d)
    if LT:
        st = np.abs(np.diff([v[1] for v in LT]))
        if (st > 0.3 + 1e-6).mean() <= 0.25: return False, R
    return True, R

if __name__ == '__main__':
    R = [json.loads(l) for l in open(sys.argv[1])]
    old = {}
    if len(sys.argv) > 2:
        h = None
        for l in open(sys.argv[2]):
            x = l.split()
            if not x: continue
            if len(x[0]) == 12 and x[0] != 'p.': h = x[0]; continue
            if x[0] == 'p.': old[(h, int(x[1]))] = x[4].rstrip(':') if x[3] == 'turn' else x[3]
    cnt = collections.defaultdict(collections.Counter); flips = collections.defaultdict(list); mism = []
    for r in R:
        if 'err' in r: cnt[r['h']]['ERR'] += 1; continue
        h, g, d = r['h'], r['g'], r['d']
        L0, w0 = verdict(r['t0'], r['t1'], d); L1, w1 = verdict(r['t0'], r['t1'], d, True); L2, w2 = verdict(r['t0'], r['t1'], d, True, True)
        c5, R5 = print_certifies(r['t0'], r['t1'], d); w5 = [] if (w0 and c5) else w0
        v = tuple(bool(w) for w in (w0, w1, w2)) + (bool(w5),); cnt[h][v] += 1
        if bool(w0) != bool(w5): flips['V0→V5'].append((h, g, d, w0, R5))
        nr = sum(1 for t in r['t0'] if rule(t) and t[3] <= 1.0 and t[4] >= 6 and t[2] >= 0.3)
        if old and (bool(w0) != ((h, g) in old)): mism.append((h, g, bool(w0), old.get((h, g))))
        if v[0] != v[1]: flips['V0→V1'].append((h, g, d, nr, w0, w1))
        if v[1] != v[2]: flips['V1→V2'].append((h, g, d, nr, w1, w2, [round(x[1], 2) for x in (L1 or [])]))
    for h, c in cnt.items(): print(h, dict(c))
    print('V0 vs wsim2 mismatches:', mism[:20], len(mism))
    for k, v in flips.items():
        print(f'\n{k}: {len(v)}')
        for x in v: print('  ', x)

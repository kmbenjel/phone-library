"""Memory governor for the long crop jobs (owner 2026-10-18: «you can add workers but when ram is about to be full you can
close browsers if no activity is done using them and if it was not sufficient you reduce the workers at that point for a
while»; then «probably you can manage better, using swap, etc. do your best in that matter»; «I use antigravity a lot as well»).
EVERY crop job runs in ONE memory pen, the user slice crop.slice (systemd-run --user --slice=crop.slice …). Every 5–20 s:
  * THE PEN'S SIZE follows what the owner uses: MemoryHigh = free memory + what the pen holds − 2.5 GB kept free (2–10 GB),
    MemoryMax 1.5 GB above. When he opens more (browsers, VS Code, Antigravity…), the pen shrinks: the crop jobs are reclaimed
    and swapped (they slow down) — never his session. When he closes things, it grows.
  * WORKERS (data/crop/workers, read by every crop tool before each new book) = (the pen's size − 0.5 GB for the job's own
    process) / 1.5 GB, 1–6 (8 cores, 2 kept for the owner); fewer at once, more only after 2 minutes — and none more for 20
    minutes after a brake. A book starts only with ≥ 3 GB free and room in the pen
    (crop_batch.room()).
  * free < 2 GB (the owner's own apps press): Brave/Chrome are closed the normal way if nobody has touched the laptop for 10
    minutes and no sound plays (tabs come back on reopening). Never VS Code, Antigravity or anything else.
  * free < 1 GB or memory pressure ≥ 20 %: the EMERGENCY BRAKE — the largest crop process is killed at once (the jobs are
    resumable; scripts/run_resumable.sh restarts them when memory is back).
Logs to logs/mem-governor.log. Run: systemd-run --user --unit=mem-governor python3 scripts/mem_governor.py"""
import glob, os, signal, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, 'data', 'crop', 'workers')
MAX, LOW, CRIT = int(os.environ.get('MAX_WORKERS', 6)), 2.0, 1.0
SLICE, KEEP, PER, FLOOR, CEIL = 'crop.slice', 2.5, 1.5, 2.0, 10.0          # GB
# (PER: on 2026-10-18 an analysis worker held 1.7–2.5 GB, its job's own process ~1.5 GB more — with 1.3 GB a worker the
# count climbed 1 → 2 → 3 every two minutes into the brake, four kills in an hour, 23:00–23:45. Since the stamps fix of
# 10-25, measured every 3 s on the 31 regression books, 2026-10-26: a whole book in one process 0.97–1.29 GB, a page worker
# ≤ 0.94 GB, crop_redo's own process small → 1.5 / 0.5 GB, the owner's word 2026-10-26 18:35; was 2.2 / 1.5)
PARENT, HOLD = 0.5, 1200                                                    # GB; s without a climb after a brake
CG = f'/sys/fs/cgroup/user.slice/user-{os.getuid()}.slice/user@{os.getuid()}.service/{SLICE}'
log = lambda *a: print(time.strftime('%F %T'), *a, flush=True)

def free_gb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable:'): return int(l.split()[1]) / 1048576
    return 99.0

def idle_min():
    try:
        out = subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.gnome.Mutter.IdleMonitor', '--object-path',
                              '/org/gnome/Mutter/IdleMonitor/Core', '--method', 'org.gnome.Mutter.IdleMonitor.GetIdletime'],
                             capture_output=True, text=True, timeout=10).stdout
        return int(out.split()[1].rstrip(',)')) / 60000
    except Exception: return 0.0                       # unknown: as if the owner were at the laptop

def sound_playing():
    return any('RUNNING' in open(f).read() for f in glob.glob('/proc/asound/card*/pcm*p/sub*/status') if os.path.exists(f))

def browsers():
    """main browser processes (not their helpers): Brave and Chrome"""
    out = []
    for pid in os.listdir('/proc'):
        if not pid.isdigit(): continue
        try: cmd = open(f'/proc/{pid}/cmdline', 'rb').read().split(b'\0')
        except OSError: continue
        exe = cmd[0].decode(errors='ignore') if cmd else ''
        if exe.endswith(('/brave', '/chrome')) and not any(c.startswith(b'--type=') for c in cmd): out.append((int(pid), exe))
    return out

JOBS = ('crop_redo.py', 'crop_batch.py', 'crop_regress.py', 'crop_minitest.py', 'crop414.py', 'crop762.py')

def pressure():
    """the memory pressure (PSI «full avg10», %): the share of time every task waited on memory — what systemd-oomd watches"""
    try: return float(open('/proc/pressure/memory').read().split('full ')[1].split()[0].split('=')[1])
    except (OSError, IndexError, ValueError): return 0.0

def brake():
    """EMERGENCY BRAKE (2026-10-18 03:05: systemd-oomd closed the owner's whole session while a crop bench filled the
    memory): the largest crop process (an analysis worker) is killed at once — the jobs are resumable, the session is not"""
    best = None
    for pid in os.listdir('/proc'):
        if not pid.isdigit(): continue
        try:
            cmd = open(f'/proc/{pid}/cmdline', 'rb').read().decode(errors='ignore')
            if not any(j in cmd for j in JOBS): continue
            rss = int(next(l for l in open(f'/proc/{pid}/status') if l.startswith('VmRSS:')).split()[1])
        except (OSError, StopIteration, ValueError): continue
        if not best or rss > best[1]: best = (int(pid), rss, cmd.replace('\0', ' ')[:80])
    if best:
        try: os.kill(best[0], signal.SIGKILL); log(f'BRAKE: killed pid {best[0]} ({best[1] // 1024} MB) {best[2]}')
        except OSError: pass
    return best

def pen_gb():
    try: return int(open(os.path.join(CG, 'memory.current')).read()) / 1073741824
    except (OSError, ValueError): return 0.0

def size_pen(gb):
    hi, mx = int(gb * 1024), int((gb + 1.5) * 1024)
    try:                                              # (a busy systemd can take > 20 s: the call timed out on 2026-10-25
        subprocess.run(['systemctl', '--user', 'set-property', '--runtime', SLICE, f'MemoryHigh={hi}M', f'MemoryMax={mx}M'],
                       capture_output=True, timeout=20)  # and the exception killed the governor — its brake off for hours)
    except subprocess.TimeoutExpired:
        print(time.strftime('%F %T'), f'pen resize to {gb:.2f} GB timed out — tried again next round', flush=True)

def get():
    try: return max(1, min(MAX, int(open(FILE).read().strip())))
    except (OSError, ValueError): return MAX

def put(n, why):
    old = get(); open(FILE, 'w').write(f'{n}\n')
    if n != old: log(f'workers {old} → {n}: {why}')

if __name__ == '__main__':
    log(f'governor up: pen {SLICE} sized from free memory (keep {KEEP} GB), ≤ {MAX} workers, brake < {CRIT} GB (pid {os.getpid()})')
    pen = None; up_since = None; closed_at = 0; low_since = None; braked = 0
    while True:
        f = free_gb(); now = time.time(); ps = pressure(); held = pen_gb()
        if f < CRIT or ps >= 20:                      # the brake first
            brake(); put(max(1, get() - 2), f'{f:.1f} GB free, pressure {ps:.0f} % (critical)'); up_since = None; braked = now
            time.sleep(5); continue
        want = round(min(CEIL, max(FLOOR, f + held - KEEP)) * 4) / 4      # in quarters of a GB
        if pen is None or abs(want - pen) >= 0.25:
            size_pen(want)
            if pen is None or abs(want - pen) >= 1: log(f'pen {pen} → {want} GB (free {f:.1f} GB, the jobs hold {held:.1f} GB)')
            pen = want
        target = max(1, min(MAX, int((pen - PARENT) / PER))); n = get()
        if target < n: put(target, f'pen {pen} GB'); up_since = None
        elif target > n and now - braked < HOLD: up_since = None        # «reduce the workers at that point for a while»
        elif target > n:
            up_since = up_since or now
            if now - up_since >= 120: put(n + 1, f'pen {pen} GB for 2 min'); up_since = now
        else: up_since = None
        if f < LOW:                                   # the owner's own apps press: idle browsers go (his rule)
            low_since = low_since or now
            br = browsers()
            if br and now - closed_at > 600 and now - low_since >= 30:
                im, snd = idle_min(), sound_playing()
                if im >= 10 and not snd:
                    for pid, exe in br:
                        try: os.kill(pid, signal.SIGTERM); log(f'{f:.1f} GB free, idle {im:.0f} min: closed {os.path.basename(exe)} (pid {pid})')
                        except OSError: pass
                    closed_at = now
        else: low_since = None
        time.sleep(5 if f < LOW + 1 else 20)            # closer watch when memory runs short

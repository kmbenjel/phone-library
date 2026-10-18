"""Memory governor for the long crop jobs (owner 2026-10-18: «you can add workers but when ram is about to be full you can
close browsers if no activity is done using them and if it was not sufficient you reduce the workers at that point for a
while»). Every 20 s it reads the free memory (MemAvailable) and keeps the number of crop workers in data/crop/workers
(read by crop_redo.py, crop_batch.py and crop_regress.py before each new book):
  * free < LOW (2 GB): if Brave/Chrome run, nobody has touched the laptop for 10 min and no sound is playing, the browsers
    are closed the normal way (SIGTERM to the main process: tabs come back on reopening); a minute later, if memory is still
    low, one worker fewer (never below 1);
  * free < CRIT (1 GB) or memory pressure ≥ 20 %: the EMERGENCY BRAKE — the largest crop process is killed at once (the
    jobs are resumable: run them through scripts/run_resumable.sh), then two workers fewer;
  * free > HIGH (4.5 GB) for 10 minutes: one worker more, up to MAX (6; the laptop has 8 cores — 2 stay for the owner).
A worker already busy finishes its book; the change applies to the next book. Logs every action to
logs/mem-governor.log. Run as a user unit: systemd-run --user --unit=mem-governor python3 scripts/mem_governor.py"""
import glob, os, signal, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, 'data', 'crop', 'workers')
MAX, LOW, CRIT, HIGH = int(os.environ.get('MAX_WORKERS', 6)), 2.0, 1.0, 4.5
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

def get():
    try: return max(1, min(MAX, int(open(FILE).read().strip())))
    except (OSError, ValueError): return MAX

def put(n, why):
    old = get(); open(FILE, 'w').write(f'{n}\n')
    if n != old: log(f'workers {old} → {n}: {why}')

if __name__ == '__main__':
    if not os.path.exists(FILE): put(MAX, 'start')
    log(f'governor up: max {MAX} workers, low {LOW} GB, critical {CRIT} GB (pid {os.getpid()})')
    low_since = high_since = None; closed_at = 0
    while True:
        f = free_gb(); n = get(); now = time.time(); ps = pressure()
        if f < CRIT or ps >= 20:                      # the brake first, then fewer workers
            brake(); put(max(1, n - 2), f'{f:.1f} GB free, pressure {ps:.0f} % (critical)'); low_since = now; high_since = None
            time.sleep(5); continue
        if f < CRIT:
            put(max(1, n - 2), f'{f:.1f} GB free (critical)'); low_since = now; high_since = None
        elif f < LOW:
            high_since = None
            br = browsers()
            if br and now - closed_at > 600:
                im, snd = idle_min(), sound_playing()
                if im >= 10 and not snd:
                    for pid, exe in br:
                        try: os.kill(pid, signal.SIGTERM); log(f'{f:.1f} GB free, idle {im:.0f} min: closed {os.path.basename(exe)} (pid {pid})')
                        except OSError: pass
                    closed_at = now; low_since = now; time.sleep(60); continue
            if low_since and now - low_since >= 60: put(max(1, n - 1), f'{f:.1f} GB free'); low_since = now
            elif not low_since: low_since = now
        else:
            low_since = None
            if f > HIGH and n < MAX:
                high_since = high_since or now
                if now - high_since >= 600: put(n + 1, f'{f:.1f} GB free for 10 min'); high_since = now
            else: high_since = None
        time.sleep(5 if f < LOW + 1 else 20)            # closer watch when memory runs short

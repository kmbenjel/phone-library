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
  * THE SESSION GUARD (2026-11-07 00:59: systemd-oomd killed the VS Code scope — 8.5 GB with every agent's shell jobs in it
    — Firefox, Antigravity and Chromium and logged the owner out, with no crop process on the laptop, so the brake found
    nothing; owner: «prevent ram from saturating and logging pc out»). Any heavy batch process (≥ 400 MB: ffmpeg, python,
    tesseract, gs, headless Chrome, compilers… — never VS Code, Antigravity, GNOME, browsers he uses, the named services):
    pressure ≥ 8 % or < 1.5 GB free → the largest is PAUSED (SIGSTOP; it keeps its memory but stops growing, swap takes it
    calmly); pressure ≥ 20 % or < 0.8 GB → the largest is KILLED; ≥ 3 GB free and calm for 20 s → the paused ones go on
    (SIGCONT), one every 30 s. Paused pids are kept in data/crop/paused so a restarted governor resumes them. Watch every
    2 s when memory is short (was 20 s: the 00:59 spike rose and killed within one sleep).
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
            # (a remote redo's coordinator, crop_redo --remote: ~140 MB, the work on the VM — killing it frees nothing and
            # stalls the run; it was the «largest crop process» twice on 2026-11-06 with no local worker around)
            if '--remote' in cmd: continue
            rss = int(next(l for l in open(f'/proc/{pid}/status') if l.startswith('VmRSS:')).split()[1])
        except (OSError, StopIteration, ValueError): continue
        if not best or rss > best[1]: best = (int(pid), rss, cmd.replace('\0', ' ')[:80])
    if best:
        try: os.kill(best[0], signal.SIGKILL); log(f'BRAKE: killed pid {best[0]} ({best[1] // 1024} MB) {best[2]}')
        except OSError: pass
    return best

# the session guard: what may be paused or killed (by process name), and what never (by unit)
HEAVY = {'ffmpeg', 'ffprobe', 'python', 'python3', 'tesseract', 'gs', 'ocrmypdf', 'magick', 'convert', 'pdftoppm',
         'pdftocairo', 'qpdf', 'mutool', 'jbig2', 'unpaper', 'sox', 'java', 'rustc', 'cargo', 'cc1', 'cc1plus', 'ld', 'go',
         'node', 'npm', 'npx', 'esbuild', 'vite', 'aria2c', 'rclone', 'xz', 'zstd', '7z', 'gzip', 'tar', 'sort'}
SAFE_UNITS = ('hifz-warsh', 'discord-listener', 'mem-governor', 'battery-guard', 'phone-watchdog', 'gnome-', 'org.gnome',
              'pipewire', 'wireplumber', 'dbus', 'xdg-')
PAUSE_MB, WARN_PS, WARN_GB, KILL_PS, KILL_GB, CALM_GB = 400, 8, 1.5, 20, 0.8, 3.0
PAUSED = os.path.join(ROOT, 'data', 'crop', 'paused')

def heavy():
    """[(rss KB, pid, label)] of the batch processes the guard may pause or kill, largest first"""
    out = []
    for pid in os.listdir('/proc'):
        if not pid.isdigit() or int(pid) == os.getpid(): continue
        try:
            st = {l.split(':')[0]: l.split(':', 1)[1].strip() for l in open(f'/proc/{pid}/status')}
            rss = int(st.get('VmRSS', '0 kB').split()[0])
            if rss < PAUSE_MB * 1024: continue
            name = st['Name']; cmd = open(f'/proc/{pid}/cmdline', 'rb').read().split(b'\0')
            cg = open(f'/proc/{pid}/cgroup').read().strip().rsplit('/', 1)[-1]
        except (OSError, KeyError, ValueError, IndexError): continue
        args = b' '.join(cmd).decode(errors='ignore')
        if any(cg.startswith(u) for u in SAFE_UNITS): continue
        headless = name in ('chrome', 'chromium', 'headless_shell') and '--headless' in args
        if name not in HEAVY and not headless: continue
        if '--remote' in args or 'mem_governor' in args: continue        # a remote redo's coordinator: the work is on the VM
        if name == 'node' and ('/.vscode/' in args or 'antigravity' in args.lower()): continue
        out.append((rss, int(pid), f'{name} {args[:90]}'))
    return sorted(out, reverse=True)

def paused_load():
    try: return {int(x) for x in open(PAUSED).read().split()}
    except (OSError, ValueError): return set()

def paused_save(ps):
    try: open(PAUSED, 'w').write(''.join(f'{p}\n' for p in sorted(ps)))
    except OSError: pass

def resume_all(*_):
    for p in paused_load():
        try: os.kill(p, signal.SIGCONT)
        except OSError: pass
    paused_save(set()); sys.exit(0)

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
    pen = None; up_since = None; closed_at = 0; low_since = None; braked = 0; calm_since = None; resumed_at = 0
    signal.signal(signal.SIGTERM, resume_all); signal.signal(signal.SIGINT, resume_all)
    paused = {p for p in paused_load() if os.path.exists(f'/proc/{p}')}
    while True:
        f = free_gb(); now = time.time(); ps = pressure(); held = pen_gb()
        paused = {p for p in paused if os.path.exists(f'/proc/{p}')}
        killed = False
        if f < KILL_GB or ps >= KILL_PS:              # the session guard's kill (it covers the crop brake's processes too)
            h = heavy(); killed = bool(h)
            if h:
                rss, pid, lab = h[0]
                try: os.kill(pid, signal.SIGKILL); log(f'GUARD: {f:.1f} GB free, pressure {ps:.0f} %: killed pid {pid} ({rss // 1024} MB) {lab}')
                except OSError: pass
                paused.discard(pid); paused_save(paused)
        elif f < WARN_GB or ps >= WARN_PS:            # pause the largest running heavy process
            h = [x for x in heavy() if x[1] not in paused]
            if h:
                rss, pid, lab = h[0]
                try: os.kill(pid, signal.SIGSTOP); paused.add(pid); paused_save(paused); log(f'GUARD: {f:.1f} GB free, pressure {ps:.0f} %: paused pid {pid} ({rss // 1024} MB) {lab}')
                except OSError: pass
            calm_since = None
        if paused and f >= CALM_GB and ps < 2:        # calm again: the paused go on, one at a time
            calm_since = calm_since or now
            if now - calm_since >= 20 and now - resumed_at >= 30:
                pid = min(paused)
                try: os.kill(pid, signal.SIGCONT); log(f'GUARD: {f:.1f} GB free, calm: resumed pid {pid}')
                except OSError: pass
                paused.discard(pid); paused_save(paused); resumed_at = now
        elif paused: calm_since = None
        if f < CRIT or ps >= 20:                      # the brake first
            killed or brake(); put(max(1, get() - 2), f'{f:.1f} GB free, pressure {ps:.0f} % (critical)'); up_since = None; braked = now
            time.sleep(2); continue
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
        time.sleep(2 if f < 4 or ps >= 3 or paused else 5)   # closer watch when memory runs short (was 5 / 20 s)

"""Keep the phone's FTP server app from going to sleep (owner 2026-10-12: «the phone said it will go into sleep mode for
lack of use»): every 2 minutes a login + NOOP + PWD + logout, so the app always sees activity. Costs nothing (no data).
Follows the phone's address (scripts/phone_host.py); logs only changes of state to logs/phone-keepalive.log.
Usage: setsid nohup python3 scripts/phone_keepalive.py [SECONDS=120] >> logs/phone-keepalive.log 2>&1 &
Stop: kill the PID from pgrep -f "[p]hone_keepalive". Keep the phone on its charger while it runs."""
import ftplib, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import phone_host
EVERY = int(sys.argv[1]) if len(sys.argv) > 1 else 120
ADDR = os.path.join(ROOT, 'data', 'phone', 'current-address.txt')
log = lambda *a: print(time.strftime('%F %T'), *a, flush=True)
host, up = None, None
log(f'keepalive every {EVERY} s (pid {os.getpid()})')
while True:
    try:
        host = host or (open(ADDR).read().strip() if os.path.exists(ADDR) else None) or phone_host.find()
        f = ftplib.FTP(); f.connect(host, phone_host.PORT, timeout=20); phone_host.login(f); f.voidcmd('NOOP'); f.pwd(); f.quit()
        if up is not True: log('phone answers on', host)
        up = True
    except ftplib.error_perm as e:                    # the server answers but refuses the login: no need to look elsewhere
        if up != 'refused': log('login refused on', host, '—', e, '(AGENTS.md §2: ~/.config/phone-library/ftp.env)')
        up = 'refused'
    except Exception as e:
        if up is not False: log('no answer on', host, '—', e)
        up, host = False, phone_host.find()           # moved? look again (the known addresses, then the /24)
    time.sleep(EVERY)

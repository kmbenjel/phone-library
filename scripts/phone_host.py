"""The phone's FTP address. The phone gets its IP by DHCP; these are the addresses it has had (newest first).
PHONE_HOST overrides; otherwise the first candidate whose FTP port answers is used, and when none answers the local
/24 network is scanned for the FTP port (the address moved three times on 2026-10-05).
`python3 scripts/phone_host.py` prints the address; `find()` returns it or None (for jobs that wait for the phone)."""
import os, socket
from concurrent.futures import ThreadPoolExecutor

CANDIDATES = ['192.168.11.100', '192.168.11.104', '192.168.11.102', '192.168.11.103']   # .100 reserved for the phone in the router (owner 2026-10-17); it wandered .100/.102/.104/.109 before; phone_watchdog.sh follows it
PORT = int(os.environ.get('PHONE_PORT', '2221'))


def _answers(host, timeout=3):
    try:
        socket.create_connection((host, PORT), timeout=timeout).close()
        return True
    except OSError:
        return False


def _scan():
    net = CANDIDATES[0].rsplit('.', 1)[0]
    hosts = [f'{net}.{i}' for i in range(2, 255) if f'{net}.{i}' not in CANDIDATES]
    with ThreadPoolExecutor(64) as ex:
        for h, ok in zip(hosts, ex.map(lambda h: _answers(h, 1), hosts)):
            if ok: return h
    return None


def find():
    """the answering address (known ones first, then a scan of the /24), or None"""
    if os.environ.get('PHONE_HOST'): return os.environ['PHONE_HOST']
    return next((h for h in CANDIDATES if _answers(h)), None) or _scan()


# THE LOGIN (owner 2026-10-18: the FTP app now has an account). Never in the repo: the user name and password live in
# ~/.config/phone-library/ftp.env (lines «USER=…» and «PASS=…», mode 600, written by the owner) or in the environment
# (PHONE_FTP_USER / PHONE_FTP_PASS); rclone keeps its own copy in its config (remote «phone:»). No file → anonymous.
CRED_FILE = os.path.expanduser('~/.config/phone-library/ftp.env')

def creds():
    """(user, password) for the phone's FTP server, or ('', '') for an anonymous login"""
    u, p = os.environ.get('PHONE_FTP_USER', ''), os.environ.get('PHONE_FTP_PASS', '')
    if not u and os.path.exists(CRED_FILE):
        for line in open(CRED_FILE, encoding='utf-8'):
            k, _, v = line.strip().partition('=')
            if k == 'USER': u = v
            elif k == 'PASS': p = v
    return u, p

def login(f):
    """log an ftplib.FTP connection in with the owner's account (or anonymously when none is set)"""
    u, p = creds()
    return f.login(u, p) if u else f.login()


HOST = find() or CANDIDATES[0]
FTP = os.environ.get('PHONE_FTP', f'ftp://{HOST}:{PORT}/Books/')

if __name__ == '__main__':
    print(HOST)

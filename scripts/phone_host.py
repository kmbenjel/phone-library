"""The phone's FTP address. The phone gets its IP by DHCP; these are the addresses it has had (newest first).
PHONE_HOST overrides; otherwise the first candidate whose FTP port answers is used, and when none answers the local
/24 network is scanned for the FTP port (the address moved three times on 2026-10-05).
`python3 scripts/phone_host.py` prints the address; `find()` returns it or None (for jobs that wait for the phone)."""
import os, socket
from concurrent.futures import ThreadPoolExecutor

CANDIDATES = ['192.168.11.100', '192.168.11.104', '192.168.11.102', '192.168.11.103']   # .100 reserved for the phone in the router (owner 2026-10-17); it wandered .100/.102/.104/.109 before; phone_watchdog.sh follows it
PORT = int(os.environ.get('PHONE_PORT', '2221'))          # the FTP app
SSH_PORT = int(os.environ.get('PHONE_SSH_PORT', '8022'))  # Termux sshd (2026-11-04)
# THE PROTOCOL: PHONE_PROTO=ftp|ssh, else ~/.config/phone-library/proto (one word, written by scripts/phone_proto.sh),
# else ftp. connect() and read_range() follow it; the address is found by the port of that protocol.
PROTO_FILE = os.path.expanduser('~/.config/phone-library/proto')
PROTO = os.environ.get('PHONE_PROTO') or (open(PROTO_FILE).read().strip() if os.path.exists(PROTO_FILE) else '') or 'ftp'
PROBE = SSH_PORT if PROTO == 'ssh' else PORT
HOME_NET = CANDIDATES[0].rsplit('.', 1)[0]
ADDR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'phone', 'current-address.txt')


def _home():
    """the laptop stands on the home network (away from it 192.168.11.x lies past the gateway, somebody else's: on 2026-11-01
    three strangers' FTP ports answered in one morning and the watchdog took each for the phone)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((HOME_NET + '.1', 9))
        return s.getsockname()[0].startswith(HOME_NET + '.')
    except OSError:
        return False
    finally:
        s.close()


def _answers(host, timeout=3):
    if host.startswith(HOME_NET + '.') and not _home():
        return False
    try:
        socket.create_connection((host, PROBE), timeout=timeout).close()
        return True
    except OSError:
        return False


def _scan():
    hosts = [f'{HOME_NET}.{i}' for i in range(2, 255) if f'{HOME_NET}.{i}' not in CANDIDATES]
    with ThreadPoolExecutor(64) as ex:
        for h, ok in zip(hosts, ex.map(lambda h: _answers(h, 1), hosts)):
            if ok: return h
    return None


def _gateway():
    """the default gateway: the phone itself when the laptop is on the phone's hotspot (172.x, a new /24 each time)"""
    try:
        for line in open('/proc/net/route'):
            f = line.split()
            if f[1] == '00000000' and f[2] != '00000000':
                return socket.inet_ntoa(bytes.fromhex(f[2])[::-1])
    except (OSError, IndexError, ValueError):
        pass
    return None


def find():
    """the answering address (known ones first, then the gateway, then a scan of the /24; away from home the last
    address written), or None"""
    if os.environ.get('PHONE_HOST'): return os.environ['PHONE_HOST']
    gw = _gateway()
    h = next((h for h in CANDIDATES if _answers(h)), None) or (gw if gw and not gw.startswith(HOME_NET + '.') and _answers(gw) else None) or _scan()
    if h or not os.path.exists(ADDR): return h
    last = open(ADDR).read().strip()
    return last if last and _answers(last) else None


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


def connect(timeout=60, host=None):
    """a logged-in connection to the phone by the chosen protocol: ftplib.FTP (utf-8) or phone_ssh.SSHPhone, which
    answers the same calls (nlst mkd rmd delete rename size retrbinary storbinary sendcmd XMD5/MD5 voidcmd quit)"""
    if PROTO == 'ssh':
        import phone_ssh
        return phone_ssh.SSHPhone(host or HOST, SSH_PORT, timeout)
    import ftplib
    f = ftplib.FTP(); f.encoding = 'utf-8'; f.connect(host or HOST, PORT, timeout=timeout); login(f); return f


def read_range(path, start, n, timeout=90):
    """n bytes of Books/<path> from offset start (fewer at the end): curl over FTP, dd over ssh. b'' when unreadable."""
    if PROTO == 'ssh':
        import phone_ssh
        for _ in range(3):
            try: return phone_ssh.SSHPhone(HOST, SSH_PORT, timeout).read_range('Books/' + path, start, n)
            except Exception: pass
        return b''
    import subprocess, urllib.parse
    u, p = creds()                                   # given on stdin, never on the command line (ps shows it)
    cfg = ('user = "%s:%s"\n' % (u.replace('"', '\\"'), p.replace('"', '\\"'))) if u else ''
    for _ in range(3):
        r = subprocess.run(['curl', '-s', '-K', '-', '--max-time', str(timeout), '-r', f'{start}-{start + n - 1}',
                            FTP + urllib.parse.quote(path)], input=cfg.encode(), capture_output=True)
        if r.returncode == 0 and r.stdout: return r.stdout
    return b''

if __name__ == '__main__':
    print(HOST, PROTO, PROBE) if '-v' in os.sys.argv else print(HOST)

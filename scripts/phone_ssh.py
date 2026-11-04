"""The phone over SSH (Termux sshd, port 8022, key login; owner 2026-11-04), with the part of ftplib.FTP the scripts use,
so a script written for FTP works unchanged: `phone_host.connect()` returns one of these when the protocol is ssh.
No new dependency: OpenSSH with one shared master connection (ControlMaster) runs coreutils on the phone (stat, mv,
md5sum, cat, dd). Paths are FTP paths (the FTP app's root = internal storage = /sdcard): '/Books/x' and 'Books/x'.
Errors look like ftplib's, so the scripts' except clauses keep working: file missing / refused → ftplib.error_perm;
connection lost → OSError. Host keys are checked under the alias «phone-termux» in ~/.ssh/known_hosts (the address
changes with every hotspot; the key does not)."""
import ftplib, os, posixpath, shlex, subprocess

PORT = int(os.environ.get('PHONE_SSH_PORT', '8022'))
KEY = os.path.expanduser(os.environ.get('PHONE_SSH_KEY', '~/.config/phone-library/phone_ssh'))
ROOT = '/sdcard'
CHUNK = 1 << 16


def ssh_args(host, port=PORT, timeout=60):
    return ['ssh', '-i', KEY, '-p', str(port), '-o', 'BatchMode=yes', '-o', 'HostKeyAlias=phone-termux',
            '-o', f'ConnectTimeout={min(int(timeout), 30)}', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=4',
            '-o', 'ControlMaster=auto', '-o', 'ControlPath=/tmp/phone-ssh-%C', '-o', 'ControlPersist=120', host]


def remote_path(p):
    """FTP path → the phone's path"""
    return posixpath.normpath(ROOT + '/' + p.lstrip('/'))


class SSHPhone:
    encoding = 'utf-8'

    def __init__(self, host=None, port=PORT, timeout=60):
        self.host, self.port, self.timeout = host, port, timeout
        if host: self.connect(host, port, timeout)

    # ---- plumbing
    def _base(self): return ssh_args(self.host, self.port, self.timeout)

    def _run(self, cmd, data=None, timeout=None):
        try:
            r = subprocess.run(self._base() + [cmd], input=data, capture_output=True, timeout=timeout or max(self.timeout, 60))
        except subprocess.TimeoutExpired as e:
            raise OSError(f'ssh timed out: {cmd[:80]}') from e
        if r.returncode == 255: raise OSError('ssh: ' + r.stderr.decode('utf-8', 'replace').strip())
        if r.returncode: raise ftplib.error_perm('550 ' + (r.stderr.decode('utf-8', 'replace').strip() or f'exit {r.returncode}'))
        return r.stdout

    @staticmethod
    def _q(p): return shlex.quote(remote_path(p))

    @staticmethod
    def _arg(cmd):                                   # 'RETR Books/x' → 'Books/x'
        return cmd.split(' ', 1)[1]

    # ---- the ftplib.FTP surface the scripts use
    def connect(self, host=None, port=None, timeout=None):
        self.host = host or self.host; self.port = port or self.port; self.timeout = timeout or self.timeout
        self._run('true'); return '220 ssh'

    def login(self, *a, **k): return '230 key'
    def voidcmd(self, cmd): return '200 ok'          # NOOP, TYPE I
    def pwd(self): return '/'
    def quit(self): return '221 bye'                 # the master connection stays (ControlPersist) for the next one
    close = quit
    def abort(self): return '226'

    def size(self, p):
        return int(self._run('stat -c %s -- ' + self._q(p)))

    def nlst(self, d):
        out = self._run(f'find {self._q(d)} -mindepth 1 -maxdepth 1 -printf "%f\\0"')
        return [posixpath.join(d, n) for n in out.decode('utf-8', 'surrogateescape').split('\0') if n]

    def mkd(self, p): self._run('mkdir -- ' + self._q(p)); return p
    def rmd(self, p): self._run('rmdir -- ' + self._q(p)); return '250'
    def delete(self, p): self._run('rm -- ' + self._q(p)); return '250'

    def rename(self, a, b):
        """never over an existing name (the caller deletes first when it means to replace)"""
        qa, qb = self._q(a), self._q(b)
        self._run(f'[ -e {qa} ] || {{ echo "{a}: no such file" >&2; exit 1; }}; '
                  f'[ -e {qb} ] && {{ echo "{b}: exists" >&2; exit 1; }}; mv -- {qa} {qb}')
        return '250'

    def md5(self, p):
        return self._run('md5sum -- ' + self._q(p)).split()[0].decode().lower()

    def sha1(self, p):
        return self._run('sha1sum -- ' + self._q(p)).split()[0].decode().lower()

    def sendcmd(self, cmd):
        verb = cmd.split(' ', 1)[0].upper()
        if verb in ('XMD5', 'MD5'):
            p = self._arg(cmd); return f'251 "{p}" {self.md5(p).upper()}'
        if verb == 'NOOP': return '200 ok'
        raise ftplib.error_perm(f'502 {verb} not done over ssh')

    def read_range(self, p, start, n):
        """n bytes from offset start (fewer at the end of the file)"""
        return self._run(f'dd if={self._q(p)} bs={CHUNK} iflag=skip_bytes,count_bytes skip={int(start)} count={int(n)} status=none')

    def retrbinary(self, cmd, callback, blocksize=CHUNK, rest=None):
        p = self._arg(cmd)
        remote = (f'tail -c +{int(rest) + 1} -- ' if rest else 'cat -- ') + self._q(p)
        pr = subprocess.Popen(self._base() + [remote], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                b = pr.stdout.read(blocksize)
                if not b: break
                callback(b)
        except BaseException:
            pr.kill(); pr.wait(); raise
        err = pr.stderr.read(); pr.wait()
        if pr.returncode == 255: raise OSError('ssh: ' + err.decode('utf-8', 'replace').strip())
        if pr.returncode: raise ftplib.error_perm('550 ' + err.decode('utf-8', 'replace').strip())
        return '226 done'

    def storbinary(self, cmd, fp, blocksize=CHUNK, callback=None, rest=None):
        verb, p = cmd.split(' ', 1)
        redir = '>>' if verb.upper() == 'APPE' else '>'
        pr = subprocess.Popen(self._base() + [f'cat {redir} {self._q(p)}'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                b = fp.read(blocksize)
                if not b: break
                pr.stdin.write(b)
                if callback: callback(b)
            pr.stdin.close()
        except BaseException:
            pr.kill(); pr.wait(); raise
        err = pr.stderr.read(); pr.wait()
        if pr.returncode == 255: raise OSError('ssh: ' + err.decode('utf-8', 'replace').strip())
        if pr.returncode: raise ftplib.error_perm('553 ' + err.decode('utf-8', 'replace').strip())
        return '226 done'

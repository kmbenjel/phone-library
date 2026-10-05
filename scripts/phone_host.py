"""The phone's FTP address. The phone gets its IP by DHCP; these are the addresses it has had (newest first).
PHONE_HOST overrides; otherwise the first candidate whose FTP port answers is used."""
import os, socket

CANDIDATES = ['192.168.11.103', '192.168.11.102', '192.168.11.100']
PORT = int(os.environ.get('PHONE_PORT', '2221'))


def _answers(host):
    try:
        socket.create_connection((host, PORT), timeout=3).close()
        return True
    except OSError:
        return False


HOST = os.environ.get('PHONE_HOST') or next((h for h in CANDIDATES if _answers(h)), CANDIDATES[0])
FTP = os.environ.get('PHONE_FTP', f'ftp://{HOST}:{PORT}/Books/')

if __name__ == '__main__':
    print(HOST)

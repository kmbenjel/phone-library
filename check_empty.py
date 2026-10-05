import ftplib
FTP_HOST = '192.168.11.100'
FTP_PORT = 2221
FTP_ROOT = '/Books'

ftp = ftplib.FTP()
ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
ftp.login()

def check_dir(path):
    try:
        ftp.cwd(path)
        items = []
        ftp.retrlines('LIST', items.append)
        print(f"Contents of {path}:")
        for item in items: print("  " + item)
    except Exception as e:
        print(f"Error reading {path}: {e}")

check_dir(f"{FTP_ROOT}/كتب التفاسير")
check_dir(f"{FTP_ROOT}/كتب أصول الفقه وقواعده")
check_dir(f"{FTP_ROOT}/كتب الأذكار والشعائر")

ftp.quit()

import ftplib
FTP_HOST = '192.168.11.100'
FTP_PORT = 2221
ftp = ftplib.FTP()
ftp.connect(FTP_HOST, FTP_PORT)
ftp.login()
try:
    ftp.rename('/Books/كتب أصول الفقه وقواعده/جمع الجوامع في أصول الفقه.pdf', '/Books/أصول الفقه/جمع الجوامع في أصول الفقه.pdf')
    print("Rename successful")
except Exception as e:
    print(f"Rename failed: {e}")
ftp.quit()

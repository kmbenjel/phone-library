import ftplib
ftp = ftplib.FTP()
ftp.connect('192.168.11.100', 2221)
ftp.login()
try:
    print(ftp.size('/Books/أصول الفقه/جمع الجوامع في أصول الفقه.pdf'))
except Exception as e:
    print(e)

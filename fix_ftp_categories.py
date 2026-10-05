import ftplib, os

FTP_HOST = '192.168.11.100'
FTP_PORT = 2221
FTP_ROOT = '/Books'

alien_cats = ['تراث شعبي', 'قصص وروايات', 'الأدب المترجم']
target_cat = 'الأدب/القصص والروايات'

try:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login()
except Exception as e:
    print(f"Failed to connect to FTP: {e}")
    exit(1)

# Ensure target base exists
try:
    ftp.mkd(f"{FTP_ROOT}/الأدب")
except: pass

try:
    ftp.mkd(f"{FTP_ROOT}/{target_cat}")
except: pass

for cat in alien_cats:
    alien_path = f"{FTP_ROOT}/{cat}"
    try:
        ftp.cwd(alien_path)
        items = ftp.nlst()
    except:
        continue # Folder doesn't exist, which is good
        
    print(f"Found alien category: {cat}")
    for item in items:
        # Avoid '.' and '..'
        if item in ['.', '..']: continue
        src = f"{alien_path}/{item}"
        dst = f"{FTP_ROOT}/{target_cat}/{item}"
        try:
            ftp.rename(src, dst)
            print(f"Moved {item} to {target_cat}")
        except Exception as e:
            print(f"Error moving {item}: {e}")
            
    # Delete the empty alien folder
    try:
        ftp.cwd('/')
        ftp.rmd(alien_path)
        print(f"Deleted empty alien folder: {cat}")
    except Exception as e:
        print(f"Error deleting {cat}: {e}")

ftp.quit()
print("FTP cleanup complete.")

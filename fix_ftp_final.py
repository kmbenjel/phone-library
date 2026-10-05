import ftplib, json

FTP_HOST = '192.168.11.100'
FTP_PORT = 2221
FTP_ROOT = '/Books'

cat_data = json.load(open('data/catalog.json'))
shamela_cats = set(b.get('cat', '') for b in cat_data['books'] if b.get('cat'))

def map_category(waqfeya_cat):
    if not waqfeya_cat: return 'كتب عامة'
    w = waqfeya_cat.replace('كتب ', '').strip()
    mapping = {
        'التوحيد والعقيدة': 'العقيدة', 'التفاسير': 'التفسير', 'أصول الفقه وقواعده': 'أصول الفقه',
        'الأذكار والشعائر': 'الرقائق والآداب والأذكار', 'الفتاوى': 'الفتاوى', 'باقي مجموعات الحديث': 'شروح الحديث'
    }
    if waqfeya_cat in mapping: return mapping[waqfeya_cat]
    if w in mapping: return mapping[w]
    if w in shamela_cats: return w
    for sc in shamela_cats:
        if w in sc or sc in w: return sc
    return 'كتب عامة'

def robust_move(ftp, src_path, dst_path):
    try:
        ftp.rename(src_path, dst_path)
        return True
    except Exception as e:
        # Check if it's a file and dst already exists
        try:
            sz = ftp.size(dst_path)
            if sz:
                # Dst exists. Delete src if it's a file
                try:
                    ftp.delete(src_path)
                    return True
                except: pass
        except: pass
        
        # Must be a directory
        try:
            ftp.cwd(src_path)
            items = ftp.nlst()
        except: return False
            
        try: ftp.mkd(dst_path)
        except: pass
        
        success = True
        for item in items:
            if item in ['.', '..']: continue
            if not robust_move(ftp, f"{src_path}/{item}", f"{dst_path}/{item}"):
                success = False
                
        if success:
            try:
                ftp.cwd('/')
                ftp.rmd(src_path)
            except: pass
        return success

ftp = ftplib.FTP()
ftp.connect(FTP_HOST, FTP_PORT)
ftp.login()

for folder in ftp.nlst(FTP_ROOT):
    folder = folder.split('/')[-1]
    if folder in ['.', '..']: continue
    if folder not in shamela_cats and folder != "الأدب":
        target = map_category(folder)
        if target != folder:
            print(f"Cleaning {folder}...")
            robust_move(ftp, f"{FTP_ROOT}/{folder}", f"{FTP_ROOT}/{target}")

ftp.quit()
print("Done")

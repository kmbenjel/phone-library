import ftplib, os, json

FTP_HOST = '192.168.11.100'
FTP_PORT = 2221
FTP_ROOT = '/Books'

cat_data = json.load(open('data/catalog.json'))
shamela_cats = set(b.get('cat', '') for b in cat_data['books'] if b.get('cat'))

def map_category(waqfeya_cat):
    if not waqfeya_cat: return 'كتب عامة'
    w = waqfeya_cat.replace('كتب ', '').strip()
    mapping = {
        'التوحيد والعقيدة': 'العقيدة',
        'الثقافة الإسلامية العامة': 'العقيدة',
        'اليهود والنصارى والمستشرقون..': 'الفرق والردود',
        'الشيعة والرافضة والباطنية والبهائية والقاديانية': 'الفرق والردود',
        'الفرق والأديان والردود': 'الفرق والردود',
        'الصهيونية والماسونية ..': 'الفرق والردود',
        'التفاسير': 'التفسير',
        'أصول التفسير': 'علوم القرآن وأصول التفسير',
        'مباحث قرآنية عامة': 'علوم القرآن وأصول التفسير',
        'علوم القرآن': 'علوم القرآن وأصول التفسير',
        'المصاحف الشريفة والتفاسير التي على هوامشه وقراءاته وأسباب نزوله..الخ': 'التفسير',
        'الكتب الستة': 'كتب السنة',
        'مسانيد الأئمة الأربعة': 'كتب السنة',
        'المسانيد الأخرى والجوامع': 'الجوامع',
        'فهارس الحديث': 'التخريج والأطراف',
        'مصطلح الحديث': 'علوم الحديث',
        'باقي مجموعات الحديث': 'شروح الحديث',
        'الفقه الشافعي': 'الفقه الشافعي',
        'الفقه الحنبلي': 'الفقه الحنبلي',
        'الفقه الحنفي': 'الفقه الحنفي',
        'الفقه المالكي': 'الفقه المالكي',
        'الفقه العام': 'الفقه العام',
        'أصول الفقه وقواعده': 'أصول الفقه',
        'الفرائض': 'الفرائض والوصايا',
        'الفتاوى': 'الفتاوى',
        'السياسة الشرعية والأحكام السلطانية': 'السياسة الشرعية والقضاء',
        'الأحوال الشخصية': 'الفقه العام',
        'السيرة النبوية': 'السيرة النبوية',
        'التراجم والأعلام': 'التراجم والطبقات',
        'التاريخ الإسلامي': 'التاريخ',
        'الأنساب': 'الأنساب',
        'تاريخ مصر': 'التاريخ',
        'تاريخ أوربا': 'التاريخ',
        'تاريخ مكة المكرمة': 'التاريخ',
        'تاريخ المملكة العربية السعودية': 'التاريخ',
        'اللغة العربية': 'كتب اللغة',
        'المعاجم اللغوية العربية': 'الغريب والمعاجم',
        'النحو والصرف': 'النحو والصرف',
        'البلاغة': 'البلاغة',
        'العروض': 'العروض والقوافي',
        'دواوين الشعر': 'الشعر ودواوينه',
        'الأدب': 'الأدب',
        'القصص والروايات': 'الأدب/القصص والروايات',
        'الأدب المترجم': 'الأدب/القصص والروايات',
        'تراث شعبي': 'الأدب/القصص والروايات',
        'التزكية والأخلاق والآداب': 'الرقائق والآداب والأذكار',
        'الأذكار والشعائر': 'الرقائق والآداب والأذكار',
        'التصوف': 'الفرق والردود',
        'الدعوة والدفاع عن الإسلام': 'كتب عامة',
        'قضايا الإصلاح الإجتماعي والأسرة والمجتمع': 'علوم أخرى',
        'الاقتصاد': 'علوم أخرى',
        'التربية والتعليم': 'علوم أخرى',
        'علم الاجتماع': 'علوم أخرى',
        'علم النفس': 'علوم أخرى',
        'الإدارة والسلطة التنفيذية الحكومية': 'علوم أخرى',
        'الجغرافيا والرحلات': 'البلدان والرحلات',
        'الطب': 'الطب',
        'الفنون': 'علوم أخرى',
        'تكنولوجيا والعلوم التطبيقية': 'علوم أخرى',
        'العلوم بحتة': 'علوم أخرى',
        'الجرح والتعديل': 'التراجم والطبقات',
        'المنطق': 'المنطق',
        'الأدلة والفهارس': 'فهارس الكتب والأدلة',
        'فهارس المخطوطات': 'فهارس الكتب والأدلة',
        'الموسوعات العامة': 'كتب عامة',
        'المجاميع': 'كتب عامة',
        'الرؤى والأحلام': 'علوم أخرى'
    }
    if waqfeya_cat in mapping: return mapping[waqfeya_cat]
    if w in mapping: return mapping[w]
    if w in shamela_cats: return w
    for sc in shamela_cats:
        if w in sc or sc in w: return sc
    return 'كتب عامة'

def ensure_dir(ftp, path):
    parts = [p for p in path.split('/') if p]
    curr = ''
    for p in parts:
        curr += '/' + p
        try: ftp.cwd(curr)
        except:
            try:
                ftp.mkd(curr)
                ftp.cwd(curr)
            except: pass

def robust_move(ftp, src_path, dst_path):
    # Try rename first. If it's a folder, some servers allow renaming it directly.
    try:
        ftp.rename(src_path, dst_path)
        return True
    except:
        # It might be a directory that the server refuses to move across paths.
        # We must recursively move its contents.
        try:
            ftp.cwd(src_path)
            items = ftp.nlst()
        except:
            return False # Not a directory or error
            
        ensure_dir(ftp, dst_path)
        
        success = True
        for item in items:
            if item in ['.', '..']: continue
            s = f"{src_path}/{item}"
            d = f"{dst_path}/{item}"
            if not robust_move(ftp, s, d):
                success = False
                
        if success:
            try:
                ftp.cwd('/')
                ftp.rmd(src_path)
            except: pass
        return success

try:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login()
except Exception as e:
    print(f"FTP Connect Error: {e}")
    exit(1)

ftp.cwd(FTP_ROOT)
try:
    folders = ftp.nlst()
except:
    folders = []

for folder in folders:
    if folder in ['.', '..']: continue
    
    # Exclude strict matches with shamela cats (and "الأدب" since we use subdirs there)
    if folder not in shamela_cats and folder != "الأدب":
        target_cat = map_category(folder)
        
        if target_cat != folder:
            print(f"Fixing '{folder}' -> '{target_cat}'")
            src = f"{FTP_ROOT}/{folder}"
            dst = f"{FTP_ROOT}/{target_cat}"
            robust_move(ftp, src, dst)
            
            # Try to delete the root alien folder if still exists
            try:
                ftp.cwd(FTP_ROOT)
                ftp.rmd(folder)
                print(f"  Deleted root alien folder: {folder}")
            except Exception as e:
                pass

ftp.quit()
print("Robust FTP cleanup complete.")

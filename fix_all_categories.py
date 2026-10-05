import csv, json, ftplib, os

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
        'القصص والروايات': 'الأدب',
        'الأدب المترجم': 'الأدب',
        'تراث شعبي': 'الأدب',
        
        'التزكية والأخلاق والآداب': 'الرقائق والآداب والأذكار',
        'الأذكار والشعائر': 'الرقائق والآداب والأذكار',
        'التصوف': 'الفرق والردود', # or الرقائق
        
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
    
    # Try exact match
    if w in shamela_cats: return w
    
    # Try substring match
    for sc in shamela_cats:
        if w in sc or sc in w: return sc
        
    return 'كتب عامة'

# 1. FIX LOCAL TSV FILES
files_to_fix = ['plans/download_batch.tsv', 'plans/download_batch_large.tsv', 'plans/download_partial.tsv']
for file_path in files_to_fix:
    if not os.path.exists(file_path): continue
    with open(file_path, 'r') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
        
    for r in rows:
        cat = r['category'].split('/')[0] # Remove any sub-category I artificially added
        r['category'] = map_category(cat)
        
    with open(file_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter='\t')
        w.writeheader()
        w.writerows(rows)
    print(f"Fixed TSV: {file_path}")


FTP_HOST = '192.168.11.100'
FTP_PORT = 2221
FTP_ROOT = '/Books'

try:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login()
except Exception as e:
    print(f"FTP Connect error: {e}")
    exit(1)

ftp.cwd(FTP_ROOT)
folders = ftp.nlst()

for folder in folders:
    if folder in ['.', '..']: continue
    
    # Is it an alien folder?
    if folder not in shamela_cats:
        # Check if it's a file, not a folder
        try:
            ftp.cwd(f"{FTP_ROOT}/{folder}")
        except:
            continue # probably a file
            
        target_cat = map_category(folder)
        
        if target_cat != folder:
            print(f"Migrating alien folder '{folder}' -> '{target_cat}'")
            
            # Ensure target exists
            try:
                ftp.cwd(FTP_ROOT)
                ftp.mkd(target_cat)
            except: pass
            
            # Move items
            ftp.cwd(f"{FTP_ROOT}/{folder}")
            items = ftp.nlst()
            for item in items:
                if item in ['.', '..']: continue
                src = f"{FTP_ROOT}/{folder}/{item}"
                dst = f"{FTP_ROOT}/{target_cat}/{item}"
                try:
                    ftp.rename(src, dst)
                except Exception as e:
                    print(f"  Error moving {item}: {e}")
            
            # Delete alien folder
            try:
                ftp.cwd(FTP_ROOT)
                ftp.rmd(folder)
                print(f"  Deleted empty folder '{folder}'")
            except Exception as e:
                print(f"  Could not delete '{folder}': {e}")
                
ftp.quit()
print("FTP cleanup completed successfully.")

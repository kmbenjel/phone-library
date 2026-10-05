import re

# We will generate plans/060-fix-bukhari-and-raw.tsv
plan_file = "plans/060-fix-bukhari-and-raw.tsv"

moves = []

# 1. Bukhari Taseel:
bukhari_folder = "Books/كتب السنة/صحيح البخاري - ط. التأصيل - البخاري؛ محمد بن إسماعيل بن إبراهيم بن المغيرة البخاري، أبو عبد الله"
clean_bukhari_folder = "Books/كتب السنة/صحيح البخاري - ط. التأصيل"

moves.append((f"{bukhari_folder}/00_144261.pdf", f"{clean_bukhari_folder}/00 - صحيح البخاري (مقدمة التحقيق والواجهة).pdf", "Bukhari Taseel cover/intro"))
for i in range(1, 10):
    moves.append((f"{bukhari_folder}/0{i}_14426{i}.pdf", f"{clean_bukhari_folder}/0{i} - صحيح البخاري (المجلد {i}).pdf", f"Bukhari Taseel volume {i}"))
moves.append((f"{bukhari_folder}/10_144270.pdf", f"{clean_bukhari_folder}/10 - صحيح البخاري (المجلد 10 - الفهارس).pdf", "Bukhari Taseel volume 10"))

# 2. Musnad Ibn Abi Shaybah:
ibn_abi_shayba = "Books/كتب السنة/مسند ابن أبي شيبة - ابن أبي شيبة؛ عبد الله بن محمد بن أبي شيبة العبسي، مولاهم، الكوفي، أبو بكر"
clean_ibn_abi_shayba = "Books/كتب السنة/مسند ابن أبي شيبة - ط. دار الوطن"
moves.append((f"{ibn_abi_shayba}/00_34995.pdf", f"{clean_ibn_abi_shayba}/00 - مسند ابن أبي شيبة (الواجهة).pdf", "Musnad Ibn Abi Shayba cover"))
moves.append((f"{ibn_abi_shayba}/01_34995.pdf", f"{clean_ibn_abi_shayba}/01 - مسند ابن أبي شيبة (المجلد الأول).pdf", "Musnad Ibn Abi Shayba vol 1"))
moves.append((f"{ibn_abi_shayba}/02_34996.pdf", f"{clean_ibn_abi_shayba}/02 - مسند ابن أبي شيبة (المجلد الثاني).pdf", "Musnad Ibn Abi Shayba vol 2"))

# 3. Single files with raw names:
moves.append(("Books/الأدب/حماسة البحتري - البحتري/K-544.pdf", "Books/الأدب/حماسة البحتري - البحتري/حماسة البحتري.pdf", "Fix raw archive filename"))
moves.append(("Books/الأدب/مقامات الحريري - الحريري؛ القاسم بن علي بن محمد بن عثمان، أبو محمد الحريري البصري/121261.pdf", "Books/الأدب/مقامات الحريري - الحريري/مقامات الحريري.pdf", "Fix raw archive filename and long folder"))
moves.append(("Books/الأدب/مقامات السيوطي - الجلال السيوطي/52456.pdf", "Books/الأدب/مقامات السيوطي - الجلال السيوطي/مقامات السيوطي.pdf", "Fix raw archive filename"))
moves.append(("Books/كتب السنة/جزء ابن عمشليق - ابن عمشليق، أحمد بن علي بن محمد الجعفري أبو الطيب/28370.pdf", "Books/كتب السنة/جزء ابن عمشليق - ابن عمشليق/جزء ابن عمشليق.pdf", "Fix raw archive filename"))
moves.append(("Books/كتب السنة/جزء لؤلؤ - لؤلؤ بن أحمد؛ لؤلؤ بن أحمد بن عبد الله، أبو الدر، نجيب الدين/37717.pdf", "Books/كتب السنة/جزء لؤلؤ - لؤلؤ بن أحمد/جزء لؤلؤ.pdf", "Fix raw archive filename"))
moves.append(("Books/كتب السنة/مجلس من أمالي أبي نعيم الأصبهاني - أبو نعيم؛ أحمد بن عبد الله بن أحمد الأصبهاني، ابو نعيم/102468.pdf", "Books/كتب السنة/مجلس من أمالي أبي نعيم الأصبهاني - أبو نعيم/مجلس من أمالي أبي نعيم الأصبهاني.pdf", "Fix raw archive filename"))
moves.append(("Books/كتب السنة/مجموع فيه مصنفات أبي العباس الأصم وإسماعيل الصفار - الأصم؛ محمد بن يعقوب بن يوسف بن معقل ابن سنان الأموي بالولاء، أبو العباس الأصم/64328.pdf", "Books/كتب السنة/مجموع فيه مصنفات أبي العباس الأصم وإسماعيل الصفار - الأصم والصفار/مجموع فيه مصنفات أبي العباس الأصم وإسماعيل الصفار.pdf", "Fix raw archive filename"))
moves.append(("Books/كتب السنة/مشيخة ابن الجوزي - ابن الجوزي؛ عبد الرحمن بن علي بن محمد الجوزي القرشي البغدادي، أبو الفرج/87447.pdf", "Books/كتب السنة/مشيخة ابن الجوزي - ابن الجوزي/مشيخة ابن الجوزي.pdf", "Fix raw archive filename"))
moves.append(("Books/التراجم والطبقات/طبقات النسابين - بكر أبو زيد/30358.pdf", "Books/التراجم والطبقات/طبقات النسابين - بكر أبو زيد/طبقات النسابين.pdf", "Fix raw archive filename"))
moves.append(("Books/الشعر ودواوينه/ديوان لبيد بن ربيعة العامري - لبيد بن ربيعة/deewan_labeed.pdf", "Books/الشعر ودواوينه/ديوان لبيد بن ربيعة العامري - لبيد بن ربيعة/ديوان لبيد بن ربيعة العامري.pdf", "Fix raw archive filename"))

# 4. Sunan al-Tirmidhi (cut folder):
tirmidhi_bad = "Books/كتب عامة/سنن الترمذي وهو الجامع الكبير - الترمذي (ت"
tirmidhi_good = "Books/كتب السنة/سنن الترمذي وهو الجامع الكبير - ط. التأصيل"
moves.append((f"{tirmidhi_bad}/00 - سنن الترمذي وهو الجامع الكبير (الواجهة).pdf", f"{tirmidhi_good}/00 - سنن الترمذي وهو الجامع الكبير (الواجهة).pdf", "Move to canonical and fix"))
moves.append((f"{tirmidhi_bad}/04 - سنن الترمذي وهو الجامع الكبير (المجلد الأول - 1الطهارة - 5العيدين - 1 - 551).pdf", f"{tirmidhi_good}/01 - سنن الترمذي وهو الجامع الكبير (المجلد الأول - الطهارة - العيدين).pdf", "Move to canonical and fix"))
moves.append((f"{tirmidhi_bad}/03 - سنن الترمذي وهو الجامع الكبير (المجلد الثاني - 6السفر - 21السير - 1615 - 1724).pdf", f"{tirmidhi_good}/02 - سنن الترمذي وهو الجامع الكبير (المجلد الثاني - السفر - السير).pdf", "Move to canonical and fix"))
moves.append((f"{tirmidhi_bad}/02 - سنن الترمذي وهو الجامع الكبير (المجلد الثالث - 22الجهاد - 41الاستئذان والأدب - 1725 - 3090).pdf", f"{tirmidhi_good}/03 - سنن الترمذي وهو الجامع الكبير (المجلد الثالث - الجهاد - الاستئذان والأدب).pdf", "Move to canonical and fix"))
moves.append((f"{tirmidhi_bad}/01 - سنن الترمذي وهو الجامع الكبير (المجلد الرابع - 42الأمثال - 47المناقب - 3091 - 4318).pdf", f"{tirmidhi_good}/04 - سنن الترمذي وهو الجامع الكبير (المجلد الرابع - الأمثال - المناقب).pdf", "Move to canonical and fix"))
moves.append((f"{tirmidhi_bad}/99 - سنن الترمذي وهو الجامع الكبير (المجلد الخامس - كتاب العلل - الفهارس).pdf", f"{tirmidhi_good}/05 - سنن الترمذي وهو الجامع الكبير (المجلد الخامس - كتاب العلل والفهارس).pdf", "Move to canonical and fix"))

# Write plan
with open(plan_file, "w") as f:
    for src, dst, r in moves:
        f.write(f"{src}\t{dst}\t{r}\n")

print(f"Generated {len(moves)} actions in {plan_file}")

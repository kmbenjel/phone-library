with open("data/shamela/books.tsv") as f:
    sh_map = {}
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) > 3:
            sh_map[parts[1].strip()] = parts[2].strip()

with open("plans/061-recat-kutub-amma.tsv") as pf:
    rows = [l.strip().split("\t") for l in pf]

plan_lines = []
for src, dst, r in rows:
    folder = src.split("/")[2]
    fname = src.split("/")[3]
    
    # Check if this belongs to 'كتب عامة'
    is_general = False
    for t, c in sh_map.items():
        if c == "كتب عامة" and (t in folder or folder.startswith(t)):
            is_general = True
            break
    if not is_general:
        if any(k in folder for k in ["مالك بن نبي", "سيد قطب", "الشريف", "الغارة على العالم", "محاضرات في النصرانية", "كتاب ميزان الحكمة"]):
            is_general = True
            
    if is_general:
        # Move back from dst (where plan 061 moved it) to src (Books/كتب عامة/...)
        plan_lines.append((dst, src, "Restore to canonical Shamela category كتب عامة"))

with open("plans/062-restore-shamela-kutub-amma.tsv", "w") as out:
    for s, d, r in plan_lines:
        out.write(f"{s}\t{d}\t{r}\n")

print(f"Generated {len(plan_lines)} restore actions in plans/062-restore-shamela-kutub-amma.tsv")

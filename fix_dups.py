import csv
from collections import defaultdict

# 1. Load current paths grouped by size
index_paths_by_size = defaultdict(list)
for p, s in csv.reader(open('data/phone/index-now.tsv'), delimiter='\t'):
    index_paths_by_size[s].append(p)

# 2. Load dup-fingerprints, grouped by size
dup_lines = []
dup_by_size = defaultdict(list)
for r in csv.reader(open('data/phone/dup-fingerprints.tsv'), delimiter='\t'):
    dup_lines.append(r)
    dup_by_size[r[0]].append(r)

changed = 0
output_lines = []
for s, lines_for_size in dup_by_size.items():
    current_paths = list(index_paths_by_size[s])
    # If the number of current paths matches the number of dup paths, we just map them.
    if len(current_paths) == len(lines_for_size):
        for i, row in enumerate(lines_for_size):
            if row[2] != current_paths[i]:
                changed += 1
            row[2] = current_paths[i]
            output_lines.append(row)
    else:
        # What if it's different? E.g. we already deleted some duplicates?
        # We can try to map by basename if possible, or just skip if we can't be sure.
        for row in lines_for_size:
            basename = row[2].rsplit('/', 1)[-1]
            matched = False
            for p in current_paths:
                if p.rsplit('/', 1)[-1] == basename:
                    if row[2] != p: changed += 1
                    row[2] = p
                    output_lines.append(row)
                    matched = True
                    break
            if not matched:
                # If we can't find it, it might be already deleted or totally renamed, we keep it as is (or it fails later)
                output_lines.append(row)

with open('data/phone/dup-fingerprints.tsv', 'w') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerows(output_lines)

print(f"Updated {changed} paths.")

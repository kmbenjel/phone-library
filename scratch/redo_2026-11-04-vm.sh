#!/usr/bin/env bash
# One-off (2026-11-04): the FULL crop redo goes on with its analysis on the cloud VM crop-vm (owner: «optimize for speed …
# I would let you pause the process … more powerful CPU/memory (cloud)»): crop_redo.py --remote, the same 1,122-book list
# and batch as crop-redo-2026-11-03b (redo-done.tsv skips the 192 done), book_crop 511f6d7a5e. The VM's output is the
# laptop's byte for byte but for the trailer /ID's second half, new at every save on either machine (Perrault, 2026-11-04).
# OWNER 2026-11-04 20:30: «Go now over 4G» / «ok with mobile data» — launched on the phone's hotspot (~12 GB of 4G for the
# VM's uploads); off home: PHONE_HOST and NETPACE_ROUTER = the hotspot gateway, and no wait_calm (it pings the home router).
# Never rerun once it has started: refuses when its marker exists; resume with crop_redo.py itself (--remote).
# At its end: the review page, the VM stopped (billing), then by hand: crop_batch.py --again for البداية والنهاية 21 and
# المغرب في حلى المغرب 01 (their SKIP rows), refresh.sh, WORKLOG, the owner.
cd "$(dirname "$0")/.."
M=data/crop/.redo-2026-11-04-vm; [ -e $M ] && { echo "already ran"; exit 1; }; touch $M
L=logs/crop-redo-2026-11-03.log
echo "$(date -u '+%F %T') redo resumes on the VM (book_crop $(md5sum scripts/book_crop.py | cut -c1-10))" >> $L
python3 -c 'import sys; sys.path.insert(0, "scripts"); import phone_host; sys.exit(0 if phone_host._home() else 1)' && python3 scripts/wait_calm.py 10 >> $L 2>&1
scripts/run_resumable.sh $L -- python3 scripts/crop_redo.py data/crop/redo-all-2026-11-03.tsv crop-redo-2026-11-03 --remote --workers 14
python3 scripts/crop_doubts_page.py crop-redo-2026-11-03 redo-277-2026-11-03 >> $L 2>&1
echo "$(date -u '+%F %T') redo finished" >> $L
gcloud compute instances stop crop-vm --zone=europe-southwest1-b >> $L 2>&1 && echo "$(date -u '+%F %T') VM crop-vm stopped" >> $L

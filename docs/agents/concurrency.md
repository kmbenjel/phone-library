# Speed, network and memory — full text

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

## 7. Speed and concurrency (binding rule)

1. **Every download goes through `scripts/fetch_queue.py`** (or follows its model). Never `curl` files one by one.
2. **Internet downloads are always parallel and multi-connection:** `aria2c -x8 -s8 -k1M --continue`, 12 files at a
   time (`DL_JOBS=12 CONN=8`). Lower these only on HTTP 429/503 or repeated resets, and raise them back afterwards.
3. **The phone takes several FTP connections** (tested 2026-10-05: 5 at once accepted; use ≤ 3 for stability) (`--checkers=2 --transfers=2 --ftp-concurrency 2`). All phone I/O
   (upload, copy from phone, moves, listings) holds the shared lock `/tmp/phone-ftp.lock` (`flock`), so several
   jobs can run at once without fighting over the phone. The phone thread is never idle while files are waiting:
   download → verify → upload are separate stages; downloads never wait for uploads (except the staging cap).
4. **Git stays packed:** large derived files (site/00 is ~30 MB) are committed often; loose objects once grew `.git` to 9 GB
   (2026-10-06). `gc.auto` is set to 300; if `git count-objects -vH` shows GBs of loose objects, run `nice git gc --prune=now`.
5. **Staging cap:** the laptop disk is small (≈15 GB free on 2026-10-03). Staged files ≤ `STAGE_GB` (6), each staged
   file is deleted right after a successful upload.
6. **Verification runs in parallel** with the downloads: exact size, `%PDF`, `%%EOF`, `pdfinfo`.
7. **Independent tasks run at the same time in the background** (catalog fetches, dup checks, phone uploads, local
   downloads). A new request from the owner never cancels a running job; only an explicit order does.
8. **Everything is resumable:** `data/queue/<name>.done` lists finished targets, `<name>.failed` the failures with the
   reason. Re-running the same queue continues where it stopped.
9. **Never make the home network lag** (other people game and call on it — owner, 2026-10-05, twice; latency-based
   pacing alone did NOT stop the lag: while someone games, PAUSE bulk transfers entirely; when the owner says they are done,
   run at full speed, `NETPACE=0`). Only ONE bulk
   transfer at a time. Long phone transfers pace themselves (`scripts/netpace.py`): worst Wi-Fi ping to the router
   > 10 ms or internet ping > its baseline + 15 ms → 40 % slower; ceiling 6 MB/s. Internet downloads (`fetch_queue.py`,
   `NET_MB`, default 3 MB/s, 1.5 while anyone is home) and other queues start only after `scripts/wait_calm.py 10`
   (10 calm minutes); `scripts/resume_when_calm.sh` chains the paused queues that way. CPU-heavy jobs run with
   `nice`. Phone-side work (`MD5`, moves, renames, deletes) costs no bandwidth and can run any time.
10. **Never build a phone path from a lookup that can come back empty.** Write `"phone:Books/${P:?empty path}"` (or check in
   Python), never `"phone:Books/$P"`: on 2026-10-08 a `grep` missed a name (different Unicode order of «لَّ») and
   `rclone copyto "phone:Books/"` copied the whole library (9.3 GB, 1,020 files) to the laptop before it was stopped. Look up
   names with Unicode-normalised comparison (`unicodedata.normalize('NFC', …)`).
12. **Memory: never let a job take the desktop down** (2026-10-17 03:38: the crop baseline ran 6 workers on a large book, memory ran
   out and systemd-oomd closed the owner's whole GNOME session — every job and his desktop with it). Heavy jobs (book_crop analyses,
   OCR, inspection) run as capped user services, ≤ 3 workers: `systemd-run --user --unit=NAME --property=MemoryHigh=3G
   --property=MemoryMax=4G --nice=10 --working-directory=$PWD CMD` (linger is on, so they survive a session end too).
   **More workers, governed (owner 2026-10-18):** the crop jobs (crop_redo, crop_batch, crop_regress) take as many books at
   once as `data/crop/workers` says (read before each book), set by `scripts/mem_governor.py` (unit `mem-governor`): up to 6;
   free memory < 2 GB → it closes Brave/Chrome the normal way if nobody has touched the laptop for 10 min and no sound plays,
   then, if still short, one worker fewer; < 1 GB or memory pressure ≥ 20 % → the EMERGENCY BRAKE: the largest crop process is
   killed at once, then two workers fewer; > 4.5 GB for 10 min → one more. **A book starts only with ≥ 3 GB free**
   (`crop_batch.room()`, in every crop tool, the bench included). **Every crop job runs in ONE memory pen, `crop.slice`**
   (`systemd-run --user --slice=crop.slice --unit=NAME --nice=10 --working-directory=$PWD scripts/run_resumable.sh LOG -- CMD`,
   no memory properties of its own): the governor sizes the pen every few seconds from what the owner uses (free memory + what the
   pen holds − 2.5 GB, 2–10 GB) — when he opens more (browsers, VS Code, Antigravity), the jobs are reclaimed and swapped, never
   his session; the worker count follows the pen (1.5 GB per book, 0.5 GB kept for the job's own process — measured 2026-10-26, a whole
   book in one process ≤ 1.29 GB; owner's word the same day, was 2.2 / 1.5; no climb for 20 minutes after a brake — owner: «reduce the workers at that point for a while»). `run_resumable.sh` reruns a killed job once memory is back.
   Never a per-unit `MemoryHigh` above the pen — a unit throttled at a high MemoryHigh reclaims
   hard, the user slice's memory pressure rises and systemd-oomd kills by reclaim, GNOME Shell first: on 2026-10-18 03:05 a
   bench with MemoryHigh=6G (raised by the agent) and 3 analyses beside the owner's browsers closed his session again.
11. **Stopping a job:** `kill <pid>` with the PID from `pgrep -f "[n]ame"` in a separate command — a `pkill -f name`
   in the same command line that restarts the job kills the shell itself.

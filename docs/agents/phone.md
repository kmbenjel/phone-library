# Phone connection — full details

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

## 2. Connecting to the phone

- The phone runs an FTP server app on port `2221`, anonymous login. The IP is DHCP; known addresses: `192.168.11.100` — reserved for the phone in the router by the owner (2026-10-17; before that it wandered .100/.102/.104/.109 with a randomized MAC), `192.168.11.104` (2026-10-17 evening), `192.168.11.102` (2026-10-11 evening: it switched .100 ↔ .102 several times;
  owner: «keep up with 102»; a DHCP reservation in the router would stop it),
  `192.168.11.103` (2026-10-05 noon), `192.168.11.102` (2026-10-04 and again 2026-10-05 afternoon) and `192.168.11.100` (before). The scripts try them, then scan the /24 for port 2221 (`phone_host.find()`)
  (`scripts/phone_host.py`; `PHONE_HOST=<ip>` overrides). If neither answers, find it with `ip neigh` and
  `nc -z <ip> 2221`, add it to the top of `CANDIDATES` in `phone_host.py` and run
  `rclone config update phone host <ip>` (rclone takes one fixed host).
- **Login (owner 2026-10-18):** the FTP app has an account. Its user name and password are NEVER written in this repo (it is pushed
  to GitHub and this guide is copied to the phone): they live in `~/.config/phone-library/ftp.env` (lines `USER=…` and `PASS=…`, mode
  600, written by the owner) and in rclone's own config for the remote `phone:`. Every script logs in through
  `phone_host.login(ftp)` (`phone_host.creds()`); without that file it logs in anonymously. Ask the owner if you need it.
- rclone remote: `phone:` (library = `phone:Books`). Optional mount:
  `rclone mount phone:Books ~/phone-books --daemon --vfs-cache-mode writes --dir-cache-time 1h`.
- Moves and renames are server-side (FTP RNFR/RNTO): nothing is re-uploaded, so they are instant.
- FTP has no checksums. Duplicates are verified with a head+tail 64 KB fingerprint plus the exact
  size (`scripts/dup_check.py`).


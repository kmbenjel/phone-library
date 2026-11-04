# Phone connection — full details

Moved verbatim from AGENTS.md (2026-10-28) to keep that guide short; AGENTS.md points here. Section numbers are the old ones (code comments cite them).

## 2. Connecting to the phone

- The phone runs an FTP server app on port `2221`, anonymous login. The IP is DHCP; known addresses: `192.168.11.100` — reserved for the phone in the router by the owner (2026-10-17; before that it wandered .100/.102/.104/.109 with a randomized MAC), `192.168.11.104` (2026-10-17 evening), `192.168.11.102` (2026-10-11 evening: it switched .100 ↔ .102 several times;
  owner: «keep up with 102»; a DHCP reservation in the router would stop it),
  `192.168.11.103` (2026-10-05 noon), `192.168.11.102` (2026-10-04 and again 2026-10-05 afternoon) and `192.168.11.100` (before). The scripts try them, then scan the /24 for port 2221 (`phone_host.find()`)
  Away from home (the laptop not on 192.168.11.x; since 2026-11-01) those addresses count as strangers and are never tried: `find()` uses the last address in `data/phone/current-address.txt` when it answers. On a new network write the phone's address there and in rclone (`rclone config update phone host …`) by hand, once.
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
  size (`scripts/dup_check.py`). Over ssh `md5sum`/`sha1sum` run on the phone (`SSHPhone.md5()`, `rclone md5sum phone:…`).
- **SSH/SFTP too (2026-11-04):** Termux (F-Droid 0.118.3) runs `sshd` on port `8022`, key login only: key
  `~/.config/phone-library/phone_ssh` (never in the repo), user `u0_a543`, storage permission granted (`/sdcard/Books` =
  the library). rclone remote `phonessh:` (library = `phonessh:/sdcard/Books`) with real `md5sum`/`sha1sum` on the phone, so
  duplicates can be proven by full hashes; `rsync` is installed. 8 parallel sessions tested fine (the FTP app is the narrow one).
  Same IP as the FTP server; on the phone's hotspot it is the gateway (`172.26.156.17` on 2026-11-04): `rclone config update
  phonessh host <ip>`. After a phone reboot, open Termux and run `sshd` (or Termux:Boot with `~/.termux/boot/start-sshd`).
  Test: `ssh -i ~/.config/phone-library/phone_ssh -p 8022 -o HostKeyAlias=phone-termux <ip> true`.
- **One switch for every script (2026-11-04): `scripts/phone_proto.sh ssh|ftp`** (no argument: prints the current one).
  It writes `~/.config/phone-library/proto`, which `phone_host.py` reads (`PHONE_PROTO=` overrides per command), and
  turns the rclone remote `phone:` into an alias of `phonessh:/sdcard` (the FTP remote kept as `phoneftp:`), so the
  rclone scripts' `phone:Books/...` paths work unchanged; `ftp` undoes it. Only while no phone job runs.
  - Scripts connect with `phone_host.connect(timeout, host)`: an `ftplib.FTP`, or a `phone_ssh.SSHPhone` that answers the
    same calls (nlst mkd rmd delete rename size retrbinary storbinary sendcmd XMD5/MD5) by running coreutils on the phone
    over one shared OpenSSH connection; its errors are ftplib's (`error_perm` = missing/refused, `OSError` = connection).
    Byte ranges: `phone_host.read_range(path, start, n)` (curl logged in over FTP, `dd` over ssh). Never `ftplib.FTP()`
    or a bare `curl ftp://` in a new script: since the FTP account (2026-10-18) an anonymous curl gets `530`.
  - The host key is pinned as `phone-termux` in `~/.ssh/known_hosts` (the address changes with each hotspot, the key
    does not); rclone checks keys by address, so `scripts/phone_ssh.py pin <ip>` adds the new address only when its key
    is the pinned one (`phone_proto.sh`, the watchdog and `fix_at_scale.py` call it).
  - `phone_host.find()` also tries the default gateway: on the phone's own hotspot the phone is the gateway.


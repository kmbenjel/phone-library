#!/usr/bin/env bash
# THE REVIEW PAGE SERVED FROM A VM (owner 2026-11-08: «serve the review page if any from a vm» — he reviews from Brave on his
# phone, away from the laptop). A small VM (review-vm, e2-micro, project phone-library-crop-261106) runs scripts/review_server.py
# on port 8765 with a secret token (~/.config/phone-library/review_token, never in the repo); the laptop pushes
# site/crop-doubts.html + site/crop-doubts/ and its comments (read-only, REVIEW_BASE) and pulls the comments he saves there
# into data/names/review-comments.jsonl, so watch_comments.py sees them as before.
# The VM runs only while the page has cards (owner 2026-11-08 «Stop review-vm when idle»): `sync` sees 0 <article> cards in
# site/crop-doubts.html → a last pull, VM stopped, units review-tunnel + review-sync stopped. `up` brings all three back.
# No static IP, no open port (owner 2026-11-08: review-ip and firewall review-web-8765 deleted): the server listens on the
# VM's 127.0.0.1 and the laptop reaches it through the ssh tunnel unit, re-pointed at the VM's current address by up/sync.
#   scripts/review_vm.sh up      start (create the first time), push, start the server + tunnel + sync loop, print the URL
#   scripts/review_vm.sh sync    push the page if changed + pull new comments (the review-sync unit calls it every 20 s)
#   scripts/review_vm.sh down    a last pull, stop the VM, the tunnel and the sync loop
#   scripts/review_vm.sh url     print the URL
set -u
cd "$(dirname "$0")/.."
VM=review-vm; PROJ=phone-library-crop-261106; ZONE=europe-southwest1-b; PORT=8765
TOK_F=~/.config/phone-library/review_token
KEY=~/.ssh/google_compute_engine
G="gcloud compute instances --project $PROJ"
[ -s $TOK_F ] || { umask 077; python3 -c 'import secrets; print(secrets.token_urlsafe(24))' > $TOK_F; }
TOK=$(cat $TOK_F)
ip() { $G describe $VM --zone $ZONE --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null; }
status() { $G describe $VM --zone $ZONE --format='value(status)' 2>/dev/null; }
SSH() { ssh -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o HostKeyAlias=$VM -o BatchMode=yes -i $KEY k@"$IP" "$@"; }
RS() { rsync -az -e "ssh -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o HostKeyAlias=$VM -o BatchMode=yes -i $KEY" "$@"; }

push() {
  RS scripts/review_server.py k@"$IP":review/scripts/ &&
  RS --delete site/crop-doubts/ k@"$IP":review/site/crop-doubts/ &&
  RS site/crop-doubts.html k@"$IP":review/site/ &&
  RS data/names/review-comments.jsonl k@"$IP":review/base.jsonl.new && SSH 'mv review/base.jsonl.new review/base.jsonl'
}
pull() {   # (the server's own log on the VM holds only what he saved there: its lines not yet here are appended)
  local t; t=$(mktemp); RS k@"$IP":review/data/names/review-comments.jsonl "$t" 2>/dev/null || { rm -f "$t"; return 0; }
  python3 - "$t" <<'EOF'
import sys
here = 'data/names/review-comments.jsonl'
have = set(open(here, encoding='utf-8').read().splitlines())
new = [l for l in open(sys.argv[1], encoding='utf-8').read().splitlines() if l.strip() and l not in have]
if new:
    with open(here, 'a', encoding='utf-8') as f: f.write(''.join(l + '\n' for l in new))
    print(f'{len(new)} comment(s) pulled from the VM')
EOF
  rm -f "$t"
}
cards() { grep -o '<article>' site/crop-doubts.html 2>/dev/null | wc -l; }
tunnel() {   # (re)start the tunnel unit when it is not running to the VM's current address
  systemctl --user is-active -q review-tunnel && systemctl --user show review-tunnel -p ExecStart | grep -qF "k@$IP " && return 0
  systemctl --user stop review-tunnel 2>/dev/null; systemctl --user reset-failed review-tunnel 2>/dev/null
  systemd-run --user -q --unit=review-tunnel -p Restart=always -p RestartSec=10s /usr/bin/ssh -N -o ServerAliveInterval=15 \
    -o ExitOnForwardFailure=yes -o HostKeyAlias=$VM -o BatchMode=yes -i $KEY -L 127.0.0.1:$PORT:127.0.0.1:$PORT k@"$IP"
}
syncloop() {
  systemctl --user is-active -q review-sync && return 0; systemctl --user reset-failed review-sync 2>/dev/null
  systemd-run --user -q --unit=review-sync --working-directory="$PWD" --setenv=PATH="$PATH" \
    /usr/bin/bash -c 'while :; do scripts/review_vm.sh sync; sleep 20; done'
}
stopall() {  # the sync unit last: it may be the caller
  $G stop $VM --zone $ZONE >/dev/null && echo "$VM stopped"
  systemctl --user stop review-tunnel 2>/dev/null; systemctl --user stop review-sync 2>/dev/null
}
serve() {
  SSH "mkdir -p review/scripts review/site review/data/names; touch review/data/names/review-comments.jsonl
       pkill -f '^python3 scripts/review_server' ; sleep 1
       cd review && REVIEW_BIND=127.0.0.1 REVIEW_BASE=\$HOME/review/base.jsonl \
         nohup python3 scripts/review_server.py $PORT >> server.log 2>&1 < /dev/null & disown; sleep 1; pgrep -f '[r]eview_server.py' >/dev/null && echo serving"
}
case "${1:-}" in
  up)
    if [ -z "$(status)" ]; then
      $G create $VM --zone $ZONE --machine-type e2-micro --image-family ubuntu-2404-lts-amd64 --image-project ubuntu-os-cloud \
        --boot-disk-size 10GB >/dev/null || exit 1
    elif [ "$(status)" != RUNNING ]; then $G start $VM --zone $ZONE >/dev/null || exit 1; fi
    for i in $(seq 1 30); do IP=$(ip); [ -n "$IP" ] && SSH true 2>/dev/null && break; sleep 5; done
    [ -n "${IP:-}" ] || { echo "VM has no address"; exit 1; }
    push && serve && tunnel && syncloop && echo "http://127.0.0.1:$PORT/crop-doubts.html?k=$TOK" ;;
  sync)
    [ "$(status)" = RUNNING ] || exit 0; IP=$(ip); pull
    if [ "$(cards)" -eq 0 ]; then echo "no cards: stopping"; stopall; exit 0; fi
    push; tunnel ;;
  down)
    if [ "$(status)" = RUNNING ]; then IP=$(ip); pull; fi; stopall ;;
  url) echo "http://127.0.0.1:$PORT/crop-doubts.html?k=$TOK" ;;
  *) echo "usage: $0 up|sync|down|url"; exit 2 ;;
esac

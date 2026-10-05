"""Wait until nobody needs the home network (no games/calls): the Wi-Fi round trip to the router and the internet round
trip stay near their quiet baselines for MINUTES in a row. Then exit 0, so a queue can start:
    python3 scripts/wait_calm.py 10 && python3 scripts/fetch_queue.py …
Thresholds: worst Wi-Fi ping < 8 ms and worst internet ping < internet baseline + 12 ms, checked every 20 s."""
import re, subprocess, sys, time
minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 10
def ping(host):
    out = subprocess.run(['ping', '-c', '5', '-i', '0.3', '-W', '1', host], capture_output=True, text=True).stdout
    return [float(x) for x in re.findall(r'time=([\d.]+)', out)]
base, calm_since = None, None
while True:
    lan, wan = ping('192.168.11.1'), ping('1.1.1.1')
    if wan: base = min(wan) if base is None else min(base * 1.002, min(wan))
    calm = bool(lan and wan) and max(lan) < 8 and max(wan) < base + 12
    now = time.time()
    calm_since = (calm_since or now) if calm else None
    if calm_since and now - calm_since >= minutes * 60:
        print(time.strftime('%T'), 'network calm for', minutes, 'min'); sys.exit(0)
    time.sleep(20)

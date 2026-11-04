"""Latency-aware pacing for transfers over the home Wi-Fi, so other people's games and calls do not lag.
A thread pings the router every 2 s; when the worst of 4 round trips rises above HIGH ms the transfer rate is cut by 30 %,
when it stays under LOW ms it grows by 15 % (between MIN and MAX bytes/s). Transfers call pacer.wait(nbytes).
Env: NETPACE=0 disables; NETPACE_MAX / NETPACE_MIN (MB/s), NETPACE_LOW / NETPACE_HIGH (ms), NETPACE_ROUTER."""
import itertools, os, re, statistics, subprocess, threading, time

def _gateway():
    try:
        for line in open('/proc/net/route'):
            f = line.split()
            if f[1] == '00000000' and f[2] != '00000000':
                import socket
                return socket.inet_ntoa(bytes.fromhex(f[2])[::-1])
    except (OSError, IndexError, ValueError):
        pass
    return None


def _network():
    """(gateway, on the phone's hotspot): the hotspot only when the gateway IS the phone (its FTP 2221 or ssh 8022 answers).
    A gateway outside 192.168.11.x is not enough: somebody else's home Wi-Fi has one too, and people use it (2026-11-04)"""
    import socket
    gw = _gateway()
    if not gw or gw.startswith('192.168.11.'): return gw, False
    for port in (2221, 8022):
        try: socket.create_connection((gw, port), timeout=2).close(); return gw, True
        except OSError: pass
    return gw, False


class Pacer:
    def __init__(self):
        # on the phone's own hotspot (default gateway outside the home 192.168.11.x) the phone↔laptop transfers go
        # between those two devices only: nobody else on that Wi-Fi, no internet used → off (owner 2026-11-04 «yes»;
        # the home-router ping got no answer there and held the rate at its minimum). NETPACE=1/0 still forces it.
        # The network is looked at again every 30 s: a run started on the hotspot that finds itself on another Wi-Fi paces
        # from then on (and the router pinged is that network's gateway, unless NETPACE_ROUTER says otherwise).
        self.forced = os.environ.get('NETPACE')
        self.gw, self.hotspot = _network()
        self.on = self.forced != '0' if self.forced else not self.hotspot
        self.max = float(os.environ.get('NETPACE_MAX', '6')) * 1e6       # ceiling: other devices game and call
        self.wan_slack = float(os.environ.get('NETPACE_WAN_SLACK', '15'))   # ms above the internet baseline
        self.wan_rtt = None
        self.min = float(os.environ.get('NETPACE_MIN', '0.4')) * 1e6
        self.low, self.high = float(os.environ.get('NETPACE_LOW', '6')), float(os.environ.get('NETPACE_HIGH', '10'))
        self.router = os.environ.get('NETPACE_ROUTER') or self.gw or '192.168.11.1'
        self.wan = os.environ.get('NETPACE_WAN', '1.1.1.1')           # games feel the internet line, not only the Wi-Fi
        self.wan_base = None
        self.rate, self.rtt = 2e6, None
        self.t, self.sent = time.time(), 0.0
        self.lock = threading.Lock()
        threading.Thread(target=self._watch, daemon=True).start()

    def _ping(self, host):
        out = subprocess.run(['ping', '-c', '4', '-i', '0.25', '-W', '1', host], capture_output=True, text=True).stdout
        return [float(x) for x in re.findall(r'time=([\d.]+)', out)]

    def _renet(self):
        gw, hs = _network()
        if (gw, hs) == (self.gw, self.hotspot): return
        self.gw, self.hotspot = gw, hs
        self.on = self.forced != '0' if self.forced else not hs
        if not os.environ.get('NETPACE_ROUTER'): self.router = gw or '192.168.11.1'
        self.wan_base, self.rtt, self.wan_rtt = None, None, None      # a new network: learn its baseline again, start low
        self.rate = min(self.rate, 1e6)
        print(time.strftime('%F %T'), f'netpace: network now gateway {gw}, {"phone hotspot" if hs else "Wi-Fi"}: pace',
              'on' if self.on else 'off', flush=True)

    def _watch(self):
        for i in itertools.count():
            if i % 15 == 0 and i:
                try: self._renet()
                except Exception: pass
            if not self.on: time.sleep(2); continue
            lan, wan = self._ping(self.router), self._ping(self.wan)
            if wan:
                w = min(wan)
                self.wan_base = w if self.wan_base is None else min(self.wan_base * 1.002, w)   # slowly forgets
            busy = False
            if lan:
                self.rtt = max(lan)                       # games feel the spikes, not the average
                busy = self.rtt > self.high
            if wan and self.wan_base:
                self.wan_rtt = max(wan)
                busy = busy or self.wan_rtt > self.wan_base + self.wan_slack
            calm = lan and self.rtt < self.low and (not wan or max(wan) < (self.wan_base or 0) + self.wan_slack / 2)
            if busy: self.rate = max(self.min, self.rate * 0.6)
            elif calm: self.rate = min(self.max, self.rate * 1.1)
            time.sleep(2)

    def wait(self, n):
        if not self.on: return
        with self.lock:
            now = time.time()
            self.sent = max(0.0, self.sent - (now - self.t) * self.rate) + n   # leaky bucket
            self.t = now
            delay = self.sent / self.rate - 0.25                                  # allow a 0.25 s burst
        if delay > 0: time.sleep(delay)

    def status(self):
        return (f'pace {self.rate / 1e6:.1f} MB/s, wifi {self.rtt if self.rtt is None else round(self.rtt, 1)} ms, '
                f'internet {self.wan_rtt if self.wan_rtt is None else round(self.wan_rtt)}/{self.wan_base if self.wan_base is None else round(self.wan_base)} ms') if self.on else ('pace off (phone hotspot)' if self.hotspot else 'pace off')

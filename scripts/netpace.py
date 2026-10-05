"""Latency-aware pacing for transfers over the home Wi-Fi, so other people's games and calls do not lag.
A thread pings the router every 2 s; when the worst of 4 round trips rises above HIGH ms the transfer rate is cut by 30 %,
when it stays under LOW ms it grows by 15 % (between MIN and MAX bytes/s). Transfers call pacer.wait(nbytes).
Env: NETPACE=0 disables; NETPACE_MAX / NETPACE_MIN (MB/s), NETPACE_LOW / NETPACE_HIGH (ms), NETPACE_ROUTER."""
import os, re, statistics, subprocess, threading, time

class Pacer:
    def __init__(self):
        self.on = os.environ.get('NETPACE', '1') != '0'
        self.max = float(os.environ.get('NETPACE_MAX', '6')) * 1e6       # ceiling: other devices game and call
        self.wan_slack = float(os.environ.get('NETPACE_WAN_SLACK', '15'))   # ms above the internet baseline
        self.wan_rtt = None
        self.min = float(os.environ.get('NETPACE_MIN', '0.4')) * 1e6
        self.low, self.high = float(os.environ.get('NETPACE_LOW', '6')), float(os.environ.get('NETPACE_HIGH', '10'))
        self.router = os.environ.get('NETPACE_ROUTER', '192.168.11.1')
        self.wan = os.environ.get('NETPACE_WAN', '1.1.1.1')           # games feel the internet line, not only the Wi-Fi
        self.wan_base = None
        self.rate, self.rtt = 2e6, None
        self.t, self.sent = time.time(), 0.0
        self.lock = threading.Lock()
        if self.on: threading.Thread(target=self._watch, daemon=True).start()

    def _ping(self, host):
        out = subprocess.run(['ping', '-c', '4', '-i', '0.25', '-W', '1', host], capture_output=True, text=True).stdout
        return [float(x) for x in re.findall(r'time=([\d.]+)', out)]

    def _watch(self):
        while True:
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
                f'internet {self.wan_rtt if self.wan_rtt is None else round(self.wan_rtt)}/{self.wan_base if self.wan_base is None else round(self.wan_base)} ms') if self.on else 'pace off'

"""Latency-aware pacing for transfers over the home Wi-Fi, so other people's games and calls do not lag.
A thread pings the router every 2 s; when the worst of 4 round trips rises above HIGH ms the transfer rate is cut by 30 %,
when it stays under LOW ms it grows by 15 % (between MIN and MAX bytes/s). Transfers call pacer.wait(nbytes).
Env: NETPACE=0 disables; NETPACE_MAX / NETPACE_MIN (MB/s), NETPACE_LOW / NETPACE_HIGH (ms), NETPACE_ROUTER."""
import os, re, statistics, subprocess, threading, time

class Pacer:
    def __init__(self):
        self.on = os.environ.get('NETPACE', '1') != '0'
        self.max = float(os.environ.get('NETPACE_MAX', '16')) * 1e6
        self.min = float(os.environ.get('NETPACE_MIN', '0.4')) * 1e6
        self.low, self.high = float(os.environ.get('NETPACE_LOW', '8')), float(os.environ.get('NETPACE_HIGH', '15'))
        self.router = os.environ.get('NETPACE_ROUTER', '192.168.11.1')
        self.rate, self.rtt = 3e6, None
        self.t, self.sent = time.time(), 0.0
        self.lock = threading.Lock()
        if self.on: threading.Thread(target=self._watch, daemon=True).start()

    def _watch(self):
        while True:
            out = subprocess.run(['ping', '-c', '4', '-i', '0.25', '-W', '1', self.router], capture_output=True, text=True).stdout
            rtts = [float(x) for x in re.findall(r'time=([\d.]+)', out)]
            if rtts:
                self.rtt = max(rtts)                      # games feel the spikes, not the average
                if self.rtt > self.high: self.rate = max(self.min, self.rate * 0.7)
                elif self.rtt < self.low: self.rate = min(self.max, self.rate * 1.15)
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
        return f'pace {self.rate / 1e6:.1f} MB/s, rtt {self.rtt if self.rtt is None else round(self.rtt, 1)} ms' if self.on else 'pace off'

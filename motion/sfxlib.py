"""Shared synth + sound-effect toolkit (48 kHz stereo buses, helpers). Import with `from sfxlib import *`."""
import numpy as np
from scipy import signal
SR = 48000; T = 25.0; N = int(SR * T)
rng = np.random.default_rng(3)
t_all = np.arange(N) / SR
MUS = np.zeros((N, 2)); SFX = np.zeros((N, 2)); VERB = np.zeros((N, 2))

def pan(x, p):  # p -1..1, equal power
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)
def add(bus, at, st, g=1.0, send=0.0):
    i = int(round(at * SR)); j = min(N, i + len(st))
    if i < 0 or i >= N: return
    bus[i:j] += g * st[:j - i]
    if send: VERB[i:j] += g * send * st[:j - i]
def env(n, a, d, hold=0.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)); e *= np.where(t < a + hold, 1, np.exp(-(t - a - hold) / d)); return e
def sos(kind, f, order=2):
    return signal.butter(order, f, kind, fs=SR, output='sos')
def filt(x, kind, f, order=2): return signal.sosfilt(sos(kind, f, order), x)
def noise(n): return rng.standard_normal(n)
def hz(midi): return 440 * 2 ** ((midi - 69) / 12)

def sweep_noise(dur, f0, f1, q=0.35, curve=1.0):
    """noise with a moving band — built in the STFT domain (clean, vectorised)"""
    n = int(dur * SR); x = noise(n)
    f, tt, Z = signal.stft(x, SR, nperseg=1024, noverlap=768)
    u = np.clip(tt / dur, 0, 1) ** curve
    fc = f0 * (f1 / f0) ** u
    bw = fc * q
    M = np.exp(-0.5 * ((f[:, None] - fc[None, :]) / bw[None, :]) ** 2)
    _, y = signal.istft(Z * M, SR, nperseg=1024, noverlap=768)
    y = y[:n]; return y / (np.abs(y).max() + 1e-9)

def whoosh(dur=.55, f0=500, f1=4500, p0=0., p1=0., g=1.):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sweep_noise(dur, f0, f1, .45, .8) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.6
    pp = np.linspace(p0, p1, n); a = (pp + 1) * np.pi / 4
    return np.stack([y * np.cos(a), y * np.sin(a)], 1) * g

def impact(sub0=70, sub1=32, dur=1.6, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(sub1 + (sub0 - sub1) * np.exp(-t * 9)) / SR
    sub = np.sin(ph) * env(n, .003, .45)
    body = filt(noise(n), 'lowpass', 900) * env(n, .001, .08) * 1.6
    crack = filt(noise(n), 'highpass', 2500) * env(n, .0005, .03) * bright
    y = np.tanh(1.6 * (sub + body * .5 + crack * .35))
    return np.stack([y, y], 1)

def supersaw(freqs, dur, voices=5, det=14, cutoff=2600, amp_env=None):
    n = int(dur * SR); t = np.arange(n) / SR; L = np.zeros(n); R = np.zeros(n)
    for f in freqs:
        for v in range(voices):
            cents = (v - (voices - 1) / 2) * det / ((voices - 1) / 2)
            fv = f * 2 ** (cents / 1200); ph0 = rng.random() * 2 * np.pi
            H = int(min(60, 11000 / fv)); y = np.zeros(n)
            for h in range(1, H + 1): y += np.sin(2 * np.pi * fv * h * t + ph0 * h) / h
            p = (v - (voices - 1) / 2) / ((voices - 1) / 2) * .7
            L += y * np.cos((p + 1) * np.pi / 4); R += y * np.sin((p + 1) * np.pi / 4)
    st = np.stack([filt(L, 'lowpass', cutoff, 4), filt(R, 'lowpass', cutoff, 4)], 1) / (len(freqs) * voices)
    if amp_env is not None: st *= amp_env[:, None]
    return st

def pluck(f, dur=.35, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for h in range(1, int(min(30, 10000 / f)) + 1):
        y += np.sin(2 * np.pi * f * h * t) / h * np.exp(-t * (6 + h * 3.5 / bright))
    return y * np.minimum(1, t / .002)

def kick(g=1.0):
    n = int(.45 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(46 + 110 * np.exp(-t * 38)) / SR
    y = np.sin(ph) * env(n, .001, .16) + filt(noise(n), 'highpass', 3000) * env(n, .0003, .004) * .5
    y = np.tanh(2.2 * y) * g; return np.stack([y, y], 1)
def clap():
    n = int(.35 * SR); y = np.zeros(n); nz = filt(noise(n), 'bandpass', [900, 2600])
    for k, off in enumerate([0, .011, .022, .034]):
        i = int(off * SR); y[i:] += nz[:n - i] * env(n - i, .0005, .012 if k < 3 else .09)
    return pan(y * .9, .0)
def hat(open_=False, p=.25):
    n = int((.25 if open_ else .06) * SR); y = filt(noise(n), 'highpass', 8000, 4) * env(n, .0005, .07 if open_ else .012)
    return pan(y, p)
def shaker(p=-.3):
    n = int(.08 * SR); y = filt(noise(n), 'bandpass', [5000, 9000]) * env(n, .008, .02); return pan(y, p)
def keyclick(big=False):
    n = int(.07 * SR); t = np.arange(n) / SR
    y = filt(noise(n), 'bandpass', [1800, 5200]) * env(n, .0004, .006) + np.sin(2 * np.pi * (190 if big else 240) * t) * env(n, .001, .018) * .7
    return pan(y * (1.4 if big else 1), rng.uniform(-.15, .15))
def tick(f=2600, g=1.0):
    n = int(.05 * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f * t) * .6 + filt(noise(n), 'highpass', 3000) * .4) * env(n, .0003, .008); return pan(y * g, 0)
def crash(dur=2.2):
    n = int(dur * SR); y = filt(noise(n), 'highpass', 5000, 2) * env(n, .002, .7); return np.stack([y, filt(noise(n), 'highpass', 5000) * env(n, .002, .7)], 1) * .5
def chime(root=74, dur=2.4):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for m, a, d in [(root, 1, .9), (root + 7, .55, .7), (root + 12, .4, .6), (root + 16, .25, .5), (root + 24, .15, .35)]:
        f = hz(m); y += a * (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4)) * np.exp(-t / d)
    y *= np.minimum(1, t / .002); return np.stack([y, np.roll(y, 240)], 1)
def braam(root=38, dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    cut = 180 + 2600 * np.exp(-t * 3.2)
    notes = [hz(root), hz(root + 7), hz(root + 12), hz(root - 12)]
    st = supersaw(notes, dur, voices=5, det=18, cutoff=9000)
    # time-varying low-pass: blockwise
    out = np.zeros_like(st); B = 1024
    for i in range(0, n, B):
        s = sos('lowpass', float(cut[min(i, n - 1)]), 2)
        out[i:i + B] = signal.sosfilt(s, st[i:i + B], axis=0)
    out *= env(n, .01, .75, .15)[:, None]
    return np.tanh(out * 5) * .8 + impact(62, 30, dur, .6) * .7

def reverse_swell(dur=.8, f=4000):
    n = int(dur * SR); y = filt(noise(n), 'highpass', f) * (np.linspace(0, 1, n) ** 3); return np.stack([y, y[::-1][::-1]], 1)
def riser(dur, f0=300, f1=5200):
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    nz = sweep_noise(dur, f0 * 2, f1 * 1.6, .6, 1.4)
    tone = np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (u ** 1.5) / 8) / SR)
    y = (nz * .8 + tone * .35) * u ** 2.2; return np.stack([y, y], 1)


"""Score + sound design for the v3 reel -> out/sound-v3.wav (48 kHz stereo, 25 s).
Act I/II (dark): drone, clock-tick tension, typing, boom + silence on "nothing.", card-flood flutters,
trailer braams on "Everywhere." and "isn't enough.", riser into the light burst.
Act III (light): 120 BPM track — kick, clap, hats, shaker, sub bass, sidechained supersaw chords, pluck arp —
every whip gets a panned whoosh, list items tick, "Handled." crashes, logo hit + chime, button click.
Master: reverb sends, glue compression, soft clip; loudness is normalised with ffmpeg afterwards."""
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

# ======================= ACT I / II — dark =======================
# drone: sub D + filtered saw, breathing, 0 → 11.35
n = int(11.6 * SR); t = np.arange(n) / SR
drone = np.sin(2 * np.pi * hz(26) * t) * .55 + filt(sum(np.sin(2 * np.pi * hz(38) * h * t) / h for h in range(1, 18)), 'lowpass', 380) * .5
drone *= (np.minimum(1, t / .4)) * (.75 + .25 * np.sin(2 * np.pi * t / 4.8)) * np.clip((11.45 - t) / .15, 0, 1)
gap = np.ones(n); gi = (t > 6.62) & (t < 7.2); gap[gi] = np.clip(np.abs(t[gi] - 6.91) / .29, 0, 1) ** 2  # silence after "nothing."
drone *= gap
add(MUS, 0, np.stack([drone, drone], 1), .3)
# airy pad above (D minor add9), subtle
air = supersaw([hz(62), hz(65), hz(69), hz(76)], 11.4, voices=3, det=10, cutoff=1400)
air *= (np.minimum(1, t[:len(air)] / 1.5) * np.clip((11.4 - t[:len(air)]) / .3, 0, 1) * gap[:len(air)])[:, None]
add(MUS, 0, air, .12, send=.6)
# opening: soft hit on "the best"
add(SFX, .1, impact(58, 34, 1.4, .3), .45, send=.5)
add(SFX, .02, reverse_swell(.25, 3000), .05)
# heartbeat pulse under the mirror + drum
for b in np.arange(.12, 3.6, 1.0):
    add(MUS, b, kick(.5), .5); add(MUS, b + .22, kick(.35), .35)
# drum mechanism
for d in [1.72, 2.3, 2.85, 3.38]:
    add(SFX, d + .05, whoosh(.38, 700, 3200, .0, .0), .22); add(SFX, d + .2, tick(1900), .4, send=.2)
# clock ticks: tension under the search
for i, b in enumerate(np.arange(3.6, 6.55, .25)):
    add(MUS, b, tick(3400 if i % 2 else 2700, .55 + .45 * (b - 3.6) / 3), .17, send=.15)
for b in np.arange(3.6, 6.6, .5): add(MUS, b, kick(.6), .55)
# whooshes on scene changes (dark)
for at, dur, f0, f1, p0, p1, g in [(1.55, .5, 400, 4200, 0, 0, .5), (3.35, .5, 400, 4200, 0, 0, .45), (3.55, .45, 4200, 600, .8, 0, .45),
                                   (5.25, .55, 300, 2500, 0, 0, .35), (9.3, .5, 5000, 500, 0, -.9, .7), (9.52, .45, 4800, 600, .9, 0, .6), (10.65, .45, 500, 4000, 0, 0, .45)]:
    add(SFX, at, whoosh(dur, f0, f1, p0, p1), g, send=.3)
# typing + enter
for k, at in enumerate(np.linspace(4.47, 5.02, 9)): add(SFX, at + rng.uniform(-.015, .015), keyclick(), .5, send=.08)
add(SFX, 5.3, keyclick(True), .8, send=.15)
# loading hum 5.55–6.0
n2 = int(.5 * SR); tt = np.arange(n2) / SR
add(SFX, 5.55, pan(np.sin(2 * np.pi * 880 * tt) * np.sin(np.pi * tt / .5) * .15 * (1 + .5 * np.sin(2 * np.pi * 12 * tt)), 0), .3)
# "nothing." — boom, then near silence; shatter at 7.0
add(SFX, 6.6, impact(55, 26, 2.4, .5), .85, send=.9)
n3 = int(.6 * SR); gl = np.zeros(n3)
for k in range(70):
    i = int(rng.uniform(0, .45) * SR); m = int(.02 * SR)
    if i + m < n3: gl[i:i + m] += filt(noise(m), 'highpass', rng.uniform(4000, 9000)) * env(m, .0003, .004) * rng.uniform(.3, 1)
add(SFX, 6.98, np.stack([gl, np.roll(gl, 90)], 1), .55, send=.5)
add(SFX, 6.95, reverse_swell(.28, 2500), .3)
# card flood: flutters as cards pass the camera, panned by side
for k in range(16):
    at = 7.3 + k * .13 + rng.uniform(-.04, .04); p = rng.uniform(-.9, .9)
    add(SFX, at, whoosh(rng.uniform(.25, .4), rng.uniform(1500, 3000), rng.uniform(400, 900), p, p * 1.1), .18 + .1 * rng.random(), send=.25)
add(SFX, 7.8, braam(38, 2.0), .55, send=.7)
add(SFX, 10.2, braam(41, 1.6), .7, send=.8)
add(SFX, 10.15, reverse_swell(.1, 2000), .2)
# riser → light burst
add(SFX, 10.75, riser(.62, 200, 4200), .55, send=.3)
add(SFX, 11.35, impact(80, 38, 1.8, 1.0), .8, send=.8)
add(SFX, 11.35, chime(86, 3.0), .22, send=1.0)
add(SFX, 11.35, crash(2.6), .35, send=.6)

# ======================= ACT III / IV — light, 120 BPM =======================
BEAT = .5; START = 12.0; END = 21.85
PROG = [(START, [62, 66, 69, 74], 50), (14.0, [61, 64, 69, 73], 45), (16.0, [62, 66, 71, 74], 47), (18.0, [62, 67, 71, 74], 43), (20.0, [62, 66, 69, 74], 50)]
kicks = [b for b in np.arange(START, END - .01, BEAT)]
duck = np.ones(N)
for b in kicks:
    i = int(b * SR); m = min(N - i, int(.4 * SR)); tt = np.arange(m) / SR; duck[i:i + m] = np.minimum(duck[i:i + m], 1 - .65 * np.exp(-tt / .11))
for b in kicks: add(MUS, b, kick(1.0), 1.05)
for b in np.arange(START + BEAT, END, 2 * BEAT): add(MUS, b, clap(), .6, send=.35)
for b in np.arange(START + BEAT / 2, END, BEAT): add(MUS, b, hat(False, .3), .28)
for b in np.arange(START + 14 * BEAT, END, 4 * BEAT): add(MUS, b + BEAT / 2, hat(True, -.2), .18)
for b in np.arange(START, END, BEAT / 4): add(MUS, b, shaker(-.35), .1 * (1 if (round(b / (BEAT / 4)) % 2) else .6))
for k, (a, notes, root) in enumerate(PROG):
    b = PROG[k + 1][0] if k + 1 < len(PROG) else END
    dur = b - a
    pad = supersaw([hz(m) for m in notes], dur + .3, voices=5, det=16, cutoff=2200)
    e = np.minimum(1, np.arange(len(pad)) / (.03 * SR)) * np.clip((dur + .3 - np.arange(len(pad)) / SR) / .3, 0, 1)
    pad *= e[:, None]
    add(MUS, a, pad * duck[int(a * SR):int(a * SR) + len(pad)][:, None] if int(a * SR) + len(pad) <= N else pad, .6, send=.35)
    for bb in np.arange(a, b - .01, BEAT / 2):  # offbeat pumping sub bass
        if round((bb - a) / (BEAT / 2)) % 2 == 1:
            n4 = int(.24 * SR); tt = np.arange(n4) / SR
            y = (np.sin(2 * np.pi * hz(root - 12) * tt) + .25 * np.sin(4 * np.pi * hz(root - 12) * tt)) * env(n4, .004, .09, .06)
            add(MUS, bb, np.stack([y, y], 1), .75)
    if a >= 14.0:  # pluck arp, 16ths
        arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12, notes[1] + 12]
        for j, bb in enumerate(np.arange(a, b - .01, BEAT / 2)):
            p = pluck(hz(arp[j % len(arp)]), .3); add(MUS, bb, pan(p, .35 if j % 2 else -.35), .13, send=.5)
# section whooshes (light)
for at, dur, f0, f1, p0, p1, g in [(11.95, .5, 400, 4500, 0, 0, .5), (13.58, .45, 5000, 500, 0, -.9, .65), (13.7, .42, 4800, 600, .9, 0, .5),
                                   (17.68, .45, 500, 4200, 0, 0, .5), (17.95, .42, 4800, 600, .9, 0, .4), (19.72, .45, 500, 4500, 0, 0, .5),
                                   (19.95, .45, 600, 3800, 0, 0, .35), (20.82, .5, 700, 3000, 0, 0, .35)]:
    add(SFX, at, whoosh(dur, f0, f1, p0, p1), g, send=.3)
# list items: swoosh-in from the right + tick + check swipe
for it in [14.5, 15.0, 15.5, 16.0, 16.5]:
    add(SFX, it - .03, whoosh(.3, 4000, 900, .8, .1), .3)
    add(SFX, it + .14, tick(2200), .35, send=.3)
add(SFX, 17.2, impact(70, 36, 1.4, .8), .55, send=.6); add(SFX, 17.2, crash(2.0), .3, send=.5)
# typing (payoff search) + enter + card
for at in np.linspace(20.22, 20.68, 9): add(SFX, at + rng.uniform(-.012, .012), keyclick(), .45, send=.08)
add(SFX, 20.78, keyclick(True), .7, send=.15)
add(SFX, 21.12, chime(81, 1.4), .12, send=.6)
# fill into the logo: snare-ish roll + riser, then a breath
for k, b in enumerate(np.arange(21.35, 21.85, BEAT / 4)): add(MUS, b, clap(), .12 + .06 * k, send=.3)
add(SFX, 21.3, riser(.58, 300, 5000), .4)
# logo: blob flight whoosh → hit + chime + resolving chord
add(SFX, 21.88, whoosh(.45, 3000, 400, .8, 0), .45, send=.3)
add(SFX, 22.32, impact(75, 36, 1.8, .9), .75, send=.7)
add(SFX, 22.32, chime(74, 2.8), .28, send=.9)
n5 = int(2.4 * SR)
res = supersaw([hz(50), hz(62), hz(66), hz(69), hz(74), hz(78)], 2.4, voices=5, det=12, cutoff=1800)
res *= (np.minimum(1, np.arange(n5) / (.02 * SR)) * np.exp(-np.arange(n5) / SR / 1.6) * np.clip((24.45 - 22.32 - np.arange(n5) / SR) / .25, 0, 1))[:, None]
add(MUS, 22.32, res, .3, send=.6)
for b in np.arange(22.82, 24.3, BEAT):
    add(MUS, b, kick(.5), .35); add(MUS, b + BEAT / 2, hat(False, .3), .15)
add(SFX, 22.55, whoosh(.5, 800, 3500, -.6, .4), .3)   # wordmark reveal
add(SFX, 22.9, whoosh(.35, 900, 3000, 0, 0), .18)
add(SFX, 23.72, keyclick(True), .8, send=.2); add(SFX, 23.74, chime(86, 1.2), .16, send=.6)

# ======================= mix & master =======================
# reverb: stereo exponential-noise IR with darkening tail
n6 = int(2.4 * SR); tt = np.arange(n6) / SR
irL = noise(n6) * np.exp(-tt / .55); irR = noise(n6) * np.exp(-tt / .55)
irL = filt(irL, 'lowpass', 6000); irR = filt(irR, 'lowpass', 6000); irL[:int(.012 * SR)] = 0; irR[:int(.017 * SR)] = 0
wet = np.stack([signal.fftconvolve(VERB[:, 0], irL)[:N], signal.fftconvolve(VERB[:, 1], irR)[:N]], 1)
wet = filt(wet.T, 'highpass', 180).T
mix = MUS + SFX + wet * .09
mix = filt(mix.T, 'highpass', 28).T
# glue compression (RMS follower) + soft clip
rms = np.sqrt(signal.sosfilt(sos('lowpass', 8), (mix ** 2).mean(1)) + 1e-9)
peak = np.percentile(rms, 99)
gain = np.minimum(1, (rms / (.55 * peak)) ** (-.35))
mix *= gain[:, None]
mix /= np.abs(mix).max() / .95
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix *= np.clip((T - t_all) / .35, 0, 1)[:, None]      # last 0.5 s falls away
mix *= np.clip(t_all / .01, 0, 1)[:, None]
import wave
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open('out/sound-v3-raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote out/sound-v3-raw.wav')

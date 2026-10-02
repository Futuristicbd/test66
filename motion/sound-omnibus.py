"""Score + sound design for the Corporate Omnibus coverage film -> out/sound-omnibus-raw.wav (48 kHz stereo, 44.6 s).
Run with SFX_T=44.6. Uplifting 120 BPM bed in D (Dmaj9 – Bm7 – Gmaj9 – A): a soft intro, the beat lands with the
title, a riser into "40+", a lighter half-time for the honours, full energy for the networking, a riser and hit as
the group photo fills the frame, a breakdown for the brand line and a resolve on the FuturisticBD logo.
Every camera flash in the picture has a shutter; every print that flies in has a whoosh."""
import os; os.environ.setdefault('SFX_T', '44.6')
from sfxlib import *
import re

BEAT = .5
FL = [float(x) for x in re.search(r'const FL=\[([^\]]+)\]', open('clips/omnibus-coverage.html').read()).group(1).split(',')]

def shutter(g=1.0):
    n = int(.16 * SR); y = np.zeros(n)
    for off, f, a in [(0, [1500, 6500], 1.0), (.055, [900, 5000], .7)]:
        i = int(off * SR); m = int(.05 * SR)
        y[i:i + m] += filt(noise(m), 'bandpass', f) * env(m, .0003, .008) * a
    t = np.arange(n) / SR; y += np.sin(2 * np.pi * 180 * t) * env(n, .001, .015) * .35
    return pan(y * g, rng.uniform(-.3, .3))
def soft_hit(g=1.0): return impact(90, 45, 1.0, .25) * g
def pop(f0=900, f1=420, g=1.0):
    n = int(.12 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 40)) / SR) * env(n, .001, .04); return pan(y * g, 0)
def sparkle(dur=.8, n_=26, lo=3500, hi=9000):
    n = int(dur * SR); L = np.zeros(n); R = np.zeros(n)
    for k in range(n_):
        i = int(rng.uniform(0, dur * .7) * SR); m = int(.18 * SR)
        if i + m >= n: continue
        tt = np.arange(m) / SR; s = np.sin(2 * np.pi * rng.uniform(lo, hi) * tt) * np.exp(-tt / rng.uniform(.03, .08)) * rng.uniform(.3, 1)
        p = rng.uniform(-.8, .8); L[i:i + m] += s * np.cos((p + 1) * np.pi / 4); R[i:i + m] += s * np.sin((p + 1) * np.pi / 4)
    return np.stack([L, R], 1)

CH = [[62, 66, 69, 73, 76], [59, 62, 66, 69], [55, 59, 62, 66, 69], [57, 61, 64, 69]]
RT = [38, 35, 31, 33]
chord_at = lambda t: int(t // 2) % 4

KICK = [(4.3, 12.8), (13.3, 23.6), (29.0, 35.2), (36.25, 38.0)]
HALF = [(23.8, 29.0)]
CLAP = [(6.3, 12.8), (15.3, 23.6), (29.0, 35.2), (36.25, 38.0)]
HATS = [(2.0, 38.0)]
inwin = lambda b, W: any(a <= b < c for a, c in W)

duck = np.ones(N)
def side(b, d=.55):
    i = int(b * SR); m = min(N - i, int(.4 * SR)); tt = np.arange(m) / SR
    duck[i:i + m] = np.minimum(duck[i:i + m], 1 - d * np.exp(-tt / .12))
for b in np.arange(0, T, BEAT):
    if inwin(b, KICK): add(MUS, b, kick(1.0), .85); side(b)
    if inwin(b, HALF) and round(b / BEAT) % 2 == 0: add(MUS, b, kick(.7), .6); side(b, .35)
    if inwin(b, HALF) and round(b / BEAT) % 4 == 2: add(MUS, b, clap(), .3, send=.5)
    if inwin(b, CLAP) and round(b / BEAT) % 2 == 1: add(MUS, b, clap(), .45, send=.3)
    if inwin(b, HATS): add(MUS, b + BEAT / 2, hat(False, .3), .2 if b < 4.3 else .28)
for b in np.arange(4.3, 38.0, BEAT / 4):
    if not inwin(b, HALF): add(MUS, b, shaker(-.35), .08 * (1 if round(b / (BEAT / 4)) % 2 else .55))

for bar in range(23):
    a = bar * 2.0
    if a >= 40.8: break
    notes = CH[bar % 4]; dur = 2.3
    cut = 1300 if a < 4 else (3000 if 28 <= a < 38 else 2300)
    pad = supersaw([hz(m) for m in notes], dur, voices=5, det=14, cutoff=cut)
    e = np.minimum(1, np.arange(len(pad)) / (.06 * SR)) * np.clip((dur - np.arange(len(pad)) / SR) / .3, 0, 1)
    i = int(a * SR); pad *= e[:, None]; seg = duck[i:i + len(pad)]
    if len(seg) < len(pad): seg = np.pad(seg, (0, len(pad) - len(seg)), constant_values=1)
    add(MUS, a, pad * seg[:, None], .45 if a >= 4 else .34, send=.35)
for b in np.arange(4.3, 38.0, BEAT / 2):
    if round(b / (BEAT / 2)) % 2 == 1 and inwin(b, KICK):
        n2 = int(.22 * SR); tt = np.arange(n2) / SR; f = hz(RT[chord_at(b)])
        y = (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)) * env(n2, .004, .08, .06)
        add(MUS, b, np.stack([y, y], 1), .6)
for b in np.arange(0.0, 40.8, BEAT / 2):
    notes = CH[chord_at(b)]; j = int(round(b / (BEAT / 2)))
    seq = [notes[0] + 12, notes[2] + 12, notes[1] + 12, notes[-1] + 12]
    g = .15 if b < 4.3 else (.18 if inwin(b, HALF) or b >= 38 else .1)
    add(MUS, b, pan(pluck(hz(seq[j % 4]), .32), .35 if j % 2 else -.35), g, send=.5)

# ---------------- sound design, locked to picture ----------------
for f in FL: add(SFX, f - .01, shutter(), .55, send=.25)
# S1
add(SFX, 0.0, soft_hit(.35), 1, send=.5); add(SFX, .35, whoosh(.5, 900, 3000, .4, 0), .16)
add(SFX, 1.3, whoosh(.7, 400, 3600, 0, 0), .3, send=.3); add(SFX, 1.45, sparkle(1.0, 16), .08, send=.6)
add(SFX, 3.0, riser(1.25, 300, 5200), .32); add(SFX, 3.75, whoosh(.5, 3500, 700, 0, 0), .25)
# S2 title
add(SFX, 4.3, braam(38, 2.4), .3, send=.4); add(SFX, 4.3, crash(2.2), .25, send=.4)
for k in range(4): add(SFX, 4.15 + k * .12, whoosh(.45, 600, 3200, [-.8, .8, .8, -.8][k], 0), .14)
add(SFX, 8.15, whoosh(.6, 3200, 600, 0, 0), .3, send=.2)
# S3
add(SFX, 8.55, whoosh(.7, 500, 2800, .7, .2), .3)
add(SFX, 10.5, reverse_swell(.4, 3000), .3); add(SFX, 10.9, soft_hit(.6), 1, send=.5)
add(SFX, 11.3, whoosh(.6, 900, 3800, 0, 0), .2)
add(SFX, 12.4, riser(.9, 400, 5200), .32); add(SFX, 13.0, whoosh(.5, 3200, 700, 0, 0), .3)
# S4 counter
tp = 13.6
while tp < 14.85:
    u = (tp - 13.6) / 1.25; add(SFX, tp, tick(1500 + 2200 * u, .5 + .5 * u), .18, send=.2); tp += .09 - .03 * u
add(SFX, 14.85, pop(800, 360, 1.3), .6); add(SFX, 14.85, sparkle(.9, 30), .14, send=.6)
for a in [14.0, 14.7, 15.4]: add(SFX, a, whoosh(.45, 700, 3200, .7, 0), .22)
add(SFX, 18.2, whoosh(.6, 3200, 600, 0, 0), .3)
# S5
for k, a in enumerate([19.0, 19.5, 20.0]): add(SFX, a, whoosh(.5, 600, 3000, .9, -.2), .24)
add(SFX, 23.45, whoosh(.6, 3200, 600, 0, 0), .3)
# S6 honours
add(SFX, 24.05, soft_hit(.7), 1, send=.6); add(SFX, 24.1, chime(74, 2.6), .16, send=.8)
add(SFX, 24.6, sparkle(2.0, 40, 4000, 10000), .1, send=.7); add(SFX, 25.4, whoosh(.5, 700, 3000, .8, .2), .2)
add(SFX, 28.5, whoosh(.6, 3200, 600, 0, 0), .3); add(SFX, 28.4, riser(.6, 500, 4000), .22)
# S7
for k, a in enumerate([29.2, 29.8, 30.4]): add(SFX, a, whoosh(.45, 700, 3200, [.8, .6, 0][k], 0), .22)
add(SFX, 33.2, whoosh(.6, 3200, 600, 0, 0), .3)
# S8 group photo fills the frame
add(SFX, 33.6, whoosh(.6, 500, 2600, 0, 0), .25)
add(SFX, 34.2, riser(1.15, 300, 5600), .38); add(SFX, 35.35, whoosh(.9, 300, 3000, 0, 0), .35, send=.3)
add(SFX, 36.25, braam(38, 2.2), .26, send=.4); add(SFX, 36.25, crash(2.4), .26, send=.4)
add(SFX, 36.45, whoosh(.5, 900, 3000, -.5, 0), .14); add(SFX, 36.85, whoosh(.5, 900, 3000, -.5, 0), .14)
add(SFX, 37.95, whoosh(.8, 3000, 500, 0, 0), .3, send=.3)
# S9 brand
add(SFX, 38.5, whoosh(.5, 900, 3000, .3, 0), .14); add(SFX, 39.25, whoosh(.7, 400, 3600, 0, 0), .26, send=.3)
add(SFX, 39.3, sparkle(.9, 18), .08, send=.6); add(SFX, 40.45, reverse_swell(.45, 3000), .28)
add(SFX, 40.85, soft_hit(.8), 1, send=.7); add(SFX, 40.85, chime(74, 3.0), .22, send=.9)
res = supersaw([hz(50), hz(62), hz(66), hz(69), hz(73)], 3.6, voices=5, det=12, cutoff=2200)
n5 = len(res); res *= (np.minimum(1, np.arange(n5) / (.03 * SR)) * np.exp(-np.arange(n5) / SR / 2.2))[:, None]
add(MUS, 40.85, res, .4, send=.6)
add(SFX, 41.2, whoosh(.6, 700, 3000, -.6, .6), .18); add(SFX, 41.9, pop(900, 600, .8), .35)
add(SFX, 42.3, sparkle(.8, 14), .07, send=.6)

# ---------------- mix & master ----------------
n6 = int(2.2 * SR); tt = np.arange(n6) / SR
irL = filt(noise(n6) * np.exp(-tt / .5), 'lowpass', 7000); irR = filt(noise(n6) * np.exp(-tt / .5), 'lowpass', 7000)
irL[:int(.014 * SR)] = 0; irR[:int(.019 * SR)] = 0
wet = np.stack([signal.fftconvolve(VERB[:, 0], irL)[:N], signal.fftconvolve(VERB[:, 1], irR)[:N]], 1)
wet = filt(wet.T, 'highpass', 200).T
mix = MUS * .9 + SFX + wet * .08
mix = filt(mix.T, 'highpass', 30).T
rms = np.sqrt(signal.sosfilt(sos('lowpass', 8), (mix ** 2).mean(1)) + 1e-9)
gain = np.minimum(1, (rms / (.55 * np.percentile(rms, 99))) ** (-.3)); mix *= gain[:, None]
mix /= np.abs(mix).max() / .95; mix = np.tanh(mix * 1.25) / np.tanh(1.25)
mix *= np.clip((T - t_all) / 1.0, 0, 1)[:, None]; mix *= np.clip(t_all / .01, 0, 1)[:, None]
import wave
with wave.open('out/sound-omnibus-raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('wrote out/sound-omnibus-raw.wav')

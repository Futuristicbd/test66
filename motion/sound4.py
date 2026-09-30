"""Score + sound design for the v4 reel -> out/sound-v4-raw.wav (48 kHz stereo, 25 s).
Bright tech-launch bed at 120 BPM in E (Emaj9 – C#m7 – Amaj9 – B), in the spirit of the LangEase film:
soft intro, beat enters with the folder, full energy through the phone tunnel, a build under the
progress bar that lands on "Live.", a lighter breakdown for the booking moment, and a resolve on the logo.
Every visual move has its sound: soft whooshes, pops, UI clicks, progress ticks, sparkles, chimes."""
from sfxlib import *

BEAT = .5
def pop(f0=900, f1=420, g=1.0):
    n = int(.12 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 40)) / SR) * env(n, .001, .04)
    return pan(y * g, 0)
def uiclick(g=1.0):
    n = int(.04 * SR); t = np.arange(n) / SR
    y = filt(noise(n), 'bandpass', [2500, 7000]) * env(n, .0003, .003) * .8 + np.sin(2 * np.pi * 1350 * t) * env(n, .0005, .01) * .5
    return pan(y * g, 0)
def sparkle(dur=.8, n_=26, lo=3500, hi=9000):
    n = int(dur * SR); L = np.zeros(n); R = np.zeros(n)
    for k in range(n_):
        i = int(rng.uniform(0, dur * .7) * SR); m = int(.18 * SR)
        if i + m >= n: continue
        tt = np.arange(m) / SR; f = rng.uniform(lo, hi)
        s = np.sin(2 * np.pi * f * tt) * np.exp(-tt / rng.uniform(.03, .08)) * rng.uniform(.3, 1)
        p = rng.uniform(-.8, .8); L[i:i + m] += s * np.cos((p + 1) * np.pi / 4); R[i:i + m] += s * np.sin((p + 1) * np.pi / 4)
    return np.stack([L, R], 1)
def soft_hit(g=1.0):
    return impact(90, 45, 1.0, .25) * g
def air_bed(dur, f0=600, f1=2400):
    n = int(dur * SR); y = sweep_noise(dur, f0, f1, .9, 1.0) * np.sin(np.pi * np.arange(n) / n) ** .8
    return np.stack([y, np.roll(y, 480)], 1)

CH = [[64, 68, 71, 75], [61, 64, 68, 71], [57, 61, 64, 68, 71], [59, 63, 66, 71]]
RT = [40, 37, 33, 35]
chord_at = lambda t: int(t // 2) % 4

# ---------------- structure ----------------
KICK = [(3.0, 11.5), (12.35, 16.75), (20.0, 24.0)]           # four-on-the-floor windows
CLAP = [(4.0, 11.5), (12.35, 16.75), (20.0, 23.5)]
HATS = [(1.0, 24.0)]
inwin = lambda b, W: any(a <= b < c for a, c in W)

duck = np.ones(N)
for b in np.arange(0, T, BEAT):
    if inwin(b, KICK):
        g = .55 if b >= 22.0 else 1.0
        add(MUS, b, kick(1.0), .85 * g)
        i = int(b * SR); m = min(N - i, int(.4 * SR)); tt = np.arange(m) / SR
        duck[i:i + m] = np.minimum(duck[i:i + m], 1 - .55 * np.exp(-tt / .12))
    if inwin(b, CLAP) and round(b / BEAT) % 2 == 1: add(MUS, b, clap(), .5, send=.3)
    if inwin(b, HATS): add(MUS, b + BEAT / 2, hat(False, .3), .22 if b < 3 else .3)
for b in np.arange(3.0, 24.0, BEAT / 4):
    if not (16.75 <= b < 19.9): add(MUS, b, shaker(-.35), .09 * (1 if round(b / (BEAT / 4)) % 2 else .55))

# pads (sidechained), one chord per bar, filter opening across the intro and the build
for bar in range(13):
    a = bar * 2.0
    if a >= 24.4: break
    notes = CH[bar % 4]; dur = 2.3
    cut = 1500 if a < 3 else (2600 if not (10 <= a < 12.3) else 3400)
    pad = supersaw([hz(m) for m in notes], dur, voices=5, det=14, cutoff=cut)
    e = np.minimum(1, np.arange(len(pad)) / (.06 * SR)) * np.clip((dur - np.arange(len(pad)) / SR) / .3, 0, 1)
    i = int(a * SR); pad *= e[:, None]; seg = duck[i:i + len(pad)]
    if len(seg) < len(pad): seg = np.pad(seg, (0, len(pad) - len(seg)), constant_values=1)
    add(MUS, a, pad * seg[:, None], .5 if a >= 3 else .38, send=.35)
# sub bass on the offbeats while the beat plays
for b in np.arange(3.0, 24.0, BEAT / 2):
    if round(b / (BEAT / 2)) % 2 == 1 and (inwin(b, KICK)):
        n2 = int(.22 * SR); tt = np.arange(n2) / SR; f = hz(RT[chord_at(b)] - 12 + 12)
        y = (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)) * env(n2, .004, .08, .06)
        add(MUS, b, np.stack([y, y], 1), .6)
# pluck arpeggio, 8ths (16ths in the tunnel), everywhere except the very end
for b in np.arange(0.0, 24.0, BEAT / 2):
    notes = CH[chord_at(b)]; j = int(round(b / (BEAT / 2)))
    seq = [notes[0] + 12, notes[2] + 12, notes[1] + 12, notes[-1] + 12]
    g = .14 if b < 3 else (.1 if not (16.75 <= b < 19.9) else .19)
    add(MUS, b, pan(pluck(hz(seq[j % 4]), .32), .35 if j % 2 else -.35), g, send=.5)
    if 6.25 <= b < 9.7: add(MUS, b + BEAT / 4, pan(pluck(hz(seq[(j + 2) % 4] + 12), .2, .8), .5 if j % 2 else -.5), .06, send=.4)

# half-time pulse through the booking breakdown
for b in np.arange(16.75, 19.9, 2 * BEAT):
    add(MUS, b, kick(.6), .5); add(MUS, b + BEAT, clap(), .22, send=.4)

# ---------------- sound design, locked to picture ----------------
# S1  Turn your expertise → Influence.
add(SFX, 0.0, soft_hit(.4), 1, send=.5); add(SFX, 0.05, whoosh(.45, 900, 3000, .5, 0), .22); add(SFX, .38, whoosh(.45, 900, 3000, .5, 0), .14)
add(SFX, 1.25, whoosh(.6, 400, 3500, 0, 0), .35, send=.3); add(SFX, 1.42, soft_hit(.45), 1, send=.5)
add(SFX, 1.42, sparkle(1.0, 18, 4000, 9000), .1, send=.6)
add(SFX, 2.85, whoosh(.45, 3500, 700, 0, 0), .3)
# S2  folder pops, grab, drag, drop into the studio
add(SFX, 3.1, whoosh(.4, 900, 3200, .6, 0), .15); add(SFX, 3.75, whoosh(.4, 900, 3200, .6, 0), .15)
add(SFX, 3.42, pop(1100, 480), .5, send=.3)
add(SFX, 4.55, uiclick(), .6); add(SFX, 4.7, whoosh(.7, 2200, 500, 0, 0), .3, send=.2)
add(SFX, 4.75, whoosh(.6, 300, 1600, 0, 0), .2)
add(SFX, 5.4, pop(520, 220, 1.2), .6, send=.4); add(SFX, 5.42, uiclick(.8), .5)
add(SFX, 5.45, chime(83, 1.4), .12, send=.7)
add(SFX, 6.05, whoosh(.6, 500, 4200, 0, 0), .4, send=.3)
# S3  tunnel: rushing air, word ticks, All done
add(SFX, 6.2, air_bed(3.6, 500, 2600), .12)
for k, a in enumerate([6.75, 7.2, 7.65, 8.1]):
    add(SFX, a, whoosh(.35, 1400, 3600, .5, -.2), .14); add(SFX, a + .05, tick(1800 + 250 * k, .7), .28, send=.3)
add(SFX, 8.72, soft_hit(.5), 1, send=.5); add(SFX, 8.72, sparkle(.8, 16), .08, send=.5)
add(SFX, 9.5, riser(.35, 600, 5000), .3)
# S4  ribbon, progress ticks accelerating, drums drop out, "Live." lands
add(SFX, 9.75, whoosh(.8, 300, 4200, -.8, .5), .55, send=.3)
tp = 10.65
while tp < 11.9:
    u = (tp - 10.65) / 1.25
    add(SFX, tp, tick(1500 + 2200 * u, .5 + .5 * u), .2, send=.2); tp += .11 - .07 * u
add(SFX, 11.1, riser(1.2, 300, 5200), .38)
add(SFX, 11.95, whoosh(.35, 2500, 700, 0, 0), .25)
add(SFX, 12.32, pop(700, 300, 1.3), .7); add(SFX, 12.35, soft_hit(.8), 1, send=.6)
add(SFX, 12.36, sparkle(1.2, 60, 3000, 10000), .22, send=.6)
add(SFX, 12.4, chime(76, 2.0), .2, send=.8); add(SFX, 12.35, crash(2.0), .26, send=.4)
# S5  carousel, calendar, click, scatter, Seen everywhere
add(SFX, 13.3, whoosh(.9, 700, 2600, .7, -.7), .25)
for k in range(3): add(SFX, 13.5 + k * .33, whoosh(.3, 2600, 900, .6, -.6), .1)
add(SFX, 14.2, whoosh(.7, 500, 3000, 0, 0), .32, send=.2)
add(SFX, 15.28, uiclick(), .6); add(SFX, 15.32, pop(900, 600, .7), .35)
add(SFX, 15.75, whoosh(.6, 3200, 600, 0, 0), .35, send=.3)
for k in range(6): add(SFX, 15.85 + k * .05, whoosh(.35, rng.uniform(1500, 3000), 800, rng.uniform(-.9, .9), 0), .08)
add(SFX, 16.0, sparkle(.9, 22), .12, send=.6)
add(SFX, 16.55, whoosh(.4, 900, 3500, 0, 0), .25)
# S6  we come to you — row, button, click, booked, collapse to sparkle
add(SFX, 16.9, whoosh(.5, 800, 2600, .6, 0), .2)
add(SFX, 17.25, pop(1000, 700, .8), .35); add(SFX, 17.65, whoosh(.5, 1200, 2800, .4, 0), .18)
add(SFX, 18.34, uiclick(1.2), .75)
add(SFX, 18.4, chime(83, .9) + np.pad(chime(88, .9)[:int(.8 * SR)], ((int(.1 * SR), 0), (0, 0)))[:int(.9 * SR)], .16, send=.6)
add(SFX, 19.15, whoosh(.4, 2800, 900, 0, 0), .2); add(SFX, 19.3, sparkle(.7, 20, 5000, 10000), .18, send=.6)
add(SFX, 19.3, pop(1400, 900, .6), .35)
# S7  star trail, Plan. Shoot. Grow.
add(SFX, 19.9, whoosh(.8, 900, 5200, -.4, .6), .35, send=.4); add(SFX, 19.95, sparkle(.8, 30, 4000, 10000), .1, send=.6)
for k, a in enumerate([20.45, 20.8, 21.15]):
    add(SFX, a, pluck(hz([76, 80, 83][k]), .6) [:, None].repeat(2, 1) * .9, .22, send=.5)
    add(SFX, a, whoosh(.3, 1400, 3200, .5, 0), .12)
add(SFX, 21.25, sparkle(.9, 16), .1, send=.6)
# S8  star → flame, wordmark, CTA, tap
add(SFX, 22.05, whoosh(.5, 3500, 600, 0, 0), .3, send=.3)
add(SFX, 22.25, soft_hit(.7), 1, send=.7); add(SFX, 22.25, chime(76, 2.6), .22, send=.9)
res = supersaw([hz(52), hz(64), hz(68), hz(71), hz(75)], 2.8, voices=5, det=12, cutoff=2200)
n5 = len(res); res *= (np.minimum(1, np.arange(n5) / (.03 * SR)) * np.exp(-np.arange(n5) / SR / 1.8))[:, None]
add(MUS, 22.25, res, .38, send=.6)
add(SFX, 22.65, whoosh(.7, 700, 3000, -.7, .6), .25)
add(SFX, 23.3, pop(900, 600, .7), .3); add(SFX, 23.5, whoosh(.4, 1200, 2800, 0, 0), .12)
add(SFX, 23.94, uiclick(1.2), .7); add(SFX, 23.97, chime(88, 1.2), .14, send=.6)

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
mix *= np.clip((T - t_all) / .6, 0, 1)[:, None]; mix *= np.clip(t_all / .01, 0, 1)[:, None]
import wave
with wave.open('out/sound-v4-raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('wrote out/sound-v4-raw.wav')

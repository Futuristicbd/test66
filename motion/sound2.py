"""Sound design for the NEXT v2 reel -> out/sound-v2.wav (48 kHz stereo, 24 s).
110 BPM pulse bed, typing ticks, drum ticks, whooshes on every scene change, pops on the avatars,
plucks on each ring bounce, shutter at 13.6, impact at 17.6, riser 20.4 -> logo hit at 22.0, music out for the last 0.5 s."""
import numpy as np, wave
SR, T = 48000, 24.0
N = int(SR * T); t_all = np.arange(N) / SR
rng = np.random.default_rng(11)
fx = np.zeros(N); bed = np.zeros(N)

def add(buf, at, sig, g=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if 0 <= i < N: buf[i:j] += g * sig[:j - i]
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, k):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y
def tone(f, dur, a=.002, d=.2):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * env(n, a, d)

# --- bed: 110 BPM kick + hat + pad, lifts in energy after the blue panel ---
beat = 60 / 110
for k in range(int(23.4 / beat) + 1):
    at = 0.02 + k * beat
    n = int(.3 * SR); t = np.arange(n) / SR
    add(bed, at, np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-t * 32)) / SR) * env(n, .002, .11), .5)
    n2 = int(.04 * SR); hz = rng.standard_normal(n2); hz = hz - lp(hz, .4)
    add(bed, at + beat / 2, hz * env(n2, .0005, .01), .07 if at < 12.4 else .12)
chord = [146.83, 220.0, 293.66, 369.99]
pad = sum(np.sin(2 * np.pi * f * t_all + i) for i, f in enumerate(chord)) / 4
bed += pad * .055 * np.clip(t_all / 1.2, 0, 1) * (.85 + .15 * np.sin(2 * np.pi * t_all / 3.3))
bed *= np.clip((23.5 - t_all) / .1, 0, 1)   # music out for the last 0.5 s

# --- typing ticks ---
for a, b in [(.45, 1.5), (6.45, 7.05), (8.2, 8.7), (11.0, 12.05)]:
    x = a
    while x < b:
        n = int(.02 * SR); s = rng.standard_normal(n); add(fx, x, (s - lp(s, .5)) * env(n, .0003, .004), .18)
        x += .045 + rng.random() * .03

# --- whooshes on scene changes ---
for m in [1.95, 4.05, 5.7, 7.95, 10.35, 12.42, 14.6, 16.85, 18.3, 20.15, 20.85, 21.45]:
    n = int(.5 * SR); t = np.arange(n) / SR; s = rng.standard_normal(n)
    add(fx, m - .1, (s - lp(s, .12)) * np.sin(np.pi * t / .5) ** 2, .13)

# --- drum ticks, avatar pops, ring plucks, list clicks ---
for d in [2.15, 2.9, 3.55]: add(fx, d + .12, tone(1800, .05, .0005, .012), .3)
for i, p in enumerate([4.3, 4.4, 4.5, 4.6]): add(fx, p, tone(520 + 90 * i, .15, .001, .05), .25)
for i, p in enumerate([9.25, 9.7, 10.15]): add(fx, p, tone([659.3, 784, 987.8][i], .5, .001, .16) + .4 * tone([1318.5, 1568, 1975.5][i], .5, .001, .1), .2)
for p in [15.4, 15.9, 16.4]: add(fx, p, tone(1400, .06, .0005, .015), .25)
add(fx, 7.35, tone(1200, .08, .0005, .02), .22)
add(fx, 12.05, tone(1046.5, .6, .002, .2), .15)

# --- shutter at 13.6 ---
for off, g in [(0, .55), (.07, .35)]:
    n = int(.06 * SR); s = rng.standard_normal(n); add(fx, 13.6 + off, (s - lp(s, .3)) * env(n, .0005, .015), g)
add(fx, 13.6, tone(140, .12, .001, .03), .3)

# --- impact on "isn't enough." ---
n = int(.8 * SR); t = np.arange(n) / SR
add(fx, 17.6, np.sin(2 * np.pi * np.cumsum(42 + 50 * np.exp(-t * 14)) / SR) * env(n, .002, .25), .55)

# --- riser into the logo, hit + chime at 22.0 ---
n = int(1.6 * SR); t = np.arange(n) / SR; u = t / 1.6; s = rng.standard_normal(n)
add(fx, 20.4, ((s - lp(s, .1)) * .5 + np.sin(2 * np.pi * np.cumsum(260 + 1000 * u ** 2) / SR) * .35) * u ** 2.2, .16)
n = int(1.4 * SR); t = np.arange(n) / SR
add(fx, 22.0, np.sin(2 * np.pi * np.cumsum(45 + 40 * np.exp(-t * 12)) / SR) * env(n, .002, .35), .6)
add(fx, 22.0, sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(1318.5, 1, .6), (1975.5, .5, .4), (987.8, .5, .7)]), .12)

out = fx + bed
out /= np.abs(out).max() / .88
out *= np.clip((24.0 - t_all) / .3, 0, 1)
pcm = (np.stack([out, out], 1) * 32767).astype(np.int16)
with wave.open('out/sound-v2.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote out/sound-v2.wav')

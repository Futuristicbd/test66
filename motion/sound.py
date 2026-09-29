"""Synthesised sound design for the NEXT reel -> out/sound.wav (48 kHz stereo, 20 s).
Pulse bed ~90 BPM, UI clicks on cursor presses, paper swish on each morph,
shutter at 12.9, chime at 15.6, riser 16.8 -> resolve on the logo hit at 18.8, music out for the last 0.5 s."""
import numpy as np, wave
SR, T = 48000, 20.0
N = int(SR * T)
rng = np.random.default_rng(7)
mix = np.zeros(N); bed = np.zeros(N)
t_all = np.arange(N) / SR

def add(buf, at, sig, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i < N: buf[i:j] += gain * sig[:j - i]

def env(n, a, d):  # attack/decay in seconds
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

def lp(x, k):  # one-pole low-pass, k in (0,1]
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y

# --- pulse bed: soft kick + muted pad, 90 BPM ---
beat = 60 / 90
for k in range(int(19.5 / beat) + 1):
    at = 0.05 + k * beat
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 52 + 60 * np.exp(-t * 30)
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.12)
    add(bed, at, kick, 0.42)
    if k % 2 == 1:  # soft off-beat tick
        n2 = int(0.05 * SR); add(bed, at + beat / 2, lp(rng.standard_normal(n2), 0.5) * env(n2, 0.001, 0.012), 0.05)
chord = [146.83, 220.0, 277.18, 329.63]  # D minor-ish add9, warm and quiet
pad = sum(np.sin(2 * np.pi * f * t_all + i) for i, f in enumerate(chord)) / len(chord)
pad *= 0.06 * (0.8 + 0.2 * np.sin(2 * np.pi * t_all / 4))
pad *= np.clip(t_all / 1.0, 0, 1)
bed += pad

# --- UI clicks ---
for c in [2.3, 3.3, 5.5, 8.3, 9.45, 11.7, 12.9, 14.95, 15.58]:
    n = int(0.03 * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 2400 * t) * 0.5 + rng.standard_normal(n) * 0.5) * env(n, 0.0005, 0.006)
    add(mix, c - 0.02, s, 0.35)

# --- paper swish on each morph ---
for m in [2.35, 4.6, 7.0, 9.6, 12.2, 15.0, 16.8, 18.6]:
    n = int(0.45 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    hp = noise - lp(noise, 0.15)
    shape = np.sin(np.pi * np.clip(t / 0.45, 0, 1)) ** 2
    add(mix, m - 0.12, hp * shape, 0.09)

# --- camera shutter at 12.9 ---
for off, g in [(0.0, 0.5), (0.07, 0.35)]:
    n = int(0.06 * SR); nz = rng.standard_normal(n)
    add(mix, 12.9 + off, (nz - lp(nz, 0.3)) * env(n, 0.0005, 0.015), g)
n = int(0.12 * SR); t = np.arange(n) / SR
add(mix, 12.9, np.sin(2 * np.pi * 140 * t) * env(n, 0.001, 0.03), 0.3)

# --- chime at 15.6 ---
n = int(1.4 * SR); t = np.arange(n) / SR
ch = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(1318.5, 1, .5), (1975.5, .5, .35), (2637, .25, .25), (987.8, .4, .6)])
add(mix, 15.6, ch * np.minimum(1, t / 0.003), 0.14)

# --- riser 16.8 -> 18.8, resolve on the logo hit ---
n = int(2.0 * SR); t = np.arange(n) / SR; u = t / 2.0
nz = rng.standard_normal(n); nz = nz - lp(nz, 0.05 + 0.4 * 0)  # airy
rise = (nz * 0.5 + np.sin(2 * np.pi * np.cumsum(300 + 900 * u ** 2) / SR) * 0.4) * (u ** 2.2)
add(mix, 16.8, rise, 0.16)
n = int(1.2 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(45 + 40 * np.exp(-t * 12)) / SR) * env(n, 0.002, 0.35)
bell = sum(np.sin(2 * np.pi * f * 2 * t) for f in chord) / 4 * env(n, 0.004, 0.45)
add(mix, 18.8, boom, 0.6); add(mix, 18.8, bell, 0.12)

# music out for the last 0.5 s
fade = np.clip((19.5 - t_all) / 0.12, 0, 1)
bed *= fade
out = mix + bed
out /= max(1e-9, np.abs(out).max()) / 0.85
tail = np.clip((20.0 - t_all) / 0.3, 0, 1); out *= tail
st = np.stack([out, out], 1)
pcm = (st * 32767).astype(np.int16)
with wave.open('out/sound.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote out/sound.wav')

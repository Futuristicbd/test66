# FuturisticBD — "NEXT" reel · timing sheet

`next-reel.mp4` · 1080×1920 (9:16) · 30 fps · 20.0 s · with synthesised sound design.
It is one continuous shape: no cuts, every state change is a morph.

**Theme:** a white and light-blue ground (#F6F9FD) with a drifting hairline grid and 8% grain. Ink is navy (#0F1B2D). The single accent is blue (#2F6BFF), used only on each beat's "win". Headlines use Instrument Serif; labels use Geist and Geist Mono.

**Safe zone:** all text stays clear of the top 220 px, the bottom 420 px and the right 140 px.

## Beats and VO (record the VO to these times)

| Time | State | VO line | Change → exact time |
|---|---|---|---|
| 0.0–2.35 | Grey profile card | "You're great at what you do. But online… nobody knows it." | DOCTOR. → LAWYER. 0.72 → C-SUITE. 1.25 · "Invisible online." + desaturate 1.55 |
| 2.35–4.6 | Search panel | "First, we research your field…" | click 2.30 → morph · query types 2.6 · RESEARCH tab click 3.30 |
| 4.6–7.0 | 3-column comparison | "…study your competition…" | bars grow 4.85 · drag highlight 5.50→6.15 · fill 6.20 · GAP FOUND 6.30 |
| 7.0–9.6 | 4×4 content calendar | "…and find the content that works for *you*." | diagonal fill 7.25 (40 ms/tile) · click 8.30 → 4 tiles turn blue · STRATEGY: LOCKED 8.60 |
| 9.6–12.2 | Script page | "We write every script." | tile click 9.45 → morph 9.6 · typing 9.95–11.6 · check drawn by cursor 11.7–12.0 |
| 12.2–15.0 | Viewfinder | "Then we come to you, and shoot everything in one day." | pin drops 12.45 · **HIT 12.9** shutter click, 6-frame flash, 4% punch-in · 1 DAY 14.2 |
| 15.0–16.8 | Phone | "You get our best work, ready to post." | stop click 14.95 → morph · reels slide up 15.12/15.24/15.36 · **HIT 15.6** check pops, DELIVERED |
| 16.8–18.6 | Upgraded profile card | "You just sit back… and watch your brand grow." | cursor leaves 16.3–16.8 · chart draws 17.15–18.1 |
| 18.6–20.0 | Logo end card | (VO optional: "Comment NEXT.") | morph 18.6 · **HIT 18.8** logo 0.9→1 · lines 18.98–19.3 · holds still 19.4–20.0 |

## Sound
- A 90 BPM soft pulse bed with a quiet pad.
- A UI click on every cursor press and a paper swish on each morph.
- A camera shutter at 12.9 and a chime at 15.6.
- A riser from 16.8 that resolves on the logo hit at 18.8.
- The music drops out for the last 0.5 s.

The track is synthesised by `motion/sound.py`. Replace it with licensed music or SFX if you prefer.

## Illustrative content
- All bars, skeleton lines, the growth curve and the calendar are illustrative. They show no numbers, counts or results.
- The profile shows no real person. The script lines are a sample hook.
- **The flame mark is a placeholder** (Lucide "flame", ISC licence). Swap in the real FuturisticBD logo in `motion/clips/next-reel.html`, in the `flame()` helper and in `#flameBig`.

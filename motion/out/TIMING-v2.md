# FuturisticBD — "NEXT" reel v2 · timing sheet

`next-reel-v2.mp4` · 1080×1920 (9:16) · 30 fps · 24.0 s · with synthesised sound design.

**Style (after the reference):**
- kinetic grotesk type that blurs in word by word, on a slowly drifting soft gradient,
- a rolling word drum,
- 3D card moves,
- a bouncing ring that hops between words,
- a full-frame colour-panel wipe,
- before/after profile cards,
- orbiting reel cards,
- a blob that becomes the logo.

**Theme (your brief):**
- White and light-blue ground (#F3F7FF) with soft blue gradient blobs.
- Navy text (#0B1B3F) and one accent blue (#2F6BFF).
- Geist Sans and Geist Mono.

**Safe zone:** all text stays clear of the top 220 px, the bottom 420 px and the right 140 px.

## Beats and VO (record the VO to these times)

| Time | On screen | VO line |
|---|---|---|
| 0.0–2.0 | HUD lines, glyphs, typed "You're **great** at what you do." | "You're great at what you do." |
| 2.0–4.2 | Word drum: **Top** Doctor. → Lawyer. → C-Suite. | "Top doctor. Top lawyer. C-suite." |
| 4.2–5.7 | Avatars pop in; your avatar is a faded dashed ghost. "But online, nobody knows **you.**" | "But online… nobody knows you." |
| 5.7–8.1 | A line runs from the ghost into the **Research** card; the search types; a row gets selected | "First, we research your field…" |
| 8.1–10.5 | Typed "We study your" → **Competitors · Content · Strategy**, with the ring landing on each | "…study your competitors, your content, your strategy." |
| 10.5–12.4 | "We write **Every script.**" A 3D script card flips in, types, and gets a check mark | "We write every script." |
| 12.4–14.7 | Blue panel wipe: viewfinder, REC, "Shot in **1 day.**" Shutter + flash + 4% punch-in at 13.6 | "Then we come to you and shoot everything in one day." |
| 14.7–17.0 | Before / After profiles. Seen → Trusted → **Chosen** (15.4 / 15.9 / 16.4) | "Your profile goes from invisible… to seen, trusted, chosen." |
| 17.0–18.4 | "Being good" → "**isn't enough.**" (impact at 17.6) | "Because being good isn't enough." |
| 18.4–20.3 | "Be the name **in your field.**" with reel cards orbiting | "Be the name in your field." |
| 20.3–21.6 | **Build** → Your **Brand** | "Build your brand…" |
| 21.6–24.0 | A blue blob lands and becomes the logo (hit at 22.0). **FuturisticBD** · Your career's **NEXT** level. · Comment "NEXT" · First 10 clients get a free consultation. Holds still from 23.4. | "…with FuturisticBD. Comment NEXT." |

## Sound (`motion/sound2.py`)
- A 110 BPM pulse bed.
- Typing ticks, drum ticks, and a whoosh on each scene change.
- Avatar pops, rising plucks on each ring bounce, and a shutter at 13.6.
- An impact at 17.6, and a riser into a logo hit and chime at 22.0.
- The music drops out for the last 0.5 s.

## What differs from the reference, and why
- **No invented numbers.** The reference shows "16.42 M impressions"; the reel shows none, because you have no case studies yet.
- **No real faces or brands.** Avatars, profiles and reel cards are placeholders.
- **The flame mark is a placeholder** (Lucide "flame", ISC licence). Swap in the real FuturisticBD logo in `motion/clips/next-reel-v2.html`, in the `flame()` helper and in `mark`.
- The reference's red/black palette is replaced by your white and light-blue theme.

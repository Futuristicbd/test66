# FuturisticBD — Corporate Omnibus event coverage film

`corporate-omnibus-coverage.mp4` · 1920×1080 (16:9) · 30 fps with motion blur · 44.6 s · scored, normalised to −14 LUFS.

The photos come from `FUTURISTIC_BD_Portfolio.pptx`. 15 event photos were extracted and saved to `motion/assets/omnibus/`. The phone-camera watermarks were cropped off two of them.

## Look
- **Background:** a pale light-blue ground with drifting soft blobs and a faint dot grid.
- **Keywords:** set in the blue → sky-blue gradient.
- **Photos:** shown as white-bordered prints that fly in and land on a spring. Each print lands with a **camera flash** and a shutter sound.
- **Viewfinder:** a camera viewfinder frames the whole coverage:
  - corner brackets;
  - the FuturisticBD flame bug;
  - ● REC with a running timecode;
  - *CORPORATE OMNIBUS · CHATTOGRAM*;
  - a live *SHOT 01/16* counter that goes up with every flash.

## The story
| Time | Scene | On screen | Photos |
|---|---|---|---|
| 0.0–4.3 | Hook | FUTURISTICBD · EVENT COVERAGE / For the first time, **in Chattogram.** | — |
| 4.3–8.7 | Title | ***Corporate* Omnibus** · CAREER FAIR · CHATTOGRAM, with four prints flying in around it | 25, 20, 1, 15 |
| 8.5–13.5 | Before → after | It began with **an empty hall.** (BEFORE) → flash → Then the doors ***opened.*** (AFTER · FULL HOUSE) | 16 → 15 |
| 13.3–18.7 | Scale | **40+** counter → companies. Leading local & multinational firms. Three prints are dealt in | 24, 23, 25 |
| 18.5–24.0 | Speakers | ***Voices* that inspired.** A filmstrip of the stage. INAUGURAL SESSION · KEYNOTES · TALKS | 19, 21, 17 |
| 23.8–29.0 | Honours | **Moments of *honour.*** A double photographer flash, with sparkles | 22, 18 |
| 28.8–33.7 | Networking | ***Conversations* that open doors.** NETWORKING · ROUND TABLES | 7, 26, 6 |
| 33.5–38.6 | Community | Group photo → the full group photo grows to fill the frame → **One community. One story.** | 20 → 1 |
| 38.1–44.6 | Brand | Every event has a story. ***We capture it.*** → FuturisticBD flame + wordmark · EVENT COVERAGE · PHOTOGRAPHY · VIDEOGRAPHY · STORYTELLING · [Book your event coverage →] · www.futuristicbd.com. Holds from 43.6 | — |

## Sound (`motion/sound-omnibus.py`)
- **Music:** an uplifting 120 BPM bed in D (Dmaj9 – Bm7 – Gmaj9 – A).
  - It opens with a soft intro.
  - The beat and a braam land on the title.
  - A riser leads into "40+", with ticks under the counter.
  - The honours get a half-time section with a chime.
  - The networking scene runs at full energy.
  - A riser and hit play as the group photo fills the frame.
  - It resolves on a chord and chime with the logo.
- **Effects:** a shutter on every flash and a whoosh on every print.

## Rebuild
```
cd motion && ./build-omnibus.sh
SFX_T=44.6 python3 sound-omnibus.py && ffmpeg -i out/sound-omnibus-raw.wav -af loudnorm=I=-14:TP=-1 out/sound-omnibus.wav
CHROMIUM=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell NODE_PATH=node_modules \
  node render-par.js dist/omnibus-coverage.html out/omnibus-video-only.mp4 30 4 4
ffmpeg -i out/omnibus-video-only.mp4 -i out/sound-omnibus.wav -c:v copy -c:a aac -b:a 256k -shortest out/corporate-omnibus-coverage.mp4
```

#!/usr/bin/env bash
# Build v3: embed Geist + Geist Mono + Instrument Serif Italic (all OFL) into the standalone reel page
set -e
cd "$(dirname "$0")"
mkdir -p dist
python3 - <<'PY'
import base64
F='../.claude/skills/motion-broll/engine/fonts/'
b=lambda f: base64.b64encode(open(f,'rb').read()).decode()
s=open('clips/next-reel-v3.html').read()
s=s.replace('__GEISTMONO__',b(F+'GeistMono-Medium.woff2')).replace('__GEIST__',b(F+'Geist-Variable.woff2')).replace('__ISERIFI__',b('fonts/InstrumentSerif-Italic.ttf'))
open('dist/next-reel-v3.html','w').write(s); print('built dist/next-reel-v3.html')
PY

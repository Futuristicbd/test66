#!/usr/bin/env bash
# Build the reel: engine wrap + embed Instrument Serif (OFL)
set -e
cd "$(dirname "$0")"
python3 ../.claude/skills/motion-broll/engine/build.py dist clips/next-reel.html
python3 - <<'PY'
import base64
p='dist/next-reel.html'; s=open(p).read()
b=lambda f: base64.b64encode(open(f,'rb').read()).decode()
s=s.replace('__ISERIFI__',b('fonts/InstrumentSerif-Italic.ttf')).replace('__ISERIF__',b('fonts/InstrumentSerif-Regular.ttf'))
open(p,'w').write(s)
PY

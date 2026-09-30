#!/usr/bin/env bash
# Build v4: embed Geist + Geist Mono (OFL) and the FuturisticBD logo parts into the standalone reel page
set -e
cd "$(dirname "$0")"
mkdir -p dist
python3 - <<'PY'
import base64
F='../.claude/skills/motion-broll/engine/fonts/'
b=lambda f: base64.b64encode(open(f,'rb').read()).decode()
s=open('clips/next-reel-v4.html').read()
s=s.replace('__GEISTMONO__',b(F+'GeistMono-Medium.woff2')).replace('__GEIST__',b(F+'Geist-Variable.woff2'))
for k,f in [('__FLAME__','assets/flame-navy.png'),('__WORDMARK__','assets/wordmark-navy.png'),('__URL__','assets/url-navy.png')]:
    s=s.replace(k,'data:image/png;base64,'+b(f))
open('dist/next-reel-v4.html','w').write(s); print('built dist/next-reel-v4.html')
PY

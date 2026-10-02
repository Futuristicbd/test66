#!/usr/bin/env bash
# Build the Corporate Omnibus coverage film: embed Geist fonts (OFL), the FuturisticBD logo parts
# and the event photos from the portfolio deck into one standalone page.
set -e
cd "$(dirname "$0")"
mkdir -p dist
python3 - <<'PY'
import base64, glob, os
F='../.claude/skills/motion-broll/engine/fonts/'
b=lambda f: base64.b64encode(open(f,'rb').read()).decode()
s=open('clips/omnibus-coverage.html').read()
s=s.replace('__GEISTMONO__',b(F+'GeistMono-Medium.woff2')).replace('__GEIST__',b(F+'Geist-Variable.woff2'))
for k,f in [('__FLAMEW__','assets/flame-white.png'),('__FLAME__','assets/flame-navy.png'),('__WORDMARK__','assets/wordmark-navy.png'),('__URL__','assets/url-navy.png')]:
    s=s.replace(k,'data:image/png;base64,'+b(f))
for f in sorted(glob.glob('assets/omnibus/p*.jpg')):
    k=os.path.basename(f)[:-4].upper()
    s=s.replace(f"'__{k}__'","'data:image/jpeg;base64,"+b(f)+"'")
assert '__P' not in s, 'missing photo'
open('dist/omnibus-coverage.html','w').write(s); print('built dist/omnibus-coverage.html', len(s)//1024, 'KB')
PY

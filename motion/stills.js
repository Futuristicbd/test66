// node stills.js dist/x.html out.png t1 t2 ... -> contact sheet at the page's own frame size
const {chromium}=require('playwright');const path=require('path');const {execSync}=require('child_process');const fs=require('fs');
(async()=>{const [html,out,...ts]=process.argv.slice(2);
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve(html)+'?render');await p.evaluate(()=>document.fonts.ready);
 const dir=fs.mkdtempSync('/tmp/st');
 for(let i=0;i<ts.length;i++){await p.evaluate(t=>seek(t),+ts[i]);await p.screenshot({path:`${dir}/${String(i).padStart(3,'0')}.png`});}
 await b.close(); const cols=Math.min(6,ts.length),rows=Math.ceil(ts.length/cols);
 execSync(`ffmpeg -loglevel error -y -i ${dir}/%03d.png -vf "scale=360:-1,tile=${cols}x${rows}:padding=6:color=black" -frames:v 1 ${out}`);
 if(errs.length) console.log('ERR',errs);})();

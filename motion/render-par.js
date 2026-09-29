// Parallel frame renderer with sub-frame motion blur.
// NODE_PATH=node_modules node render-par.js dist/page.html out/video.mp4 [fps=60] [subframes=6] [workers=4]
// Each worker renders a contiguous frame range to its own segment; segments are then concatenated losslessly.
const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');const path=require('path');const fs=require('fs');
const [html,out,fpsA='60',kA='6',wA='4']=process.argv.slice(2);
const FPS=+fpsA, K=+kA, NW=+wA, SH=0.5/FPS;   // 180° shutter
async function worker(id,f0,f1,seg){
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
  const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+path.resolve(html)+'?render');await p.evaluate(()=>document.fonts.ready);
  const vf=`format=gbrp,tmix=frames=${K}:weights='${Array(K).fill(1).join(' ')}',select='eq(mod(n\\,${K})\\,${K-1})',setpts=N/(${FPS})/TB`;
  const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS*K),'-c:v','png','-i','-','-vf',vf,'-r',String(FPS),'-c:v','libx264','-crf','15','-preset','medium','-pix_fmt','yuv420p',seg]);
  ff.stderr.on('data',d=>process.stderr.write(d));
  for(let f=f0;f<f1;f++){for(let k=0;k<K;k++){const t=Math.max(0,f/FPS+(k-(K-1)/2)*SH/K);
      await p.evaluate(t=>seek(t),t);const buf=await p.screenshot({type:'png'});
      if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));}
    if((f-f0)%60==0) console.log(`w${id} ${f-f0}/${f1-f0}`);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
  if(errs.length) console.log(`w${id} ERR`,errs[0]);
}
(async()=>{
  const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+path.resolve(html)+'?render');
  const T=await p.evaluate(()=>window.DURATION);await b.close();
  const N=Math.round(T*FPS), per=Math.ceil(N/NW), dir=path.dirname(out), segs=[];
  const jobs=[];for(let i=0;i<NW;i++){const f0=i*per,f1=Math.min(N,f0+per);if(f0>=f1)break;const seg=path.join(dir,`_seg${i}.mp4`);segs.push(seg);jobs.push(worker(i,f0,f1,seg));}
  await Promise.all(jobs);
  const list=path.join(dir,'_segs.txt');fs.writeFileSync(list,segs.map(s=>`file '${path.resolve(s)}'`).join('\n'));
  execFileSync('ffmpeg',['-loglevel','error','-y','-f','concat','-safe','0','-i',list,'-c','copy','-movflags','+faststart',out]);
  segs.forEach(s=>fs.unlinkSync(s));fs.unlinkSync(list);
  console.log('rendered',out,N,'frames @',FPS,'fps,',K,'subframes');
})();

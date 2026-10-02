// Parallel, resumable frame renderer with sub-frame motion blur.
// NODE_PATH=node_modules node render-par.js dist/page.html out/video.mp4 [fps=60] [subframes=6] [workers=4]
// Frames are rendered in chunks (1 s each) by a pool of browser workers; each finished chunk is kept in
// work/chunks-<name>/ so an interrupted render resumes where it stopped. Chunks are concatenated losslessly.
const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');const path=require('path');const fs=require('fs');
const [html,out,fpsA='60',kA='6',wA='4']=process.argv.slice(2);
const FPS=+fpsA, K=+kA, NW=+wA, SH=0.5/FPS, CH=FPS;   // 180° shutter, 1-second chunks
const dir=path.join('work','chunks-'+path.basename(out,'.mp4')); fs.mkdirSync(dir,{recursive:true});
let VW=1080,VH=1920;
async function worker(id,queue){
  const b=await chromium.launch({executablePath:process.env.CHROMIUM||undefined});const p=await b.newPage({viewport:{width:VW,height:VH}});
  const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+path.resolve(html)+'?render');await p.evaluate(()=>document.fonts.ready);
  const vf=`format=gbrp,tmix=frames=${K}:weights='${Array(K).fill(1).join(' ')}',select='eq(mod(n\\,${K})\\,${K-1})',setpts=N/(${FPS})/TB`;
  let job; while((job=queue.shift())){
    const [c,f0,f1]=job, seg=path.join(dir,`c${String(c).padStart(3,'0')}.mp4`), tmp=seg+'.part.mp4';
    const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS*K),'-c:v','png','-i','-','-vf',vf,'-r',String(FPS),'-c:v','libx264','-crf','15','-preset','medium','-pix_fmt','yuv420p',tmp]);
    ff.stderr.on('data',d=>process.stderr.write(d));
    for(let f=f0;f<f1;f++) for(let k=0;k<K;k++){const t=Math.max(0,f/FPS+(k-(K-1)/2)*SH/K);
      await p.evaluate(t=>seek(t),t);const buf=await p.screenshot({type:'png'});
      if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));}
    ff.stdin.end();await new Promise(r=>ff.on('close',r)); fs.renameSync(tmp,seg);
    console.log(`w${id} chunk ${c} done`);}
  await b.close(); if(errs.length) console.log(`w${id} ERR`,errs[0]);
}
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROMIUM||undefined});const p=await b.newPage();await p.goto('file://'+path.resolve(html)+'?render');
  const [T,vw,vh]=await p.evaluate(()=>[window.DURATION,window.VW||1080,window.VH||1920]);await b.close(); VW=vw; VH=vh;
  const N=Math.round(T*FPS), NC=Math.ceil(N/CH), queue=[];
  for(let c=0;c<NC;c++){const seg=path.join(dir,`c${String(c).padStart(3,'0')}.mp4`); if(!fs.existsSync(seg)) queue.push([c,c*CH,Math.min(N,(c+1)*CH)]);}
  console.log(`${NC-queue.length}/${NC} chunks already done, rendering ${queue.length}`);
  await Promise.all([...Array(Math.min(NW,queue.length))].map((_,i)=>worker(i,queue)));
  const segs=[...Array(NC)].map((_,c)=>path.resolve(dir,`c${String(c).padStart(3,'0')}.mp4`));
  const list=path.join(dir,'list.txt');fs.writeFileSync(list,segs.map(s=>`file '${s}'`).join('\n'));
  execFileSync('ffmpeg',['-loglevel','error','-y','-f','concat','-safe','0','-i',list,'-c','copy','-movflags','+faststart',out]);
  console.log('rendered',out,N,'frames @',FPS,'fps,',K,'subframes');
})();

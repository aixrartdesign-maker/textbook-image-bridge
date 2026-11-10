// report images whose displayed aspect ratio differs from the natural one (distortion); usage: node imgaspect.js book.html
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:794,height:1123}});
  await p.emulateMedia({media:'print'});
  await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready);
  const r=await p.evaluate(async()=>{
    const imgs=[...document.querySelectorAll('img')];
    await Promise.all(imgs.map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r})));
    const near=el=>{let x=el; while(x&&!x.id) x=x.parentElement; return x?x.id:'';};
    const out=[];
    for(const i of imgs){
      if(!i.naturalWidth||!i.clientWidth) continue;
      const cs=getComputedStyle(i);
      if(cs.objectFit==='cover'||cs.objectFit==='contain') continue;
      const nat=i.naturalWidth/i.naturalHeight, disp=i.clientWidth/i.clientHeight;
      if(Math.abs(disp/nat-1)>0.03) out.push({near:near(i),src:i.getAttribute('src'),nat:+nat.toFixed(3),disp:+disp.toFixed(3),w:i.clientWidth,h:i.clientHeight});
    }
    return out;});
  console.log(JSON.stringify(r,null,0).replace(/\},\{/g,'},\n{'));
  await b.close();
})();

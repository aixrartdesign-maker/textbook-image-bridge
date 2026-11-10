// Does anything make the printed document wider than the page content box (which makes Chromium shrink every page)?
// usage: node docwidth.js book.html
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:612,height:900}});
  await p.emulateMedia({media:'print'});
  await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready);
  await p.addScriptTag({path:'/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/en/fitsvg.js'});
  await p.evaluate(()=>window.__fitSvg());
  const r=await p.evaluate(()=>{
    const de=document.documentElement; const W=de.clientWidth;
    const wide=[];
    for(const el of document.querySelectorAll('body *')){
      const bb=el.getBoundingClientRect();
      if(bb.width>0 && bb.right>W+1){ let x=el; while(x&&!x.id) x=x.parentElement; wide.push({id:x?x.id:'',tag:el.tagName,cls:(el.className&&el.className.baseVal===undefined)?el.className:'',right:Math.round(bb.right)}); }
    }
    const seen=new Set(); const top=[];
    for(const w of wide.sort((a,b)=>b.right-a.right)){ const k=w.id+w.cls; if(seen.has(k)) continue; seen.add(k); top.push(w); if(top.length>8) break; }
    return {clientWidth:W, scrollWidth:de.scrollWidth, n:wide.length, top};
  });
  console.log(process.argv[2], JSON.stringify(r));
  await b.close();
})();

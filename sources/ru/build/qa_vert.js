// Vertical overflow: boxes whose content is taller than the box (text running out of cards, cells, bars).
// usage: node qa_vert.js book.html
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:612,height:900}});
  await p.emulateMedia({media:'print'});
  await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready);
  await p.addScriptTag({path:'/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/en/fitsvg.js'});
  await p.evaluate(()=>window.__fitSvg());
  const r=await p.evaluate(()=>{
    const near=el=>{let x=el; while(x&&!x.id) x=x.parentElement; return x?x.id:'';};
    const out=[];
    for(const el of document.querySelectorAll('body *')){
      if(el.closest('svg')) continue;
      const cs=getComputedStyle(el);
      if(cs.display==='inline'||cs.display==='none') continue;
      if(el.clientHeight>0 && el.scrollHeight>el.clientHeight+3){
        // ignore overflow caused only by absolutely positioned decorations
        let textOver=false;
        const bb=el.getBoundingClientRect();
        const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
        let n; while((n=walker.nextNode())){ if(!n.textContent.trim()) continue; const range=document.createRange(); range.selectNodeContents(n);
          for(const rc of range.getClientRects()){ if(rc.bottom>bb.bottom+2){ textOver=true; break; } } if(textOver) break; }
        if(textOver) out.push({near:near(el),tag:el.tagName.toLowerCase(),cls:(typeof el.className==='string'?el.className:''),over:el.scrollHeight-el.clientHeight,h:el.clientHeight,t:(el.innerText||'').trim().slice(0,60)});
      }
    }
    return out;});
  console.log(JSON.stringify(r,null,0).replace(/\},\{/g,'},\n{'));
  console.error('vertical overflow',r.length);
  await b.close();
})();

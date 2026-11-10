// Layout QA for a built book.html: SVG labels that overflow/overlap or had to shrink a lot,
// and HTML boxes whose text overflows horizontally.  usage: node qa_html.js book.html > report.json
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:612,height:900}});
  await p.emulateMedia({media:'print'});
  await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready);
  // remember the authored font sizes before fitting
  await p.evaluate(()=>{for(const t of document.querySelectorAll('svg text')) t.dataset.fs0=parseFloat(getComputedStyle(t).fontSize)||0;});
  await p.addScriptTag({path:'/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/en/fitsvg.js'});
  await p.evaluate(()=>window.__fitSvg());
  const r=await p.evaluate(()=>{
    const near=el=>{let x=el; while(x&&!x.id) x=x.parentElement; return x?x.id:'';};
    const out={svg:[],shrunk:[],html:[]};
    let k=0;
    for(const svg of document.querySelectorAll('svg')){
      k++; const vb=svg.viewBox&&svg.viewBox.baseVal; if(!vb||!vb.width) continue;
      const texts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()&&!t.closest('defs'));
      const boxes=texts.map(t=>{try{const bb=t.getBBox();return {el:t,t:t.textContent.trim().slice(0,50),x:bb.x,y:bb.y,w:bb.width,h:bb.height}}catch(e){return null}}).filter(Boolean);
      const issues=[];
      for(const bb of boxes){ if(bb.x<vb.x-1||bb.x+bb.w>vb.x+vb.width+1) issues.push('OUT:'+bb.t);
        const f0=parseFloat(bb.el.dataset.fs0||0), f1=parseFloat(getComputedStyle(bb.el).fontSize)||0;
        if(f0&&f1/f0<0.8) out.shrunk.push({svg:k,near:near(svg),t:bb.t,ratio:+(f1/f0).toFixed(2)}); }
      for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],c=boxes[j];
        const ix=Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x), iy=Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y);
        if(ix>2&&iy>a.h*0.35&&iy>c.h*0.35) issues.push('OVL:'+a.t+' | '+c.t);}
      if(issues.length) out.svg.push({svg:k,near:near(svg),issues:issues.slice(0,8),n:issues.length});
    }
    // HTML horizontal overflow inside figures, cards, tables, labels
    const sel='.fg *, figure *, .card, .card *, td, th, .lab *, .kv *, .steps *, .vs *, .board *, .summary *, h1, h2, h3, h4, .crumb, .num';
    for(const el of document.querySelectorAll(sel)){
      if(el.closest('svg')) continue;
      const cs=getComputedStyle(el); if(cs.display==='inline'||cs.display==='none') continue;
      if(el.scrollWidth>el.clientWidth+2 && el.clientWidth>0){
        const txt=(el.innerText||'').trim().slice(0,70);
        if(!txt) continue;
        out.html.push({near:near(el),tag:el.tagName.toLowerCase(),cls:el.className&&el.className.baseVal===undefined?el.className:'',over:el.scrollWidth-el.clientWidth,w:el.clientWidth,t:txt});
      }
    }
    return out;
  });
  console.log(JSON.stringify(r,null,1));
  console.error('svg issues',r.svg.length,'| shrunk<0.8',r.shrunk.length,'| html overflow',r.html.length);
  await b.close();
})();

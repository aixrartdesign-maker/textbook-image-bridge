// SVG text QA after label fitting: (1) text outside the viewBox vertically (clipped/invisible),
// (2) white text not contained in a shape drawn before it (it disappears on the light figure background).
// usage: node qa_svg2.js book.html
const {chromium}=require('playwright'); const path=require('path');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:612,height:900}});
  await p.emulateMedia({media:'print'});
  await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready);
  await p.addScriptTag({path:'/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/en/fitsvg.js'});
  await p.evaluate(()=>window.__fitSvg());
  const r=await p.evaluate(()=>{
    const near=el=>{let x=el; while(x&&!x.id) x=x.parentElement; return x?x.id:'';};
    const white=c=>/^(#fff|#ffffff|white|rgb\(255, 255, 255\))$/i.test((c||'').trim());
    const out=[];
    for(const svg of document.querySelectorAll('svg')){
      const vb=svg.viewBox&&svg.viewBox.baseVal; if(!vb||!vb.width) continue;
      const all=[...svg.querySelectorAll('*')];
      const shapes=[];
      for(const el of all){
        const tag=el.tagName.toLowerCase();
        if(['rect','circle','ellipse','polygon','path'].includes(tag)){
          const cs=getComputedStyle(el); const f=cs.fill;
          const m=(f||'').match(/rgba?\(([\d.]+), ([\d.]+), ([\d.]+)(?:, ([\d.]+))?\)/);
          if(m){ // effective luminance over the light figure background (opacity mixes the colour with it)
            let a=parseFloat(cs.opacity||1)*parseFloat(cs.fillOpacity||1)*(m[4]!==undefined?parseFloat(m[4]):1);
            const bg=[246,245,243]; const c=[+m[1],+m[2],+m[3]].map((v,i)=>v*a+bg[i]*(1-a));
            const lum=(0.2126*c[0]+0.7152*c[1]+0.0722*c[2])/255;
            if(lum<0.62){ try{const bb=el.getBBox();
              shapes.push({el,bb,idx:all.indexOf(el),tf:!!(el.getAttribute('transform')||el.parentElement.getAttribute('transform'))});}catch(e){} } }
        }
        if(tag==='text'&&el.textContent.trim()&&!el.closest('defs')){
          let bb; try{bb=el.getBBox();}catch(e){continue}
          const tr=(el.getAttribute('transform')||'')+(el.parentElement.getAttribute&&el.parentElement.getAttribute('transform')||'');
          const t=el.textContent.trim().slice(0,60);
          if(!/rotate/.test(tr) && (bb.y<vb.y-0.5||bb.y+bb.height>vb.y+vb.height+0.5)) out.push({kind:'V-OUT',near:near(svg),t,y:+bb.y.toFixed(1),h:+bb.height.toFixed(1),vbh:vb.height});
          const fill=el.getAttribute('fill')||getComputedStyle(el).fill;
          if(white(fill)&&!/rotate/.test(tr)){
            const idx=all.indexOf(el);
            const ok=shapes.some(s=>s.idx<idx&&!s.tf&&bb.x>=s.bb.x-1&&bb.x+bb.width<=s.bb.x+s.bb.width+1&&bb.y+bb.height*0.25>=s.bb.y-1&&bb.y+bb.height*0.8<=s.bb.y+s.bb.height+1);
            if(!ok) out.push({kind:'WHITE-OUT',near:near(svg),t,x:+bb.x.toFixed(1),w:+bb.width.toFixed(1)});
          }
        }
      }
    }
    return out;});
  console.log(JSON.stringify(r,null,0).replace(/\},\{/g,'},\n{'));
  console.error('issues',r.length);
  await b.close();
})();

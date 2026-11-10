// Shrink SVG labels that run outside the viewBox or into a neighbouring label on the same line.
window.__fitSvg = function(){
  let changed=0;
  const fs = t => parseFloat(getComputedStyle(t).fontSize)||12;
  const anc = t => (t.getAttribute('text-anchor')||getComputedStyle(t).textAnchor||'start');
  const rotated = t => { const tr=(t.getAttribute('transform')||'')+(t.parentElement&&t.parentElement.getAttribute?(t.parentElement.getAttribute('transform')||''):''); return /rotate/.test(tr); };
  const scale=(t,f)=>{ if(!(f<0.999)) return; f=Math.max(f,0.55);
    const base=fs(t); t.style.fontSize=(base*f)+'px';
    for(const ts of t.querySelectorAll('tspan')){ const b=parseFloat(getComputedStyle(ts).fontSize); if(b) ts.style.fontSize=(b*f)+'px'; }
    changed++; };
  for(const svg of document.querySelectorAll('svg')){
    const vb=svg.viewBox&&svg.viewBox.baseVal; if(!vb||!vb.width) continue;
    const L=vb.x+2, R=vb.x+vb.width-2;
    const texts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()&&!t.closest('defs')&&!rotated(t));
    for(const t of texts){
      let bb; try{bb=t.getBBox();}catch(e){continue}
      if(bb.width<=0) continue;
      const a=anc(t); let avail;
      if(a==='middle'){ const c=bb.x+bb.width/2; avail=2*Math.min(c-L,R-c); }
      else if(a==='end'){ avail=(bb.x+bb.width)-L; } else { avail=R-bb.x; }
      if(bb.x<L-0.5||bb.x+bb.width>R+0.5) scale(t,avail/bb.width);
    }
    for(let pass=0;pass<3;pass++){
      const boxes=texts.map(t=>{try{const b=t.getBBox();return {t,b,a:anc(t)}}catch(e){return null}}).filter(x=>x&&x.b.width>0);
      let any=false;
      for(const p of boxes) for(const q of boxes){
        if(p===q) continue;
        const left = p.b.x<=q.b.x ? p : q, right = left===p ? q : p; if(left!==p) continue;
        const iy=Math.min(p.b.y+p.b.height,q.b.y+q.b.height)-Math.max(p.b.y,q.b.y);
        if(iy<0.5*Math.min(p.b.height,q.b.height)) continue;
        const ix=(left.b.x+left.b.width)-right.b.x; if(ix<=0.5) continue;
        if(right.b.x+right.b.width<=left.b.x+left.b.width) continue; // contained: leave
        const need=ix+4;
        const kL = left.a==='start'?1:(left.a==='middle'?0.5:0);   // right-edge movement per unit width lost
        const kR = right.a==='end'?1:(right.a==='middle'?0.5:0);   // left-edge movement per unit width lost
        if(kL+kR===0) continue;
        const shareL = kL/(kL+kR), shareR = kR/(kL+kR);
        if(kL>0) scale(left.t, 1 - (need*shareL/kL)/left.b.width);
        if(kR>0) scale(right.t, 1 - (need*shareR/kR)/right.b.width);
        any=true;
      }
      if(!any) break;
    }
  }
  return changed;
};

const { chromium } = require('playwright'); const path=require('path');
(async()=>{ const [,, inHtml, outPdf] = process.argv;
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('file://'+path.resolve(inHtml),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready); await p.addScriptTag({path:'/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/en/fitsvg.js'}); const nfit=await p.evaluate(()=>window.__fitSvg()); console.log('svg labels fitted',nfit);
  await p.pdf({path:outPdf,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false,margin:{top:'17mm',bottom:'20mm',left:'24mm',right:'24mm'}});
  await b.close(); })();

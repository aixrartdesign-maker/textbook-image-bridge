const { chromium } = require('playwright'); const path=require('path');
(async()=>{ const [,, inHtml, outPdf] = process.argv;
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('file://'+path.resolve(inHtml),{waitUntil:'load',timeout:600000}); await p.evaluate(()=>document.fonts.ready);
  await p.pdf({path:outPdf,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false,margin:{top:0,bottom:0,left:0,right:0}});
  await b.close(); })();

#!/usr/bin/env python3
"""v2 assembly: new part order, renumbering, generated-image substitution, prologue, image appendix,
2-pass render with TOC page numbers + running-head overlay."""
import re, json, subprocess, os, html, glob, sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/en')
from meas import is_meas
B='/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad'
os.chdir(B+'/book')

OLD_TITLES={1:'영상이란 무엇인가',2:'영상의 언어',3:'촬영 기기와 촬영 기술',4:'조명과 사운드',5:'편집과 후반 작업',6:'기획과 프리프로덕션',7:'매체 규격과 실감콘텐츠',8:'광고 제작과 사례 연구',9:'플랫폼 운영과 생성형 AI',10:'산업과 시장의 흐름',11:'취업과 커리어',12:'AI 전환기의 실무와 진로',13:'미디어아트와 확장 영상',14:'부록'}
NEW_ORDER=[2,6,3,4,5,7,8,9,10,11,12,1,13,14]
NEWNUM={old:i+1 for i,old in enumerate(NEW_ORDER)}
NEW_TITLES={NEWNUM[o]:t for o,t in OLD_TITLES.items()}
NEW_TITLES[1]='영상의 언어'
SEC6={7:1,8:1,9:1,10:2,11:2,1:3,2:4,3:5,4:6,5:7,6:8,12:9,13:10,14:11,15:12,16:13}
MAXSEC={1:14,2:20,3:14,4:10,5:13,6:16,7:14,8:19,9:14,10:6,11:17,12:14,13:8}
UNIT=r'(?!\d)(?!\s?(?:s|m|mm|cm|km|초|배|분|시간|x|k|K|%|stop|MB|GB|fps|배속|배율)\b)'

def secmap(p,s):
    if p not in NEWNUM or p==14: return None
    if s>MAXSEC.get(p,99): return None
    if p==6: return (2,SEC6.get(s,s))
    return (NEWNUM[p],s)

def renum(t):
    # PART tokens
    def ptok(m):
        a=int(m.group(1)); b=m.group(2)
        pad=len(m.group(1))==2
        def f(n): return f'{NEWNUM.get(n,n):02d}' if pad else str(NEWNUM.get(n,n))
        return 'PART '+f(a)+(('~'+f(int(b))) if b else '')
    t=re.sub(r'PART (\d{1,2})(?:~(\d{1,2}))?',ptok,t)
    t=re.sub(r'<small>PART</small>(\d{2})',lambda m:f'<small>PART</small>{NEWNUM.get(int(m.group(1)),int(m.group(1))):02d}',t)
    # structural numbers
    def nm(m):
        p,s=int(m.group(2)),int(m.group(3)); r=secmap(p,s)
        return m.group(1)+(f'{r[0]}.{r[1]}' if r else m.group(2)+'.'+m.group(3))
    # prose refs outside svg
    parts=re.split(r'(<svg.*?</svg>)',t,flags=re.S)
    for i in range(0,len(parts),2):
        parts[i]=re.sub(r'(?<=[(\s→·,>])(\d{1,2})\.(\d{1,2})(?=[)\s,·~<]|절|에|과|와|의|A|B|C|$)'+UNIT,
                        lambda m:m.group(0) if is_meas(m.string,m.start(),m.end()) else (lambda r:f'{r[0]}.{r[1]}' if r else m.group(0))(secmap(int(m.group(1)),int(m.group(2)))),parts[i])
    return ''.join(parts)

def rd(p): return open(p,encoding='utf-8').read()
SVG_SCALE=1.25
def feat(p):
    t=rd(p)
    def scale_svg(m):
        return re.sub(r'font-size="(\d+(?:\.\d+)?)"',lambda k:f'font-size="{float(k.group(1))*SVG_SCALE:.1f}"',m.group(0))
    t=re.sub(r'<svg.*?</svg>',scale_svg,t,flags=re.S)
    t=re.sub(r'<h2 class="spread-title">.*?</h2>\s*(?:<p>.*?</p>\s*)?(?:<aside class="(?:tip|note)">.*?</aside>\s*)?<figure class="(?:wide|ph wide)[^"]*"[^>]*>.*?</figure>',lambda m:'<div class="keep">'+m.group(0)+'</div>',t,flags=re.S)
    return t

# ---------- generated images: placeholder substitution ----------
PLAN={p['id']:p for p in json.load(open('imgplan.json'))}
HAVE={os.path.basename(f)[:-4] for f in glob.glob('img_new/*.jpg')}
USED=set()
def sub_ph(t):
    def rep(m):
        cls,mid,inner=m.group(1),m.group(2),m.group(3)
        USED.add(mid)
        cap=re.search(r'<figcaption>.*?</figcaption>',inner,flags=re.S)
        cap=cap.group(0) if cap else ''
        if mid in HAVE:
            c=' '.join(x for x in cls.split() if x!='ph')
            return f'<figure class="{c}"><img src="img_new/{mid}.jpg" alt=""/>{cap}</figure>'
        return m.group(0)
    return re.sub(r'<figure class="(ph[^"]*)"[^>]*data-id="([^"]+)"[^>]*>(.*?)</figure>',rep,t,flags=re.S)

imgs_by_page=json.load(open(B+'/src/imgs_by_page.json'))
part_photo={}; opener_img={}
ranges={1:(19,56),2:(57,112),3:(113,149),4:(150,181),5:(182,217),6:(218,260),7:(261,297),8:(298,338),9:(339,372),10:(373,389),11:(390,428),12:(429,460),13:(461,479),14:(480,533)}
for n,(a,b) in ranges.items():
    for p in range(a,b+1):
        for im in imgs_by_page.get(str(p),[]):
            if im['kind']=='part': part_photo.setdefault(n,im['file'])
            if im['kind']=='opener': opener_img.setdefault(n,im['file'])

# ---------- assemble ----------
front=renum(rd('parts/part00.html'))
prologue=feat('parts/prologue.html')
body=[]
for old in NEW_ORDER:
    if old==14:
        s=rd('parts/part14a.html')+'\n'+rd('parts/part14b.html')
    else:
        s=rd(f'parts/part{old:02d}.html')
    if old==6:
        s=s.replace('<!-- FEATURE:STORYBOARD -->','').replace('<!-- FEATURE:PPM -->','')
        feats=feat('parts/feature_storyboard.html')+'\n'+feat('parts/feature_ppm.html')
        anchor=s.find('<section class="essay page" id="essay-9"')
        if anchor<0: anchor=s.find('<article class="sec page" id="s6-1"')
        s=s[:anchor]+feats+'\n'+s[anchor:]
    if old==4:
        s=s.replace('<!-- FEATURE:LIGHTING -->',feat('parts/feature_lighting.html'))
    body.append(renum(s))
H='\n'.join(body)

# part openers: swap baked opener for the part photo; drop duplicated hero
for n in range(1,15):
    op=opener_img.get(n); ph=part_photo.get(n)
    if op and ph:
        H=H.replace(f'src="{op}"',f'src="{ph}"')
        H=re.sub(r'<figure class="(?:hero wide|wide hero|wide)">\s*<img src="'+re.escape(ph)+r'"[^>]*>\s*<figcaption>.*?</figcaption>\s*</figure>','',H,flags=re.S)
    elif op and not ph:
        H=re.sub(r'<div class="photo">\s*<img src="'+re.escape(op)+r'"[^>]*>','<div class="photo nophoto">',H)
H=H.replace('<div class="label">PART</div>','<div class="label">VIDEO PRODUCTION HANDBOOK</div>')
if os.path.exists('img_new/P02-OPENER.jpg'):
    H=re.sub(r'(<section class="part" id="part2">\s*<div class="photo"><img src=")[^"]+',lambda m:m.group(1)+'img_new/P02-OPENER.jpg',H)

# image appendix (부록 W)
rows=[]
for mid,p in PLAN.items():
    st='✔' if mid in HAVE else '—'
    rows.append(f'<tr><td>{mid}</td><td>{html.escape(p["cap"])}</td><td class="c">{st}</td><td class="pr">{html.escape(p["prompt"])}</td></tr>')
appW=f'''<article class="sec page" id="app-W"><header><div class="crumb"><b>부록</b>생성 이미지</div><div class="num">W</div><h2>생성 참고 사진 목록과 프롬프트</h2><p class="lead">이 판에서 새로 생성한 참고 사진 {len(PLAN)}컷의 ID·캡션·생성 프롬프트입니다. 실존 인물·브랜드·로고 없이 생성했으며, 같은 프롬프트로 재생성하거나 교체할 수 있습니다.</p></header>
<table class="t compact wide prompts"><thead><tr><th>ID</th><th>캡션</th><th>수록</th><th>프롬프트</th></tr></thead><tbody>{''.join(rows)}</tbody></table></article>'''
H=H+'\n'+rd('parts/templates.html')+'\n'+appW
H=sub_ph(H); front=sub_ph(front); prologue=sub_ph(prologue)

# markers
def add_marker(m): return m.group(0)+f'<span class="mk">[[MK:{m.group(2)}]]</span>'
MK=r'<(section|article) class="(?:part|sec page|essay page|feature page|feature page prologue|part-end page|front page|front page cont|howto page|page brk)"[^>]*? id="([^"]+)"[^>]*>'
H=re.sub(MK,add_marker,H); front=re.sub(MK,add_marker,front); prologue=re.sub(MK,add_marker,prologue)

cover_img='img_new/COVER-FRONT.jpg' if os.path.exists('img_new/COVER-FRONT.jpg') else ('img_new/COVER.jpg' if os.path.exists('img_new/COVER.jpg') else 'img/cover_crop.png')
cover=f'''<section class="cover" id="cover"><span class="mk">[[MK:cover]]</span>
  <div class="cover-top" style="visibility:hidden">
    <div class="cover-kicker">VIDEO PRODUCTION · A PRACTICAL TEXTBOOK</div>
    <h1 class="cover-title">영상 제작<br>실무 교본</h1>
    <p class="cover-sub">기획에서 납품까지, 수업과 현장에서 함께 펼치는 13개 챕터</p>
    <p class="cover-author">안지아</p>
  </div>
</section>'''
back_img='img_new/COVER-BACK.jpg' if os.path.exists('img_new/COVER-BACK.jpg') else cover_img
backcover=f'''<section class="backcover" id="backcover">
  <div class="back-text" style="visibility:hidden">
    <p class="back-lead">영상은 찍는 일이 아니라<br>보여 줄 것과 감출 것을 고르는 일이다.</p>
    <p class="back-body">스토리보드 한 칸에서 LED 파사드까지, 첫 콜타임에서 첫 릴까지. 이 책은 기법의 목록이 아니라 현장에서 내리는 판단의 순서를 담았다. 실습을 먼저 하고 이론은 뒤에 두었으며, 모든 도판은 "왜 이렇게 찍는가"에 답하도록 다시 그렸다. 생성형 AI가 공정에 들어온 지금, 바뀌지 않는 것 — 눈, 약속, 마무리 — 을 연습하는 책이다.</p>
    <p class="back-author">안지아 지음</p>
  </div>
</section>'''
halftitle='''<section class="blankpg" id="blank-f1"><span class="mk">[[MK:blank-f1]]</span></section>
<section class="halftitle" id="halftitle"><span class="mk">[[MK:halftitle]]</span>
  <div class="ht-k">VIDEO PRODUCTION · A PRACTICAL TEXTBOOK</div>
  <h1>영상 제작 실무 교본</h1>
  <p class="ht-s">기획에서 납품까지, 수업과 현장에서 함께 펼치는 13개 챕터</p>
  <p class="ht-a">안지아 지음</p>
</section>
<section class="blankpg" id="blank-f2"><span class="mk">[[MK:blank-f2]]</span></section>'''
H=cover+'\n'+halftitle+'\n<!--TOC-->\n'+front+'\n'+prologue+'\n'+H+'\n'+backcover
# ---- editorial: in flagged sections, open with text, figure follows the first paragraph ----
FIG_AFTER_P=['s1-11','s4-3','s12-8','s12-11','s7-14','s7-10','s2-7','s9-13','s10-6','s12-9','s7-8','s9-11','s2-10','s13-1']
for sid in FIG_AFTER_P:
    m=re.search(r'<article class="sec page"[^>]*id="'+sid+r'"[^>]*>',H)
    if not m: print('!! fig-after-p: no section',sid); continue
    i=H.find('</header>',m.end())+len('</header>')
    j=i
    while H[j] in ' \n\t': j+=1
    if H.startswith('<figure',j): endtag='</figure>'
    elif H.startswith('<table',j): endtag='</table>'
    else: print('!! fig-after-p: first element not figure/table',sid); continue
    k=H.find(endtag,j)+len(endtag)
    block=H[j:k]; rest=H[k:]
    art_end=rest.find('</article>')
    mp=re.compile(r'\n  <p[ >]').search(rest)   # top-level paragraph only (2-space indent)
    if not mp or mp.start()>art_end or mp.start()>1500: print('!! fig-after-p: no nearby top-level paragraph, left in place',sid); continue
    pe=rest.find('</p>',mp.start())
    if pe<0 or pe>art_end: print('!! fig-after-p: no paragraph end',sid); continue
    pe+=len('</p>')
    H=H[:j]+rest[:pe]+'\n  '+block+rest[pe:]
print('fig-after-p applied')
# ---- sequential figure renumbering by order of appearance ----
_caps=re.findall(r'<figcaption>\s*<b>그림 ([\d]+(?:-[\d]+)?)</b>',H)
_map={}; _n=0
for _c in _caps:
    if _c not in _map:
        _n+=1; _map[_c]=str(_n)
def _ren(m):
    old=m.group(1)
    return '그림 '+_map.get(old,old)
H=re.sub(r'그림 (\d+(?:-\d+)?)(?![\d-])',_ren,H)
print('figures renumbered',_n)

CSS_EXTRA='''
:root{--z:'''+os.environ.get('BOOK_Z','1')+'''; --margin-col:calc(40mm/var(--z)); --gutter:calc(7mm/var(--z)); --main:calc(115mm/var(--z))}
body{zoom:var(--z)}
.part,.cover{width:calc(var(--margin-col) + var(--gutter) + var(--main))}
.tpl figure{margin:0 0 0 calc(-1 * (var(--margin-col) + var(--gutter)))}
.tplwrap svg{width:calc(var(--margin-col) + var(--gutter) + var(--main));height:calc(236mm/var(--z))}
.fg .rb{min-width:0;overflow-wrap:anywhere}
.blankpg{break-before:page;break-after:page;height:120mm}
.epi{height:calc(236mm/var(--z));position:relative}
.epi .q{position:absolute;left:0;bottom:calc(30mm/var(--z));width:calc(118mm/var(--z))}
.epi .q small{display:block;font-family:var(--sans);font-size:7pt;letter-spacing:.3em;color:var(--wine);margin-bottom:5mm}
.epi .q p{font-family:var(--serif);font-weight:300;font-size:17pt;line-height:1.6;letter-spacing:-.02em;color:var(--ink);margin:0}
/* ---- v7 page-fill polish ---- */
.part-end ul.dash{break-inside:avoid}
.feature:not(.prologue){break-before:auto;margin-top:18mm}
.feature>header{break-after:avoid;break-inside:avoid}
#app-X{break-before:auto;margin-top:18mm}
.memo .ln:last-child{border-bottom:1px solid var(--line)}
.sec{margin-top:12mm}
.sec>header{break-after:auto}
.sec>header+*{break-before:auto}
.memo{margin-top:7mm;position:relative;break-inside:avoid}
.memo small{display:block;font-family:var(--sans);font-size:7pt;letter-spacing:.3em;color:var(--mut);margin-bottom:2mm}
.memo .ln{height:calc(9mm/var(--z));border-bottom:1px solid var(--line)}
p,li,dd{orphans:3;widows:3}
.essay{break-before:auto;margin-top:16mm}
.essay header{break-after:avoid;break-inside:avoid}
.howto+.essay{margin-top:10mm}
.part-end{break-before:auto;margin-top:16mm}
.part-end>header,.part-end>h2{break-after:avoid}
.cards,.kv,.steps,.vs,.gallery,.board,.summary,.qa,.tt,.misel,.two{break-inside:auto}
.qa dt{break-after:avoid;break-inside:avoid}.qa dd{break-inside:avoid}.tt>*{break-inside:avoid}
.card,.kv>*,.steps>*,.vs>*,.board .cell,.summary>*{break-inside:avoid}
.summary .card{display:block}.summary .card h4{float:left;width:40mm;margin:0}.summary .card p{margin:0 0 0 44mm}.summary .card::after{content:"";display:block;clear:both}
/* leftover cells: galleries */
.gallery.cols-2>figure:last-child:nth-child(2n){grid-column:1/-1}
.gallery.cols-2>figure:last-child:nth-child(2n) img{aspect-ratio:2.7/1}
.gallery.cols-3{grid-template-columns:repeat(6,1fr)}
.gallery.cols-3>figure{grid-column:span 2}
.gallery.cols-3>figure:last-child:nth-child(3n+2){grid-column:span 6}
.gallery.cols-3>figure:last-child:nth-child(3n+2) img{aspect-ratio:3/1}
.gallery.cols-3>figure:nth-last-child(2):nth-child(3n+2),.gallery.cols-3>figure:nth-last-child(2):nth-child(3n+2)~figure{grid-column:span 3}
.gallery.cols-4{grid-template-columns:repeat(12,1fr)}
.gallery.cols-4>figure{grid-column:span 3}
.gallery.cols-4>figure:last-child:nth-child(4n+2){grid-column:span 12}
.gallery.cols-4>figure:last-child:nth-child(4n+2) img{aspect-ratio:3.2/1}
.gallery.cols-4>figure:nth-last-child(2):nth-child(4n+2),.gallery.cols-4>figure:nth-last-child(2):nth-child(4n+2)~figure{grid-column:span 6}
.gallery.cols-4>figure:nth-last-child(3):nth-child(4n+2),.gallery.cols-4>figure:nth-last-child(3):nth-child(4n+2)~figure{grid-column:span 4}
/* leftover cells: cards */
.cards:not(.cols-3):not(.cols-1)>.card:last-child:nth-child(odd){grid-column:1/-1}
.cards.cols-3{grid-template-columns:repeat(6,1fr)}
.cards.cols-3>.card{grid-column:span 2}
.cards.cols-3>.card:last-child:nth-child(3n+1){grid-column:span 6}
.cards.cols-3>.card:nth-last-child(2):nth-child(3n+1),.cards.cols-3>.card:nth-last-child(2):nth-child(3n+1)~.card{grid-column:span 3}
.notepg{height:auto;margin-top:calc(8mm/var(--z));position:relative;padding-top:calc(4mm/var(--z))}
.notepg .ln{height:calc(9mm/var(--z));border-bottom:1px solid var(--line)}
.notepg .nt{position:absolute;top:calc(-6mm/var(--z));left:0;font-family:var(--sans);font-size:7pt;letter-spacing:.3em;color:var(--mut)}
.halftitle{break-before:page;break-after:page;height:240mm;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.halftitle .ht-k{font-family:var(--sans);font-size:7.5pt;letter-spacing:.34em;color:var(--wine);font-weight:500;margin-bottom:10mm}
.halftitle h1{font-family:var(--serif);font-weight:600;font-size:30pt;letter-spacing:-.03em;margin:0 0 6mm;color:var(--ink)}
.halftitle .ht-s{font-family:var(--serif);font-size:10.5pt;color:var(--ink-2);margin:0 0 14mm}
.halftitle .ht-a{font-family:var(--sans);font-size:9.5pt;font-weight:500;margin:0}
.mk{display:block;height:0;line-height:0;font-size:5pt;color:rgba(0,0,0,0);font-family:monospace}
.part .photo.nophoto{background:linear-gradient(135deg,#5E1420,#7A1C2B 60%,#8E3242)}
.cover-kicker{font-family:var(--sans);font-size:7.5pt;letter-spacing:.34em;color:var(--wine);font-weight:500;margin-bottom:9mm}
.cover-title{font-family:var(--serif);font-weight:600;font-size:52pt;line-height:1.1;letter-spacing:-.04em;color:var(--ink);margin:0 0 7mm}
.cover-sub{font-family:var(--serif);font-size:12.5pt;color:var(--ink-2);margin:0 0 3mm;letter-spacing:-.01em}
.cover-author{font-family:var(--sans);font-size:10pt;color:var(--ink);margin:0;font-weight:500}
.keep{break-inside:avoid}
table.prompts td.pr{font-size:6.6pt;line-height:1.35;color:var(--mut)}
table.prompts td{vertical-align:top}
'''
def write_html(toc_html):
    open('book.html','w',encoding='utf-8').write(f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>영상 제작 실무 교본</title>
<link rel="stylesheet" href="book.css"><style>{CSS_EXTRA}</style></head><body>
{H.replace('<!--TOC-->',toc_html)}
</body></html>''')

def pagemap(pdf):
    txt=subprocess.run(['pdftotext','-layout',pdf,'-'],capture_output=True,text=True).stdout
    pages=txt.split('\f'); mp={}
    for i,pg_ in enumerate(pages,1):
        for mid in re.findall(r'\[\[MK:([^\]]+)\]\]',pg_): mp[mid]=i
    return mp,len(pages)-1

# ---- TOC structure
def short(t,n):
    t=t.strip()
    if len(t)>n:
        for sep in (' — ',' – ',': ','—'):
            if sep in t: t=t.split(sep)[0].strip(); break
    return t
def toc_html(first):
    def pg(mid):
        v=first.get(mid,'')
        return v-2 if isinstance(v,int) else v
    items=[]
    for m in re.finditer(r'<(?:article|section) class="(sec page|essay page|feature page prologue|feature page|part-end page|front page cont|front page)"[^>]*? id="([^"]+)"[^>]*>.*?(?:<div class="num">(.*?)</div>)?.*?<h(?:1|2)>(.*?)</h(?:1|2)>',H,flags=re.S):
        kind,mid,num,title=m.group(1),m.group(2),m.group(3) or '',m.group(4)
        title=re.sub(r'<br\s*/?>',' ',title); title=re.sub('<.*?>','',title).strip()
        if kind=='front page cont': continue
        items.append((kind,mid,re.sub('<.*?>','',num).strip(),title,m.start()))
    spreads=[(m.group(1),re.sub('<.*?>','',m.group(3)).strip(),m.start()) for m in re.finditer(r'<section class="page brk" id="([^"]+)">.*?<h2 class="spread-title"><small>(.*?)</small>(.*?)</h2>',H,flags=re.S)]
    parts_pos=[(m.start(),m.group(1),re.sub('<.*?>','',m.group(2))) for m in re.finditer(r'<section class="part" id="(part\d+)">.*?<h1>(.*?)</h1>',H,flags=re.S)]
    out=['<section class="front page toc-page" id="toc"><span class="mk">[[MK:toc]]</span><h1>차례</h1><div class="toc">']
    fp=parts_pos[0][0]
    out.append('<div class="p"><b>—</b><span>앞부속</span></div><ul>')
    for kind,mid,num,title,pos in items:
        if pos<fp and kind=='front page' and mid!='toc': out.append(f'<li><em>{pg(mid)}</em>{html.escape(title)}</li>')
    out.append('</ul>')
    pro=[it for it in items if it[4]<fp and it[0] in ('sec page','feature page prologue')]
    if pro:
        out.append(f'<div class="p"><b>00</b><span>프롤로그 — 화면의 기본 단위<em class="pg">{pg("prologue")}</em></span></div><ul>')
        for kind,mid,num,title,pos in pro:
            if kind=='sec page': out.append(f'<li><em>{pg(mid)}</em>{html.escape(num+" "+title)}</li>')
        out.append('</ul>')
    for i,(pos,pid,ptitle) in enumerate(parts_pos):
        end=parts_pos[i+1][0] if i+1<len(parts_pos) else len(H)
        old=int(pid.replace('part','')); n=NEWNUM.get(old,old)
        out.append(f'<div class="p"><b>{n:02d}</b><span>{html.escape(ptitle)}<em class="pg">{pg(pid)}</em></span></div><ul>')
        for kind,mid,num,title,ipos in items:
            if not (pos<=ipos<end) or kind.startswith('front'): continue
            cls={'essay page':'ess','feature page':'feat','part-end page':'end'}.get(kind,'')
            label=f'{num} ' if num and kind in('sec page','feature page') else ''
            if kind=='feature page': label=f'{num} 특집 · '; title=title.split(',')[0].split(' — ')[0]
            title=short(title,20)
            out.append(f'<li class="{cls}"><em>{pg(mid)}</em>{html.escape(label+title)}</li>')
            if kind=='feature page':
                nxt=min([x[4] for x in items if x[4]>ipos]+[end])
                for sid,stitle,spos in spreads:
                    if ipos<spos<nxt: out.append(f'<li class="sub"><em>{pg(sid)}</em>{html.escape(short(stitle,16))}</li>')
        out.append('</ul>')
    out.append('</div></section>')
    css='<style>.toc-page .toc li.sub{color:var(--mut);font-size:7.6pt}.toc li em{min-width:8mm;text-align:right;margin-right:1mm}.toc .p span{display:flex;justify-content:space-between;align-items:baseline}.toc .p span em.pg{font-style:normal;font-size:8pt;color:var(--mut);font-weight:400}.toc-page{break-before:page}.toc ul{column-count:2}</style>'
    return css+'\n'.join(out)

# pass 1: no TOC → map; pass 2: TOC with numbers; pass 3 if TOC page count changed
write_html(''); subprocess.run(['node','render.js','book.html','pass1.pdf'],check=True)
m1,n1=pagemap('pass1.pdf'); print('pass1',n1)
write_html(toc_html(m1)); subprocess.run(['node','render.js','book.html','pass2.pdf'],check=True)
m2,n2=pagemap('pass2.pdf'); print('pass2',n2)
shift=m2.get('part2',0)-m1.get('part2',0)
if shift:
    sh={k:v+shift for k,v in m1.items()}
    write_html(toc_html(sh)); subprocess.run(['node','render.js','book.html','pass2.pdf'],check=True)
    m2,n2=pagemap('pass2.pdf'); print('pass3',n2,'shift',shift)
# ---- recto-start for PART openers + signature padding (print imposition) ----
def blank_html(i): return f'<section class="blankpg" id="blank-{i}"><span class="mk">[[MK:blank-{i}]]</span></section>\n'
EPI={1:'카메라는 보는 기계가 아니라<br>고르는 기계다.',2:'좋은 촬영은<br>촬영 전날 밤에 이미 끝나 있다.',3:'빛을 셀 줄 알면<br>카메라는 더 이상 블랙박스가 아니다.',4:'조명은 밝히는 일이 아니라<br>어둠을 배치하는 일이다.',5:'컷은 자르는 자리가 아니라<br>관객이 숨을 쉬는 자리다.',6:'화면이 벽을 떠나는 순간,<br>관객이 카메라가 된다.',7:'광고는 15초를 파는 일이 아니라<br>15초 뒤에 남을 기억을 파는 일이다.',8:'알고리즘은 취향이 없다.<br>취향은 끝까지 사람의 몫이다.',9:'시장은 기술을 따라가지 않는다.<br>습관을 따라간다.',10:'포트폴리오는 잘한 것의 목록이 아니라<br>다음에 맡길 수 있다는 증거다.',11:'도구가 바뀌어도 바뀌지 않는 것 —<br>눈, 약속, 마무리.',12:'모든 영상은 질문 하나로 시작한다.<br>누가, 왜 보는가.',13:'기술은 재료다.<br>작품은 재료를 다루는 태도에서 나온다.',14:'현장의 서류는<br>기억보다 오래 남는다.'}
def epi_html(i,n): return f'<section class="blankpg epi" id="blank-{i}"><span class="mk">[[MK:blank-{i}]]</span><div class="q"><small>PART {n:02d}</small><p>{EPI.get(n,"")}</p></div></section>\n'
openers=sorted([(m2[f'part{o}'],f'part{o}') for o in NEW_ORDER if f'part{o}' in m2])
ins_pages=[]; c=0; k=0
for p,pid in openers:
    if (p+c)%2==0:
        H=H.replace(f'<section class="part" id="{pid}">',epi_html(k,NEWNUM[int(pid[4:])])+f'<section class="part" id="{pid}">',1)
        ins_pages.append(p); c+=1; k+=1
# signature padding: the printer imposes in 8-page signatures, so the whole PDF (covers included) must be a
# multiple of 8 pages. NOTE pages fill the gap, then one 표3 blank before the back cover: total + pad + 1 = 0 (mod 8)
SIG=8
total=n2+c
pad=(-(total+1))%SIG
def note_html(i): return f'<section class="blankpg notepg" id="blank-{i}"><span class="mk">[[MK:blank-{i}]]</span><div class="nt">NOTE</div>'+'<div class="ln"></div>'*25+'</section>\n'
tail=''.join(note_html(k+i) for i in range(pad))+blank_html(k+pad)
H=H.replace('<section class="backcover"',tail+'<section class="backcover"',1)
pred={mid:p+sum(1 for ip in ins_pages if ip<=p) for mid,p in m2.items()}
write_html(toc_html(pred)); subprocess.run(['node','render.js','book.html','pass2.pdf'],check=True)
m3,n3=pagemap('pass2.pdf'); print('pass4 (recto/pad)',n3,'blanks before parts',c,'pad',pad+1)
if any(m3.get(k_)!=v for k_,v in pred.items()):
    print('!! prediction mismatch, re-render with measured map'); write_html(toc_html(m3)); subprocess.run(['node','render.js','book.html','pass2.pdf'],check=True); m3,n3=pagemap('pass2.pdf')
m2,n2=m3,n3
print('PART opener pages (should all be odd):',[(pid,m2[pid]) for _,pid in openers])
print('total pages',n2,'| multiple of',SIG,'OK' if n2%SIG==0 else '!! NO')
# ---- chapter-end memo filler: measure leftover on each chapter's last page and fill with ruled memo lines
import shutil
from PIL import Image
import numpy as np
shutil.rmtree('lo_m',ignore_errors=True); os.makedirs('lo_m')
subprocess.run(['pdftoppm','-r','12','-gray','-png','pass2.pdf','lo_m/p'],check=True)
def leftover(p):
    f=f'lo_m/p-{p:03d}.png'
    if not os.path.exists(f): f=f'lo_m/p-{p:04d}.png'
    a=np.asarray(Image.open(f).convert('L')); h,w=a.shape
    body=a[int(h*17/297):int(h*(297-22)/297), int(w*22/210):int(w*188/210)]
    rows=(body<235).any(axis=1)
    return 258 if not rows.any() else (len(rows)-1-np.where(rows)[0].max())/len(rows)*258
blankpages={p for mid,p in m2.items() if mid.startswith('blank-')}
openers=sorted([(m2[f'part{o}'],f'part{o}') for o in NEW_ORDER if f'part{o}' in m2])
memos=0
for p,pid in openers:
    q=p-1
    while q in blankpages: q-=1
    if q<=m2.get('toc',0): continue
    gap=leftover(q)
    n=NEWNUM[int(pid[4:])]
    hmm=gap-10
    if hmm<40: continue
    lines=int((hmm-22)/9)
    lab_=('MEMO · 프롤로그' if n==1 else f'MEMO · PART {n-1:02d}')
    memo=f'<section class="memo"><small>{lab_}</small>'+'<div class="ln"></div>'*lines+'</section>\n'
    key=f'<section class="blankpg epi" id="blank-'
    # insert before the epigraph (if any) that precedes this opener, else before the opener
    i=H.find(f'<section class="part" id="{pid}">')
    j=H.rfind(key,0,i)
    if j>0 and H.find('</section>',j)+10>=i-2: pass
    else: j=i
    if j<0: continue
    H=H[:j]+memo+H[j:]; memos+=1; print('memo',pid,'page',q,'gap',round(gap),'lines',lines)
print('memo blocks inserted',memos)
if memos:
    def memo_ok():
        write_html(toc_html(m2)); subprocess.run(['node','render.js','book.html','pass2.pdf'],check=True)
        m5,n5=pagemap('pass2.pdf')
        ok = n5==n2 and all(m5.get(k_)==v for k_,v in m2.items() if k_.startswith('part'))
        return ok,m5,n5
    ok,m5,n5=memo_ok()
    tries=0
    while not ok and tries<8:
        tries+=1
        shifted=[k_ for k_,v in m2.items() if k_.startswith('part') and m5.get(k_)!=v]
        shifted.sort(key=lambda k_:m2[k_])
        first=shifted[0] if shifted else None
        if first is None: break
        n=NEWNUM[int(first[4:])]
        lab=('MEMO · 프롤로그' if n==1 else f'MEMO · PART {n-1:02d}')
        if lab not in H:
            # culprit may be the memo before the previous opener
            prev=[k_ for k_ in m2 if k_.startswith('part') and m2[k_]<m2[first]]
            prev.sort(key=lambda k_:m2[k_])
            lab=f'MEMO · PART {NEWNUM[int(prev[-1][4:])]-1:02d}' if prev else lab
        print('!! memo shifted pages at',first,'→ removing',lab)
        H2=re.sub(r'<section class="memo"><small>'+re.escape(lab)+r'</small>(?:<div class="ln"></div>)*</section>\n','',H)
        if H2==H: break
        H=H2; ok,m5,n5=memo_ok()
    if not ok:
        print('!! memos removed'); H=re.sub(r'<section class="memo">.*?</section>\n','',H,flags=re.S); ok,m5,n5=memo_ok()
    m2,n2=m5,n5
json.dump(m2,open('pagemap.json','w'),ensure_ascii=False,indent=0)
N=n2

# ---- running heads overlay
part_start=sorted([(m2[f'part{o}'],NEWNUM[o]) for o in NEW_ORDER if f'part{o}' in m2])
skip={1,N}|{p for p,_ in part_start}|{p for mid,p in m2.items() if mid.startswith('blank') or mid=='halftitle'}
sec_titles={}
for m in re.finditer(r'<article class="sec page"[^>]*? id="([^"]+)"[^>]*>.*?<h2>(.*?)</h2>',H,flags=re.S):
    sec_titles[m.group(1)]=re.sub('<.*?>','',m.group(2)).strip()
for m in re.finditer(r'<section class="feature page[^"]*" id="([^"]+)">.*?<h2>(.*?)</h2>',H,flags=re.S):
    sec_titles[m.group(1)]='특집 · '+re.sub(r'<br\s*/?>',' ',re.sub('<.*?>','',m.group(2))).strip()
marks_by_page={}
for mid,p in m2.items(): marks_by_page.setdefault(p,[]).append(mid)
page_sec={}; cur=''
for p in range(1,N+1):
    for mid in marks_by_page.get(p,[]):
        if mid in sec_titles: cur=sec_titles[mid]
        elif mid.startswith(('part','essay','end','toc')): cur=''
    page_sec[p]=cur
def part_of(p):
    n=0
    for sp,pn in part_start:
        if sp<=p: n=pn
    return n
pro_pages=set(range(m2.get('prologue',10**9),part_start[0][0])) if 'prologue' in m2 else set()
ov=['<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4;margin:0}body{margin:0;font-family:"Noto Sans CJK KR"}.pg{width:210mm;height:297mm;position:relative;break-after:page}.rh{position:absolute;top:9.5mm;left:24mm;right:24mm;display:flex;justify-content:space-between;font-size:7pt;color:#7A7A80;letter-spacing:.06em}.rh b{font-weight:500;color:#1B1B1D}.rh .pt{color:#7A1C2B;font-weight:500;margin-right:2.5mm}.pn{position:absolute;bottom:10mm;font-size:8.5pt;color:#1B1B1D;font-weight:500}.pn.l{left:24mm}.pn.r{right:24mm}.ft{position:absolute;bottom:10.3mm;font-size:6.8pt;color:#A8A8AE;letter-spacing:.1em}.ft.l{left:24mm}.ft.r{right:24mm}.ft .pt{color:#7A1C2B;margin-right:2.5mm}</style></head><body>']
for p in range(1,N+1):
    if p in skip: ov.append('<div class="pg"></div>'); continue
    n=part_of(p); even=(p%2==0)
    left_txt='영상 제작 실무 교본'
    right_txt=(f'<span class="pt">PART {n:02d}</span>{NEW_TITLES[n]}' if n else ('<span class="pt">프롤로그</span>화면의 기본 단위' if p in pro_pages else ''))
    sec=page_sec.get(p,'')
    if even:
        ov.append(f'<div class="pg"><div class="rh"><span><b>{left_txt}</b></span><span>{html.escape(sec)}</span></div><div class="pn l">{p-2}</div><div class="ft r">{right_txt}</div></div>')
    else:
        ov.append(f'<div class="pg"><div class="rh"><span>{html.escape(sec)}</span><span>{right_txt}</span></div><div class="pn r">{p-2}</div><div class="ft l">{left_txt}</div></div>')
ov.append('</body></html>')
open('overlay.html','w',encoding='utf-8').write('\n'.join(ov))
subprocess.run(['node','render_plain.js','overlay.html','overlay.pdf'],check=True)
from pypdf import PdfReader, PdfWriter
# ---- full-bleed covers rendered separately (zero margins) ----
cov_html=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="book.css"><style>
@page{{size:A4;margin:0}} body{{margin:0}} .pg{{width:210mm;height:297mm;position:relative;overflow:hidden;break-after:page;background:#fff}}
.pg img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(.6)}}
.ft{{position:absolute;left:24mm;bottom:30mm;width:130mm}}
.ft .k{{font-family:var(--sans);font-size:7.5pt;letter-spacing:.34em;color:var(--wine);font-weight:500;margin-bottom:8mm}}
.ft h1{{font-family:var(--serif);font-weight:600;font-size:56pt;line-height:1.08;letter-spacing:-.04em;color:var(--ink);margin:0 0 8mm}}
.ft .s{{font-family:var(--serif);font-size:12pt;color:var(--ink-2);margin:0 0 4mm;letter-spacing:-.01em}}
.ft .a{{font-family:var(--sans);font-size:10.5pt;color:var(--ink);font-weight:500;margin:0}}
.bk{{position:absolute;left:28mm;top:110mm;width:118mm}}
.bk .l{{font-family:var(--serif);font-size:16.5pt;line-height:1.5;color:var(--ink);font-weight:500;letter-spacing:-.02em;margin:0 0 9mm}}
.bk .b{{font-family:var(--serif);font-size:9.8pt;line-height:1.9;color:var(--ink-2);margin:0 0 9mm;text-align:justify}}
.bk .a{{font-family:var(--sans);font-size:9pt;color:var(--ink);font-weight:500;margin:0}}
.bk .isbn{{position:absolute;left:0;top:150mm;font-family:var(--sans);font-size:7pt;color:var(--mut);letter-spacing:.08em}}
</style></head><body>
<div class="pg"><img src="{cover_img}"><div class="ft"><div class="k">VIDEO PRODUCTION · A PRACTICAL TEXTBOOK</div><h1>영상 제작<br>실무 교본</h1><p class="s">기획에서 납품까지, 수업과 현장에서 함께 펼치는 13개 챕터</p><p class="a">안지아</p></div></div>
<div class="pg"><img src="{back_img}"><div class="bk"><p class="l">영상은 찍는 일이 아니라<br>보여 줄 것과 감출 것을 고르는 일이다.</p><p class="b">스토리보드 한 칸에서 LED 파사드까지, 첫 콜타임에서 첫 릴까지. 이 책은 기법의 목록이 아니라 현장에서 내리는 판단의 순서를 담았다. 실습을 먼저 하고 이론은 뒤에 두었으며, 모든 도판은 "왜 이렇게 찍는가"에 답하도록 다시 그렸다. 생성형 AI가 공정에 들어온 지금, 바뀌지 않는 것 — 눈, 약속, 마무리 — 을 연습하는 책이다.</p><p class="a">안지아 지음</p></div></div>
</body></html>'''
open('covers.html','w',encoding='utf-8').write(cov_html)
subprocess.run(['node','render_plain.js','covers.html','covers.pdf'],check=True)
base=PdfReader('pass2.pdf'); over=PdfReader('overlay.pdf'); cov=PdfReader('covers.pdf'); w=PdfWriter()
for i,page in enumerate(base.pages):
    if i==0: w.add_page(cov.pages[0]); continue
    if i==len(base.pages)-1: w.add_page(cov.pages[1]); continue
    if i<len(over.pages): page.merge_page(over.pages[i])
    w.add_page(page)
w.add_metadata({'/Title':'영상 제작 실무 교본 — 재디자인판','/Author':'안지아'})
with open('영상제작실무교본_재디자인.pdf','wb') as f: w.write(f)
missing=[k for k in PLAN if k not in USED]
print('pages',N,'| placeholders in plan not placed:',len(missing),missing[:20],'| have files:',len(HAVE))

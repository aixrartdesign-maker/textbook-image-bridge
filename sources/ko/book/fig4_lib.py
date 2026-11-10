# -*- coding: utf-8 -*-
"""Round-4 figure builders (PART 3/4/5). Imported by fig_compose4.py and export."""
import math
from glyphs import profile, figure, camera_side, person_top, camera_top, light_top, softbox_top
I=lambda k:f'img_new/{k}.jpg'
SV='xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans CJK KR"'
WINE='#7A1C2B'; INK='#1B1B1D'; INK2='#3C3C40'; MUT='#7A7A80'; LINE='#D9D9DE'; CARD='#F6F5F3'; CARD2='#E5E3DE'
def it(k,title,sub='',num='',img=True):
    n=f'<i>{num}</i>' if num else ''
    src=f'<img src="{I(k)}" alt="">' if img else k
    return f'<div class="it">{src}<b>{n}{title}</b>{f"<span>{sub}</span>" if sub else ""}</div>'
def fig(inner,cap,cls='fg wide',ttl=''):
    t=f'<div class="ttl">{ttl}</div>' if ttl else ''
    return f'<figure class="{cls}">{t}{inner}<figcaption>{cap}</figcaption></figure>'
def facts(title,lines,title2=None,lines2=None):
    s=f'<div class="facts"><b>{title}</b>'+''.join(f'<span>{l}</span>' for l in lines)
    if title2: s+=f'<b>{title2}</b>'+''.join(f'<span>{l}</span>' for l in lines2)
    return s+'</div>'

# ---------- 그림 30 노출 삼각형 ----------
def tri_svg(a,s,i):
    # three vertical sliders: aperture, shutter, iso. values 0..1
    s_=f'<svg viewBox="0 0 240 150" {SV} font-size="9"><rect width="240" height="150" fill="{CARD}"/>'
    for n,(lab,v,lo,hi) in enumerate([('조리개',a,'f/16','f/1.8'),('셔터',s,'1/1000','1/15'),('ISO',i,'100','6400')]):
        x=40+n*80
        s_+=f'<line x1="{x}" y1="28" x2="{x}" y2="118" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
        y=118-90*v
        s_+=f'<line x1="{x}" y1="118" x2="{x}" y2="{y}" stroke="{WINE}" stroke-width="6" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="6" fill="#fff" stroke="{WINE}" stroke-width="2"/>'
        s_+=f'<text x="{x}" y="18" text-anchor="middle" font-weight="500" fill="{INK}">{lab}</text><text x="{x}" y="134" text-anchor="middle" fill="{MUT}" font-size="8">{lo}</text><text x="{x}" y="{y-10}" text-anchor="middle" fill="{WINE}" font-size="8" font-weight="500">{hi if v>0.6 else ""}</text>'
    return s_+'</svg>'
def F30():
    cols=[('EXP-SHALLOW','조리개를 열었다','f/1.8 · 1/1000 · ISO 100','배경이 흐려진다 — 심도가 얕아진 대가',(1,0,0)),
          ('EXP-NOISE','ISO를 올렸다','f/16 · 1/1000 · ISO 6400','어두운 부분에 노이즈 — 민감도의 대가',(0,0,1)),
          ('EXP-BLUR','셔터를 늦췄다','f/16 · 1/15 · ISO 100','물줄기가 흐른다 — 시간의 대가',(0,1,0))]
    g='<div class="grid c3">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b><span class="mono">{v}</span><span>{d}</span>{tri_svg(*tv)}</div>' for k,t,v,d,tv in cols)+'</div>'
    rule=f'<div class="rulebar"><b>세 장 모두 같은 밝기다.</b> 빛의 양은 같지만 어디서 값을 치렀는지가 다르다 — <b>조리개</b>는 심도로, <b>셔터</b>는 흔들림으로, <b>ISO</b>는 노이즈로. 하나를 두 배 열면 다른 하나를 반으로 닫는다(1스톱).</div>'
    return fig(g+rule,'<b>그림 30</b> 노출 삼각형 — 같은 장면, 같은 밝기, 세 가지 다른 선택. 슬라이더는 어떤 값을 끝까지 밀었는지를 보여 준다.',ttl='같은 밝기, 다른 그림 — 셋 중 하나를 바꾸면 나머지 하나로 되갚는다')
# ---------- 그림 31 심도 ----------
def F31():
    cols=[('DOF-F14','f/1.4 · 얕은 심도','인물만 남고 배경이 녹는다 — 집중 · 감정 · 뷰티'),('DOF-F4','f/4 · 중간 심도','인물이 또렷하고 배경은 분위기로 — 인터뷰 · 드라마의 기본'),('DOF-F11','f/11 · 깊은 심도','앞뒤가 모두 선명 — 풍경 · 제품 전체 · 정보 전달')]
    g='<div class="grid c3">'+''.join(it(k,t,s) for k,t,s in cols)+'</div>'
    chips='<div class="chips"><b>심도를 얕게 만드는 네 가지</b><span>조리개를 연다 f/1.4</span><span>렌즈를 길게 85→200mm</span><span>피사체에 다가간다</span><span>배경을 멀리 둔다</span></div>'
    return fig(g+chips,'<b>그림 31</b> 조리개에 따른 심도 — 같은 자리, 같은 사람, 조리개만 바꿨다. 심도는 "어디까지 선명하게 둘 것인가"에 대한 연출 결정이다.',ttl='조리개 숫자가 작을수록 선명한 구간이 얇아진다')
# ---------- 그림 32/33 해상도·화면비 ----------
def F32():
    svg=f'<svg viewBox="0 0 320 180" {SV} font-size="9"><rect width="320" height="180" fill="{CARD}"/>'
    for w,h,lab,op in [(300,168,'8K 7680×4320',.08),(225,126,'6K 6144×3456',.12),(150,84,'4K UHD 3840×2160',.2),(75,42,'FHD 1920×1080',.4),(50,28,'HD 1280×720',.6)]:
        svg+=f'<rect x="10" y="{176-h}" width="{w}" height="{h}" fill="{WINE}" opacity="{op}" stroke="{WINE}" stroke-width=".8"/><text x="{14}" y="{176-h+11}" font-size="8" fill="{INK}" font-weight="500">{lab}</text>'
    svg+='</svg>'
    crop=f'<div class="crop4k"><img src="{I("DOF-F11")}"><i class="fhd"></i><em class="l4k">4K로 촬영한 전체 프레임</em><em class="lfhd">FHD 납품 크기 — 2배 확대해도 선명</em></div>'
    return fig(f'<div class="grid plan">{crop}<div>{svg}{facts("해상도 = 가로 × 세로 점의 수",["4K는 FHD의 4배 — 가로 2배 × 세로 2배","같은 모니터면 4K가 더 촘촘하고, 같은 점 수면 큰 화면일수록 거칠다","최종이 FHD여도 4K로 찍는다 — 여유 화소가 편집에서 크롭·줌·안정화의 자유가 된다"])}</div></div>',
        '<b>그림 32</b> 해상도 체계 — 4K 프레임 안의 FHD. 붉은 틀 안이 FHD 한 장 크기이며, 4K 원본에서는 이 틀을 어디로든 옮겨 쓸 수 있다.',ttl='해상도는 "몇 개의 점으로 그리는가"다')
def F33():
    rows=[('SB1-43','4:3','1.33 · 레트로 TV · 회상 장면'),('SB1-169','16:9','1.78 · 유튜브 · TV · 기본'),('SB1-219','21:9','2.39 · 영화 · 레터박스'),('SB1-11','1:1','피드 · 썸네일'),('SB1-916','9:16','숏폼 · 세로 LED')]
    g='<div class="rrow bottom">'+''.join(f'<div class="rb" style="height:{48 if k in ("SB1-11","SB1-916") else 40}mm"><img src="{I(k)}"><b>{r}</b><span>{s}</span></div>' for k,r,s in rows)+'</div>'
    return fig(g+'<div class="rulebar">화면비는 "가로를 세로로 나눈 값"이다. 같은 장면도 비율이 바뀌면 인물의 크기와 배경의 몫이 달라진다 — 납품 비율로 처음부터 찍는다.</div>',
        '<b>그림 33</b> 주요 화면비 — 같은 장면을 다섯 비율로 잘라 본 것. 가로형은 공간을, 세로형은 인물을 보여 준다.',ttl='화면비 — 가로를 세로로 나눈 값')
# ---------- 그림 35 셔터앵글 ----------
def disc(deg):
    r=22; cx=cy=26
    if deg>=360: return f'<svg viewBox="0 0 52 52" {SV}><circle cx="{cx}" cy="{cy}" r="{r}" fill="{WINE}"/></svg>'
    a=math.radians(deg); x=cx+r*math.sin(a); y=cy-r*math.cos(a); large=1 if deg>180 else 0
    return f'<svg viewBox="0 0 52 52" {SV}><circle cx="{cx}" cy="{cy}" r="{r}" fill="{CARD2}"/><path d="M{cx},{cy} L{cx},{cy-r} A{r},{r} 0 {large},1 {x:.1f},{y:.1f} Z" fill="{WINE}"/></svg>'
def F35():
    cols=[('SA-45','45°','1/192초','뚝뚝 끊기는 선명함 — 전투 · 폭발 · 과장된 긴박',45),('SA-180','180°','1/48초','자연스러운 잔상 — 영화의 기본값',180),('SA-360','360°','1/24초','길게 번지는 흐름 — 꿈 · 취기 · 회상',360)]
    g='<div class="grid c3">'+''.join(f'<div class="it"><img src="{I(k)}"><div class="discrow">{disc(d)}<div><b>{a} <small>{t}</small></b><span>{s}</span></div></div></div>' for k,a,t,s,d in cols)+'</div>'
    rule='<div class="rulebar"><b>셔터앵글</b>은 회전 셔터가 열려 있는 각도다. 한 프레임(1/24초) 중 열린 비율만큼 빛이 들어오고, 그만큼 움직임이 번진다. <b>규칙: 셔터 속도 = 1 ÷ (fps × 2)</b> → 24fps는 1/48, 60fps는 1/120. 영상에서 셔터는 밝기가 아니라 <b>잔상의 양</b>을 정하는 값이다 — 밝기는 ND 필터로 맞춘다.</div>'
    return fig(g+rule,'<b>그림 35</b> 셔터앵글과 잔상 (24fps 기준) — 원의 붉은 부분이 셔터가 열린 시간이다. 각도가 클수록 한 프레임에 담기는 움직임이 길어진다.',ttl='셔터앵글 — 한 프레임 동안 셔터가 열려 있는 비율')
# ---------- 그림 36 색온도 ----------
def F36():
    srcs=[('LS-CANDLE','1,900K','촛불'),('LS-TUNGSTEN','3,200K','텅스텐 · 백열등'),('LS-FLUO','4,200K','형광등'),('LS-SUN','5,600K','한낮 태양 · LED 주광'),('LS-OVERCAST','6,500K','흐린 날'),('LS-SHADE','8,000K','그늘 · 푸른 하늘빛')]
    bar=f'<svg viewBox="0 0 600 22" {SV} preserveAspectRatio="none"><defs><linearGradient id="kg"><stop offset="0" stop-color="#F0A24B"/><stop offset=".35" stop-color="#F5D9A8"/><stop offset=".6" stop-color="#FFFFFF"/><stop offset="1" stop-color="#9FBBDD"/></linearGradient></defs><rect width="600" height="22" fill="url(#kg)"/></svg>'
    g='<div class="grid c6">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b><span>{s}</span></div>' for k,t,s in srcs)+'</div>'
    ends='<div class="ends"><span>따뜻하다 — 주황 · 숫자가 낮다</span><span>차갑다 — 파랑 · 숫자가 높다</span></div>'
    return fig(ends+bar+g,'<b>그림 36</b> 광원별 색온도 — 같은 "흰 빛"이라도 광원마다 색이 다르다. 숫자가 낮을수록 붉고, 높을수록 푸르다.',ttl='빛에는 색이 있다 — 켈빈(K)으로 읽는다')
# ---------- 그림 37 WB ----------
def F37():
    hdr='<div class="wbhead"><span></span><b>WB 3200K</b><b>WB 5600K</b><b>WB 7500K</b></div>'
    def row(label,sub,keys,ok):
        cells=''.join(f'<div class="it{" ok" if i==ok else ""}"><img src="{I(k)}">{"<em>정확</em>" if i==ok else ""}<span>{c}</span></div>' for i,(k,c) in enumerate(keys))
        return f'<div class="wbrow"><div class="lab2"><b>{label}</b><span>{sub}</span></div>{cells}</div>'
    r1=row('텅스텐 조명 아래','3200K 광원',[('WB-TUNG-3200','흰 것이 희게'),('WB-TUNG-5600','주황빛으로'),('WB-TUNG-7500','더 주황빛으로')],0)
    r2=row('주광 아래','5600K 광원',[('WB-DAY-3200','푸르게'),('WB-DAY-5600','흰 것이 희게'),('WB-DAY-7500','주황빛으로')],1)
    rule='<div class="rulebar">카메라의 WB 값이 광원보다 <b>낮으면 푸르게</b>, <b>높으면 주황으로</b> 찍힌다. 어긋남은 의도적으로 쓴다 — 새벽의 푸름, 밤의 따뜻함. 다만 한 씬 안에서는 반드시 하나로 통일한다.</div>'
    return fig(hdr+r1+r2+rule,'<b>그림 37</b> 화이트밸런스 — 광원의 색온도와 카메라 설정이 같을 때만 흰 종이가 희게 찍힌다. 같은 사진에서 WB 값만 바꾼 결과.',ttl='광원과 카메라 설정이 같을 때만 흰 것이 희게 찍힌다')
# ---------- 렌즈 트리오 ----------
def LENS():
    g=f'<div class="grid lens"><img src="{I("LENS-SONY")}"><div class="facts"><b>55 mm — 눈으로 보는 거리감</b><span>인터뷰 · 제품 · 브이로그. 왜곡 없음, 밝고 가볍다. 하나만 산다면 이것</span><b>85 mm — 얼굴이 가장 예쁜 거리</b><span>클로즈업 · 뷰티. 배경이 크게 흐려지고 얼굴이 납작하게 정리된다. 작은 방에선 뒤로 물러설 자리가 필요</span><b>200 mm — 멀리서 끌어당긴다</b><span>무대 · 스포츠 · 다큐 관찰. 배경이 압축되어 바짝 붙어 보인다. 흔들림이 크니 삼각대·모노포드</span></div></div>'
    return fig(g,'<b>참고</b> 풀프레임 미러리스용 55 · 85 · 200 — 숫자(초점거리)가 커질수록 화각은 좁아지고 피사체와의 거리는 멀어진다. 어떤 렌즈를 고르느냐는 "관객을 인물에서 몇 m 떨어뜨릴 것인가"를 고르는 일이다.',ttl='렌즈 세 개로 끝내기 — 55 · 85 · 200')
# ---------- PART 4 ----------
def isq_svg():
    s=f'<svg viewBox="0 0 320 120" {SV} font-size="9"><rect width="320" height="120" fill="{CARD}"/><circle cx="22" cy="60" r="7" fill="{WINE}"/><text x="22" y="84" text-anchor="middle" fill="{MUT}" font-size="8">광원</text>'
    for d,sz,pct in [(1,14,'100%'),(2,28,'25%'),(3,42,'11%'),(4,56,'6%')]:
        x=60+(d-1)*68; op=1.0/(d*d)
        s+=f'<rect x="{x-sz/2}" y="{60-sz/2}" width="{sz}" height="{sz}" fill="{WINE}" opacity="{0.15+0.8*op}" stroke="{WINE}" stroke-width=".8"/><text x="{x}" y="{60+sz/2+12}" text-anchor="middle" fill="{INK}" font-weight="500">{d} m</text><text x="{x}" y="{60-sz/2-6}" text-anchor="middle" fill="{WINE}" font-weight="500">{pct}</text>'
        s+=f'<line x1="29" y1="60" x2="{x-sz/2}" y2="{60-sz/2}" stroke="{LINE}" stroke-width=".6"/><line x1="29" y1="60" x2="{x-sz/2}" y2="{60+sz/2}" stroke="{LINE}" stroke-width=".6"/>'
    return s+'</svg>'
def F38():
    g='<div class="grid c3">'+it('ISQ-STAGE','무대 — 스포트라이트 아래','발밑은 하얗고 두 걸음 밖은 어둠. 배우가 반 발만 벗어나도 얼굴이 꺼진다')+it('ISQ-CAR','밤길 — 헤드라이트','바로 앞 10 m는 환하고 그 뒤는 급히 사라진다. 가까운 빛은 가파르게 떨어진다')+it('ISQ-WINDOW','방 — 창가의 빛','창에 붙은 자리와 방 안쪽의 밝기 차가 수 스톱. 인물을 창에 붙이면 배경이 어두워진다')+'</div>'
    g+=f'<div class="grid plan">{isq_svg()}{facts("거리가 두 배 → 밝기는 1/4",["같은 빛이 네 배 넓은 면에 퍼지기 때문","가까운 조명은 가파르게, 먼 조명은 완만하게 떨어진다"],"현장에서 쓰는 법",["배경을 어둡게: 조명을 인물 가까이 (배경은 금세 어두워진다)","인물과 배경을 비슷하게: 조명을 멀리 두고 출력을 올린다","인물이 움직이는 컷: 조명을 멀리 — 한두 걸음에 밝기가 튀지 않는다"])}</div>'
    return fig(g,'<b>그림 38</b> 역제곱 법칙 — 거리가 두 배가 되면 빛은 네 배 넓은 면에 퍼져 1/4로 어두워진다. 무대·도로·창가에서 눈으로 보는 같은 법칙.',ttl='거리가 두 배가 되면 빛은 네 배 넓은 면에 퍼진다')
def plan3():
    s=f'<svg viewBox="0 0 320 246" {SV} font-size="9.5"><rect width="320" height="246" fill="{CARD}"/><rect x="60" y="14" width="200" height="7" fill="#B9B5AC"/><text x="160" y="34" text-anchor="middle" fill="{MUT}" font-size="8.5">배경</text>'
    s+=person_top(160,120,r=11,angle=180)+f'<text x="160" y="146" text-anchor="middle">인물</text>'
    s+=camera_top(160,204,w=24,fill=WINE)+f'<text x="160" y="241" text-anchor="middle" fill="{WINE}" font-weight="500">카메라</text>'
    # key 45 left-front
    s+=f'<polygon points="160,120 70,180 100,205" fill="{WINE}" opacity=".12"/>{softbox_top(78,192,w=22,fill=WINE,angle=45)}<text x="52" y="214" fill="{WINE}" font-weight="500">키 KEY</text><text x="52" y="224" fill="{MUT}" font-size="8">45° · 눈높이보다 조금 위</text>'
    # fill right-front
    s+=f'<polygon points="160,120 250,180 230,200" fill="#B9B5AC" opacity=".25"/>{light_top(242,192,r=7,fill=INK,angle=-45,hollow=True)}<text x="232" y="214" fill="{INK}" font-weight="500">필 FILL</text><text x="218" y="224" fill="{MUT}" font-size="8">키의 반대쪽 · 키의 ½~¼</text>'
    # back light
    s+=f'<polygon points="160,120 230,48 246,66" fill="#B9B5AC" opacity=".25"/>{light_top(240,56,r=7,fill=INK,angle=-135)}<text x="252" y="50" fill="{INK}" font-weight="500">백 BACK</text><text x="252" y="60" fill="{MUT}" font-size="8">뒤 위에서 머리·어깨 윤곽</text>'
    return s+'</svg>'
def F39():
    g=f'<div class="grid blk"><div class="it">{plan3()}<b>위에서 본 배치</b><span>키를 먼저 놓고, 그림자를 필로 달래고, 백으로 떼어낸다 — 조명은 개수가 아니라 순서다</span></div>'+it('3PT-SET','현장에서 — 같은 배치','왼쪽 소프트박스가 키, 오른쪽 작은 등이 필, 뒤쪽 높은 등이 백라이트')+'</div>'
    return fig(g,'<b>그림 39</b> 3점 조명 — 평면 배치와 실제 세팅. 결과 사진은 아래 참고 사진 4.2A(키만 → 키+필 → 키+필+백 → 백만).',ttl='키를 먼저 놓고, 그림자를 필로 달래고, 백으로 떼어낸다')
def keytop(angle,elev='',cam=True,back=False):
    # top view: subject center, camera bottom, key light at angle (deg from camera axis, + = subject's left/camera-left)
    s=f'<svg viewBox="0 0 120 120" {SV} font-size="8"><rect width="120" height="120" fill="{CARD}"/>'+person_top(60,56,r=9,angle=180)+camera_top(60,102,w=14,fill=MUT)
    if back:
        s+=light_top(60,14,r=5,fill=WINE,angle=180)+f'<polygon points="60,20 50,47 70,47" fill="{WINE}" opacity=".2"/>'
    else:
        a=math.radians(180-angle); x=60+40*math.sin(a); y=56+40*math.cos(a)
        # light at (x,y) pointing to subject
        s+=f'<polygon points="{x:.1f},{y:.1f} {60+9*math.cos(a):.1f},{56-9*math.sin(a):.1f} {60-9*math.cos(a):.1f},{56+9*math.sin(a):.1f}" fill="{WINE}" opacity=".2"/>'+light_top(x,y,r=5,fill=WINE,angle=180-angle)
        if angle: s+=f'<text x="{x:.1f}" y="{y+16:.1f}" text-anchor="middle" fill="{WINE}" font-weight="500">{angle}°</text>'
    if elev: s+=f'<text x="60" y="118" text-anchor="middle" fill="{MUT}">{elev}</text>'
    return s+'</svg>'
def F40():
    cols=[('LOOK-FLAT','플랫 FLAT',0,'카메라 옆 · 눈높이','그림자 없음 — 밝고 평평, 뉴스 · 뷰티'),('P04-LOOK-LOOP','루프 LOOP',35,'35° · 조금 위','코 옆에 작은 고리 그림자 — 가장 무난'),('P04-LOOK-REMBRANDT','렘브란트',45,'45° · 45° 위','뺨에 빛 삼각형 — 깊이, 드라마'),('P04-LOOK-SPLIT','스플릿 SPLIT',90,'90° · 눈높이','얼굴이 반으로 — 갈등, 양면성'),('P04-LOOK-BUTTERFLY','버터플라이',0,'정면 · 높이 위','코 밑 나비 그림자 — 광대, 글래머'),('P04-LOOK-RIM','림 RIM',0,'뒤쪽 · 위','윤곽선만 — 실루엣, 신비')]
    g='<div class="grid c6">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b>{keytop(a,e,back=(t.startswith("림")))}<span>{s}</span></div>' for k,t,a,e,s in cols)+'</div>'
    return fig(g,'<b>그림 40</b> 키라이트 위치에 따른 인물 조명 6패턴 — 조명 하나의 위치만 다르다. 아래 평면도의 붉은 점이 키라이트, 회색 사각형이 카메라.',ttl='키라이트를 어디에 두느냐가 얼굴의 인상을 정한다')
def F41():
    cols=[('RATIO-2','2 : 1','1스톱 차이','밝고 편안 — 광고 · 뷰티 · 정보 전달'),('RATIO-4','4 : 1','2스톱 차이','표준 인물 — 인터뷰 · 드라마의 기본'),('RATIO-8','8 : 1','3스톱 차이','극적 — 긴장 · 고백 · 느와르 직전'),('RATIO-16','16 : 1','4스톱 차이','로우키 — 어둠이 얼굴을 지배')]
    g='<div class="grid c4">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t} <small>{d}</small></b><span>{s}</span></div>' for k,t,d,s in cols)+'</div>'
    return fig(g+'<div class="rulebar">조명비 = 밝은 면 : 어두운 면. 키라이트는 그대로 두고 <b>필라이트의 세기만</b> 바꾼 결과다. 필을 끄면 비율이 커지고, 필을 키와 같게 하면 1:1 — 그림자가 사라진다.</div>','<b>그림 41</b> 조명비에 따른 대비의 변화 — 같은 모델, 같은 키, 필라이트만 네 단계.',ttl='키와 필의 밝기 차이가 얼굴의 입체와 분위기를 정한다')
def chroma_plan():
    s=f'<svg viewBox="0 0 400 260" {SV} font-size="9.5"><rect width="400" height="260" fill="{CARD}"/>'
    s+=f'<rect x="60" y="18" width="280" height="10" fill="#3FA55A"/><text x="200" y="14" text-anchor="middle" fill="{INK}" font-weight="500" font-size="9">그린 배경 — 밝기 편차 ±1/3스톱</text>'
    for x in (90,160,240,310): s+=f'<circle cx="{x}" cy="48" r="7" fill="none" stroke="{INK}" stroke-width="1.6"/><polygon points="{x-5},54 {x+5},54 {x+16},28 {x-16},28" fill="#3FA55A" opacity=".18"/>'
    s+=f'<text x="200" y="70" text-anchor="middle" fill="{MUT}" font-size="8.5">배경광 4등 — 좌우 45° 교차, 같은 거리</text>'
    s+=f'<line x1="200" y1="30" x2="200" y2="128" stroke="{WINE}" stroke-width="1.2" stroke-dasharray="4 3"/><text x="206" y="100" fill="{WINE}" font-weight="500">2 m 이상</text>'
    s+=person_top(200,140,r=10,angle=180)+f'<text x="200" y="166" text-anchor="middle">인물</text>'
    s+=camera_top(200,232,w=24,fill=MUT)+f'<text x="200" y="256" text-anchor="middle" fill="{INK2}">카메라</text>'
    s+=f'{softbox_top(73,199,w=32,fill=WINE,angle=55)}<text x="30" y="232" fill="{WINE}" font-weight="500">키 (소프트 45°)</text>'
    s+=f'{light_top(325,203,r=8,fill=INK,angle=-55,hollow=True)}<text x="296" y="232" fill="{INK}" font-weight="500">필 (바운스)</text>'
    s+=f'{light_top(277,102,r=7,fill=INK,angle=-140)}<text x="292" y="92" fill="{INK}" font-weight="500">백 · 헤어 라이트</text><text x="292" y="103" fill="{MUT}" font-size="8">마젠타 젤 — 초록 스필 상쇄</text>'
    s+=f'<rect x="12" y="12" width="36" height="236" fill="none" stroke="{LINE}" stroke-dasharray="3 3"/><text x="30" y="130" text-anchor="middle" fill="{MUT}" font-size="8" transform="rotate(-90 30 130)">배경광은 배경만 · 인물광은 인물만</text>'
    return s+'</svg>'
def F42_1():
    g=f'<div class="grid plan">{chroma_plan()}{facts("두 세계를 분리한다",["배경광 4등은 그린 천만 비춘다 — 인물에 닿지 않게","인물 3점은 인물만 — 그린 천에 그림자를 떨어뜨리지 않게","그 사이가 2 m — 거리가 그림자와 초록 반사를 함께 없앤다"],"현장 체크 셋",["그린 배경의 노출 = 얼굴보다 같거나 1스톱 아래","머리카락 가장자리에 백라이트가 있는가","노트북으로 그 자리에서 키잉해 본다"])}</div>'
    return fig(g,'<b>그림 42-1</b> 크로마키 조명 평면도 — 배경 4등과 인물 3점 조명을 완전히 분리한다. 거리 2 m가 가장 확실한 해결책이다.',ttl='배경과 인물의 빛을 따로 만든다')
def F42_NOTE():
    return facts("그림 42 읽는 법",["① 촬영: 초록은 고르게, 인물은 2 m 앞에서 따로 조명","② 매트: 소프트웨어가 초록을 투명으로 바꾼다 — 흰 부분만 남는다","③ 합성: 남은 인물을 새 배경 위에 얹고 색·그림자·가장자리를 맞춘다"],"실패하는 이유 셋",["초록 얼룩(밝기 편차) → 매트에 구멍","인물이 배경에 가까움 → 그림자 + 초록 반사(스필)","머리카락에 백라이트 없음 → 가장자리가 지저분"])
# LT-2 beam
def LT2():
    cols=[('BEAM-PIN','핀스폿 PIN SPOT','4~10° · 아주 좁다','얼굴 하나만 — 무대 솔로, 제품 하이라이트'),('BEAM-SPOT','스폿 SPOT','15~30° · 좁다','경계가 보이는 원 — 프레넬, 레코 · 강조와 분리'),('BEAM-FLOOD','플러드 FLOOD','45~70° · 넓다','넓게 고르게 — 오픈페이스, LED 패널 · 베이스 조명'),('BEAM-SOFT','소프트 SOFT','확산 · 경계 없음','감싸는 빛 — 소프트박스, 북라이트 · 피부 · 인터뷰'),('BEAM-AMBIENT','앰비언트 AMBIENT','무지향 · 사방','그림자 없는 바닥 밝기 — 천장 바운스, 흐린 날')]
    g='<div class="grid c5">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b><span class="deg">{d}</span><span>{s}</span></div>' for k,t,d,s in cols)+'</div>'
    arrow=f'<div class="ends"><span>← 좁다 · 하드 · 경계 선명 · 극적</span><span>넓다 · 소프트 · 경계 없음 · 전체 →</span></div>'
    return fig(g+arrow,'<b>도판 LT-2</b> 빔 각도에 따른 다섯 가지 빛 — 같은 사람, 같은 자리, 램프 앞의 도구만 바꿨다. 왼쪽으로 갈수록 "무엇을 보여줄지", 오른쪽으로 갈수록 "얼마나 밝을지"를 정한다.',ttl='핀스폿에서 앰비언트까지 — 빔 각도가 바꾸는 다섯 가지')
def LT3():
    svg=f'<svg viewBox="0 0 320 120" {SV} font-size="9"><rect width="320" height="120" fill="{CARD}"/>'
    svg+=f'<circle cx="30" cy="40" r="5" fill="{WINE}"/><circle cx="110" cy="60" r="10" fill="{INK}"/><polygon points="30,40 104,52 104,68" fill="{WINE}" opacity=".15"/><rect x="124" y="54" width="40" height="12" fill="{INK}" opacity=".8"/><text x="60" y="100" text-anchor="middle" font-weight="500">작은 소스 · 멀리 → 하드</text><text x="60" y="112" text-anchor="middle" fill="{MUT}" font-size="8">그림자 경계가 칼같이</text>'
    svg+=f'<rect x="180" y="20" width="8" height="60" fill="{WINE}"/><circle cx="270" cy="60" r="10" fill="{INK}"/><polygon points="188,20 188,80 262,66 262,54" fill="{WINE}" opacity=".15"/><rect x="284" y="52" width="30" height="16" fill="{INK}" opacity=".3"/><text x="245" y="100" text-anchor="middle" font-weight="500">큰 소스 · 가까이 → 소프트</text><text x="245" y="112" text-anchor="middle" fill="{MUT}" font-size="8">그림자가 번지며 사라진다</text></svg>'
    g=f'<div class="grid blk"><div class="it"><img src="{I("HARDSOFT")}"><b>왼쪽 하드 · 오른쪽 소프트</b><span>같은 얼굴, 같은 노출. 왼쪽은 맨 전구 하나, 오른쪽은 2 m 소프트박스</span></div><div class="it">{svg}<b>하드와 소프트를 가르는 것</b><span>램프의 종류가 아니라 피사체에서 본 광원의 <b>크기</b>다. 크게 만들거나(디퓨전·바운스) 가까이 가져가면 소프트해진다</span></div></div>'
    chips='<div class="chips"><b>변형 도구 — 무엇을 조절하는가</b><span>소프트박스 · 디퓨전 → 크기(부드러움)</span><span>바운스(천장·벽·폼보드) → 크기 + 방향</span><span>그리드 · 반도어 → 번짐을 자른다</span><span>플래그 → 빛을 막는다</span><span>젤(CTO·CTB) → 색</span><span>ND → 밝기만</span></div>'
    return fig(g+chips,'<b>도판 LT-3</b> 하드와 소프트 — 광원의 "보이는 크기"와 거리가 정한다. 변형 도구는 이 두 가지를 바꾸는 손잡이다.',ttl='부드러움 = 광원의 보이는 크기')
def lt4_panel(n,title,lights,note):
    # lights: list of (angle_deg_from_camera, kind, label) kind: key/fill/back/bg ; angle 0 = camera position, 180 = behind subject
    s=f'<svg viewBox="0 0 180 170" {SV} font-size="9.5"><rect width="180" height="170" fill="{CARD}"/><text x="8" y="16" font-size="11.5" font-weight="600" fill="{INK}"><tspan fill="{WINE}">{n}</tspan>  {title}</text>'
    s+=f'<rect x="50" y="30" width="80" height="5" fill="#B9B5AC"/>'+person_top(90,92,r=10,angle=180)+camera_top(90,146,w=16,fill=MUT)+f'<text x="90" y="166" text-anchor="middle" fill="{MUT}" font-size="8.5">카메라</text>'
    for ang,kind,lab in lights:
        a=math.radians(ang); r=44
        if kind in ('keyc','softc'): r=27
        x=90+r*math.sin(a); y=92+r*math.cos(a)
        if kind=='keyc': s+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{WINE}"/><text x="{x+10:.1f}" y="{y+3:.1f}" fill="{INK2}" font-size="8.5" font-weight="500">{lab}</text>'; continue
        if kind=='softc': s+=f'<rect x="{x-9:.1f}" y="{y-4:.1f}" width="18" height="8" fill="{WINE}" opacity=".85"/><text x="{x+12:.1f}" y="{y+3:.1f}" fill="{INK2}" font-size="8.5" font-weight="500">{lab}</text>'; continue
        if kind=='key': s+=f'<polygon points="{x:.1f},{y:.1f} {90+10*math.cos(a):.1f},{92-10*math.sin(a):.1f} {90-10*math.cos(a):.1f},{92+10*math.sin(a):.1f}" fill="{WINE}" opacity=".18"/><circle cx="{x:.1f}" cy="{y:.1f}" r="0"/>'+light_top(x,y,r=6.5,fill=WINE,angle=180-ang)
        elif kind=='fill': s+=light_top(x,y,r=6,fill=INK,angle=180-ang,hollow=True)
        elif kind=='back': s+=light_top(x,y,r=5.5,fill=INK,angle=180-ang)
        elif kind=='soft': s+=f'<rect x="{x-9:.1f}" y="{y-4:.1f}" width="18" height="8" fill="{WINE}" opacity=".85" transform="rotate({-ang:.0f} {x:.1f} {y:.1f})"/>'
        elif kind=='bounce': s+=f'<rect x="{x-9:.1f}" y="{y-2:.1f}" width="18" height="4" fill="#fff" stroke="{INK}" transform="rotate({-ang:.0f} {x:.1f} {y:.1f})"/>'
        elif kind=='neg': s+=f'<rect x="{x-9:.1f}" y="{y-2:.1f}" width="18" height="4" fill="{INK}" transform="rotate({-ang:.0f} {x:.1f} {y:.1f})"/>'
        if lab:
            lx=90+(r+17)*math.sin(a); ly=92+(r+17)*math.cos(a)+3
            anc='middle' if abs(math.sin(a))<.3 else ('start' if math.sin(a)>0 else 'end')
            s+=f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anc}" fill="{INK2}" font-size="8.5" font-weight="500">{lab}</text>'
    s+=f'<text x="90" y="26" text-anchor="middle" fill="{MUT}" font-size="8">배경</text>'
    return f'<div class="it">{s}</svg><span>{note}</span></div>'
def LT4():
    P=[('01','기본 3점',[(-45,'key','키'),(45,'fill','필'),(150,'back','백')],'인터뷰 · 설명 영상의 출발점. 키 : 필 = 2:1~4:1'),
       ('02','렘브란트',[(-45,'key','키 45°↑'),(60,'neg','검은 판')],'필 대신 검은 판 — 뺨에 빛 삼각형, 드라마'),
       ('03','버터플라이',[(0,'keyc','키 정면 · 높이'),(40,'bounce','반사판 턱 아래')],'뷰티 · 화장품. 코 밑 나비 그림자'),
       ('04','스플릿',[(-90,'key','키 90°')],'갈등 · 비밀. 얼굴이 정확히 반으로'),
       ('05','루프',[(-35,'key','키 35°'),(50,'fill','약한 필')],'가장 무난한 인물 조명. 코 옆 작은 고리'),
       ('06','북라이트',[(-110,'key','키'),(-70,'bounce','바운스'),(-35,'soft','디퓨전')],'키를 바운스시켜 디퓨전을 통과 — 가장 부드러운 빛'),
       ('07','역광 · 림',[(150,'back','백 ×2'),(210,'back',''),(20,'bounce','바운스')],'윤곽선만. 실루엣 · 신비 · 땀과 머리카락'),
       ('08','제품 톱라이트',[(180,'soft',''),(-80,'bounce','흰 판'),(80,'bounce','흰 판'),(0,'softc','톱 소프트 (위)')],'위에서 큰 소프트 + 뒤 스트립, 양옆 흰 판 — 유리·금속의 반사 선')]
    g='<div class="grid c4">'+''.join(lt4_panel(*p) for p in P)+'</div>'
    leg='<div class="chips"><b>도면 읽는 법</b><span><i class="lg k"></i> 키(붉은 원)</span><span><i class="lg f"></i> 필(빈 원)</span><span><i class="lg b"></i> 백(검은 원)</span><span><i class="lg s"></i> 소프트 · 디퓨전</span><span><i class="lg w"></i> 흰 반사판</span><span><i class="lg n"></i> 검은 판(네거티브 필)</span></div>'
    return fig(g+leg,'<b>도판 LT-4</b> 여덟 가지 조명 배치의 평면도 — 인물은 가운데, 카메라는 아래. 사진으로 보면 "분위기"로 기억되지만 도면으로 보면 "각도"로 기억된다. 현장에서 재현되는 것은 후자다.',ttl='여덟 가지 배치 — 위에서 본 도면')
def LT5():
    cols=[('AE-PARALLEL','Parallel 평행광','태양 · HMI','평행하고 균일 — 그림자가 모두 같은 방향, 거리와 무관'),('AE-SPOT','Spot 스폿','프레넬 · 소프트박스','원뿔 — 키라이트의 기본. Cone Angle · Feather · Falloff'),('AE-POINT','Point 점광','전구 · 촛불 · 튜브','사방으로 — 거리에 따라 어두워진다(Falloff)'),('AE-AMBIENT','Ambient 환경광','천장 바운스 · 흐린 날','그림자 없는 바닥 밝기 — 10~30%만, 많으면 평평해진다')]
    g='<div class="grid c4">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b><span class="deg">현장 대응 · {d}</span><span>{s}</span></div>' for k,t,d,s in cols)+'</div>'
    chips='<div class="chips"><b>세팅 순서</b><span>① Ambient 10~20%로 바닥 밝기</span><span>② Spot 하나로 키 (Shadow 켜기)</span><span>③ Point 또는 약한 Spot으로 필 (Shadow 끄기)</span><span>④ 뒤에서 Spot으로 림</span><span>⑤ 재질 옵션: Accepts Shadows · Casts Shadows</span></div>'
    return fig(g+chips,'<b>도판 LT-5</b> 애프터이펙트 3D 라이트 네 종류와 현장 장비의 대응 — 같은 구와 상자를 네 가지 빛으로만 비춘 것. 소프트웨어의 빛은 현장 조명의 축소 모형이다.',ttl='소프트웨어의 빛 — 네 가지 라이트')
# ---------- 사운드 ----------
def sync_svg():
    s=f'<svg viewBox="0 0 560 170" {SV} font-size="9.5"><rect width="560" height="170" fill="{CARD}"/>'
    s+=f'<text x="14" y="20" font-weight="500" fill="{INK}">영상 트랙 — 슬레이트가 "닫히는" 프레임</text>'
    for i in range(12):
        x=14+i*44; on=(i==6)
        s+=f'<rect x="{x}" y="28" width="40" height="30" fill="{"#fff"}" stroke="{WINE if on else LINE}" stroke-width="{2 if on else .8}"/>'
        # clapper icon: open or closed
        if i<6: s+=f'<line x1="{x+8}" y1="52" x2="{x+32}" y2="52" stroke="{INK}" stroke-width="3"/><line x1="{x+8}" y1="52" x2="{x+28}" y2="{36+i*2.2:.0f}" stroke="{INK}" stroke-width="3"/>'
        else: s+=f'<line x1="{x+8}" y1="50" x2="{x+32}" y2="50" stroke="{INK}" stroke-width="3"/><line x1="{x+8}" y1="46" x2="{x+32}" y2="46" stroke="{INK}" stroke-width="3"/>'
    s+=f'<line x1="298" y1="24" x2="298" y2="150" stroke="{WINE}" stroke-width="1.4" stroke-dasharray="4 3"/>'
    s+=f'<text x="14" y="86" font-weight="500" fill="{INK}">오디오 트랙 — "딱" 소리의 피크</text>'
    # waveform
    import random; random.seed(3)
    pts=[]
    for x in range(14,542,3):
        amp= 3+random.random()*4
        if 290<=x<=306: amp=38-abs(x-298)*3
        elif 306<x<340: amp=(340-x)/34*18+3
        pts.append((x,amp))
    s+='<path d="M'+' L'.join(f'{x},{120-a:.1f}' for x,a in pts)+' L'+' L'.join(f'{x},{120+a:.1f}' for x,a in reversed(pts))+f' Z" fill="{INK}" opacity=".75"/>'
    s+=f'<text x="306" y="98" fill="{WINE}" font-weight="500">피크를 닫힌 프레임에 맞춘다</text>'
    s+=f'<text x="14" y="152" fill="{INK2}">빛은 즉시 도착한다(30만 km/s). 소리는 340 m/s — 카메라에서 34 m 떨어진 슬레이트는 <tspan fill="{WINE}" font-weight="500">0.1초(약 2.4프레임) 늦게</tspan> 들린다.</text><text x="14" y="165" fill="{INK2}">멀리서 찍을수록 슬레이트는 카메라 가까이에서 친다.</text>'
    return s+'</svg>'
def SYNC():
    g=f'<div class="grid blk">{sync_svg()}'+it('SLATE','슬레이트 — 보이는 순간과 들리는 순간을 한 점으로','막대가 닫히는 프레임 = 파형의 피크. 편집에서 이 두 점을 겹치면 화면과 소리가 맞는다')+'</div>'
    return fig(g,'<b>그림 43</b> 싱크 — 보는 것은 듣는 것보다 빠르다. 눈은 빛으로, 귀는 공기의 진동으로 받기 때문에 소리는 늘 조금 늦게 도착한다. 슬레이트는 그 차이를 맞추기 위한 "눈과 귀의 공통 기준점"이다.',ttl='보는 것은 빛, 듣는 것은 공기 — 그래서 소리를 "맞춘다"')
def LEVEL():
    s=f'<svg viewBox="0 0 560 120" {SV} font-size="9.5"><rect width="560" height="120" fill="{CARD}"/>'
    segs=[(-60,-30,'#D7D4CD','과소 녹음 — 노이즈가 올라온다'),(-30,-18,'#B9B5AC','조용한 구간 · 룸톤'),(-18,-12,WINE,'대사 평균 -18 ~ -12'),(-12,-6,'#A8465A','피크 허용 구간'),(-6,0,'#1B1B1D','위험 — 0에 닿으면 복구 불가')]
    for lo,hi,col,lab in segs:
        x0=30+(lo+60)/60*500; x1=30+(hi+60)/60*500
        s+=f'<rect x="{x0:.1f}" y="40" width="{x1-x0:.1f}" height="26" fill="{col}"/>'
        s+=f'<text x="{(x0+x1)/2:.1f}" y="{84 if (lo in(-60,-18,-6)) else 100}" text-anchor="middle" fill="{INK2}" font-size="8.5">{lab}</text>'
    for v in (-60,-30,-18,-12,-6,0):
        x=30+(v+60)/60*500; s+=f'<line x1="{x:.1f}" y1="34" x2="{x:.1f}" y2="70" stroke="{INK}" stroke-width=".8"/><text x="{x:.1f}" y="28" text-anchor="middle" font-weight="500">{v}</text>'
    s+=f'<text x="540" y="28" text-anchor="start" fill="{MUT}" font-size="8">dBFS</text>'
    s+=f'<text x="30" y="116" fill="{INK}" font-weight="500">피크 미터 기준 — 대사는 -12 근처에서 춤추고, -6을 넘기지 않는다. 디지털은 0을 넘는 순간 잘린다(클리핑).</text>'
    return fig(s+'</svg>','<b>그림 43-1</b> 녹음 레벨 안전 구간 — 조용하면 나중에 키울 수 있지만, 깨진 소리는 되살릴 수 없다. 늘 조금 낮게.',ttl='녹음 레벨 — 안전 구간')
def polar(kind):
    s=f'<svg viewBox="0 0 150 150" {SV} font-size="8"><circle cx="75" cy="75" r="60" fill="#fff" stroke="{LINE}"/><circle cx="75" cy="75" r="30" fill="none" stroke="{LINE}" stroke-dasharray="2 2"/>'
    import math as m
    def shape(f):
        pts=[]
        for d in range(0,360,4):
            t=m.radians(d); r=60*max(0,f(t))
            pts.append(f'{75+r*m.sin(t):.1f},{75-r*m.cos(t):.1f}')
        return f'<polygon points="{" ".join(pts)}" fill="{WINE}" opacity=".35" stroke="{WINE}" stroke-width="1.2"/>'
    if kind=='omni': s+=shape(lambda t:1)
    elif kind=='card': s+=shape(lambda t:(1+m.cos(t))/2)
    elif kind=='super': s+=shape(lambda t:abs(0.37+0.63*m.cos(t)))
    elif kind=='fig8': s+=shape(lambda t:abs(m.cos(t)))
    elif kind=='shot': s+=shape(lambda t:max(0,m.cos(t))**3+0.12*abs(m.cos(t)))
    s+=f'<rect x="69" y="66" width="12" height="18" rx="2" fill="{INK}"/><text x="75" y="12" text-anchor="middle" fill="{MUT}">앞 (말하는 사람)</text><text x="75" y="146" text-anchor="middle" fill="{MUT}">뒤</text>'
    return s+'</svg>'
def F44():
    cols=[('omni','무지향 Omni','모든 방향을 똑같이','라발리에 · 공간감 · 자연음'),('card','카디오이드','앞을 받고 뒤를 버린다','인터뷰 · 보컬 · 가장 흔함'),('super','슈퍼카디오이드','앞이 더 좁고 뒤가 조금','붐 · 현장 대사'),('shot','샷건','아주 좁은 앞 — 멀리서도','붐 마이크 · 야외 · 다큐'),('fig8','양지향 Fig-8','앞뒤를 받고 옆을 버린다','마주 보는 대담 · MS 스테레오')]
    g='<div class="grid c5">'+''.join(f'<div class="it">{polar(k)}<b>{t}</b><span>{s}</span><span class="deg">{u}</span></div>' for k,t,s,u in cols)+'</div>'
    g+='<div class="grid c2 mics">'+it('MIC-BOOM','붐 샷건 — 프레임 바로 위에서 입을 향해','좁은 지향 = 각도가 1 m만 벗어나도 소리가 얇아진다')+it('MIC-STUDIO','스튜디오 콘덴서 — 내레이션·더빙','카디오이드 · 팝필터 · 15~30 cm · 방의 울림을 먼저 잡는다')+'</div>'
    return fig(g,'<b>그림 44</b> 마이크 지향성 — 붉은 면적이 소리를 받는 방향과 세기다. 면적이 좁을수록 멀리서도 또렷하지만 각도에 민감하다. 비싼 마이크보다 가까운 마이크가 낫다.',ttl='마이크가 어느 방향의 소리를 받는가')
def F45():
    W=560; s=f'<svg viewBox="0 0 {W} 250" {SV} font-size="9.5"><rect width="{W}" height="250" fill="{CARD}"/>'
    x0=90; sc=(W-x0-14)/15
    def X(t): return x0+t*sc
    for a,b,lab,sub in [(0,3,'후킹','첫 3초에 멈춰 세운다'),(3,11,'전개','정보와 감정을 쌓는다'),(11,15,'마무리','이름을 각인한다')]:
        s+=f'<rect x="{X(a):.1f}" y="14" width="{X(b)-X(a):.1f}" height="26" fill="{WINE}" opacity="{.9 if lab=="후킹" else .55 if lab=="전개" else .75}"/><text x="{(X(a)+X(b))/2:.1f}" y="26" text-anchor="middle" fill="#fff" font-weight="500">{lab}</text><text x="{(X(a)+X(b))/2:.1f}" y="36" text-anchor="middle" fill="#fff" font-size="7.5">{sub}</text>'
    lanes=[('내레이션',[(0.5,3,'하루의 시작이'),(4.5,9,'도시보다 먼저'),(12,14.5,'오늘도, 브랜드')],INK,'#fff'),
           ('음악',[(0,15,'피아노 92 BPM — 후킹에서 작게, 전개에서 올리고, 로고 직전 빈다')],'#A8465A','#fff'),
           ('효과음',[(0,.6,'물방울'),(3,3.5,'뚜껑'),(7,7.6,'도시'),(11,11.4,'whoosh')],'#8E8A82','#fff'),
           ('사운드 로고',[(13.8,15,'♪ 징글')],WINE,'#fff')]
    y=58
    for name,blocks,col,fc in lanes:
        s+=f'<text x="{x0-8}" y="{y+17}" text-anchor="end" font-weight="500" fill="{INK}">{name}</text><line x1="{x0}" y1="{y+28}" x2="{W-14}" y2="{y+28}" stroke="{LINE}"/>'
        for a,b,lab in blocks:
            w=max(X(b)-X(a),6)
            s+=f'<rect x="{X(a):.1f}" y="{y+2}" width="{w:.1f}" height="22" rx="2" fill="{col}" opacity=".9"/>'
            if w>40: s+=f'<text x="{X(a)+5:.1f}" y="{y+16}" fill="{fc}" font-size="8.5">{lab}</text>'
            else: s+=f'<text x="{X(a)+w/2:.1f}" y="{y+36}" text-anchor="middle" fill="{INK2}" font-size="7.5">{lab}</text>'
        y+=44
    for t in (0,3,6,9,11,15): s+=f'<line x1="{X(t):.1f}" y1="44" x2="{X(t):.1f}" y2="{y}" stroke="{LINE}" stroke-dasharray="2 3"/><text x="{X(t):.1f}" y="{y+12}" text-anchor="middle" fill="{MUT}" font-size="8">{t}초</text>'
    s+=f'<text x="{x0}" y="{y+30}" fill="{INK}" font-weight="500">말이 있을 때 음악을 내리고, 말이 없을 때 효과음이 숨을 쉰다. 네 층이 같은 순간에 모두 크면 아무것도 들리지 않는다.</text>'
    return fig(s+'</svg>','<b>그림 45</b> 15초 광고의 사운드 4층 타임라인 — 내레이션 · 음악 · 효과음 · 사운드 로고. 가로가 시간, 블록이 소리가 "들리는" 구간이다.',ttl='소리는 네 층으로 쌓는다')
def F46():
    W=560; s=f'<svg viewBox="0 0 {W} 230" {SV} font-size="9.5"><rect width="{W}" height="230" fill="{CARD}"/>'
    x0=70; sc=(W-x0-14)/100
    X=lambda t:x0+t*sc
    tracks=[('V2 자막',[(10,24,'#D8C7CB'),(52,66,'#D8C7CB')],30),('V1 영상',[(0,30,'#B9B5AC'),(30,58,'#8E8A82'),(58,100,'#B9B5AC')],62),('A1 대사',[(0,36,'#C9D6D0'),(36,52,'#A8BFB4'),(52,100,'#C9D6D0')],104),('A2 음악 · 효과',[(0,100,'#EFE9DF')],136)]
    for name,blocks,y in tracks:
        s+=f'<text x="{x0-8}" y="{y+16}" text-anchor="end" font-weight="500" fill="{INK}">{name}</text>'
        for a,b,c in blocks: s+=f'<rect x="{X(a):.1f}" y="{y}" width="{X(b)-X(a)-1:.1f}" height="24" fill="{c}"/>'
    # cut points
    s+=f'<line x1="{X(30):.1f}" y1="56" x2="{X(30):.1f}" y2="90" stroke="{INK}" stroke-width="1.2"/><line x1="{X(36):.1f}" y1="98" x2="{X(36):.1f}" y2="132" stroke="{INK}" stroke-width="1.2"/>'
    s+=f'<path d="M{X(30):.1f},88 L{X(30):.1f},96 L{X(36):.1f},96 L{X(36):.1f},100" fill="none" stroke="{WINE}" stroke-width="1.4"/><text x="{X(33):.1f}" y="176" text-anchor="middle" fill="{WINE}" font-weight="500">L 컷</text><text x="{X(36):.1f}" y="188" text-anchor="end" fill="{INK2}" font-size="8">앞 장면의 소리가 뒤 화면 위로 남는다</text>'
    s+=f'<line x1="{X(58):.1f}" y1="56" x2="{X(58):.1f}" y2="90" stroke="{INK}" stroke-width="1.2"/><line x1="{X(52):.1f}" y1="98" x2="{X(52):.1f}" y2="132" stroke="{INK}" stroke-width="1.2"/>'
    s+=f'<path d="M{X(58):.1f},88 L{X(58):.1f},96 L{X(52):.1f},96 L{X(52):.1f},100" fill="none" stroke="{WINE}" stroke-width="1.4"/><text x="{X(55):.1f}" y="176" text-anchor="middle" fill="{WINE}" font-weight="500">J 컷</text><text x="{X(52):.1f}" y="188" text-anchor="start" fill="{INK2}" font-size="8">뒤 장면의 소리가 먼저 들어온다</text>'
    s+=f'<line x1="{X(44):.1f}" y1="20" x2="{X(44):.1f}" y2="164" stroke="{WINE}" stroke-width="1.6"/><polygon points="{X(44)-5:.1f},14 {X(44)+5:.1f},14 {X(44):.1f},22" fill="{WINE}"/><text x="{X(44)+6:.1f}" y="18" fill="{WINE}" font-size="8">재생 헤드</text>'
    s+=f'<text x="{x0}" y="214" fill="{INK}" font-weight="500">영상과 소리의 경계를 어긋나게 두면 컷이 매끄러워진다. 같은 자리에서 둘을 함께 자르면 "툭" 끊긴다.</text>'
    return fig(s+'</svg>','<b>그림 46</b> 편집 타임라인의 구조 — 위 두 줄은 "보여 주는 것", 아래 두 줄은 "들려 주는 것". J컷과 L컷은 소리의 경계를 영상보다 먼저 또는 나중에 두는 기법이다.',ttl='타임라인은 네 줄로 읽는다')
def F47():
    rows=[('6','카메라','가상 카메라 — 모든 층을 내려다본다'),('5','라이트','3D 레이어에만 그림자와 밝기를 준다'),('4','3D 텍스트','깊이를 가진 글자 — 카메라가 돌면 옆면이 보인다'),('3','인물 (키잉)','배경을 지운 촬영 소스'),('2','중간 배경','그래픽 · 그라디언트 — 깊이감'),('1','배경 플레이트','가장 아래 — 바탕 영상')]
    ol='<ol class="misel">'+''.join(f'<li><i>{n}</i><span><b>{a}</b> — {b}</span></li>' for n,a,b in rows)+'<li class="x">맨 위 층이 화면의 맨 앞. 순서를 바꾸면 가려지는 것이 바뀐다 — 편집은 시간으로, 합성은 층으로 생각한다.</li></ol>'
    return fig(f'<div class="grid plan"><img src="{I("LAYERS-ISO")}">{ol}</div>','<b>그림 47</b> 애프터이펙트의 레이어 스택 — 아래에서 위로 쌓인 여섯 층. 카메라와 라이트는 그림이 아니라 "층을 보는 방식"이다.',ttl='편집은 시간으로, 합성은 층으로 생각한다')
PRINC=[('01','스쿼시 앤 스트레치','부피는 유지한 채 눌리고 늘어난다 — 무게와 탄성'),('02','예비 동작','큰 동작 전에 반대 방향으로 먼저 움직인다'),('03','스테이징','실루엣만 봐도 동작의 의도가 읽힌다'),('04','포즈 투 포즈','핵심 포즈(키)를 먼저 정하고 사이를 채운다'),('05','팔로 스루 · 오버래핑','몸이 멈춰도 머리카락과 옷자락은 늦게 멈춘다'),('06','슬로우 인 · 슬로우 아웃','움직임의 시작과 끝에 프레임을 모은다'),('07','아크','관절의 움직임은 직선이 아니라 호를 그린다'),('08','보조 동작','주 동작을 돕는 작은 동작이 성격을 만든다'),('09','타이밍','같은 거리도 프레임 수가 무게와 속도를 정한다'),('10','과장','현실보다 한 단계 더 — 의도를 선명하게'),('11','입체적 표현','부피 · 무게 · 균형이 있는 형태로 그린다'),('12','어필','단순한 형태와 선명한 성격이 매력을 만든다')]
def F48():
    g='<div class="grid c4">'+''.join(f'<div class="it"><img src="{I("ANIM-"+n)}"><b><i>{n}</i>{t}</b><span>{s}</span></div>' for n,t,s in PRINC)+'</div>'
    return fig(g,'<b>그림 48</b> 애니메이션 12 원칙 — 한 캐릭터로 보는 열두 가지 움직임의 규칙(디즈니, 1981). 붉은 선이 각 원칙이 가리키는 "움직임"이다.',ttl='애니메이션 12 원칙 — 캐릭터로 보는 움직임')
def ball_svg():
    W=560; s=f'<svg viewBox="0 0 {W} 210" {SV} font-size="9"><rect width="{W}" height="210" fill="{CARD}"/><line x1="10" y1="180" x2="{W-10}" y2="180" stroke="{INK}" stroke-width="1.2"/>'
    # bounces: heights decreasing; positions sampled at equal time steps
    g=9.8; x=20; bounces=[(150,180),(95,130),(55,95),(30,65)]
    import math as m
    for H,span in bounces:
        T=2*m.sqrt(2*H/g)  # total time of flight (units arbitrary)
        n=int(6*m.sqrt(H/150))+5
        for i in range(n+1):
            t=T*i/n; y=180-(H*(1-((2*t/T-1)**2)))
            px=x+span*i/n
            v=abs(2*t/T-1)  # speed proxy 0 at apex, 1 at contact
            rx=10-3*v if False else 10; ry=10
            # stretch when fast (near contact), squash at contact
            if i in (0,n): rx,ry=11,6
            else: ry=8+3.5*v; rx=8-1.6*v
            s+=f'<ellipse cx="{px:.1f}" cy="{y-ry:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{WINE if i in (0,n) else "#fff"}" stroke="{WINE if i in (0,n) else INK}" stroke-width="{1.4 if i in (0,n) else 1}" opacity=".95"/>'
        s+=f'<path d="M{x},180 Q{x+span/2},{180-2*H} {x+span},180" fill="none" stroke="{LINE}" stroke-dasharray="3 3"/>'
        x+=span
    s+=f'<text x="230" y="22" fill="{INK}" font-weight="500">정점 — 간격이 촘촘하다 (느리다 · 슬로우 인/아웃)</text><text x="20" y="200" fill="{WINE}" font-weight="500">붉은 공 = 착지, 눌린다 (스쿼시)</text><text x="260" y="200" fill="{INK2}">떨어질 때 — 간격이 넓고 세로로 늘어난다 (스트레치)</text><text x="330" y="80" fill="{MUT}">튈 때마다 높이와 시간이 줄어든다 (타이밍)</text>'
    return s+'</svg>'
def F49():
    return fig(ball_svg(),'<b>그림 49</b> 바운싱 볼 — 아크 · 타이밍 · 스페이싱 · 스쿼시 앤 스트레치가 한 공에 다 들어 있다. 공은 같은 시간 간격으로 그렸다: 정점에서 느려 촘촘하고, 바닥 근처에서 빨라 성기다. 붉은 공이 바닥에 닿는 순간(눌림)이다.',ttl='바운싱 볼 하나에 네 가지 원칙이 들어 있다')
def F50():
    W=560; s=f'<svg viewBox="0 0 {W} 190" {SV} font-size="9.5"><rect width="{W}" height="190" fill="{CARD}"/>'
    rows=[('등간격 — 기계적',[i/10 for i in range(11)],INK,'로봇 · 컨베이어. 생명이 없다'),('이즈 인·아웃 — 자연스러움',[(1-math.cos(math.pi*i/10))/2 for i in range(11)],INK,'출발과 도착이 부드럽다. 대부분의 움직임'),('빠름 → 느림 — 도착 강조',[1-(1-i/10)**2.4 for i in range(11)],WINE,'튀어나와 멈춘다. 팝업 · 강조 · UI'),('느림 → 빠름 — 출발 강조',[(i/10)**2.4 for i in range(11)],WINE,'망설이다 떠난다. 점프 · 발사')]
    y=30
    for name,ps,col,note in rows:
        s+=f'<text x="14" y="{y+4}" font-weight="500" fill="{INK}">{name}</text><text x="14" y="{y+16}" fill="{MUT}" font-size="8">{note}</text>'
        for p in ps: s+=f'<circle cx="{230+p*310:.1f}" cy="{y}" r="5" fill="none" stroke="{col}" stroke-width="1.3"/>'
        y+=40
    s+=f'<text x="230" y="{y-6}" fill="{INK2}">같은 거리 · 같은 11프레임 — 간격만 다르다. <tspan font-weight="500">타이밍</tspan> = 프레임 개수, <tspan font-weight="500">스페이싱</tspan> = 프레임 사이 간격</text>'
    return fig(s+'</svg>','<b>그림 50</b> 타이밍과 스페이싱 — 모든 줄이 같은 거리를 같은 프레임 수로 이동한다. 원 사이의 간격이 넓은 곳이 빠른 곳이다.',ttl='같은 거리, 같은 프레임 수 — 간격만 바꾸면 완전히 다른 움직임이 된다')

def G15():
    W=560; H=230; s=f'<svg viewBox="0 0 {W} {H}" {SV} font-size="9.5"><rect width="{W}" height="{H}" fill="{CARD}"/><line x1="20" y1="186" x2="{W-20}" y2="186" stroke="{INK}" stroke-width="1.2"/>'
    # one bounce: ball leaves ground at x0, apex at mid, lands at x1 ; equal time steps
    x0,x1,h,N=70,490,130,14
    r=11.0; A=math.pi*r*r
    s+=f'<path d="M{x0},186 Q{(x0+x1)/2},{186-2*h} {x1},186" fill="none" stroke="{LINE}" stroke-dasharray="3 3"/>'
    for i in range(N+1):
        t=i/N; u=2*t-1; y=186-h*(1-u*u); x=x0+(x1-x0)*t
        v=abs(u)  # 0 apex, 1 contact
        if i in (0,N):
            rx=r*1.35; ry=A/(math.pi*rx); cy=186-ry; fill=WINE; stroke=WINE
        else:
            ry=r*(1+0.45*v*v); rx=A/(math.pi*ry); cy=y-ry; fill='#fff'; stroke=INK
        s+=f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>'
        if i==N//2: s+=f'<text x="{x:.1f}" y="{cy-ry-8:.1f}" text-anchor="middle" fill="{INK}" font-weight="500">정점 — 둥글다, 느리다(간격 좁음)</text>'
    s+=f'<text x="{x0:.0f}" y="206" text-anchor="middle" fill="{WINE}" font-weight="500">접지 — 납작하게 눌린다</text><text x="{x1:.0f}" y="206" text-anchor="middle" fill="{WINE}" font-weight="500">접지 — 다시 눌린다</text>'
    s+=f'<text x="150" y="150" text-anchor="middle" fill="{INK2}">빠를수록 진행 방향으로 늘어난다</text><text x="410" y="150" text-anchor="middle" fill="{INK2}">간격이 넓다 = 빠르다</text>'
    s+=f'<text x="20" y="224" fill="{INK}" font-weight="500">규칙: 늘어나면 그만큼 가늘어지고, 눌리면 그만큼 넓어진다 — 부피(면적)는 언제나 같다. 모든 공은 같은 시간 간격으로 그렸다.</text>'
    return fig(s+'</svg>','<b>G-15</b> 스쿼시 앤 스트레치 — 튀는 공의 한 포물선. 정점에서 둥글고 촘촘, 떨어질수록 길어지며 성기고, 바닥에 닿는 순간 납작해진다. 공의 면적은 열다섯 장 모두 같다.',ttl='스쿼시 앤 스트레치 — 튀는 공의 연속 동작')

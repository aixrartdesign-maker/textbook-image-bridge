#!/usr/bin/env python3
"""Compose photo-based figures and patch them into the part files."""
import re, os, sys
sys.path.insert(0,'.')
from glyphs import profile, figure, camera_side, person_top, camera_top, light_top, softbox_top
os.chdir('/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/book')
def rd(p): return open(p,encoding='utf-8').read()
def wr(p,s): open(p,'w',encoding='utf-8').write(s)
I=lambda k:f'img_new/{k}.jpg'
def it(k,title,sub='',num=''):
    n=f'<i>{num}</i>' if num else ''
    return f'<div class="it"><img src="{I(k)}" alt=""><b>{n}{title}</b>{f"<span>{sub}</span>" if sub else ""}</div>'
def fig(inner,cap,cls='fg wide',ttl=''):
    t=f'<div class="ttl">{ttl}</div>' if ttl else ''
    return f'<figure class="{cls}">{t}{inner}<figcaption>{cap}</figcaption></figure>'

# ---------- SVG helpers ----------
SV='xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans CJK KR"'
def topview(kind):
    # camera at bottom, person mid, background bar top. kind: start/zoom/dolly/dz
    cam_y={'start':170,'zoom':170,'dolly':110,'dz':190}[kind]
    half={'start':60,'zoom':22,'dolly':60,'dz':22}[kind]
    s=f'<svg viewBox="0 0 200 210" {SV} font-size="9">'
    s+='<rect x="0" y="0" width="200" height="210" fill="#F6F5F3"/>'
    s+='<rect x="20" y="14" width="160" height="8" fill="#B9B5AC"/><text x="100" y="10" text-anchor="middle" fill="#7A7A80" font-size="8">배경</text>'
    # cone from camera to top
    s+=f'<polygon points="100,{cam_y} {100-half*(cam_y-22)/60},22 {100+half*(cam_y-22)/60},22" fill="#7A1C2B" opacity=".12"/>'
    s+=f'<line x1="100" y1="{cam_y}" x2="{100-half*(cam_y-22)/60}" y2="22" stroke="#7A1C2B" stroke-width="1"/><line x1="100" y1="{cam_y}" x2="{100+half*(cam_y-22)/60}" y2="22" stroke="#7A1C2B" stroke-width="1"/>'
    s+=person_top(100,78,r=7,angle=180)
    s+=camera_top(100,cam_y,w=22,fill="#1B1B1D")
    if kind=='dolly': s+='<line x1="130" y1="178" x2="130" y2="124" stroke="#7A1C2B" stroke-width="2"/><polygon points="126,128 130,118 134,128" fill="#7A1C2B"/>'
    if kind=='dz': s+='<line x1="130" y1="150" x2="130" y2="194" stroke="#7A1C2B" stroke-width="2"/><polygon points="126,190 130,200 134,190" fill="#7A1C2B"/>'
    if kind=='zoom': s+='<text x="100" y="205" text-anchor="middle" fill="#7A1C2B" font-size="8.5">화각만 좁아진다</text>'
    if kind=='start': s+='<text x="100" y="205" text-anchor="middle" fill="#7A7A80" font-size="8.5">기준</text>'
    return s+'</svg>'
def sideview(kind):
    # camera height vs head: high/eye/low
    cy={'high':22,'eye':60,'low':98}[kind]
    s=f'<svg viewBox="0 0 200 120" {SV} font-size="9"><rect width="200" height="120" fill="#F6F5F3"/>'
    s+=profile(156,118,h=92,fill="#8E8A82")
    s+=camera_side(44,cy,w=46,fill="#1B1B1D",flip=True)
    s+=f'<line x1="66" y1="{cy}" x2="140" y2="60" stroke="#7A1C2B" stroke-width="1.4" stroke-dasharray="4 3"/>'
    s+='<line x1="20" y1="60" x2="200" y2="60" stroke="#D9D9DE" stroke-width=".8"/><text x="22" y="56" fill="#7A7A80" font-size="7.5">눈높이</text>'
    return s+'</svg>'

# ---------- F20 ----------
F20=fig('<div class="grid c4">'+''.join([
 it('FIG20-PAN','팬 PAN','제자리에서 좌우로 돌린다','01'),it('FIG20-TILT','틸트 TILT','제자리에서 위아래로','02'),
 it('FIG20-DOLLY','달리 인 DOLLY IN','카메라가 다가간다','03'),it('FIG20-TRACK','트랙 TRACK','피사체와 나란히 이동','04'),
 it('FIG20-ARC','아크 ARC','대상 주위를 원형으로','05'),it('FIG20-CRANE','크레인 CRANE','수직으로 오르내린다','06'),
 it('FIG20-HANDHELD','핸드헬드 HH','호흡이 담기는 흔들림','07'),it('FIG20-LOCKED','고정 LOCKED','움직이지 않는다 — 기준','08')])+'</div>',
 '<b>그림 20</b> 카메라 무빙 8종의 궤적. 빨간 화살표가 카메라의 이동, 흰 인형이 피사체다.',ttl='카메라가 움직이는 여덟 가지 방식')
# ---------- F21 ----------
F21=fig('<div class="grid c4 tv">'+''.join(f'<div class="it">{topview(k)}<b>{t}</b></div>' for k,t in [('start','시작'),('zoom','줌 인'),('dolly','달리 인'),('dz','달리 줌')])+'</div>'
 +'<div class="grid c4">'+it('FIG21-START','기준 화면','인물 작게, 배경 넓게')+it('FIG21-ZOOM','인물과 배경이 함께 커진다','원근이 납작해진다')+it('FIG21-DOLLY','인물만 커지고 배경은 그대로','깊이가 살아난다')+it('FIG21-DOLLYZOOM','인물은 그대로, 배경이 다가온다','현기증 — 달리 줌')+'</div>',
 '<b>그림 21</b> 줌과 달리 — 같은 크기, 다른 공간. 윗줄은 위에서 본 카메라 위치와 화각, 아랫줄은 그 결과 화면이다.',ttl='줌은 화각을 바꾸고, 달리는 공간을 바꾼다')
# ---------- F22 ----------
match_svg=f'<svg viewBox="0 0 160 90" {SV} font-size="8"><rect width="160" height="90" fill="#F6F5F3"/><circle cx="80" cy="45" r="26" fill="none" stroke="#1B1B1D" stroke-width="1.2" stroke-dasharray="4 3"/><circle cx="80" cy="45" r="26" fill="#7A1C2B" opacity=".1"/><text x="80" y="84" text-anchor="middle" fill="#7A1C2B">같은 자리 · 같은 크기</text></svg>'
def row(cells,label,sub):
    return f'<div class="grid cutrow">{"".join(cells)}<div class="lab2"><b>{label}</b><span>{sub}</span></div></div>'
F22=fig(row([f'<img src="{I("FIG22-ACT1")}">',f'<img src="{I("FIG22-ACT2")}">',f'<img src="{I("FIG22-ACT3")}">'],'액션 컷','동작이 진행되는 중간에서 자른다')
 +row([f'<img src="{I("FIG22-CLOCK")}">',f'<img src="{I("FIG22-SUN")}">',match_svg],'매치 컷','닮은 형태로 시공간을 건넌다')
 +row([f'<img src="{I("FIG22-JUMP1")}">',f'<img src="{I("FIG22-JUMP2")}">',f'<img src="{I("FIG22-JUMP3")}">'],'점프 컷','같은 구도에서 시간을 건너뛴다'),
 '<b>그림 22</b> 컷 연결 방식 세 가지. 빨간 세로선 자리가 편집점이다.',ttl='컷과 컷을 잇는 세 가지 방식')
# ---------- F23 chart ----------
def chart23():
    rows=[('긴박','36컷','0.5초','추격 · 사고 · 경고',36,'#7A1C2B'),('경쾌','15컷','1.2초','제품 소개 · 브이로그',15,'#A8465A'),('공감','7컷','2.6초','인터뷰 · 다큐',7,'#8E8A82'),('경이','4컷','4.5초','풍경 · 브랜드 무드',4,'#B9B5AC')]
    s=f'<svg viewBox="0 0 980 360" {SV} font-size="12">'
    s+='<text x="150" y="26" font-size="13" fill="#7A7A80">같은 18초</text><line x1="150" y1="34" x2="930" y2="34" stroke="#1B1B1D" stroke-width="1"/><polygon points="150,30 142,34 150,38" fill="#1B1B1D"/><polygon points="930,30 938,34 930,38" fill="#1B1B1D"/>'
    y=60
    for name,cnt,dur,ex,n,col in rows:
        s+=f'<text x="130" y="{y+22}" text-anchor="end" font-size="20" font-weight="500" fill="#1B1B1D">{name}</text><text x="130" y="{y+40}" text-anchor="end" font-size="10.5" fill="#7A7A80">{cnt} · {ex}</text>'
        w=780/n
        for i in range(n):
            s+=f'<rect x="{150+i*w+1.5:.1f}" y="{y}" width="{w-3:.1f}" height="44" fill="{col}" opacity="{0.95 if i%2==0 else 0.55}"/>'
        s+=f'<rect x="935" y="{y+10}" width="42" height="24" rx="12" fill="{col}"/><text x="956" y="{y+26}" text-anchor="middle" fill="#fff" font-size="11" font-weight="500">{dur}</text>'
        y+=68
    s+='<text x="150" y="345" font-size="12" fill="#1B1B1D" font-weight="500">컷을 짧게 자르면 맥박이 빨라지고, 길게 두면 생각할 틈이 생긴다.</text>'
    return s+'</svg>'
F23=fig(chart23(),'<b>그림 23</b> 감정에 따른 컷 길이 분포 — 같은 18초라도 몇 컷으로 나누느냐가 감정을 정한다.',ttl='같은 길이의 영상도 컷의 길이가 감정을 정한다')
# ---------- F25 ----------
F25=fig('<div class="grid c3">'+''.join(f'<div class="it"><img src="{I(k)}">{sideview(sk)}<b>{t}</b><span>{s}</span></div>' for k,sk,t,s in [('FIG25-HIGH','high','하이 앵글','이마가 커지고 턱이 작아진다 — 약하고 보호가 필요한 인물'),('FIG25-EYE','eye','아이 레벨','비례 그대로 — 중립, 인터뷰의 기본'),('FIG25-LOW','low','로우 앵글','턱과 콧구멍이 드러난다 — 권위, 위협')])+'</div>',
 '<b>그림 25</b> 같은 사람도 카메라 높이 하나로 성격이 달라진다. 인터뷰의 기본은 눈높이다.',ttl='카메라 높이가 얼굴의 비례와 인상을 바꾼다')
# ---------- F26 ----------
eyes=f'<svg viewBox="0 0 60 90" {SV}><line x1="4" y1="45" x2="56" y2="45" stroke="#7A1C2B" stroke-width="2"/><polygon points="52,40 60,45 52,50" fill="#7A1C2B"/><polygon points="8,40 0,45 8,50" fill="#7A1C2B"/></svg>'
F26=fig('<div class="sub">마주봄 — 두 시선이 한 선 위에서 만난다</div><div class="grid pair">'+f'<div class="it"><img src="{I("FIG26-A")}"><b>A — 화면 오른쪽을 본다</b></div><div class="mid">{eyes}</div><div class="it"><img src="{I("FIG26-B")}"><b>B — 화면 왼쪽을 본다</b></div></div>'
 +'<div class="sub">따라봄 — 시선이 다음 컷을 부른다</div><div class="grid seq3">'+it('FIG26-LOOK','본다','시선이 화면 밖으로','①')+'<div class="mid ar">→</div>'+it('FIG26-INSERT','보이는 것','관객이 같은 것을 본다','②')+'<div class="mid ar">→</div>'+it('FIG26-REACT','반응','의미가 완성된다','③')+'</div>',
 '<b>그림 26</b> 시선의 두 가지 쓰임 — 마주봄의 아이라인 매치와 따라봄의 시선 연결(쿨레쇼프 효과). 보는 사람 · 보이는 것 · 반응은 영상 문법에서 가장 자주 쓰이는 묶음이다.',ttl='시선은 컷과 컷을 잇는 가장 강한 끈이다')
# ---------- F27 ----------
def p27(title,sub,shape,note):
    s=f'<svg viewBox="0 0 300 190" {SV} font-size="10"><rect width="300" height="190" fill="#F6F5F3"/>'
    s+=f'<text x="14" y="26" font-size="15" font-weight="600">{title}</text><text x="{14+len(title)*17+8}" y="26" font-size="10" fill="#7A7A80">{sub}</text>'
    s+='<text x="14" y="70" fill="#7A7A80" font-size="9">이야기</text><text x="14" y="142" fill="#7A7A80" font-size="9">화면</text>'
    s+='<line x1="60" y1="66" x2="280" y2="66" stroke="#1B1B1D" stroke-width="1"/><line x1="60" y1="138" x2="280" y2="138" stroke="#1B1B1D" stroke-width="1"/>'
    s+=shape+f'<text x="150" y="176" text-anchor="middle" fill="#3C3C40" font-size="9.5">{note}</text></svg>'
    return s
W_='fill="#7A1C2B" opacity=".55"'
shapes={
 '연속':f'<polygon points="80,66 260,66 260,138 80,138" {W_}/>',
 '생략':f'<polygon points="80,66 120,66 150,138 140,138" {W_}/><polygon points="200,66 260,66 200,138 160,138" {W_}/><line x1="120" y1="66" x2="200" y2="66" stroke="#7A1C2B" stroke-width="4" stroke-dasharray="3 3"/><text x="160" y="58" text-anchor="middle" font-size="8.5" fill="#7A1C2B">잘린 시간</text>',
 '압축':''.join(f'<polygon points="{70+i*44},66 {90+i*44},66 {130+i*20},138 {120+i*20},138" {W_}/>' for i in range(5)),
 '확장':f'<polygon points="150,66 170,66 260,138 70,138" {W_}/>',
 '역행':f'<polygon points="80,66 130,66 230,138 170,138" fill="#8E8A82" opacity=".5"/><polygon points="180,66 230,66 130,138 80,138" {W_}/><text x="206" y="58" text-anchor="middle" font-size="8.5" fill="#7A7A80">과거</text>',
 '평행':''.join(f'<rect x="{80+i*36}" y="66" width="18" height="72" fill="{"#7A1C2B" if i%2==0 else "#8E8A82"}" opacity=".55"/>' for i in range(5))+'<text x="100" y="58" font-size="8.5" fill="#7A1C2B">장소 A</text><text x="136" y="58" font-size="8.5" fill="#7A7A80">장소 B</text>',
}
F27=fig('<div class="grid c3">'+''.join(f'<div class="it">{p27(t,s,shapes[t],n)}</div>' for t,s,n in [('연속','이야기 시간 = 화면 시간','롱테이크 · 실시간'),('생략','지루한 시간을 잘라 낸다','점프 컷 · 출퇴근을 한 컷에'),('압축','긴 시간을 짧게 모은다','몽타주 시퀀스 · 계절이 바뀐다'),('확장','짧은 순간을 길게 늘린다','슬로모션 · 여러 각도의 반복'),('역행','과거로 돌아간다','플래시백 · 기억'),('평행','다른 장소를 번갈아 잇는다','교차 편집 · 동시에 벌어진 일')])+'</div>',
 '<b>그림 27</b> 이야기 시간과 화면 시간 — 여섯 가지 시공간 이동. 위 선이 이야기의 시간, 아래 선이 화면의 시간이다.',ttl='컷은 시간과 공간을 끊고 다시 잇는다 — 영상은 움직이는 시공간의 편집이다')
# ---------- F57 (cell anatomy) ----------
def cellhtml(img,cut='CUT 02',scene='S#1 카페 · 낮 · INT',tc='2.5 s · 02:30–05:00',meta1='MCU · EYE · 50mm · DOLLY IN slow · CUT TO',meta2='지문 제품을 집어 든다 · 시선은 제품으로',meta3='N 하루의 시작이 달라집니다 · SE 뚜껑 · M 피아노 in',marks=False):
    m=''
    if marks:
        m=''.join(f'<span class="mk{n}">{n}</span>' for n in [1,2,3,4,6,7,8,9])
    return f'<div class="cellx">{m}<div class="hd"><span>{cut}</span><span class="sc">{scene}</span><span>{tc}</span></div><div class="fr"><img src="{I(img)}"></div><div class="me"><div>{meta1}</div><div>{meta2}</div><div>{meta3}</div></div></div>'
F57=fig('<div class="grid cellgrid">'+cellhtml('FIG57-SCENE',marks=True)+'<ol class="nine">'+''.join(f'<li><i>{n}</i><b>{a}</b><span>{b}</span></li>' for n,a,b in [(1,'컷 번호 · 씬','순서와 참조의 기준'),(2,'시간','지속 초 + 누적 타임코드'),(3,'화면(프레임)','구도 · 위치 · 시선 · 화살표'),(4,'샷 사이즈 · 앵글 · 렌즈','ELS~ECU · EYE/HIGH/LOW'),(5,'카메라 워킹','방향 + 속도 한 단어'),(6,'지문','사건을 동사로'),(7,'내레이션 · 대사','N / V.O. / SYNC'),(8,'사운드','M · SE · ATM'),(9,'전환','CUT / DIS / FI / FO')])+'</ol></div>',
 '<b>그림 57</b> 스토리보드 한 칸의 구성 요소. 아홉 가지가 다 적혀 있어야 다른 사람이 같은 그림을 찍을 수 있다.',ttl='한 칸의 해부 — 아홉 가지')
# ---------- SB-1 ratios ----------
def rb(k,ratio,res,h):
    return f'<div class="rb" style="height:{h}mm"><img src="{I(k)}"><b>{ratio}</b><span>{res}</span></div>'
SB1=fig('<div class="rrow">'+rb('SB1-43','4:3','1440×1080 · 레트로',40)+rb('SB1-169','16:9','1920×1080 · 기본',40)+rb('SB1-219','21:9','3840×1608 · 시네마',40)+'</div>'
 +'<div class="rrow">'+rb('SB1-11','1:1','1080×1080 · 피드',52)+rb('SB1-45','4:5','1080×1350 · 피드 최대',52)+rb('SB1-916','9:16','1080×1920 · 숏폼',52)+rb('SB1-921','9:21','1080×2520 · 세로 LED',52)+f'<div class="rb eq" style="height:52mm"><div class="eqw"><img src="{I("SB1-EQUI")}"><i></i></div><b>2:1 등장방형</b><span>4096×2048 · 360/VR — 붉은 틀이 정면 90°</span></div>'+'</div>',
 '<b>도판 SB-1</b> 같은 장면, 아홉 가지 비율. 비율이 바뀌면 인물의 크기와 배경의 몫이 달라진다 — 보드는 납품 비율 그대로 그린다.',ttl='화면 비율별 칸 템플릿')
# ---------- SB-2 ----------
SB2=fig('<div class="grid sb2">'+f'<div class="it"><img src="{I("SB2-CROP")}"><b>✕ 16:9를 가운데만 잘라 낸 세로</b><span>인물도 창도 반쪽 — 자르는 것은 설계가 아니다</span></div><div class="it tall"><img src="{I("SB2-VERT")}"><b>○ 세로로 다시 설계한 컷</b><span>얼굴은 위 1/3, 제품은 중앙, 배경은 줄인다</span></div>'+'<div class="rules"><b>세로로 옮길 때</b><span>샷은 한 단계 타이트하게</span><span>배경 설명은 별도 컷으로</span><span>시선과 동선은 위에서 아래로</span><span>자막은 가운데 60% 띠 안에</span><span>컷 수는 20~30% 늘어난다</span></div></div>',
 '<b>도판 SB-2</b> 가로와 세로는 다른 언어다. 센터 크롭(왼쪽)과 재설계(가운데)의 차이.',ttl='같은 컷을 두 번 설계한다')
# ---------- SB-3 ----------
top360=f'<svg viewBox="0 0 240 240" {SV} font-size="10"><circle cx="120" cy="120" r="100" fill="#F6F5F3" stroke="#1B1B1D"/><path d="M120,120 L82,28 A100,100 0 0 1 158,28 Z" fill="#7A1C2B" opacity=".12"/><circle cx="120" cy="120" r="6" fill="#1B1B1D"/><text x="120" y="140" text-anchor="middle" font-size="9">카메라 = 관객</text><circle cx="120" cy="40" r="9" fill="#B9B5AC"/><text x="136" y="44">A 0°</text><circle cx="36" cy="150" r="8" fill="#D7D4CD"/><text x="4" y="176" font-size="9">B −130°</text><path d="M120,60 A62,62 0 0 0 66,138" fill="none" stroke="#7A1C2B" stroke-width="2" stroke-dasharray="5 3"/><polygon points="62,130 66,142 74,134" fill="#7A1C2B"/><text x="120" y="20" text-anchor="middle" fill="#7A1C2B" font-size="9" font-weight="500">정면 90°</text></svg>'
SB3=fig('<div class="grid sb3"><div class="col">'+''.join(f'<div class="it"><img src="{I(k)}"><b><i>{n}</i>{t}</b><span>{s}</span></div>' for k,n,t,s in [('SB3-EQ1','01','0–8초 · 정면 고정','A의 독백, 공간을 익힌다'),('SB3-EQ2','02','8–14초 · 소리가 부른다','왼쪽 뒤 문소리 → A가 돌아본다 → 관객이 따라 돈다'),('SB3-EQ3','03','14–22초 · 새 정면','−130°가 새 정면이 된다. B 등장')])+'</div>'
 +f'<div class="col side">{top360}<b>시점도</b><span>사건의 위치를 각도로 적는다. 한 씬에서 돌아야 하는 각도 합이 180°를 넘으면 멀미.</span><span>칸마다 적는 것: 예상 정면 각도 · 시선 유도 장치(소리·빛·시선) · 회전 시간(90°에 2초+)</span></div></div>',
 '<b>도판 SB-3</b> 360·VR 보드 — 전개도 세 칸과 시점도 한 장. 뒤쪽의 사건은 그림이 아니라 소리로 부른다.',ttl='360·VR 보드 — 주의의 축을 설계한다')
# ---------- SB-4 ----------
SB4=fig('<div class="grid c2">'+f'<div class="it"><img src="{I("SB4-CURVED")}"><b>곡면·원통 LED — 평면도 + 전개도</b><span>관람점에서 왜곡 없는 반경을 먼저 정한다 · 글자와 얼굴은 아이라인 밴드(바닥 1.4~1.8 m)에만 · 이음새 위에 글자를 올리지 않는다 · 수평 이동은 초당 15° 이하</span></div><div class="it"><img src="{I("SB4-FACADE")}"><b>미디어 파사드 — 입면 픽셀 지도 + 보는 거리</b><span>최소 관람 거리(m) ≈ 픽셀 피치(mm) · 글자 높이는 거리의 1/250 → 사실상 글자 금지, 형태와 색만 · 보행 20 m / 길 건너 60 m / 원경 150 m 세 지점에서 시뮬레이션</span></div></div>',
 '<b>도판 SB-4</b> 곡면 LED와 미디어 파사드의 보드. "화면"이 아니라 "관객이 어디서 얼마나 오래 보는가"가 첫 칸이다.',ttl='곡면 LED · 미디어 파사드 — 보는 자리를 그린다')
# ---------- SB-5 ----------
SB5=fig('<div class="grid c3">'+f'<div class="it"><img src="{I("SB5-AR")}"><b>AR — 칸이 층으로 갈라진다</b><span>현실 / 추적면 / 가상 오브젝트 / UI 네 층을 따로 그린다 · 전환 기호 대신 "무엇을 해야 다음 칸인가"(탭·회전·접근) · 실패 분기 한 칸 필수</span></div><div class="it"><img src="{I("SB5-MR")}"><b>MR — 방의 지도 위에 그린다</b><span>가상물은 벽·바닥·테이블 앵커에 붙는다 · 실제 가구가 가상물을 가려야 믿긴다 · 이동 반경 2 m, 가디언 밖으로 유도 금지</span></div><div class="it"><img src="{I("P07-LEDWALL")}"><b>XR 스테이지 — 네 트랙 보드</b><span>실세트·배우 / LED 배경(언리얼) / 카메라 트래킹 / 조명 연동을 한 컷에 네 줄로 · 내부/외부 프러스텀, 플레이트 버전, 월 밝기를 적는다</span></div></div>',
 '<b>도판 SB-5</b> AR은 층으로, MR은 방 지도로, XR은 트랙으로 — 매체가 바뀌면 "한 칸"의 정의가 바뀐다. 공통점은 관객(또는 카메라)이 어디에 있는지를 먼저 그리는 것.',ttl='AR · MR · XR 보드')
# ---------- SB-6 replacement: notation panels + styles ----------
SB6=fig('<div class="grid c4">'+''.join(it(k,t,s) for k,t,s in [('SBMOVE-PAN','PAN','좌우 양방향 화살표'),('SBMOVE-TILT','TILT','세로 화살표'),('SBMOVE-ZOOMIN','ZOOM IN','안으로 모이는 네 화살표'),('SBMOVE-ZOOMOUT','ZOOM OUT','밖으로 퍼지는 네 화살표'),('FIG57-SCENE','DOLLY IN','바닥을 따라 다가가는 화살표'),('SBMOVE-TRACK','TRACK','인물과 나란한 긴 화살표'),('SBMOVE-CRANE','CRANE','위로 휘는 큰 화살표'),('SBMOVE-HANDHELD','HANDHELD','모서리의 지그재그')])+'</div>',
 '<b>도판 SB-6</b> 카메라 워킹을 보드에 그리는 법 — 인물의 이동은 검정, 카메라는 빨강 하나. 기호는 첫 칸 범례에 묶어 둔다.',ttl='칸 안에 그리는 카메라 언어 — 워킹 기호 8종')
SBSTYLE=fig('<div class="grid c2">'+''.join(it(k,t,s) for k,t,s in [('SBSTYLE-THUMB','섬네일 — 생각하는 그림','10초에 한 칸, 연출 혼자 본다. 버리기 쉬워서 좋다'),('SBSTYLE-LINE','클린 라인 — 현장의 그림','정보가 또렷하다. 광고·PPM 제출의 표준'),('SBSTYLE-TONAL','톤 보드 — 빛을 그리는 그림','명암 세 단계로 조명 방향까지. 영화·브랜드 필름'),('SBSTYLE-COLOR','컬러 콤프 — 애니매틱 직전','색과 리듬을 함께 검증. 모션그래픽·애니메이션')])+'</div>',
 '<b>도판 SB-6′</b> 스토리보드의 네 가지 스타일. 정밀도는 용도가 정한다 — 혼자 볼 그림과 열 명이 볼 그림은 다르다.',ttl='스토리보드 스타일 네 가지')
# ---------- SB-7 three lanes ----------
cols=[('01','0–2.5','SB7-01','ECU · 물방울'),('02','2.5–4.5','SB7-02','MCU · 병을 집는다'),('03','4.5–7','SB7-03','CU · 한 모금'),('04','7–9.5','SB7-04','LS · 도시 아침'),('05','9.5–11.5','SB7-05','ECU · 테이블 위'),('06','11.5–15','SB7-06','MS · 로고 CG')]
pic=''.join(f'<div class="pc"><div class="h"><span>{n}</span><span>{t}</span></div><img src="{I(k)}"><span>{c}</span></div>' for n,t,k,c in cols)
def lane(name,cells):
    return f'<div class="ln"><div class="nm">{name}</div><div class="cells">'+''.join(f'<div class="cl {c}">{x}</div>' for x,c in cells)+'</div></div>'
SB7=fig('<div class="lanes"><div class="ln"><div class="nm">PICTURE</div><div class="cells">'+pic+'</div></div>'
 +lane('VOICE',[('',''),('N 하루의 시작이 달라집니다','v'),('SYNC "음."','s'),('N 도시보다 먼저','v'),('',''),('N 오늘도, 브랜드명','v')])
 +lane('MUSIC',[('MUTE','m0'),('♪ 피아노 in','m'),('','m'),('','m'),('비트','m'),('엔딩 스팅 · 페이드','m')])
 +lane('SE',[('물방울','e'),('뚜껑','e'),('',''),('ATM 도시','e'),('',''),('whoosh','e')])
 +lane('CAP',[('',''),('하루의 시작','c'),('',''),('',''),('',''),('SUPER · TAG','c')])+'</div>',
 '<b>도판 SB-7</b> 15초 광고 6컷의 3레인 보드. 칸의 가로 길이가 곧 시간이다 — 내레이션이 칸보다 길면 그 자리에서 잘라야 한다. 음악 전환점은 컷 경계와 맞춘다.',ttl='내레이션과 소리를 보이게 — 3레인 보드')
# ---------- SB-8 ----------
SB8=fig('<div class="grid c2">'+f'<div class="it bad"><img src="{I("SB8-BAD")}"><b>✕ 읽히지 않는 칸</b><span>얇은 회색 선 · 네 가지 색 화살표 · 작은 글씨 · 번호 없음</span></div><div class="it">{cellhtml("FIG57-SCENE")}<b>○ 3 m 밖에서도 읽히는 칸</b><span>세 톤 · 화살표 한 색 · 큰 번호와 시간 · 글자는 칸 아래 두 줄</span></div></div>',
 '<b>도판 SB-8</b> 같은 정보, 다른 가독성. 보드는 모니터가 아니라 세트장 벽에 붙어 3 m 밖에서 읽히는 문서다.',ttl='잘 보이게 그리는 법')
# ---------- Vertical board ----------
VB=fig('<div class="grid c6">'+''.join(f'<div class="vb"><div class="h"><span>{n}</span><span>{t}</span></div><img src="{I(k)}"><b>{a}</b><span>{b}</span></div>' for n,t,k,a,b in [('01','0–1.5','VB-01','CU · LOCKED','하품 · 자막 "아침마다 이거?"'),('02','1.5–3.5','VB-02','ECU · HIGH · 푸시 인','손이 병을 집는다 · SE 뚜껑'),('03','3.5–6','VB-03','MCU · HH','한 모금, 눈을 뜬다 · "오."'),('04','6–8','VB-04','LS · LOW · TILT UP','창밖 도시 · N 도시보다 먼저'),('05','8–10','VB-05','2S · LOCKED','병 부딪힘 · SYNC 웃음'),('06','10–15','VB-06','MS · 푸시 인','제품 중앙 · 로고 CG · N 오늘도')])+'</div>',
 '<b>도판 SB-9</b> 세로 보드 샘플 — 15초 숏폼 광고(9:16, 6컷). 세로 칸은 좁으니 지문은 한 줄, 소리는 한 단어.',ttl='세로 보드 샘플')
# ---------- PPM-1 mood ----------
PPM1=fig('<div class="grid c3 mood">'+''.join(it(k,t,s) for k,t,s in [('TM-LIGHT','빛','이른 측광 · 긴 그림자 · 5600K'),('TM-COLOR','색','웜그레이 60 · 더스티블루 30 · 와인 10'),('TM-TEXTURE','질감','리넨 · 유리 · 물방울 · 나뭇결'),('TM-MOVE','움직임','slow dolly만 · 핸드헬드 금지'),('TM-PERSON','인물','과장 없는 표정 · 시선 아래→카메라'),('TM-ANTI','✕ 안티 레퍼런스','채도 높은 숏폼 룩 — 이렇게는 안 간다')])+'</div>'
 +'<div class="grid kwrow"><div class="kw"><b>맑은</b><span>대비 중간-높음 · 흰색 안 날림</span></div><div class="kw"><b>이른</b><span>창가 단일 광원 · 긴 그림자</span></div><div class="kw"><b>가벼운</b><span>컷 평균 2.5초 · 피아노 92 BPM</span></div>'
 +'<div class="sws"><i style="background:#EFE9DF"></i><i style="background:#8FA7B5"></i><i style="background:#7A1C2B"></i><i style="background:#F8F6F1"></i><i style="background:#3C3F45"></i><i style="background:#D9B38C"></i></div></div>',
 '<b>도판 PPM-1</b> 톤앤매너 보드 — 형용사 세 개, 레퍼런스 다섯 장과 안티 레퍼런스 한 장, 팔레트. 한 장이 촬영·미술·후반의 공통 언어가 된다.',ttl='톤앤매너 보드 · 아침 음료 15초')
# ---------- PPM-2 location ----------
plan=f'<svg viewBox="0 0 400 260" {SV} font-size="10"><rect width="400" height="260" fill="#F6F5F3" stroke="#1B1B1D"/><rect x="90" y="0" width="220" height="7" fill="#8FA7B5"/><text x="200" y="22" text-anchor="middle" fill="#3C3C40" font-size="9">창 (남동) · 07–10시 직사광</text><rect x="150" y="60" width="100" height="56" rx="4" fill="#D7D4CD" stroke="#1B1B1D"/><text x="200" y="92" text-anchor="middle">테이블</text>{person_top(180,134,r=8,fill="#1B1B1D",angle=180)}<text x="180" y="158" text-anchor="middle" font-size="9">배우 A</text><line x1="180" y1="222" x2="180" y2="170" stroke="#7A1C2B" stroke-width="4"/><text x="190" y="200" fill="#7A1C2B" font-size="9" font-weight="500">돌리 2 m</text><g font-weight="500">{camera_top(180,226,w=22,fill="#7A1C2B")}<text x="180" y="254" text-anchor="middle">C1 · 02·06</text>{camera_top(336,130,w=18,fill="#1B1B1D",angle=-90)}<text x="336" y="158" text-anchor="middle">C2 · 03</text>{camera_top(46,160,w=18,fill="#1B1B1D",angle=90)}<text x="46" y="188" text-anchor="middle">C3 · 04</text></g><g font-size="9"><circle cx="300" cy="50" r="8" fill="none" stroke="#1B1B1D" stroke-width="1.5"/><text x="312" y="54">K 키 LED 600W</text><circle cx="90" cy="90" r="8" fill="none" stroke="#1B1B1D" stroke-width="1.5"/><text x="18" y="114">F 바운스 4×4</text><rect x="230" y="150" width="12" height="12" fill="none" stroke="#1B1B1D" stroke-width="1.5"/><text x="248" y="160">B 튜브 3200K</text></g><rect x="360" y="220" width="40" height="40" fill="#E5E3DE"/><text x="380" y="244" text-anchor="middle" font-size="8">계단</text><rect x="0" y="180" width="30" height="80" fill="#E5E3DE"/><text x="15" y="222" text-anchor="middle" font-size="8" transform="rotate(-90 15 222)">카운터</text></svg>'
PPM2=fig('<div class="grid c4">'+''.join(it(k,t,s) for k,t,s in [('LOC-N','N 창가','메인 세트 · 07~10시 직사광'),('LOC-E','E 카운터','소음원 · 촬영 중 10분 정지'),('LOC-S','S 계단','장비 2인 운반 · 엘리베이터 없음'),('LOC-W','W 벽','리버스 숏 배경')])+'</div>'
 +f'<div class="grid plan"><div>{plan}</div><div class="facts"><b>측정값</b><span>전원 220V 2구 × 3 (3 kW) → 조명 2 kW 이하</span><span>천장 2.9 m · 창 폭 3.2 m · 원목 바닥(돌리 가능)</span><span>소음 72 dB(머신) · 주차 2대 · 화장실 1층</span><span>허가 07:00–10:30 대관 · 보험 ✔</span><b>우천 대안</b><span>키 LED로 창가 빛 재현, 또는 예비일 D+2 · L-02 스튜디오 가예약</span></div></div>',
 '<b>도판 PPM-2</b> 로케이션 시트 — 네 방향 사진(같은 시간, 같은 24mm)과 평면도. 평면도에 카메라·조명·돌리·전원·소음원이 들어가야 당일 세팅이 반으로 준다.',ttl='공간 레퍼런스 시트 · L-01 카페 2층')
# ---------- PPM-3 casting ----------
PPM3=fig('<div class="grid c3 cast">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b>{"".join(f"<span>{x}</span>" for x in ss)}</div>' for k,t,ss in [('CAST-A','후보 A — 1순위 ★',['인상 ●●●●○ · 광고 3편','가용 4/9 · 4/11 · 예비일 ○','초상권 1년 온라인+옥외','미소가 작아도 눈이 먼저 웃는다']),('CAST-B','후보 B — 2순위',['인상 ●●●○○ · 뮤직비디오 1편','가용 4/9만 · 예비일 ✕','초상권 6개월 온라인','미소가 크다 → "입꼬리만"']),('CAST-C','후보 C — 대안',['인상 ●●○○○ · 경험 없음','전일 가용 · 예비일 ○','교육용 한정','리허설 +30분 · 학생작이면 1순위'])])+'</div>',
 '<b>도판 PPM-3</b> 캐스팅 시트 — 같은 배경·같은 빛으로 찍은 정면 한 컷과 네 줄(인상·가용·초상권·선택 이유). 선택 이유는 톤앤매너의 말로 쓴다.',ttl='배우 시트 · 역할 A "아침을 시작하는 사람"')
# ---------- PPM-4 wardrobe + mise ----------
marks=[(52,56,'1'),(72,62,'2'),(63,78,'3'),(50,16,'4'),(16,52,'5'),(50,92,'6')]
mise=f'<div class="mise"><img src="{I("MISE-FRAME")}">'+''.join(f'<span class="pm" style="left:{x}%;top:{y}%">{n}</span>' for x,y,n in marks)+'</div>'
PPM4=fig('<div class="grid c2">'+it('WARD-1','LOOK 1 · 배우 A','리넨 셔츠 웜그레이 + 면 팬츠 차콜 · CUT 02·03·05·06 · 예비 1벌 · 금지: 로고·줄무늬·순백')+it('WARD-2','LOOK 2 · 배우 B','니트 더스티블루 + 오프화이트 · CUT 05 · A와 명도 차 2단계')+'</div>'
 +f'<div class="grid plan">{mise}<ol class="misel"><li><i>1</i>제품 — 라벨 정면, 와인색은 여기만</li><li><i>2</i>커피잔 — 아침 신호, 60% 색</li><li><i>3</i>책 + 리넨 냅킨 — 30% 색, 전경 깊이</li><li><i>4</i>창 + 블라인드 — 빛의 출처를 보여 준다</li><li><i>5</i>유칼립투스 — 왼쪽 여백, 유도선</li><li><i>6</i>원목 상판 — 질감 키워드</li><li class="x">치운 것: 메뉴판 · 냅킨 홀더 · 콘센트 · 포스터</li></ol></div>',
 '<b>도판 PPM-4</b> 의상 보드와 미장센 지도. 프레임 안 모든 물건에 "있는 이유"를 적지 못하면 치운다 — 이것이 미장센의 전부다.',ttl='의상 보드 · 미장센 지도 (CUT 06)')
# ---------- F60 interview ----------
int_top=f'<svg viewBox="0 0 300 200" {SV} font-size="10"><rect width="300" height="200" fill="#F6F5F3"/><rect x="40" y="10" width="220" height="8" fill="#B9B5AC"/><text x="150" y="30" text-anchor="middle" font-size="9" fill="#7A7A80">배경 — 깊이를 두고 얕은 심도</text>{person_top(150,80,r=10,angle=180)}<text x="150" y="108" text-anchor="middle">출연자</text><circle cx="60" cy="70" r="9" fill="none" stroke="#1B1B1D" stroke-width="1.5"/><line x1="54" y1="64" x2="66" y2="76" stroke="#1B1B1D"/><line x1="66" y1="64" x2="54" y2="76" stroke="#1B1B1D"/><text x="60" y="52" text-anchor="middle" font-size="9">키</text>{camera_top(150,168,w=22,fill="#7A1C2B")}<text x="150" y="196" text-anchor="middle" fill="#7A1C2B" font-weight="500">메인 카메라</text>{person_top(116,170,r=7,fill="#8E8A82")}<text x="104" y="196" text-anchor="middle" font-size="9">인터뷰어</text><line x1="150" y1="92" x2="122" y2="160" stroke="#7A1C2B" stroke-width="1.2" stroke-dasharray="4 3"/>{camera_top(240,146,w=18,fill="#1B1B1D",angle=-35)}<text x="262" y="172" text-anchor="middle" font-size="9">서브 (45°)</text></svg>'
F60=fig('<div class="grid c3">'+f'<div class="it">{int_top}<b>위에서 본 세팅</b><span>인터뷰어는 렌즈 바로 옆 — 시선은 거의 정면이면서 대화하듯 편안하다</span></div>'+it('INT-MAIN','메인 — 카메라 옆을 본다','시선 방향에 여백(룩룸)을 둔다')+it('INT-SUB','서브 — 표정을 받는다','45° 옆에서 클로즈업, 편집의 숨구멍')+'</div>',
 '<b>그림 60</b> 인터뷰 촬영 표준 세팅과 결과 화면. 정면 응시는 긴장을 만든다 — 인터뷰어를 렌즈 옆에 앉힌다.',ttl='인터뷰 — 두 대의 카메라, 한 사람의 시선')
# ---------- F62 blocking ----------
blk=f'<svg viewBox="0 0 300 200" {SV} font-size="10"><rect width="300" height="200" fill="#F6F5F3"/><rect x="20" y="40" width="8" height="60" fill="#8FA7B5"/><text x="34" y="46" font-size="9" fill="#7A7A80">창</text><rect x="250" y="20" width="30" height="8" fill="#B9B5AC"/><text x="265" y="42" text-anchor="middle" font-size="9">문</text>{person_top(262,52,r=7,fill="#8E8A82",angle=215)}<text x="262" y="76" text-anchor="middle" font-size="9">B</text>{person_top(110,130,r=9,angle=160)}<text x="110" y="156" text-anchor="middle" font-size="9">A</text><circle cx="200" cy="120" r="6" fill="#F0E6D6" stroke="#1B1B1D"/><text x="200" y="138" text-anchor="middle" font-size="8">스탠드</text>{camera_top(81,176,w=22,fill="#7A1C2B",angle=-20)}<text x="81" y="198" text-anchor="middle" fill="#7A1C2B" font-weight="500">카메라</text><polygon points="81,170 20,60 262,20" fill="#7A1C2B" opacity=".08"/><line x1="262" y1="62" x2="150" y2="118" stroke="#1B1B1D" stroke-width="1.5" stroke-dasharray="5 3"/><polygon points="150,112 142,122 156,124" fill="#1B1B1D"/><text x="214" y="98" font-size="9">B가 다가온다</text></svg>'
F62=fig('<div class="grid blk">'+f'<div class="it"><img src="{I("BLOCK-FRAME")}"><b>카메라가 보는 화면</b><span>전경 A — 크게, 주도권 · 후경 B — 작게, 문틀 속, 거리와 긴장</span></div><div class="it">{blk}<b>위에서 본 블로킹</b><span>미장센 = 화면 안에 놓인 모든 것 · 블로킹 = 배우와 카메라의 동선 설계</span></div></div>',
 '<b>그림 62</b> 미장센과 블로킹 — 화면 안의 배치와 위에서 본 동선. 깊이(전경·후경)가 관계를 말한다.',ttl='한 프레임 안의 두 사람')
# ---------- RES pixel figure ----------
res_svg=f'<svg viewBox="0 0 300 180" {SV} font-size="10"><rect x="10" y="10" width="280" height="158" fill="none" stroke="#1B1B1D" stroke-width="1.5"/><text x="16" y="24" font-size="10" font-weight="500">8K 7680×2160</text><rect x="10" y="89" width="140" height="79" fill="#7A1C2B" opacity=".12" stroke="#7A1C2B"/><text x="16" y="103" font-size="10" font-weight="500" fill="#7A1C2B">4K UHD 3840×2160</text><rect x="10" y="128" width="70" height="40" fill="#7A1C2B" opacity=".25" stroke="#7A1C2B"/><text x="14" y="140" font-size="8.5" fill="#1B1B1D">FHD 1920×1080</text><rect x="10" y="148" width="47" height="20" fill="#7A1C2B" opacity=".45"/><text x="13" y="162" font-size="7" fill="#fff">HD 1280×720</text></svg>'
RES=fig('<div class="grid c4">'+''.join(it(k,t,s) for k,t,s in [('RES-16','16 × 9 = 144픽셀','점이 보인다'),('RES-64','64 × 36 = 2,304픽셀','형태가 보인다'),('RES-256','256 × 144','표정이 보인다'),('RES-FULL','1920 × 1080 = 207만 픽셀','FHD — 픽셀이 사라진다')])+'</div>'
 +f'<div class="grid resrow"><div>{res_svg}</div><div class="facts"><b>해상도 = 점의 개수</b><span>HD의 4배가 FHD, FHD의 4배가 4K, 4K의 4배가 8K</span><span>같은 화면 크기면 점이 많을수록 선명하고, 같은 점 수면 화면이 클수록 거칠어진다(LED 피치)</span><span>4K로 찍고 FHD로 납품하면 두 배까지 잘라 써도 선명하다</span></div></div>',
 '<b>그림 0-1</b> 해상도와 픽셀 — 같은 사진을 144개, 2,304개, 3만 6천 개, 207만 개의 점으로 그린 것. 점이 보이지 않게 되는 순간이 "화질"이다.',ttl='픽셀이 모여 화면이 된다')

# ================= PATCH =================
def repl_fig(s,num,new):
    pat=re.compile(r'<figure class="wide diagram">\s*<img src="img/[^"]+"[^>]*>\s*<figcaption><b>'+num+r'</b>.*?</figcaption>\s*</figure>',re.S)
    s2,n=pat.subn(new,s,count=1)
    if n==0: print('!! not found',num)
    return s2
# part02
s=rd('parts/part02.html')
for num,new in [('그림 20',F20),('그림 21',F21),('그림 22',F22),('그림 23',F23),('그림 25',F25),('그림 26',F26),('그림 27',F27)]: s=repl_fig(s,num,new)
def add_to_gallery(s,title,k,cap,sub=''):
    m=re.search(r'(<div class="gallery[^"]*"><div class="title"><b>'+re.escape(title)+r'</b>.*?)(</div>\s*)(?=<(?!figure)|$)',s,flags=re.S)
    # find the gallery block end: the first "</div>" that closes gallery after last figure
    i=s.find('<b>'+title+'</b>')
    if i<0: print('!! gallery not found',title); return s
    j=s.find('</div>\n',s.find('</figure>',i))
    # move to last </figure> within this gallery: iterate while next tag is <figure
    k2=i
    while True:
        nf=s.find('<figure',k2); ng=s.find('</div>',k2)
        if nf!=-1 and nf<ng: k2=s.find('</figure>',nf)+len('</figure>')
        else: break
    ins=f'<figure><img src="{I(k)}" alt=""><figcaption><b>{cap}</b>{sub}</figcaption></figure>'
    return s[:k2]+ins+s[k2:]
s=add_to_gallery(s,'참고 사진 2.14A','P02-COLOR-WARM','황금빛 역광','향수와 따뜻함 — 가족·회상·명절 광고. 노을 시간대 역광')
s=add_to_gallery(s,'참고 사진 2.17A','P02-FACE-DUTCH','얼굴 더치 앵글','수평선이 기운다 — 불안·취기·광기. 스릴러의 신호')
s=add_to_gallery(s,'참고 사진 2.18A','P02-GAZE-LEVEL','눈높이의 차이','내려다봄과 올려다봄 — 시선 높이가 권력 관계를 말한다')
wr('parts/part02.html',s)
# part03 lens gallery
s=rd('parts/part03.html'); s=add_to_gallery(s,'참고 사진 3.4A','P03-LENS300','d','300mm — 극단적 압축, 거리의 관찰자'); wr('parts/part03.html',s)
# part06: TEAM2, F60, F62
s=rd('parts/part06.html')
s=repl_fig(s,'그림 60',F60); s=repl_fig(s,'그림 62',F62); wr('parts/part06.html',s)
# prologue: RES after P00-FPS figure in 0.2
s=rd('parts/prologue.html'); i=s.find('data-id="P00-FPS"'); j=s.find('</figure>',i)+len('</figure>'); s=s[:j]+'\n'+RES+s[j:]; wr('parts/prologue.html',s)
# storyboard feature
s=rd('parts/feature_storyboard.html')
def repl_block(s,start_marker,end_marker,new,label):
    i=s.find(start_marker)
    if i<0: print('!! block not found',label); return s
    j=s.find(end_marker,i)+len(end_marker)
    return s[:i]+new+s[j:]
# 57' svg figure + 57 original
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 1000 470"','</figure>',F57,'57p')
s=repl_block(s,'<figure class="wide diagram"><img src="img/p234_252_1831x997.png"','</figure>','','57orig')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 640"','</figure>',SB1,'SB1')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 420"','</figure>',SB2,'SB2')
# vertical board block
s=s.replace('<h3>세로 보드 샘플 — 15초 숏폼 광고 (9:16, 8컷)</h3>','<h3>세로 보드 샘플 — 15초 숏폼 광고 (9:16, 6컷)</h3>')
i=s.find('<div class="board cols-6">'); j=s.find('<p class="small sans">세로 보드는 한 줄에 6칸',i); s=s[:i]+VB+'\n  '+s[j:]
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 520"','</figure>',SB3,'SB3')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 560"','</figure>',SB4,'SB4')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 600"','</figure>',SB5,'SB5')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 700"','</figure>',SB6+SBSTYLE,'SB6')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 400"','</figure>',SB7,'SB7')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 300"','</figure>',SB8,'SB8')
# remove the P06-SB-360 / P06-SB-FACADE placeholders now redundant? keep SB-360 (photo), drop FACADE placeholder
s=re.sub(r'<figure class="ph wide" data-id="P06-SB-FACADE".*?</figure>\n?','',s,flags=re.S)
wr('parts/feature_storyboard.html',s)
# PPM feature
s=rd('parts/feature_ppm.html'); s=s.replace('data-id="P06-TEAM"','data-id="P06-TEAM2"').replace('>P06-TEAM<','>P06-TEAM2<')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 520"','</figure>',PPM1,'PPM1')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 500"','</figure>',PPM2,'PPM2')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 420"','</figure>',PPM3,'PPM3')
s=repl_block(s,'<figure class="wide diagram">\n    <svg viewBox="0 0 980 520"','</figure>',PPM4,'PPM4')
# swatches block in PPM1 now redundant -> remove
s=re.sub(r'<div class="swatches">.*?</div>\n','',s,count=1,flags=re.S)
# remove duplicate photo placeholders that the new boards already cover
for k in ['P06-MOOD','P06-SCOUT','P06-CASTING','P06-WARDROBE','P06-PROPS']:
    s=re.sub(r'<figure class="ph[^"]*" data-id="'+k+r'".*?</figure>\n?','',s,flags=re.S)
# shooting time schedule: add thumbnails
thumbs={'CUT 02':'SB7-02','CUT 03':'SB7-03','CUT 06':'SB7-06','CUT 05':'SB7-05','CUT 01':'SB7-01'}
def tt_row(m):
    row=m.group(0)
    for k,v in thumbs.items():
        if f'<b>{k}' in row:
            return row.replace('<div class="bar">',f'<div class="th"><img src="{I(v)}"></div><div class="bar">',1)
    return row.replace('<div class="bar">','<div class="th"></div><div class="bar">',1)
s=re.sub(r'<div class="h">.*?</div><div class="bar">.*?</div>',tt_row,s,flags=re.S)
s=s.replace('<div class="tt">','<div class="tt tt3">')
wr('parts/feature_ppm.html',s)
print('patched')

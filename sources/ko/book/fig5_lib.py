# -*- coding: utf-8 -*-
"""Round-5 builders: PART 5 end, PART 7 (media), PART 8 (ads)."""
import math
from fig4_lib import *
from glyphs import profile, figure, camera_side, person_top, camera_top, light_top, softbox_top

def F54():
    cols=[('AM-CEL','셀 애니메이션','투명 셀에 그려 배경 위에 겹친다'),('AM-CUTOUT','컷아웃','관절로 나눈 종이를 조금씩 움직인다'),('AM-SAND','샌드 애니메이션','빛 위의 모래를 한 프레임씩 흩는다'),('AM-PIXIL','픽실레이션','사람을 인형처럼 한 장씩 찍는다'),
          ('AM-PAPER','페이퍼 드로잉','종이 한 장에 한 프레임, 넘기며 확인'),('AM-CLAY','클레이 · 스톱모션','입체 인형을 조금씩 움직여 촬영'),('AM-3D','3D CG','리그를 움직이고 컴퓨터가 계산한다'),('AM-ROTO','로토스코프','실사 위에 한 장씩 따라 그린다')]
    g='<div class="grid c4">'+''.join(it(k,t,s) for k,t,s in cols)+'</div>'
    return fig(g,'<b>그림 54</b> 애니메이션의 여덟 가지 방식 — 재료가 달라지면 움직임의 질감과 제작 방식이 함께 달라진다. 왼쪽 위에서 오른쪽 아래로 갈수록 "그림"에서 "계산"으로 옮겨 간다.',ttl='무엇으로 한 프레임을 만드는가에 따라 방식이 갈린다')
def F55():
    g=f'<div class="grid c2"><div class="it"><img src="{I("AN-2D")}"><b>2D — 한 장씩 그린다</b><span>그림 한 장 = 한 프레임. 원본 그림 위에 다음 그림을 그린다 · 선·색·움직임이 한 손에서 나온다 · 수정은 다시 그리는 일</span></div><div class="it"><img src="{I("AN-3D")}"><b>3D — 모델을 움직인다</b><span>리그(뼈대)를 만든 뒤 포즈 = 키프레임만 찍는다 · 사이는 컴퓨터가 계산 · 카메라·조명·재질을 따로 바꿀 수 있다 · 수정은 값을 고치는 일</span></div></div>'
    return fig(g+'<div class="rulebar"><b>고를 때의 기준</b> — 손맛과 과장이 필요하면 2D, 카메라가 돌고 같은 캐릭터를 여러 각도·여러 편에서 써야 하면 3D. 실무에서는 둘을 섞는다(2D 룩의 3D, 3D 배경 위 2D 인물).</div>','<b>그림 55</b> 2D와 3D — 그림이 움직임을 만드는 방식과 움직임을 설계하는 방식. 왼쪽은 연속 프레임 드로잉, 오른쪽은 리그와 키프레임이 보이는 3D 뷰포트.',ttl='2D는 움직임을 그리고, 3D는 움직임을 설계한 뒤 계산한다')
def F65():
    vf=f'<div class="eqw2"><img src="{I("EQUI-SQ")}"><i></i></div>'
    g=f'<div class="grid c3 arrows"><div class="it"><img src="{I("FISHEYE")}"><b><i>1</i>두 개의 어안 렌즈</b><span>앞뒤 180°씩 두 장의 둥근 그림</span></div><div class="it"><img src="{I("EQUI-SQ")}"><b><i>2</i>이어 붙인 한 장 — 등장방형 2:1</b><span>지구본을 펼친 세계지도처럼, 위아래가 늘어난다</span></div><div class="it">{vf}<b><i>3</i>관객이 보는 창</b><span>헤드셋·폰은 이 지도의 90° 정도만 보여 준다 — 붉은 틀</span></div></div>'
    g+='<div class="chips"><b>그래서 360은 "프레임"이 아니라 "시선을 부르는 수단"을 설계한다</b><span>소리 — 뒤에서 나는 소리</span><span>빛 — 밝은 쪽을 본다</span><span>움직임 — 움직이는 것을 따라간다</span><span>인물 시선 — 그가 보는 곳을 본다</span><span>선 · 통로 — 길을 따라간다</span></div>'
    return fig(g,'<b>그림 65</b> 360 영상의 구조 — 두 장의 어안 화면을 이어 붙여 한 장의 지도(등장방형)로 만들고, 관객은 그 지도의 일부만 창으로 본다.',ttl='360 영상은 두 장의 어안 화면을 이어 붙여 한 장의 지도로 편다')
def vr_room():
    s=f'<svg viewBox="0 0 560 300" {SV} font-size="11"><rect width="560" height="300" fill="{CARD}"/>'
    # one-point perspective floor
    s+=f'<polygon points="0,300 560,300 400,120 160,120" fill="#EDEAE4"/><rect x="160" y="40" width="240" height="80" fill="#E3E0D9"/>'
    # distance bands
    for (y0,y1,col,op,lab,sub) in [(230,300,WINE,.18,'0.5 m 안 — 불편 구역','초점이 안 맞고 눈이 아프다'),(150,230,WINE,.08,'1 ~ 3 m — 상호작용 구역','손이 닿고 입체감이 가장 또렷하다'),(120,150,'#8E8A82',.15,'8 m 밖 — 배경 구역','깊이감이 사라져 그림처럼 보인다')]:
        # trapezoid between y0,y1 following perspective
        def xl(y): return 160+(0-160)*(y-120)/180
        def xr(y): return 400+(560-400)*(y-120)/180
        s+=f'<polygon points="{xl(y0):.0f},{y0} {xr(y0):.0f},{y0} {xr(y1):.0f},{y1} {xl(y1):.0f},{y1}" fill="{col}" opacity="{op}"/>'
        s+=f'<text x="{xr(y0)-8 if y0>140 else 404:.0f}" y="{y0+20 if y0>140 else 136}" text-anchor="{"end" if y0>140 else "start"}" fill="{INK}" font-weight="600" font-size="12">{lab}</text>'
    # objects: same-size cubes at 1,3,8 m appear smaller
    for (cx,cy,sz) in [(120,222,46),(230,172,24),(300,132,10)]:
        s+=f'<rect x="{cx-sz/2}" y="{cy-sz}" width="{sz}" height="{sz}" fill="{INK}" opacity=".85"/>'
    s+=f'<text x="120" y="262" text-anchor="middle" fill="{INK}" font-size="12" font-weight="600">1 m</text><text x="230" y="194" text-anchor="middle" fill="{INK}" font-size="12" font-weight="600">3 m</text><text x="300" y="152" text-anchor="middle" fill="{INK}" font-size="12" font-weight="600">8 m</text>'
    # viewer
    s+=person_top(280,284,r=12,fill=WINE,angle=0)+f'<text x="310" y="290" fill="{WINE}" font-size="11" font-weight="600">관객</text>'
    return s+'</svg>'
def F65_1():
    g=f'<div class="grid plan">{vr_room()}{facts("같은 크기의 상자 세 개",["1 m — 크고 입체적, 손이 닿을 듯","3 m — 적당히, 가장 편한 거리","8 m — 작고 납작, 배경처럼"],"멀미를 줄이는 다섯 가지",["가속하지 않는다 — 등속 이동 또는 순간이동","수평선을 기울이지 않는다","카메라를 관객 키 높이(1.6 m)에 둔다","중요한 것은 정면 ±60° 안에","60 fps 이상, 지연 20 ms 이하"])}</div>'
    return fig(g,'<b>그림 65-1</b> VR 공간의 거리 설계 — 관객이 선 자리에서 1 m, 3 m, 8 m에 놓인 같은 상자는 크기와 입체감이 다르다. 상호작용은 1~3 m, 배경은 8 m 밖에 둔다.',ttl='VR 공간은 거리로 설계한다')
def xr_plan():
    s=f'<svg viewBox="0 0 560 250" {SV} font-size="10"><rect width="560" height="250" fill="{CARD}"/><rect x="20" y="20" width="520" height="210" fill="#fff" stroke="{INK}" stroke-width="1.2"/>'
    rooms=[(20,20,120,100,'입구 · 대기','헤드셋 착용 · 안내 2분',''),(140,20,130,100,'체험존 A','90초','01'),(270,20,130,100,'체험존 B','90초','02'),(400,20,140,100,'체험존 C','90초','03'),(20,120,120,110,'소독 · 반납','',''),(140,120,260,110,'포토존','사진 · 공유 60초','04'),(400,120,140,110,'출구 · 굿즈','','05')]
    for x,y,w,h,n,t,num in rooms:
        fill='#F3EEF0' if num else '#F6F5F3'
        s+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{INK}" stroke-width=".8"/><text x="{x+10}" y="{y+22}" font-weight="500" fill="{INK}" font-size="11">{n}</text><text x="{x+10}" y="{y+36}" fill="{INK2}" font-size="8.5">{t}</text>'
        if num: s+=f'<circle cx="{x+w-16}" cy="{y+18}" r="9" fill="{WINE}"/><text x="{x+w-16}" y="{y+21.5}" text-anchor="middle" fill="#fff" font-size="8.5" font-weight="500">{num}</text>'
    # route
    s+=f'<path d="M40,210 L40,70 L80,70 L205,70 L335,70 L470,70 L470,160 L270,175 L80,175 L80,200" fill="none" stroke="{WINE}" stroke-width="2.5" stroke-dasharray="7 4"/>'
    s+=f'<polygon points="470,155 465,145 475,145" fill="{WINE}"/><polygon points="85,198 75,198 80,208" fill="{WINE}"/>'
    s+=f'<text x="30" y="226" fill="{WINE}" font-size="9" font-weight="500">IN</text><text x="505" y="226" fill="{WINE}" font-size="9" font-weight="500">OUT →</text>'
    return s+'</svg>'
def F67():
    return fig(xr_plan()+'<div class="rulebar">입구에서 출구까지 <b>한 줄</b>로. 되돌아오는 동선이 생기면 헤드셋을 쓴 사람과 벗은 사람이 부딪힌다. 체험 90초 × 3 + 포토 60초 + 대기 = 1인 약 8분, 시간당 약 40명.</div>','<b>그림 67</b> XR 전시관 평면 동선도 — 붉은 점선이 관람 동선, 번호가 체험 순서다.',ttl='관람 동선은 입구에서 출구까지 하나의 줄로 설계한다')
def anam_svg():
    s=f'<svg viewBox="0 0 560 250" {SV} font-size="10"><rect width="560" height="250" fill="{CARD}"/>'
    # two walls of a corner in perspective: left face and right face meeting at x=200
    s+=f'<polygon points="40,60 200,30 200,210 40,190" fill="#E5E3DE" stroke="{INK}" stroke-width="1"/><polygon points="200,30 360,60 360,190 200,210" fill="#D7D4CD" stroke="{INK}" stroke-width="1"/>'
    # distorted box drawn across both faces (sheared)
    s+=f'<polygon points="90,90 200,70 200,150 90,160" fill="{WINE}" opacity=".55"/><polygon points="200,70 300,95 300,160 200,150" fill="{WINE}" opacity=".75"/><polygon points="90,90 140,75 250,55 200,70" fill="{WINE}" opacity=".35"/>'
    s+=f'<text x="120" y="182" text-anchor="middle" fill="{INK2}" font-size="9">면 A — 늘려 그린 그림</text><text x="282" y="182" text-anchor="middle" fill="{INK2}" font-size="9">면 B — 늘려 그린 그림</text>'
    # sweet spot viewer and sight lines
    s+=f'<circle cx="470" cy="150" r="12" fill="{INK}"/><text x="470" y="178" text-anchor="middle" fill="{INK}" font-weight="500">기준 시점</text><text x="470" y="190" text-anchor="middle" fill="{INK2}" font-size="8.5">이 자리에서만 상자로 보인다</text>'
    for (x,y) in [(90,90),(300,95),(300,160),(90,160)]: s+=f'<line x1="470" y1="150" x2="{x}" y2="{y}" stroke="{WINE}" stroke-width=".7" stroke-dasharray="3 3"/>'
    # off-axis viewer
    s+=f'<circle cx="120" cy="232" r="9" fill="none" stroke="{MUT}" stroke-width="1.5"/><text x="140" y="236" fill="{MUT}" font-size="8.5">옆에서 보면 찌그러진 두 장의 그림</text>'
    # inset: what sweet spot sees
    s+=f'<rect x="400" y="24" width="140" height="92" fill="#fff" stroke="{INK}"/><text x="470" y="40" text-anchor="middle" font-size="8.5" fill="{INK2}">기준 시점에서 본 화면</text>'
    s+=f'<polygon points="430,66 490,56 490,96 430,106" fill="{WINE}" opacity=".55"/><polygon points="490,56 520,66 520,106 490,96" fill="{WINE}" opacity=".75"/><polygon points="430,66 460,52 520,52 490,56" fill="{WINE}" opacity=".35"/>'
    return s+'</svg>'
def F68():
    g='<div class="grid c2">'+it('ANAM-FRONT','기준 시점에서 — 상자가 튀어나와 보인다','두 면의 그림이 한 지점에서 하나로 합쳐진다')+it('ANAM-SIDE','옆에서 — 찌그러진 두 장의 그림','기준 시점을 벗어나면 착시가 풀린다')+'</div>'
    return fig(g+'<div class="rulebar">두 면에 <b>일부러 왜곡해</b> 그린 그림이 한 지점에서만 하나로 합쳐진다. 그래서 설계의 첫 질문은 "관객이 어디에 서는가"이고, 그 자리가 곧 촬영 포인트(온라인 확산의 출발점)다. 보도 폭·횡단보도·건너편 인도를 먼저 잰다.</div>','<b>그림 68</b> 아나몰픽 착시의 원리 — 기준 시점에서는 상자, 옆에서는 찌그러진 그림 두 장.',ttl='두 면에 나누어 왜곡된 그림이 한 지점에서만 하나로 합쳐진다')
def dist_svg():
    s=f'<svg viewBox="0 0 560 230" {SV} font-size="10"><rect width="560" height="230" fill="{CARD}"/><rect x="24" y="30" width="22" height="170" fill="{INK}"/><text x="35" y="22" text-anchor="middle" font-size="9" fill="{INK}">LED 벽</text><line x1="46" y1="200" x2="540" y2="200" stroke="{INK}"/>'
    # three viewers at 5/15/40 m, letter height proportional to distance/250: 2cm, 6cm, 16cm → draw letter sizes 8,16,30
    for (x,d,sz,cm) in [(150,'5 m',9,'2 cm'),(300,'15 m',18,'6 cm'),(500,'40 m',34,'16 cm')]:
        s+=f'<circle cx="{x}" cy="150" r="8" fill="{INK}"/><line x1="{x}" y1="158" x2="{x}" y2="200" stroke="{INK}" stroke-width="3"/><text x="{x}" y="218" text-anchor="middle" font-weight="500">{d}</text>'
        s+=f'<text x="{x}" y="{100}" text-anchor="middle" font-family="Noto Sans CJK KR" font-weight="700" font-size="{sz}" fill="{WINE}">가</text><text x="{x}" y="{112+sz*0.2:.0f}" text-anchor="middle" font-size="8.5" fill="{INK2}">최소 {cm}</text>'
        s+=f'<line x1="46" y1="{115-sz*0.4:.0f}" x2="{x}" y2="150" stroke="{LINE}" stroke-width=".8"/>'
    s+=f'<text x="300" y="42" text-anchor="middle" fill="{INK}" font-weight="500">멀수록 글자가 커야 읽힌다 — 최소 글자 높이 ≈ 거리 ÷ 250</text>'
    return s+'</svg>'
def F66_1():
    return fig(dist_svg(),'<b>그림 66-1</b> 관람 거리와 글자 크기 — 5 m에서 2 cm, 15 m에서 6 cm, 40 m에서 16 cm. 반대로 가까이 보는 화면일수록 픽셀 피치가 촘촘해야 한다(최소 관람 거리 m ≈ 피치 mm).',ttl='거리가 글자 크기를 정한다')
def F71():
    g='<div class="grid c2">'+it('PROJ-MAP','프로젝션 매핑 — 빛을 쏘아 입힌다','어두워야 보인다 · 건물 형태가 곧 캔버스 · 설치가 빠르고 일회성 행사에 유리 · 투사 거리와 프로젝터 수가 관건')+it('LED-FACADE','LED 사이니지 · 미디어 파사드 — 면 자체가 빛난다','낮에도 보인다 · 상시 운영 · 픽셀 피치와 보는 거리가 관건 · 설치비는 높지만 콘텐츠 교체가 쉽다')+'</div>'
    return fig(g+'<div class="rulebar">프로젝션은 <b>표면</b>을 빌리고, LED는 <b>표면</b>을 만든다. 하룻밤 행사면 프로젝션, 매일 켜야 하면 LED.</div>','<b>그림 71</b> 프로젝션 매핑과 LED 사이니지 — 같은 "건물에 영상"이지만 빛의 출처가 다르다.',ttl='빛을 쏘아 입히는 방식과 면 자체가 빛나는 방식')
def throw_svg():
    s=f'<svg viewBox="0 0 300 150" {SV} font-size="9"><rect width="300" height="150" fill="{CARD}"/><rect x="14" y="66" width="30" height="16" fill="{INK}"/><polygon points="44,74 250,22 250,126" fill="{WINE}" opacity=".15"/><rect x="250" y="18" width="8" height="112" fill="#B9B5AC"/>'
    s+=f'<line x1="44" y1="140" x2="250" y2="140" stroke="{INK}"/><text x="147" y="136" text-anchor="middle" fill="{INK}" font-weight="500">투사 거리 D</text><line x1="276" y1="18" x2="276" y2="130" stroke="{INK}"/><text x="290" y="76" fill="{INK}" font-weight="500" transform="rotate(90 290 76)">화면 폭 W</text>'
    s+=f'<text x="147" y="104" text-anchor="middle" fill="{WINE}" font-weight="500" font-size="10">D = W × 투사비</text><text x="147" y="118" text-anchor="middle" fill="{INK2}" font-size="8.5">투사비 1.5 · 폭 6 m → 9 m 뒤에 둔다</text></svg>'
    return s
def F72():
    g=f'<div class="grid blk">'+it('PROJECTOR','프로젝터는 거리로 화면을 만든다','멀수록 크고 어두워진다 — 밝기(루멘)는 면적에 비례해 필요')+f'<div class="it">{throw_svg()}<b>실무에서 쓰는 식</b><span>투사비(Throw Ratio) = 거리 ÷ 폭. 단초점 0.3~0.8, 표준 1.2~2.0, 장초점 2.0 이상 · 밝기 목표: 실내 어두움 1,000~2,000 lm/m², 밝은 로비 3,000 lm/m²</span></div></div>'
    return fig(g,'<b>그림 72</b> 프로젝터 투사 거리와 화면 크기 — 거리·화면 폭·투사비 셋 중 둘을 정하면 나머지가 정해진다. 설치 전 가장 먼저 재는 숫자다.',ttl='투사 거리 = 화면 폭 × 투사비')
def F74():
    g=f'<div class="grid lens"><img src="{I("VR-STEREO")}">{facts("두 눈의 시차가 깊이가 된다",["사람의 두 눈은 약 65 mm 떨어져 있다 — 같은 물체를 조금 다른 각도로 본다","뇌가 그 차이(시차)를 깊이로 읽는다","공간 영상은 렌즈 두 개로 이 두 장을 그대로 기록하고, 헤드셋은 각 눈에 제 그림을 보여 준다","시차가 클수록 가까워 보이고, 과하면 눈이 아프다"])}</div>'
    return fig(g,'<b>그림 74</b> 공간 영상의 양안 기록 원리 — 두 눈이 보는 두 장을 그대로 기록해 두 눈에 돌려준다.',ttl='공간 영상은 두 눈의 시차를 그대로 기록해 깊이를 만든다')
def dim_svg():
    s=f'<svg viewBox="0 0 560 230" {SV} font-size="10"><rect width="560" height="230" fill="{CARD}"/>'
    items=[('점','0차원','위치만 있다','칸딘스키 1926'),('선','1차원','점이 움직인 자취','파울 클레 1925'),('면','2차원','선이 움직인 자취','말레비치 1915'),('입체','3차원','면이 움직인 자취','피카소 · 브라크 1907'),('시간','4차원','입체가 시간 속을 움직인다','뤼미에르 1895')]
    for i,(t,d,desc,ref) in enumerate(items):
        x=20+i*108
        s+=f'<text x="{x}" y="28" font-size="17" font-weight="600" fill="{INK}">{t}</text><text x="{x+34}" y="28" font-size="9" fill="{WINE}" font-weight="500">{d}</text>'
        cx,cy=x+44,100
        if i==0: s+=f'<circle cx="{cx}" cy="{cy}" r="6" fill="{WINE}"/>'
        elif i==1: s+=f'<line x1="{cx-36}" y1="{cy}" x2="{cx+36}" y2="{cy}" stroke="{WINE}" stroke-width="3"/><circle cx="{cx-36}" cy="{cy}" r="4" fill="{WINE}"/>'
        elif i==2: s+=f'<polygon points="{cx-30},{cy+22} {cx+14},{cy+22} {cx+30},{cy-22} {cx-14},{cy-22}" fill="{WINE}" opacity=".8"/>'
        elif i==3: s+=f'<polygon points="{cx-28},{cy-6} {cx+8},{cy-6} {cx+8},{cy+30} {cx-28},{cy+30}" fill="{WINE}" opacity=".85"/><polygon points="{cx-28},{cy-6} {cx-12},{cy-24} {cx+24},{cy-24} {cx+8},{cy-6}" fill="{WINE}" opacity=".55"/><polygon points="{cx+8},{cy-6} {cx+24},{cy-24} {cx+24},{cy+12} {cx+8},{cy+30}" fill="{WINE}" opacity=".7"/>'
        else:
            for k in range(4):
                o=k*14; op=.25+.2*k
                s+=f'<polygon points="{cx-34+o},{cy+4} {cx-10+o},{cy+4} {cx-10+o},{cy+28} {cx-34+o},{cy+28}" fill="{WINE}" opacity="{op}"/><polygon points="{cx-34+o},{cy+4} {cx-24+o},{cy-8} {cx+o},{cy-8} {cx-10+o},{cy+4}" fill="{WINE}" opacity="{op-.1}"/>'
            s+=f'<line x1="{cx-40}" y1="{cy+40}" x2="{cx+50}" y2="{cy+40}" stroke="{INK}"/><polygon points="{cx+50},{cy+36} {cx+58},{cy+40} {cx+50},{cy+44}" fill="{INK}"/><text x="{cx+52}" y="{cy+54}" font-size="8" fill="{MUT}">t</text>'
        if i<4: s+=f'<text x="{x+96}" y="{cy+4}" fill="{MUT}" font-size="14">→</text>'
        s+=f'<text x="{x}" y="166" fill="{INK}" font-weight="500" font-size="9.5">{desc}</text><text x="{x}" y="180" fill="{MUT}" font-size="7.8">{ref}</text>'
    s+=f'<rect x="20" y="196" width="520" height="22" fill="{WINE}" opacity=".08"/><text x="280" y="211" text-anchor="middle" fill="{INK}" font-weight="500" font-size="9.5">실감 콘텐츠는 여기에 관객의 몸이 움직이는 "장소의 이동"을 더한다 — 보는 화면에서 들어가는 공간으로</text>'
    return s+'</svg>'
def F75():
    return fig(dim_svg(),'<b>그림 75</b> 조형의 차원 — 움직임이 차원을 하나씩 더한다. 점이 움직여 선, 선이 면, 면이 입체, 입체가 시간 속을 움직여 영상이 된다.',ttl='움직임이 차원을 하나씩 더한다')
HOOKS=[('HOOK-ANOMALY','시각적 이상','있어서는 안 될 것이 있다'),('HOOK-QUESTION','즉각적 질문','저 안에 뭐가 있지?'),('HOOK-MOTION','급격한 움직임','쏟아지고 터진다'),('HOOK-SILENCE','소리의 단절','시끄러운 곳의 고요'),('HOOK-FAMILIAR','친숙한 상황','"저거 나잖아"'),('HOOK-RESULT','결과 선공개','끝을 먼저 보여 준다')]
def F77():
    g='<div class="grid c3">'+''.join(f'<div class="it"><img src="{I(k)}"><b><i>0{i+1}</i>{t}</b><span>{s}</span></div>' for i,(k,t,s) in enumerate(HOOKS))+'</div>'
    return fig(g,'<b>그림 77</b> 후킹 3초의 여섯 가지 장치 — 첫 장면 한 장으로 손가락을 멈추게 하는 여섯 가지 방법. 하나만 골라 첫 컷에 쓴다.',ttl='첫 3초를 만드는 여섯 가지 장치')
def hook_tl():
    W=560; s=f'<svg viewBox="0 0 {W} 150" {SV} font-size="9.5"><rect width="{W}" height="150" fill="{CARD}"/>'
    x0=24; sc=(W-48)/15
    X=lambda t:x0+t*sc
    s+=f'<rect x="{X(0)}" y="40" width="{X(3)-X(0)}" height="18" fill="{WINE}"/><rect x="{X(3)}" y="40" width="{X(11)-X(3)}" height="18" fill="#B9B5AC"/><rect x="{X(11)}" y="40" width="{X(15)-X(11)}" height="18" fill="{INK}"/>'
    s+=f'<text x="{(X(0)+X(3))/2}" y="53" text-anchor="middle" fill="#fff" font-weight="500" font-size="9">후킹 0–3초</text><text x="{(X(3)+X(11))/2}" y="53" text-anchor="middle" fill="#fff" font-weight="500" font-size="9">전개 — 문제 → 제품 → 사용 장면</text><text x="{(X(11)+X(15))/2}" y="53" text-anchor="middle" fill="#fff" font-weight="500" font-size="9">CTA · 브랜드</text>'
    for n,(t,lab,sub) in enumerate([(0.5,'0.5초','질문 · 충돌'),(1.5,'1.5초','얼굴 · 움직임'),(3,'3초','약속'),(6,'6초','첫 이탈 구간 통과'),(12,'12초','브랜드 노출 시작')]):
        yy=80 if n%2==0 else 93
        s+=f'<line x1="{X(t):.1f}" y1="30" x2="{X(t):.1f}" y2="{yy-10}" stroke="{INK}" stroke-width="1"/><text x="{X(t):.1f}" y="24" text-anchor="middle" fill="{INK}" font-weight="500">{lab}</text><text x="{X(t):.1f}" y="{yy}" text-anchor="{"start" if n<3 else "middle"}" fill="{INK2}" font-size="8.5">{sub}</text>'
    s+=f'<text x="{x0}" y="116" fill="{INK}" font-weight="500">관객이 떠나는 두 개의 문: 1.5초(스크롤)와 6초(스킵 버튼). 첫 문 앞에 장치를, 두 번째 문 앞에 약속을 둔다.</text>'
    s+=f'<text x="{x0}" y="132" fill="{INK2}" font-size="9">세로 숏폼은 0–1.5초가 전부라고 보고, 자막 한 줄을 0초부터 띄운다.</text>'
    return s+'</svg>'
def F77_1():
    thumbs='<div class="grid c6 thumbs">'+''.join(f'<div class="it"><img src="{I(k)}"><b>{t}</b></div>' for k,t,_ in HOOKS)+'</div>'
    return fig(hook_tl()+thumbs,'<b>그림 77-1</b> 후킹 타임라인 — 0.5초에 질문이나 충돌, 1.5초에 얼굴이나 움직임, 3초에 약속. 아래는 첫 컷에 쓸 수 있는 여섯 장치.',ttl='후킹 타임라인 — 15초 안에서 손을 멈추게 하는 순서')
def funnel_svg():
    W=560; s=f'<svg viewBox="0 0 {W} 250" {SV} font-size="10"><rect width="{W}" height="250" fill="{CARD}"/>'
    rows=[('인지','브랜드 필름 · 범퍼 6초 · 숏폼','도달 · 조회수','보여 준다',.95),('관심','제품 시연 · 비교 · 언박싱','평균 시청 시간','궁금하게 한다',.72),('고려','후기 · 증언 · 사용기 · 라이브','클릭 · 저장 · 공유','믿게 한다',.5),('전환','혜택 고지 · 한정 · 리타기팅','구매 · 전환율 · CPA','움직이게 한다',.3)]
    y=20
    for i,(st,fm,kpi,job,w) in enumerate(rows):
        hw=130*w; cx=120
        nxt=rows[i+1][4]*130 if i<3 else 130*.18
        s+=f'<polygon points="{cx-hw},{y} {cx+hw},{y} {cx+nxt},{y+48} {cx-nxt},{y+48}" fill="{WINE}" opacity="{.95-.2*i}"/><text x="{cx}" y="{y+29}" text-anchor="middle" fill="#fff" font-weight="600" font-size="12">{st}</text>'
        s+=f'<text x="270" y="{y+18}" fill="{INK}" font-weight="500">{job}</text><text x="270" y="{y+33}" fill="{INK2}" font-size="9">{fm}</text><text x="470" y="{y+26}" fill="{WINE}" font-size="9" font-weight="500">{kpi}</text>'
        s+=f'<line x1="260" y1="{y+48}" x2="{W-20}" y2="{y+48}" stroke="{LINE}"/>'
        y+=54
    s+=f'<text x="270" y="{y+8}" fill="{MUT}" font-size="8.5">위는 많이·짧게, 아래는 적게·길게 — 한 영상으로 네 단계를 다 하지 않는다.</text><text x="470" y="20" fill="{MUT}" font-size="8">보는 지표</text>'
    return s+'</svg>'
def F78():
    return fig(funnel_svg(),'<b>그림 78</b> 마케팅 퍼널과 영상 형식의 대응 — 단계마다 영상의 역할, 형식, 보는 지표가 다르다.',ttl='단계마다 필요한 영상의 종류와 성과 지표가 다르다')

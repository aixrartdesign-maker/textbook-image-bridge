# -*- coding: utf-8 -*-
"""Professional silhouette glyphs for diagrams (SVG fragments). All drawn around origin, scale via transform."""
INK='#1B1B1D'; WINE='#7A1C2B'; MUT='#8E8A82'
# Side profile bust facing LEFT, height ~100 units: head top at y=-100, shoulders at y=0 (baseline), eye at (-14,-72)
PROFILE_PATH=("M-4,-100 C-22,-100 -34,-86 -33,-68 C-33,-58 -29,-50 -22,-44 C-19,-41 -18,-36 -20,-33 "
              "C-15,-30 -9,-29 -4,-30 L-2,-18 C-14,-14 -36,-10 -52,2 L52,2 C40,-10 24,-14 12,-18 L12,-34 "
              "C24,-40 32,-56 30,-74 C27,-92 14,-100 -4,-100 Z")
def profile(x,y,h=100,fill=INK,flip=False,opacity=1):
    """Side-view bust, facing left (flip=True → facing right). h = height in px."""
    s=h/100.0; fx=-1 if flip else 1
    return f'<path d="{PROFILE_PATH}" transform="translate({x},{y}) scale({fx*s},{s})" fill="{fill}" opacity="{opacity}"/>'
# Standing figure (front view) height 100: head at top
FIGURE_PATH=("M0,-100 C-7,-100 -11,-95 -11,-88 C-11,-81 -7,-76 0,-76 C7,-76 11,-81 11,-88 C11,-95 7,-100 0,-100 Z "
             "M-6,-73 L6,-73 C14,-73 19,-68 20,-60 L23,-30 L17,-29 L14,-55 L13,-40 L15,0 L5,0 L2,-36 L-2,-36 L-5,0 L-15,0 L-13,-40 L-14,-55 L-17,-29 L-23,-30 L-20,-60 C-19,-68 -14,-73 -6,-73 Z")
def figure(x,y,h=100,fill=INK,opacity=1):
    s=h/100.0
    return f'<path d="{FIGURE_PATH}" transform="translate({x},{y}) scale({s})" fill="{fill}" opacity="{opacity}"/>'
# Camera side view facing LEFT, width ~60 (lens at left): origin = body center
def camera_side(x,y,w=60,fill=INK,flip=False,label=''):
    s=w/60.0; fx=-1 if flip else 1
    g=(f'<g transform="translate({x},{y}) scale({fx*s},{s})">'
       f'<rect x="-14" y="-12" width="34" height="24" rx="3" fill="{fill}"/>'
       f'<rect x="-30" y="-8" width="17" height="16" rx="2" fill="{fill}"/><rect x="-34" y="-6" width="5" height="12" fill="{fill}"/>'
       f'<rect x="-8" y="-18" width="14" height="7" rx="1.5" fill="{fill}"/><rect x="8" y="-16" width="8" height="5" rx="1" fill="{fill}"/>'
       f'<rect x="-4" y="12" width="8" height="10" fill="{fill}"/><rect x="-12" y="20" width="24" height="3" fill="{fill}"/>'
       f'</g>')
    if label: g+=f'<text x="{x}" y="{y+36*s}" text-anchor="middle" font-size="{9}" fill="{fill}" font-weight="500">{label}</text>'
    return g
# Top-view person: head circle + shoulders + nose pointing UP (angle deg rotates: 0 = facing up)
def person_top(x,y,r=10,fill=INK,angle=0,opacity=1):
    return (f'<g transform="translate({x},{y}) rotate({angle})" opacity="{opacity}">'
            f'<ellipse cx="0" cy="{r*0.35:.1f}" rx="{r*1.9:.1f}" ry="{r*0.75:.1f}" fill="{fill}" opacity=".55"/>'
            f'<circle cx="0" cy="0" r="{r}" fill="{fill}"/><polygon points="{-r*0.35:.1f},{-r*0.9:.1f} {r*0.35:.1f},{-r*0.9:.1f} 0,{-r*1.35:.1f}" fill="{fill}"/></g>')
# Top-view camera pointing UP: body + lens trapezoid
def camera_top(x,y,w=22,fill=WINE,angle=0,label='',lab_fill=None):
    s=w/22.0
    g=(f'<g transform="translate({x},{y}) rotate({angle}) scale({s})">'
       f'<rect x="-11" y="-4" width="22" height="14" rx="2" fill="{fill}"/><polygon points="-5,-4 5,-4 7,-13 -7,-13" fill="{fill}"/>'
       f'<rect x="-9" y="10" width="6" height="3" fill="{fill}"/><rect x="3" y="10" width="6" height="3" fill="{fill}"/></g>')
    if label: g+=f'<text x="{x}" y="{y+22*s+4}" text-anchor="middle" font-size="9" fill="{lab_fill or fill}" font-weight="500">{label}</text>'
    return g
# Light fixture top view (fresnel-like): circle with barn doors, pointing in direction angle (0 = up)
def light_top(x,y,r=7,fill=WINE,angle=0,hollow=False):
    f='none' if hollow else fill
    return (f'<g transform="translate({x},{y}) rotate({angle})"><circle cx="0" cy="0" r="{r}" fill="{f}" stroke="{fill}" stroke-width="1.6"/>'
            f'<line x1="{-r*1.1:.1f}" y1="{-r*0.9:.1f}" x2="{-r*1.5:.1f}" y2="{-r*1.9:.1f}" stroke="{fill}" stroke-width="1.6"/><line x1="{r*1.1:.1f}" y1="{-r*0.9:.1f}" x2="{r*1.5:.1f}" y2="{-r*1.9:.1f}" stroke="{fill}" stroke-width="1.6"/></g>')
# Softbox top view: rectangle panel
def softbox_top(x,y,w=22,fill=WINE,angle=0):
    return f'<g transform="translate({x},{y}) rotate({angle})"><rect x="{-w/2}" y="-4" width="{w}" height="8" rx="1" fill="{fill}"/><rect x="-3" y="4" width="6" height="6" fill="{fill}"/></g>'
# Camera side view small with tripod (for side elevations)
def camera_tripod_side(x,y,h=40,fill=INK,flip=False):
    s=h/40.0; fx=-1 if flip else 1
    return (f'<g transform="translate({x},{y}) scale({fx*s},{s})"><rect x="-10" y="-40" width="20" height="13" rx="2" fill="{fill}"/><rect x="-18" y="-37" width="9" height="8" rx="1" fill="{fill}"/>'
            f'<line x1="0" y1="-27" x2="0" y2="-16" stroke="{fill}" stroke-width="2"/><line x1="0" y1="-16" x2="-10" y2="0" stroke="{fill}" stroke-width="2"/><line x1="0" y1="-16" x2="10" y2="0" stroke="{fill}" stroke-width="2"/><line x1="0" y1="-16" x2="0" y2="0" stroke="{fill}" stroke-width="2"/></g>')

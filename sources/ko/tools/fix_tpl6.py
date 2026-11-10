"""Rebuild the cells of storyboard template tpl-6 (4:5 feed) so the notes column sits inside each cell.
Usage: python3 fix_tpl6.py <templates.html> ko|en"""
import re, sys
path, lang = sys.argv[1], sys.argv[2]
L = {'ko': dict(labels=['SIZE', 'MOVE', '지문', 'N', 'SE'], memo='메모', head='헤드라인 영역'),
     'en': dict(labels=['SIZE', 'MOVE', 'Action', 'N', 'SE'], memo='NOTES', head='Headline area')}[lang]
s = open(path, encoding='utf-8').read()
a = s.index('<section class="page brk tpl" id="tpl-6">')
b = s.index('</section>', a)
sec = s[a:b]
lines = sec.split('\n')
# keep header lines (title, subtitle, project, director, separator) and footnote
head = [l for l in lines if ('y="22"' in l or 'y="40"' in l or 'y1="52"' in l or '<svg' in l) and '<rect' not in l]
foot = [l for l in lines if 'y="1178"' in l]
tail = [l for l in lines if l.startswith('</svg>')]
assert len(foot) == 1 and tail, (len(foot), len(tail))
W, H, G = 259.3333, 355.3333, 16
out = []
f = lambda v: f'{v:.1f}'
for r in range(3):
    for c in range(3):
        n = r * 3 + c + 1
        x0 = c * (W + G); y0 = 66 + r * (H + G)
        out.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(W)}" height="{f(H)}" fill="none" stroke="#1B1B1D" stroke-width="1"/>')
        out.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(W)}" height="18" fill="#1B1B1D"/><text x="{f(x0+6)}" y="{f(y0+13)}" fill="#fff" font-weight="500" font-size="9.5">CUT {n:02d}</text><text x="{f(x0+W-6)}" y="{f(y0+13)}" fill="#fff" text-anchor="end" font-size="9.5">____ s  ·  __:__–__:__</text>')
        fx, fy, fw, fh = x0 + 8, y0 + 26, 172.0, 215.0
        out.append(f'<rect x="{f(fx)}" y="{f(fy)}" width="{f(fw)}" height="{f(fh)}" fill="#F7F6F3" stroke="#1B1B1D" stroke-width="1"/>')
        out.append(f'<rect x="{f(fx+fw*.05)}" y="{f(fy+fh*.05)}" width="{f(fw*.9)}" height="{f(fh*.9)}" fill="none" stroke="#B8B4AC" stroke-dasharray="3 3" stroke-width=".6"/>')
        hx, hy, hw, hh = fx + fw * .08, fy + fh * .62, fw * .84, fh * .22
        out.append(f'<rect x="{f(hx)}" y="{f(hy)}" width="{f(hw)}" height="{f(hh)}" fill="none" stroke="#7A1C2B" stroke-dasharray="3 2" stroke-width=".7"/><text x="{f(hx+hw/2)}" y="{f(hy+hh/2+2.3)}" font-size="6.5" fill="#7A1C2B" text-anchor="middle">{L["head"]}</text>')
        # notes column right of the frame
        cx, cr = fx + fw + 9, x0 + W - 8
        blk = fh / 5
        for i, lab in enumerate(L['labels']):
            by = fy + i * blk
            out.append(f'<text x="{f(cx)}" y="{f(by+8)}" font-size="6.8" fill="#7A1C2B" font-weight="500">{lab}</text>')
            for k in (1, 2):
                ly = by + 8 + k * 12.5
                out.append(f'<line x1="{f(cx)}" y1="{f(ly)}" x2="{f(cr)}" y2="{f(ly)}" stroke="#D9D9DE" stroke-width=".6"/>')
        # notes rows under the frame
        my = fy + fh + 16
        out.append(f'<text x="{f(fx)}" y="{f(my)}" font-size="6.8" fill="#7A1C2B" font-weight="500">{L["memo"]}</text>')
        for k in range(1, 6):
            ly = my + k * 14
            if ly > y0 + H - 6:
                break
            out.append(f'<line x1="{f(fx)}" y1="{f(ly)}" x2="{f(cr)}" y2="{f(ly)}" stroke="#D9D9DE" stroke-width=".6"/>')
new = '\n'.join(head + out + foot + tail) + '\n'
s = s[:a] + new + s[b:]
open(path, 'w', encoding='utf-8').write(s)
print('tpl-6 rebuilt', lang, len(out), 'elements')

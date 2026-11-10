"""Text width in SVG user units for Noto Sans CJK (Latin/Cyrillic glyphs = Source Sans) at a given font size/weight."""
from PIL import ImageFont
_F = {}
W = {'400': 'Regular', '500': 'Medium', '600': 'Bold', '700': 'Bold', 'normal': 'Regular', 'bold': 'Bold'}


def tw(text, size, weight='400'):
    w = W.get(str(weight), 'Regular')
    if w not in _F:
        _F[w] = ImageFont.truetype(f'/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc', 100, index=1)
    return _F[w].getlength(text) * size / 100.0

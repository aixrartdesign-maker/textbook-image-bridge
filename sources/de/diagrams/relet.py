"""Re-letter an English diagram with translated strings.
python3 relet.py <lang> [stem ...]
inputs : inv3/<stem>.json (inventory), tr_<lang>/<stem>.json ({"<id>": "text", ...}; "\n" = forced break),
         EN image book_en/img_en/EN-<stem>.png
outputs: out_<lang>/<LANG>-<stem>.png, out_<lang>/<stem>_report.json
Erase: text components (alpha towards the text colour) that belong to the OCR line boxes -> flat fill with the
local background or inpainting on busy backgrounds. Draw: Noto Sans CJK (Latin/Cyrillic = Source Sans design),
same weight/size/colour/alignment/baseline; shrink (to 80 %) or wrap only when the space needs it; collision test
against the remaining artwork, against new text already placed and against the reserved boxes of the others."""
import json, os, re, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

S = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad'
D = S + '/ml/diag/'
IMG = S + '/book_en/img_en/'
FONTF = {w: f'/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc' for w in ['Regular', 'Medium', 'Bold', 'Black', 'DemiLight', 'Light']}
_fc = {}


def font(w, size):
    k = (w, round(size, 2))
    if k not in _fc:
        _fc[k] = TF(w, size)
    return _fc[k]


INTER = {'Regular': 'Regular', 'Medium': 'Medium', 'Bold': 'Bold', 'Black': 'Black', 'DemiLight': 'Light', 'Light': 'Light'}
FALLBACK = set('×…·')  # full-width (or, for the middle dot, double-width) in Noto Sans CJK -> take them from Inter


class TF:
    """Noto Sans CJK (Latin/Cyrillic = Source Sans design) with a few glyphs from Inter."""
    def __init__(self, w, size):
        self.w, self.size = w, size
        self.main = ImageFont.truetype(FONTF[w], size, index=1)
        self.fb = ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{INTER[w]}.otf', size)
        self.path = FONTF[w]

    def runs(self, text):
        out, cur, cf = [], '', None
        for ch in text:
            f = self.fb if ch in FALLBACK else self.main
            if f is not cf and cur:
                out.append((cur, cf)); cur = ''
            cf = f; cur += ch
        if cur:
            out.append((cur, cf))
        return out

    def getlength(self, text):
        return sum(f.getlength(t) for t, f in self.runs(text))

    def mask(self, text):
        """anti-aliased coverage (uint8) and the offset of pixel (0,0) relative to the left baseline origin"""
        rs = self.runs(text)
        x = 0.0; L = T = 1e9; R = B = -1e9; pos = []
        for t, f in rs:
            l, tp, r, b = f.getbbox(t, anchor='ls')
            L, T, R, B = min(L, x + l), min(T, tp), max(R, x + r), max(B, b)
            pos.append((x, t, f)); x += f.getlength(t)
        pad = 4
        W_, H_ = int(np.ceil(R - L)) + 2 * pad, int(np.ceil(B - T)) + 2 * pad
        im = Image.new('L', (max(1, W_), max(1, H_)), 0)
        d = ImageDraw.Draw(im)
        ox, oy = int(np.floor(L)) - pad, int(np.floor(T)) - pad
        for x0, t, f in pos:
            d.text((x0 - ox, -oy), t, font=f, fill=255, anchor='ls')
        return np.array(im), ox, oy

    def shift(self, text, anc):
        if anc == 'ms':
            return -self.getlength(text) / 2
        if anc == 'rs':
            return -self.getlength(text)
        return 0.0


def ink_mask(a):
    bg = np.stack([cv2.medianBlur(np.ascontiguousarray(a[:, :, c]), 41) for c in range(3)], 2)
    d = np.abs(a.astype(int) - bg.astype(int)).max(2)
    return d > 45


def alpha(reg, bg, color):
    bgv = np.array(bg, float); cv = np.array(color, float) - bgv
    n2 = (cv ** 2).sum()
    if n2 < 200:
        return np.zeros(reg.shape[:2])
    return ((reg.astype(float) - bgv) @ cv) / n2


def restore_lines(a, X0, Y0, X1, Y1, bgc, h, k=5, tol=14):
    """Thin straight lines (frame edges, chip borders) that run through an erased box are redrawn from their profile
    just outside it, together with the few pixels beside them: glyphs that overlapped a border leave neither a gap in
    the line nor bits of the old letters stuck to it."""
    H, W = a.shape[:2]
    maxw = max(16, int(0.6 * h))

    def thin_runs(flag):
        out = np.zeros_like(flag)
        n = len(flag); i = 0
        while i < n:
            if flag[i]:
                j = i
                while j < n and flag[j]:
                    j += 1
                if j - i <= maxw:
                    out[i:j] = True
                i = j
            else:
                i += 1
        return out

    def fix(seg_a, seg_b, region):
        # seg_a/seg_b: (k, n, 3) reference strips on both sides; region: (m, n, 3) view to repaint along axis 1
        ma, mb = np.median(seg_a, 0), np.median(seg_b, 0)
        sa, sb = seg_a.std(0).mean(1), seg_b.std(0).mean(1)
        cons = (np.abs(ma - mb).max(1) < tol) & (sa < 10) & (sb < 10)
        # only thin structures: the run of non-background columns (rows) must be narrow on both sides,
        # so a wide coloured area next to the box (a panel, the gap colour between chips) is never smeared into it
        nonbg = (np.abs(ma - bgc).max(1) > 12) & (np.abs(mb - bgc).max(1) > 12)
        closed = np.convolve(nonbg.astype(int), np.ones(7, int), 'same') > 0          # bridge gaps of <= 3 px
        closed = (np.convolve((~closed).astype(int), np.ones(7, int), 'same') == 0) | nonbg  # (closing = dilate + erode)
        line = thin_runs(closed) & nonbg & cons
        if not line.any():
            return
        near = np.convolve(line.astype(int), np.ones(9, int), 'same') > 0
        sel = near & cons
        prof = ((ma + mb) / 2).round().clip(0, 255).astype(np.uint8)
        region[:, sel] = prof[sel]

    if Y0 - k - 1 >= 0 and Y1 + k + 1 <= H and X1 > X0:
        fix(a[Y0 - k - 1:Y0 - 1, X0:X1].astype(float), a[Y1 + 1:Y1 + k + 1, X0:X1].astype(float), a[Y0:Y1, X0:X1])
    # (horizontal lines never cross a label in these figures; restoring them only smeared neighbouring colours)


def erase(a, e, protect):
    """remove the text of element e from image a (in place).
    Everything inside the padded line box is repainted with the local background, except marks that belong to other
    artwork (components that reach well outside the text box). Busy backgrounds are inpainted instead."""
    H, W = a.shape[:2]
    busy = False
    for b in e['lines']:
        x0, y0, x1, y1 = b
        h = y1 - y0
        pad = max(5, int(round(0.3 * h)))
        X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
        reg = a[Y0:Y1, X0:X1].copy()
        bgref = np.array(e['bg'], float)
        diff = np.abs(reg.astype(float) - bgref).max(2)
        m = (diff > 18).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        cm = max(3, int(round(0.15 * h)))
        core = np.zeros(m.shape, bool)
        core[max(0, y0 - Y0 - cm):y1 - Y0 + cm, max(0, x0 - X0 - cm):x1 - X0 + cm] = True
        text = np.zeros(m.shape, bool); other = np.zeros(m.shape, bool)
        # long straight lines (frames, axes) around this text, measured in a larger window
        Lk = max(40, int(2.5 * h))
        YA, YB, XA, XB = max(0, Y0 - Lk), min(H, Y1 + Lk), max(0, X0 - Lk), min(W, X1 + Lk)
        bigm = (np.abs(a[YA:YB, XA:XB].astype(float) - bgref).max(2) > 18).astype(np.uint8)
        lines_big = cv2.morphologyEx(bigm, cv2.MORPH_OPEN, np.ones((1, Lk), np.uint8)) | cv2.morphologyEx(bigm, cv2.MORPH_OPEN, np.ones((Lk, 1), np.uint8))
        lines_reg = cv2.dilate(lines_big, np.ones((3, 3), np.uint8)).astype(bool)[Y0 - YA:Y1 - YA, X0 - XA:X1 - XA]
        for i in range(1, n):
            comp = lab == i
            tot = int(st[i, 4])
            ins = int((comp & core).sum())
            touches = st[i, 0] == 0 or st[i, 1] == 0 or st[i, 0] + st[i, 2] >= m.shape[1] or st[i, 1] + st[i, 3] >= m.shape[0]
            if ins >= 0.75 * tot and not (touches and ins < tot):
                text |= comp
            elif ins > 0:
                # artwork touching a glyph (frame line through a letter): keep only the long straight lines
                resid = comp & ~lines_reg & core
                text |= resid
                other |= comp & ~resid
            else:
                other |= comp
        other_d = cv2.dilate(other.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        er = ~other_d & ~protect[Y0:Y1, X0:X1]
        er &= cv2.dilate(core.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) | cv2.dilate(text.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        # the soft halo of the old glyphs reaches ~0.3 h; the background colour is measured outside it
        R_ = max(6, int(round(0.3 * h)))
        near_wide = cv2.dilate(text.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * R_ + 1, 2 * R_ + 1))).astype(bool)
        bgpix = reg[(diff <= 18) & ~other_d]
        if len(bgpix) < 30:
            bgpix = reg[~text & ~other_d]
        if len(bgpix):
            # the dominant colour (mode), not the median: the halo of the old glyphs and a sliver of a neighbouring
            # area must not tint the fill
            q = (bgpix // 3).astype(np.int64)
            key = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
            vals, cnts = np.unique(key, return_counts=True)
            k = vals[np.argmax(cnts)]
            mode = np.array([k // 10000, (k // 100) % 100, k % 100], float) * 3 + 1
            near_mode = np.abs(bgpix.astype(float) - mode).max(1) <= 6
            bgc = np.median(bgpix[near_mode], 0) if near_mode.sum() >= 10 else np.median(bgpix, 0)
            # spread of the background itself (outside the halo) decides flat fill vs inpainting
            bgo = reg[(diff <= 18) & ~other_d & ~near_wide]
            sd = float(np.std((bgo if len(bgo) >= 30 else bgpix).astype(float), 0).mean())
        else:
            bgc = bgref; sd = 99
        flat = len(bgpix) >= 30 and sd < 5 and not e.get('busy')
        if flat:
            # repaint the glyphs (with their anti-aliased rim) and anything already close to the background colour,
            # but never a neighbouring flat area of a slightly different colour (the white page above a grey panel)
            near_bg = np.abs(reg.astype(float) - bgc).max(2) <= 8
            near_text = cv2.dilate(text.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
            # the halo is repainted where the pixel lies between the background and the text colour
            # (a lighter page next to a grey panel is not a halo)
            v_ = np.array(e['color'], float) - bgc
            vv = float((v_ * v_).sum())
            if vv > 400:
                t_ = ((reg.astype(float) - bgc) * v_).sum(2) / vv
                halo = near_wide & (t_ > 0)
            else:
                halo = near_wide
            er_full = ~other_d & ~protect[Y0:Y1, X0:X1] & (near_text | near_bg | halo)
            reg[er_full] = bgc.astype(np.uint8)
            a[Y0:Y1, X0:X1] = reg
            restore_lines(a, X0, Y0, X1, Y1, bgc, h)
        else:
            busy = True
            pad2 = 14
            XA, YA, XB, YB = max(0, X0 - pad2), max(0, Y0 - pad2), min(W, X1 + pad2), min(H, Y1 + pad2)
            big = np.ascontiguousarray(a[YA:YB, XA:XB])
            mk = np.zeros(big.shape[:2], np.uint8)
            tm = cv2.dilate(text.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            mk[Y0 - YA:Y1 - YA, X0 - XA:X1 - XA][tm] = 255
            res = cv2.inpaint(big, mk, 7, cv2.INPAINT_TELEA)
            a[YA:YB, XA:XB] = res
    return busy


def ink_mask_local(reg):
    g = reg.astype(int)
    med = np.median(g.reshape(-1, 3), 0)
    return np.abs(g - med).max(2) > 60


SEPS = {'·', '–', '—', '→', '=', '/', '|', '+'}


def wrap_options(text, f, maxw, nlines):
    # a separator (·, dash, arrow) stays at the end of its line instead of starting the next one
    words = []
    for w_ in text.split(' '):
        if words and w_ in SEPS:
            words[-1] += ' ' + w_
        else:
            words.append(w_)
    if nlines == 1 or len(words) < nlines:
        return [[text]] if nlines == 1 else []
    best = None
    import itertools
    for cuts in itertools.combinations(range(1, len(words)), nlines - 1):
        parts = []
        prev = 0
        for c in list(cuts) + [len(words)]:
            parts.append(' '.join(words[prev:c])); prev = c
        w = max(f.getlength(p) for p in parts)
        if best is None or w < best[0]:
            best = (w, parts)
    return [best[1]] if best else []


_ib = {}


def ink_bbox(text, f, anc):
    """true ink box of the rendered text relative to the anchor point"""
    k = (text, f.path, round(f.size, 2), anc)
    if k in _ib:
        return _ib[k]
    m, ox, oy = f.mask(text)
    sx = f.shift(text, anc)
    ys, xs = np.nonzero(m > 40)
    if len(xs) == 0:
        res = (sx, -f.size * 0.7, sx + f.getlength(text), 0)
    else:
        res = (xs.min() + ox + sx, ys.min() + oy, xs.max() + 1 + ox + sx, ys.max() + 1 + oy)
    _ib[k] = res
    return res


def layout(e, text, scale, nl, forced):
    w = e.get('weight', 'Regular')
    size = e['size'] * scale
    f = font(w, size)
    if forced:
        lines = text.split('\n')
    else:
        opts = wrap_options(text, f, None, nl)
        if not opts:
            return None
        lines = opts[0]
    k0 = len(e['lines'])
    bl0 = [b for b in (e.get('baselines') or []) if b is not None]
    pitch = e.get('pitch') or round(1.32 * e['size'], 1)
    pitch_new = pitch * (scale if not e.get('pitch') else 1.0)
    if len(lines) != k0 and e.get('pitch'):
        pitch_new = e['pitch'] * min(1.0, 0.5 + 0.5 * scale)
    # vertical anchoring
    if bl0:
        first = bl0[0]
    else:
        first = e['box'][3]
    n = len(lines)
    r_ = e.get('room', {})
    vc_box = bool(r_.get('ub') and r_.get('db') and abs(r_.get('up', 0) - r_.get('down', 0)) <= 0.35 * (r_.get('up', 0) + r_.get('down', 0)) + 4)
    if n == k0:
        bls = [bl0[i] if i < len(bl0) else first + i * pitch_new for i in range(n)]
        if scale < 1 and vc_box:
            # shrunk text inside a frame keeps its optical centre, not its baseline
            bls = [b_ - (1 - scale) * 0.36 * e['size'] for b_ in bls]
    else:
        vcenter = e.get('vcenter')
        if vcenter is None:
            r = e.get('room', {})
            vcenter = bool(r.get('ub') and r.get('db') and abs(r.get('up', 0) - r.get('down', 0)) <= 0.35 * (r.get('up', 0) + r.get('down', 0)) + 4 and k0 >= 1 and e.get('align') == 'center')
        if vcenter:
            mid_old = (bl0[0] + bl0[-1]) / 2 if bl0 else first
            start = mid_old - (n - 1) * pitch_new / 2
            bls = [start + i * pitch_new for i in range(n)]
        else:
            bls = [first + i * pitch_new for i in range(n)]
    al = e.get('align', 'left')
    xs = e.get('xs') or []
    ib = e.get('inkboxes') or []
    out = []
    for i, (ln, y) in enumerate(zip(lines, bls)):
        j = min(i, len(e['lines']) - 1)
        lb = e['lines'][j]
        if al == 'left':
            x = (xs[j] if j < len(xs) and xs[j] is not None else lb[0]); anc = 'ls'
            x = min(x, (xs[0] if xs and xs[0] is not None else x))
        elif al == 'right':
            x = (ib[j][2] if j < len(ib) and ib[j] else lb[2]); anc = 'rs'
        else:
            if j < len(ib) and ib[j]:
                x = (ib[j][0] + ib[j][2]) / 2
            else:
                x = (lb[0] + lb[2]) / 2
            if len(lines) != len(e['lines']):
                x = (e['box'][0] + e['box'][2]) / 2
            if e.get('center_x') is not None:
                x = e['center_x']
            anc = 'ms'
        bb = ink_bbox(ln, f, anc)
        out.append(dict(text=ln, x=float(x), y=float(y), anchor=anc, bbox=[x + bb[0], y + bb[1], x + bb[2], y + bb[3]],
                        core=[x + bb[0], y - 0.68 * size, x + bb[2], y], extra=(i >= len(e['lines'])), font=f))
    return dict(lines=out, size=size, weight=w, scale=scale, ox0=e['box'][0], ox1=e['box'][2])


def clearance(blocked, box):
    """free distance from box to the nearest blocked pixel to the left/right/up/down (within the box band)"""
    H, W = blocked.shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    band = blocked[max(0, y0):min(H, y1)].any(0)
    L = 0
    x = x0 - 1
    while x >= 0 and not band[x] and L < 4000:
        L += 1; x -= 1
    R = 0
    x = x1
    while x < W and not band[x] and R < 4000:
        R += 1; x += 1
    col = blocked[:, max(0, x0):min(W, x1)].any(1)
    U = 0
    y = y0 - 1
    while y >= 0 and not col[y]:
        U += 1; y -= 1
    Dn = 0
    y = y1
    while y < H and not col[y]:
        Dn += 1; y += 1
    return L, R, U, Dn


def margins(e, cl, M):
    """per-direction margins. Inside a frame, a left-aligned text keeps on the right at least 3/4 of the padding it
    has on the left (and vice versa), so long translations do not run into the frame edge."""
    cL = min(c[0] for c in cl); cR = min(c[1] for c in cl)
    mL, mR = M, M
    al = e.get('align')
    if al == 'left' and cL < 3 * e['size']:
        mR = max(M, 0.75 * cL)
    if al == 'right' and cR < 3 * e['size']:
        mL = max(M, 0.75 * cR)
    tol = 0.15 * e['size']  # glyph side bearings differ between the English and the new text

    def m_(want, c):
        # keep at least ~70 % of the clearance the English text had (up to 1.5 M), never more than the clearance itself
        return max(1, min(c - 2, max(min(want, c - 2 - tol), min(0.5 * c, 1.5 * M))))
    return (m_(mL, cL), m_(mR, cR), max(1, min(0.5 * M, cl[0][2] - 2)), max(1, min(0.5 * M, cl[-1][3] - 2)))


def collides(lay, blocked, W, H, mg):
    """A: horizontal margins on the x-height/cap band (neighbours left/right);
    B: the full glyph box (ascenders, descenders, umlauts, commas) only needs a small clearance above/below,
       except on added lines, which keep the normal vertical margins."""
    mL, mR, mU, mD = mg
    border = 0.022 * W
    for l in lay['lines']:
        x0, y0, x1, y1 = l['bbox']
        if x0 - mL < 0 or x1 + mR > W or y0 < 1 or y1 > H - 1:
            return True
        if (x0 < border and x0 < lay.get('ox0', 0) - 1) or (x1 > W - border and x1 > lay.get('ox1', W) + 1):
            return True
        c0, c1, c2, c3 = l['core']
        X0, Y0, X1, Y1 = int(np.floor(x0 - mL)), int(np.floor(c1)), int(np.ceil(x1 + mR)), int(np.ceil(c3))
        if blocked[max(0, Y0):Y1, max(0, X0):X1].any():
            return True
        if l.get('extra'):
            X0, Y0, X1, Y1 = int(np.floor(x0 - 2)), int(np.floor(y0 - mU)), int(np.ceil(x1 + 2)), int(np.ceil(y1 + mD))
            if Y0 < 0 or Y1 > H or blocked[Y0:Y1, max(0, X0):X1].any():
                return True
            continue
        # glyph mask (dilated by 3 px) against the artwork: descenders/umlauts may pass close to it
        gm, ox, oy = glyph_mask(l['text'], l['font'], l['anchor'])
        gx0, gy0 = int(round(l['x'])) + ox - 3, int(round(l['y'])) + oy - 3
        gh, gw = gm.shape
        if gx0 < 0 or gy0 < 0 or gx0 + gw > W or gy0 + gh > H:
            return True
        if (blocked[gy0:gy0 + gh, gx0:gx0 + gw] & gm).any():
            return True
    return False


_gm = {}


def glyph_mask(text, f, anc):
    k = (text, f.path, round(f.size, 2), anc)
    if k not in _gm:
        m, ox, oy = f.mask(text)
        mm = np.pad(m > 60, 3)
        mm = cv2.dilate(mm.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        # offset of the padded mask's (0,0) relative to the anchor point, plus 3 (collides() subtracts 3)
        _gm[k] = (mm, int(round(ox + f.shift(text, anc))), oy)
    return _gm[k]


def paste(b, m, X, Y, color):
    """alpha-blend colour through coverage mask m (uint8) at (X, Y) into image array b"""
    H, W = b.shape[:2]
    h, w = m.shape
    x0, y0 = max(0, X), max(0, Y)
    x1, y1 = min(W, X + w), min(H, Y + h)
    if x1 <= x0 or y1 <= y0:
        return
    al = (m[y0 - Y:y1 - Y, x0 - X:x1 - X].astype(float) / 255.0)[..., None]
    reg = b[y0:y1, x0:x1].astype(float)
    b[y0:y1, x0:x1] = np.clip(reg * (1 - al) + np.array(color, float) * al, 0, 255).astype(np.uint8)


def run(lang, stem):
    inv = json.load(open(D + f'inv3/{stem}.json'))
    trp = D + f'tr_{lang}/{stem}.json'
    tr = json.load(open(trp)) if os.path.exists(trp) else {}
    pil = Image.open(IMG + f'EN-{stem}.png').convert('RGB')
    a = np.array(pil)
    H, W = a.shape[:2]
    els = {str(e['id']): e for e in inv['elements']}
    # harmonise weights: elements of one row with the same size and colour take the majority weight
    allels = list(els.values())
    for e in allels:
        if not e.get('size') or not e.get('baselines') or e.get('weight_fixed'):
            continue
        grp = [o for o in allels if o.get('size') and o.get('baselines') and o['baselines'][0] is not None and e['baselines'][0] is not None
               and abs(o['baselines'][0] - e['baselines'][0]) <= 0.12 * e['size'] and abs(o['size'] / e['size'] - 1) <= 0.12
               and sum(abs(p_ - q_) for p_, q_ in zip(o['color'], e['color'])) < 60]
        if len(grp) >= 3:
            cnt = {}
            for o in grp:
                cnt[o.get('weight', 'Regular')] = cnt.get(o.get('weight', 'Regular'), 0) + 1
            best = max(cnt.items(), key=lambda kv: (kv[1], -['Regular', 'Medium', 'Bold'].index(kv[0]) if kv[0] in ('Regular', 'Medium', 'Bold') else 0))
            if best[1] > len(grp) / 2:
                e['weight_h'] = best[0]
    for e in allels:
        if e.get('weight_h'):
            e['weight'] = e.pop('weight_h')
    # harmonise sizes in a row (labels under a row of pictures etc.): same baseline, colour and weight, sizes within 15 %
    done_ = set()
    for e in allels:
        if e['id'] in done_ or not e.get('size') or not e.get('baselines') or e['baselines'][0] is None:
            continue
        grp = [o for o in allels if o.get('size') and o.get('baselines') and o['baselines'][0] is not None
               and abs(o['baselines'][0] - e['baselines'][0]) <= 0.12 * e['size'] and o.get('weight') == e.get('weight')
               and sum(abs(p_ - q_) for p_, q_ in zip(o['color'], e['color'])) < 60]
        if len(grp) < 3:
            continue
        med = float(np.median([o['size'] for o in grp]))
        if all(abs(o['size'] / med - 1) <= 0.15 for o in grp):
            for o in grp:
                o['size'] = med; done_.add(o['id'])
    ovp = D + 'overrides.json'
    if os.path.exists(ovp):
        for k, v in json.load(open(ovp)).get(stem, {}).items():
            if k in els:
                els[k].update(v)
    todo = []
    for k in tr:
        if k not in els or tr[k] is None or tr[k] == els[k]['en']:
            continue
        e = els[k]
        dup = False
        for o in todo:
            b1, b2 = e['box'], o['box']
            ix = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0])); iy = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
            u = (b1[2] - b1[0]) * (b1[3] - b1[1]) + (b2[2] - b2[0]) * (b2[3] - b2[1]) - ix * iy
            if u and ix * iy / u > 0.5:
                dup = True
        if not dup:
            todo.append(e)
    report = dict(stem=stem, lang=lang, placed=[], failed=[], unknown=[k for k in tr if k not in els])
    groups = {}
    for e in todo:
        groups.setdefault(e.get('rot', 0), []).append(e)
    for rot, es in groups.items():
        img = Image.fromarray(a)
        if rot:
            img = img.rotate(rot, expand=True)
        b = np.array(img)
        h_, w_ = b.shape[:2]
        protect = np.zeros((h_, w_), bool)
        # 1) erase all
        busy = {}
        for e in es:
            busy[e['id']] = erase(b, e, protect)
        # 2) blocked map: remaining artwork + reserved original boxes
        ink = ink_mask(b)
        g = cv2.GaussianBlur(cv2.cvtColor(b, cv2.COLOR_RGB2GRAY), (3, 3), 0).astype(float)
        gx = np.zeros_like(g); gy = np.zeros_like(g)
        gx[:, 2:-2] = np.abs(g[:, 4:] - g[:, :-4]); gy[2:-2, :] = np.abs(g[4:, :] - g[:-4, :])
        edges = (np.maximum(gx, gy) > 8)
        edges = cv2.morphologyEx(edges.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, 1), np.uint8)).astype(bool)
        placed_boxes = []
        reserved = {}
        for e in es:
            reserved[e['id']] = e['box']
        for e in sorted(es, key=lambda e: -len(tr[str(e['id'])])):
            pass
        for e in es:
            text = tr[str(e['id'])].strip()
            forced = '\n' in text
            k0 = len(e['lines'])
            blocked = ink | edges
            for oid, rb in reserved.items():
                if oid == e['id']:
                    continue
                x0, y0, x1, y1 = rb
                blocked[max(0, y0 - 2):y1 + 3, max(0, x0 - 2):x1 + 3] = True
            for pb in placed_boxes:
                x0, y0, x1, y1 = pb
                blocked[max(0, int(y0) - 2):int(y1) + 3, max(0, int(x0) - 2):int(x1) + 3] = True
            if e.get('busy') or busy.get(e['id']):
                for lb in e['lines']:
                    x0, y0, x1, y1 = lb
                    blocked[max(0, y0 - 3):y1 + 4, max(0, x0 - 3):x1 + 4] = False
            # per-direction margins: never stricter than the clearance the English text had
            cl = [clearance(blocked, lb) for lb in e['lines']]
            M = max(6, 0.6 * e['size'])
            mg = margins(e, cl, M)
            maxlines = e.get('maxlines') or (k0 + 1 if e.get('align') == 'center' or k0 > 1 else k0 + (1 if e['room']['down'] > 1.6 * e['size'] else 0))
            minscale = e.get('minscale', 0.8)
            cands = []
            line_opts = [len(text.split('\n'))] if forced else ([k0] + [n for n in range(1, maxlines + 1) if n != k0])
            scales = [round(1.0 - 0.02 * i, 2) for i in range(int((1.0 - minscale) / 0.02) + 1)]
            chosen = None
            # preference: original line count at full size, then fewer shrink steps; extra lines only after mild shrink
            order = []
            for sc in scales:
                for nl in line_opts:
                    pen = (1.0 - sc) * 10 + (0 if nl == k0 else (0.6 if nl < k0 else 1.2))
                    order.append((pen, sc, nl))
            order.sort()
            for pen, sc, nl in order:
                lay = layout(e, text, sc, nl, forced)
                if lay is None:
                    continue
                if not collides(lay, blocked, w_, h_, mg):
                    chosen = lay; break
            if chosen is None:
                # last resort: report, draw the full-size single line so the problem is visible
                lay = layout(e, text, minscale, line_opts[0], forced)
                report['failed'].append(dict(id=e['id'], en=e['en'], text=text))
                chosen = lay
            f = font(chosen['weight'], chosen['size'])
            for l in chosen['lines']:
                m, ox, oy = f.mask(l['text'])
                X = int(round(l['x'] + f.shift(l['text'], l['anchor']))) + ox
                Y = int(round(l['y'])) + oy
                if busy.get(e['id']) or e.get('busy'):
                    sw = max(1, int(round(chosen['size'] * 0.07)))
                    halo = cv2.dilate(m, np.ones((2 * sw + 1, 2 * sw + 1), np.uint8))
                    paste(b, halo, X, Y, e['bg'])
                paste(b, m, X, Y, e['color'])
                placed_boxes.append(l['bbox'])
            del reserved[e['id']]
            report['placed'].append(dict(id=e['id'], en=e['en'], text=text, scale=chosen['scale'], lines=len(chosen['lines']),
                                         bboxes=[[round(v) for v in l['bbox']] for l in chosen['lines']], rot=rot))
        img = Image.fromarray(b)
        if rot:
            img = img.rotate(-rot, expand=True)
        a = np.array(img)
    os.makedirs(D + f'out_{lang}', exist_ok=True)
    Image.fromarray(a).save(D + f'out_{lang}/{lang.upper()}-{stem}.png')
    json.dump(report, open(D + f'out_{lang}/{stem}_report.json', 'w'), ensure_ascii=False, indent=1)
    return report


if __name__ == '__main__':
    lang = sys.argv[1]
    stems = sys.argv[2:] or sorted(os.path.basename(p)[:-5] for p in __import__('glob').glob(D + f'tr_{lang}/*.json'))
    for s in stems:
        r = run(lang, s)
        print(f"{s}: placed {len(r['placed'])} | shrunk {sum(p['scale'] < 1 for p in r['placed'])} | rewrapped {sum(1 for p in r['placed'] if p['lines'] != 1)} | FAILED {[(f['id'], f['text']) for f in r['failed']]} | unknown ids {r['unknown']}", flush=True)

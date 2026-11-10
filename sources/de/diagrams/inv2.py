"""Inventory of text elements in the English diagrams (for re-lettering in DE / RU).
python3 inv2.py [stem ...]   -> inv/<stem>.json + inv/<stem>_boxes.png
Steps: OCR words (psm 11) -> fallback crops for uncovered glyph clusters -> lines -> segments (leading
bullets/numbers split off) -> label-driven merge of wrapped lines -> style by template matching
(weight, size, baseline, colour) -> alignment -> free room -> completeness check against the label list."""
import csv, difflib, glob, io, json, os, re, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

S = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad'
IMG = S + '/book_en/img_en/'
OUT = S + '/ml/diag/inv/'
os.makedirs(OUT, exist_ok=True)
FONTS = {w: f'/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc' for w in ['Regular', 'Medium', 'Bold']}
_fc = {}


def font(w, size):
    k = (w, round(size, 2))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS[w], size, index=1)
    return _fc[k]


labels = {}
for f in sorted(glob.glob(S + '/en/labels/g*.json')):
    for fn, items in json.load(open(f)).items():
        labels[fn.rsplit('.', 1)[0]] = [x['en'].replace('~', '–') for x in items]
EXTRA = {'p287_288_1375x661': ['14 fL'], 'p072_070_1831x681': ["Worm's-eye"]}


def norm(s):
    s = s.replace('’', "'").replace('‘', "'")
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def tess(img, psm, scale=1.0):
    """run tesseract on a PIL image; return word dicts in original coordinates"""
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    with tempfile.NamedTemporaryFile(suffix='.png', dir=OUT) as tf:
        img.save(tf.name)
        out = subprocess.run(['tesseract', tf.name, '-', '--psm', psm, 'tsv'], capture_output=True, text=True).stdout
    rows = list(csv.DictReader(io.StringIO(out), delimiter='\t', quoting=csv.QUOTE_NONE))
    ws = []
    for r in rows:
        if r['level'] != '5' or not r['text'].strip():
            continue
        x0, y0 = int(r['left']) / scale, int(r['top']) / scale
        ws.append(dict(text=r['text'].strip(), conf=float(r['conf']), box=[x0, y0, x0 + int(r['width']) / scale, y0 + int(r['height']) / scale],
                       line=(int(r['block_num']), int(r['par_num']), int(r['line_num']))))
    return ws


def ink_mask(a):
    bg = np.stack([cv2.medianBlur(np.ascontiguousarray(a[:, :, c]), 41) for c in range(3)], 2)
    d = np.abs(a.astype(int) - bg.astype(int)).max(2)
    return d > 55, bg


def iou(b1, b2):
    ix = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0])); iy = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
    i = ix * iy
    u = (b1[2] - b1[0]) * (b1[3] - b1[1]) + (b2[2] - b2[0]) * (b2[3] - b2[1]) - i
    return i / u if u > 0 else 0


def render_mask(text, w, size):
    f = font(w, size)
    l, t, r, b = f.getbbox(text, anchor='ls')
    W, H = int(r - l + 20), int(b - t + 20)
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=f, fill=255, anchor='ls')
    m = np.array(im) > 110
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    # ink bbox and the baseline origin relative to the ink bbox
    x0, y0 = xs.min(), ys.min()
    crop = m[y0:ys.max() + 1, x0:xs.max() + 1]
    ox, oy = (10 - l) - x0, (10 - t) - y0  # origin (anchor 'ls') relative to ink top-left
    return crop, ox, oy


def alpha_mask(a, box, bg, color, pad=4):
    """text coverage in [0,1] by projecting pixels on the bg->text colour axis"""
    H, W = a.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    reg = a[Y0:Y1, X0:X1].astype(float)
    bgv = np.array(bg, float); cv = np.array(color, float) - bgv
    n2 = (cv ** 2).sum()
    if n2 < 300:
        return None, (X0, Y0)
    al = ((reg - bgv) @ cv) / n2
    return np.clip(al, 0, 1.2), (X0, Y0)


def stroke_width(m):
    from skimage.morphology import skeletonize
    if m.sum() < 10:
        return 0
    sk = skeletonize(m)
    return m.sum() / max(1, sk.sum())


def fit_style(a, box, text, bg, color):
    """weight by stroke width, size by ink width, baseline/x by alignment of ink boxes"""
    al, (X0, Y0) = alpha_mask(a, box, bg, color)
    if al is None:
        return None
    m = al > 0.5
    ys, xs = np.nonzero(m)
    if len(xs) < 5:
        return None
    ib = [X0 + xs.min(), Y0 + ys.min(), X0 + xs.max() + 1, Y0 + ys.max() + 1]
    orig = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    tw, th = orig.shape[1], orig.shape[0]
    swo = stroke_width(orig)
    cands = []
    for w in FONTS:
        r = render_mask(text, w, 100)
        if r is None:
            return None
        sw_ = 100 * tw / r[0].shape[1]
        sh_ = 100 * th / r[0].shape[0]
        # size by cap/x-height when the original face is narrower or wider than Noto Sans
        size = (sw_ + sh_) / 2 if abs(sw_ / sh_ - 1) <= 0.06 else max(sw_, sh_)
        r = render_mask(text, w, size)
        if r is None:
            continue
        rm, ox, oy = r
        swr = stroke_width(rm)
        hh, ww = max(rm.shape[0], th), max(rm.shape[1], tw)
        A = np.zeros((hh + 8, ww), bool); B = np.zeros((hh + 8, ww), bool)
        A[4:4 + th, :tw] = orig; B[4:4 + rm.shape[0], :rm.shape[1]] = rm
        sc, bshift = 0, 0
        for dy in range(-3, 4):
            Bs = np.roll(B, dy, 0)
            v = (A & Bs).sum() / max(1, (A | Bs).sum())
            if v > sc:
                sc, bshift = v, dy
        hdiff = (rm.shape[0] - th) / max(th, 1)
        cands.append(dict(weight=w, size=round(size, 2), ox=int(ox), oy=int(oy + bshift), score=round(sc, 3), hdiff=round(hdiff, 3),
                          sw=round(swr, 2), swo=round(swo, 2), err=abs(swr - swo) / max(swo, 0.5)))
    if not cands:
        return None
    best = min(cands, key=lambda c: c['err'])
    best['inkbox'] = [int(v) for v in ib]
    best['x'] = int(ib[0] + best['ox'])  # anchor 'ls' x
    best['baseline'] = int(ib[1] + best['oy'])
    best['alts'] = {c['weight']: round(c['err'], 2) for c in cands}
    return best


def colour(a, ink, box, bg):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    reg = a[y0:y1, x0:x1].astype(int)
    d = np.abs(reg - np.array(bg)).sum(2)
    if d.max() < 30:
        return [0, 0, 0]
    core = d > 0.75 * d.max()
    return [int(v) for v in np.median(reg[core], 0)]


def ring_bg(a, box, pad=5):
    H, W = a.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W - 1, x1 + pad), min(H - 1, y1 + pad)
    reg = a[Y0:Y1 + 1, X0:X1 + 1].astype(int)
    ring = np.concatenate([reg[0], reg[-1], reg[:, 0], reg[:, -1]])
    return [int(v) for v in np.median(ring, 0)], round(float(np.std(ring, 0).mean()), 1)


def free_room(ink, box, exclude):
    """free space (px) left/right/up/down of box, ignoring ink inside the boxes in `exclude`"""
    H, W = ink.shape
    m = ink.copy()
    for b in exclude:
        x0, y0, x1, y1 = [int(round(v)) for v in b]
        m[max(0, y0 - 2):y1 + 3, max(0, x0 - 2):x1 + 3] = False
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    band = m[max(0, y0 - 3):min(H, y1 + 4)]
    col = band.any(0)
    L = 0
    x = x0 - 1
    while x >= 0 and not col[x]:
        L += 1; x -= 1
    Lb = x >= 0
    R = 0
    x = x1
    while x < W and not col[x]:
        R += 1; x += 1
    Rb = x < W
    vb = m[:, max(0, x0 - 3):min(W, x1 + 4)].any(1)
    U = 0
    y = y0 - 1
    while y >= 0 and not vb[y]:
        U += 1; y -= 1
    Ub = y >= 0
    D = 0
    y = y1
    while y < H and not vb[y]:
        D += 1; y += 1
    Db = y < H
    return dict(left=L, right=R, up=U, down=D, lb=bool(Lb), rb=bool(Rb), ub=bool(Ub), db=bool(Db))


BULLET = re.compile(r'^([0-9]{1,2}|[①-⑳]|[x×•·✕✓○●■□▶►]|0[1-9])$')


def analyze(stem):
    path = IMG + f'EN-{stem}.png'
    pil = Image.open(path).convert('RGB')
    a = np.array(pil)
    H, W = a.shape[:2]
    ink, bgimg = ink_mask(a)
    words = tess(pil, '11')
    words = [w for w in words if w['conf'] >= 30 or re.search(r'[A-Za-z]{2,}', w['text'])]
    # ---- fallback: glyph clusters not covered by OCR words
    n, lab, st, cen = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
    cov = np.zeros_like(ink)
    for w in words:
        x0, y0, x1, y1 = [int(round(v)) for v in w['box']]
        cov[max(0, y0 - 3):y1 + 4, max(0, x0 - 3):x1 + 4] = True
    comps = []
    for i in range(1, n):
        x, y, w_, h_, ar = st[i]
        if not (7 <= h_ <= 120 and w_ <= 3.5 * h_ and ar >= 6):
            continue
        if cov[y:y + h_, x:x + w_].mean() > 0.5:
            continue
        comps.append([x, y, x + w_, y + h_])
    comps.sort()
    clusters = []
    for c in comps:
        placed = False
        for cl in clusters:
            b = cl['box']
            h = max(b[3] - b[1], c[3] - c[1])
            vo = min(b[3], c[3]) - max(b[1], c[1])
            if vo > 0.35 * min(b[3] - b[1], c[3] - c[1]) and 0 <= c[0] - b[2] < 0.9 * h:
                cl['box'] = [min(b[0], c[0]), min(b[1], c[1]), max(b[2], c[2]), max(b[3], c[3])]; cl['n'] += 1; placed = True; break
        if not placed:
            clusters.append(dict(box=list(c), n=1))
    extra_words = []
    rejected = []
    for cl in clusters:
        b = cl['box']; h = b[3] - b[1]
        if cl['n'] < 2 or b[2] - b[0] < 0.8 * h:
            continue
        p = int(0.35 * h) + 2
        crop = pil.crop((max(0, b[0] - p), max(0, b[1] - p), min(W, b[2] + p), min(H, b[3] + p)))
        ws = tess(crop, '7', 2.0)
        txt = ' '.join(w['text'] for w in ws)
        conf = np.mean([w['conf'] for w in ws]) if ws else 0
        if ws and conf >= 55 and re.search(r'[A-Za-z0-9]{2,}', txt):
            ox, oy = max(0, b[0] - p), max(0, b[1] - p)
            for w in ws:
                w['box'] = [w['box'][0] + ox, w['box'][1] + oy, w['box'][2] + ox, w['box'][3] + oy]
                w['line'] = ('x', b[0], b[1]); w['fallback'] = True
            extra_words += ws
        else:
            rejected.append(dict(box=b, text=txt, conf=round(float(conf), 1)))
    words += extra_words
    # ---- lines
    d = {}
    for w in words:
        d.setdefault(w['line'], []).append(w)
    lines = []
    for k, ws in d.items():
        ws.sort(key=lambda w: w['box'][0])
        # split a line at very large gaps (separate labels on one OCR line)
        cur = [ws[0]]
        groups = [cur]
        for w in ws[1:]:
            h = max(cur[-1]['box'][3] - cur[-1]['box'][1], w['box'][3] - w['box'][1])
            if w['box'][0] - cur[-1]['box'][2] > 1.6 * h:
                cur = [w]; groups.append(cur)
            else:
                cur.append(w)
        for g in groups:
            # leading bullet / number as its own untouched token
            if len(g) > 1 and BULLET.match(g[0]['text']):
                h = g[1]['box'][3] - g[1]['box'][1]
                if g[1]['box'][0] - g[0]['box'][2] > 0.45 * h:
                    lines.append(dict(words=[g[0]], keep=True))
                    lines.append(dict(words=g[1:], keep=False, after_bullet=g[0]['text']))
                    continue
            lines.append(dict(words=g, keep=False))
    for l in lines:
        ws = l['words']
        l['box'] = [min(w['box'][0] for w in ws), min(w['box'][1] for w in ws), max(w['box'][2] for w in ws), max(w['box'][3] for w in ws)]
        l['text'] = ' '.join(w['text'] for w in ws)
        l['conf'] = round(float(np.mean([w['conf'] for w in ws])), 1)
        l['fallback'] = any(w.get('fallback') for w in ws)
        bg, bgstd = ring_bg(a, l['box'])
        l['bg'], l['bgstd'] = bg, bgstd
        l['color'] = colour(a, ink, l['box'], bg)
        l['h'] = l['box'][3] - l['box'][1]
    lines.sort(key=lambda l: (l['box'][1], l['box'][0]))
    # ---- label matching and merge of wrapped lines
    known = labels.get(stem, []) + EXTRA.get(stem, [])
    kn = [norm(k) for k in known]

    def best_label(t):
        nt = norm(t)
        if not nt:
            return None, 0
        bi, br = None, 0
        for i, k in enumerate(kn):
            r = difflib.SequenceMatcher(None, nt, k).ratio()
            if r > br:
                bi, br = i, r
        return bi, br

    def part_of_label(t):
        nt = norm(t)
        if len(nt) < 3:
            return []
        return [i for i, k in enumerate(kn) if nt in k and len(nt) < len(k)]

    def line_truth(l):
        bi, br = best_label(l['text'])
        if bi is None or br < 0.8:
            return None, br
        t = known[bi]
        if l.get('after_bullet'):
            t = re.sub(r'^\S+\s+', '', t) if norm(t.split(' ')[0]) == norm(l['after_bullet']) else t
        return t, br

    def same_style(cur, m):
        gap = m['box'][1] - cur['box'][3]
        ovx = min(cur['box'][2], m['box'][2]) - max(cur['box'][0], m['box'][0])
        if not (-2 <= gap < 1.1 * max(cur['h'], m['h']) and ovx > 0 and abs(cur['h'] - m['h']) < 0.45 * max(cur['h'], m['h'])):
            return False
        return sum(abs(p - q) for p, q in zip(cur['color'], m['color'])) <= 100

    used = set()
    elems = []
    order = list(range(len(lines)))
    for i in order:
        if i in used:
            continue
        l = lines[i]
        used.add(i)
        group = [l]
        if not l['keep']:
            while True:
                cur = group[-1]
                joined = ' '.join(g['text'] for g in group)
                parts = part_of_label(joined)
                bi, br = best_label(joined)
                nxt = None
                for j in order:
                    if j in used or lines[j]['keep'] or j == i:
                        continue
                    m = lines[j]
                    if m['box'][1] <= cur['box'][1] or not same_style(cur, m):
                        continue
                    t2 = joined + ' ' + m['text']
                    b2, r2 = best_label(t2)
                    cont = bool(re.match(r'^[a-z(]', m['text'])) and not re.search(r'[.!?:]$', cur['text'])
                    if (parts or br < 0.9) and r2 > br + 0.05 and (r2 >= 0.85 or part_of_label(t2)):
                        nxt = j
                    elif cont:
                        nxt = j
                    break
                if nxt is None:
                    break
                used.add(nxt); group.append(lines[nxt])
        text = ' '.join(g['text'] for g in group)
        bi, br = best_label(text)
        if bi is not None and br >= 0.85:
            truth = known[bi]
            if group[0].get('after_bullet') and norm(truth.split(' ')[0]) == norm(group[0]['after_bullet']):
                truth = re.sub(r'^\S+\s+', '', truth)
        else:
            pts = [line_truth(g) for g in group]
            truth = ' '.join(t for t, _ in pts) if all(t for t, _ in pts) else None
            if truth:
                br = min(r for _, r in pts)
        elems.append(dict(lines=group, ocr=text, en=truth if truth else text, matched=truth is not None, ratio=round(br, 2), keep=group[0]['keep']))
    # ---- style per element
    out = []
    for e in elems:
        g = e['lines']
        boxes = [x['box'] for x in g]
        ub = [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]
        # per-line texts for template matching: split the truth text across the lines proportionally to OCR words
        if len(g) == 1:
            ltexts = [e['en']]
        else:
            tw = e['en'].split(' ')
            counts = [len(x['words']) for x in g]
            if sum(counts) == len(tw):
                ltexts, k = [], 0
                for c in counts:
                    ltexts.append(' '.join(tw[k:k + c])); k += c
            else:
                ltexts = [x['text'] for x in g]
        styles = []
        for x, t in zip(g, ltexts):
            stl = fit_style(a, x['box'], t, x['bg'], x['color']) if not e['keep'] else None
            styles.append(stl)
        ok = [s for s in styles if s]
        el = dict(id=len(out), en=e['en'], ocr=e['ocr'], matched=e['matched'], ratio=e['ratio'], keep=e['keep'], fallback=any(x['fallback'] for x in g),
                  box=[int(v) for v in ub], lines=[[int(v) for v in b] for b in boxes], ltexts=ltexts,
                  color=g[0]['color'], bg=g[0]['bg'], bgstd=max(x['bgstd'] for x in g), conf=round(float(np.mean([x['conf'] for x in g])), 1))
        if ok:
            # weight by majority/score, size = median
            wts = {}
            for s in ok:
                wts[s['weight']] = wts.get(s['weight'], 0) + s['score']
            el['weight'] = max(wts, key=wts.get)
            el['size'] = round(float(np.median([s['size'] for s in ok])), 2)
            el['score'] = round(float(np.mean([s['score'] for s in ok])), 3)
            el['baselines'] = [s['baseline'] if s else None for s in styles]
            el['xs'] = [s['x'] if s else None for s in styles]
            el['inkboxes'] = [s['inkbox'] if s else None for s in styles]
            bl = [s['baseline'] for s in ok]
            el['pitch'] = round(float(np.median(np.diff(bl))), 1) if len(bl) > 1 else None
        out.append(el)
    # ---- alignment
    for e in out:
        if e['keep']:
            e['align'] = 'left'; continue
        if len(e['lines']) > 1:
            L = [b[0] for b in e['lines']]; R = [b[2] for b in e['lines']]; C = [(b[0] + b[2]) / 2 for b in e['lines']]
            sp = {'left': max(L) - min(L), 'right': max(R) - min(R), 'center': max(C) - min(C)}
            e['align'] = min(sp, key=sp.get)
            e['align_src'] = 'lines'
            continue
        x0, y0, x1, y1 = e['box']; cx = (x0 + x1) / 2; h = y1 - y0
        votes = {'left': 0, 'right': 0, 'center': 0}
        for o in out:
            if o is e or o['keep']:
                continue
            if abs(o['box'][1] - y0) > 8 * h or abs((o['box'][3] - o['box'][1]) - h) > 0.5 * h:
                continue
            ox0, _, ox1, _ = o['box']
            dd = {'left': abs(ox0 - x0), 'right': abs(ox1 - x1), 'center': abs((ox0 + ox1) / 2 - cx)}
            srt = sorted(dd.items(), key=lambda kv: kv[1])
            if srt[0][1] <= 4 and srt[1][1] >= 2 * srt[0][1] + 3:
                votes[srt[0][0]] += 1
        if max(votes.values()) > 0:
            e['align'] = max(votes, key=votes.get); e['align_src'] = 'neighbours'
        elif abs(cx - W / 2) < 0.02 * W and (x1 - x0) > 0.3 * W:
            e['align'] = 'center'; e['align_src'] = 'page'
        else:
            e['align'] = None
    allboxes = [e['box'] for e in out]
    for e in out:
        e['room'] = free_room(ink, e['box'], [e['box']])
        if e.get('align') is None:
            r = e['room']
            if r['lb'] and r['rb'] and abs(r['left'] - r['right']) <= 0.12 * (r['left'] + r['right']) + 6:
                e['align'] = 'center'; e['align_src'] = 'container'
            else:
                e['align'] = 'left'; e['align_src'] = 'default'
    # ---- completeness: every label word must be found
    found = {}
    for e in out:
        for t in norm_words(e['en'] if e['matched'] else e['ocr']):
            found[t] = found.get(t, 0) + 1
    need = {}
    for k in known:
        for t in norm_words(k):
            need[t] = need.get(t, 0) + 1
    missing = {t: c - found.get(t, 0) for t, c in need.items() if c > found.get(t, 0)}
    res = dict(stem=stem, size=[W, H], elements=out, missing_words=missing, rejected=rejected,
               unmatched=[e['id'] for e in out if not e['matched'] and not e['keep']])
    json.dump(res, open(OUT + stem + '.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    # debug drawing
    dbg = pil.copy(); dr = ImageDraw.Draw(dbg)
    for e in out:
        col = (0, 160, 0) if e['matched'] else ((0, 0, 255) if e['keep'] else (255, 0, 0))
        for b in e['lines']:
            dr.rectangle(b, outline=col, width=2)
        dr.text((e['box'][0], e['box'][1] - 14), f"{e['id']}{e['align'][0]}{e.get('weight', '')[:2]}", fill=col, font=font('Regular', 13))
    dbg.save(OUT + stem + '_boxes.png')
    return res


def norm_words(s):
    return [w for w in (norm(x) for x in re.split(r'[\s·—–/→+=]+', s)) if w]


if __name__ == '__main__':
    stems = sys.argv[1:] or [os.path.basename(p)[3:-4] for p in sorted(glob.glob(IMG + 'EN-*.png'))]
    for s in stems:
        r = analyze(s)
        print(f"{s}: elements {len(r['elements'])} | unmatched {len(r['unmatched'])} | missing words {r['missing_words']} | fallback {sum(e['fallback'] for e in r['elements'])}", flush=True)

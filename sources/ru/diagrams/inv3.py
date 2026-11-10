"""Label-anchored inventory of the text in the English diagrams.
python3 inv3.py [stem ...] -> inv3/<stem>.json, inv3/<stem>_boxes.png
- OCR words: psm 11 on the image, on the inverted image (white text on dark fills), and on crops of
  uncovered glyph clusters (text inside frames that full-page OCR skips).
- Rows: words on one baseline with ordinary spacing.
- Every label of the diagram (the English strings it was drawn with) is located as a span of words in one row
  or as a wrapped span over 2-3 rows (longest labels first).
- Left-over words: numbers/units/acronyms become elements too (they may need localisation: decimal comma,
  units); everything else is treated as picture noise and left alone.
- Manual additions/overrides from manual.json (boxes found by eye) are merged in.
- Style per element (weight by stroke width, size by ink width, baseline), alignment, free room."""
import difflib, glob, json, os, re, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inv2 import (S, IMG, font, labels, EXTRA, norm, tess, ink_mask, fit_style, colour, ring_bg, free_room)

OUT = S + '/ml/diag/inv3/'
os.makedirs(OUT, exist_ok=True)
MANUAL = json.load(open(S + '/ml/diag/manual.json')) if os.path.exists(S + '/ml/diag/manual.json') else {}
NUMERIC = re.compile(r'^[+\-–—~±×x]?[\d][\d.,:%°′″x×\-–~/+]*(?:[a-zA-Z%°]{0,4}\+?)$')
ACRO = re.compile(r'^[A-Z][A-Z0-9]{1,5}\+?$')
BULLET = re.compile(r'^([0-9]{1,2}|[①-⑳]|0[1-9])$')


def overlap_v(a, b):
    return min(a[3], b[3]) - max(a[1], b[1])


def ocr_all(pil, ink):
    W, H = pil.size
    words = [w for w in tess(pil, '11') if w['conf'] >= 30 or re.search(r'[A-Za-z]{2,}', w['text'])]
    for w in words:
        w['src'] = 'page'
    inv = ImageOps.invert(pil)
    for w in tess(inv, '11'):
        if w['conf'] < 60 or not re.search(r'[A-Za-z0-9]', w['text']):
            continue
        if any(iou_box(w['box'], v['box']) > 0.3 for v in words):
            continue
        w['src'] = 'inverted'; w['line'] = ('inv',) + tuple(w['line'])
        words.append(w)
    # uncovered glyph clusters -> crop OCR
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
    cov = np.zeros_like(ink)
    for w in words:
        x0, y0, x1, y1 = [int(round(v)) for v in w['box']]
        cov[max(0, y0 - 3):y1 + 4, max(0, x0 - 3):x1 + 4] = True
    comps = []
    for i in range(1, n):
        x, y, w_, h_, ar = st[i]
        if 7 <= h_ <= 120 and w_ <= 3.5 * h_ and ar >= 6 and cov[y:y + h_, x:x + w_].mean() <= 0.5:
            comps.append([x, y, x + w_, y + h_])
    comps.sort()
    clusters = []
    for c in comps:
        for cl in clusters:
            b = cl['box']
            h = max(b[3] - b[1], c[3] - c[1])
            if overlap_v(b, c) > 0.35 * min(b[3] - b[1], c[3] - c[1]) and -2 <= c[0] - b[2] < 0.9 * h:
                cl['box'] = [min(b[0], c[0]), min(b[1], c[1]), max(b[2], c[2]), max(b[3], c[3])]; cl['n'] += 1
                break
        else:
            clusters.append(dict(box=list(c), n=1))
    for cl in clusters:
        b = cl['box']; h = b[3] - b[1]
        if cl['n'] < 2 or b[2] - b[0] < 0.8 * h:
            continue
        p = int(0.35 * h) + 2
        X0, Y0 = max(0, b[0] - p), max(0, b[1] - p)
        crop = pil.crop((X0, Y0, min(W, b[2] + p), min(H, b[3] + p)))
        ws = tess(crop, '7', 2.0)
        if not ws:
            continue
        if np.mean([w['conf'] for w in ws]) < 55:
            ws2 = tess(ImageOps.invert(crop), '7', 2.0)
            if ws2 and np.mean([w['conf'] for w in ws2]) > np.mean([w['conf'] for w in ws]):
                ws = ws2
        for w in ws:
            w['box'] = [w['box'][0] + X0, w['box'][1] + Y0, w['box'][2] + X0, w['box'][3] + Y0]
            w['line'] = ('x', b[0], b[1]); w['src'] = 'crop'
        words += ws
    return words


def iou_box(b1, b2):
    ix = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0])); iy = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
    i = ix * iy
    u = (b1[2] - b1[0]) * (b1[3] - b1[1]) + (b2[2] - b2[0]) * (b2[3] - b2[1]) - i
    return i / u if u > 0 else 0


def build_rows(words):
    ws = sorted(range(len(words)), key=lambda i: words[i]['box'][0])
    rows = []
    for i in ws:
        b = words[i]['box']; h = b[3] - b[1]
        best, bo = None, 0
        for r in rows:
            lb = words[r[-1]]['box']
            gap = b[0] - lb[2]
            hh = max(h, max(words[q]['box'][3] - words[q]['box'][1] for q in r))
            ov = overlap_v(b, lb) / max(1, min(h, lb[3] - lb[1]))
            if ov >= 0.5 and -0.3 * hh <= gap < 2.6 * hh and abs(h - (lb[3] - lb[1])) < 0.6 * hh and ov > bo:
                best, bo = r, ov
        if best is not None:
            best.append(i)
        else:
            rows.append([i])
    rows.sort(key=lambda r: (min(words[i]['box'][1] for i in r), words[r[0]]['box'][0]))
    return rows


def box_of(words, ids):
    bs = [words[i]['box'] for i in ids]
    return [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]


def text_of(words, ids):
    return ' '.join(words[i]['text'] for i in ids)


def analyze(stem):
    path = IMG + f'EN-{stem}.png'
    pil = Image.open(path).convert('RGB')
    a = np.array(pil)
    H, W = a.shape[:2]
    ink, _ = ink_mask(a)
    words = [w for w in ocr_all(pil, ink) if re.search(r'[A-Za-z0-9]', w['text'])]
    for w in words:
        w['h'] = w['box'][3] - w['box'][1]
    rows = build_rows(words)
    row_of = {}
    for ri, r in enumerate(rows):
        for k, i in enumerate(r):
            row_of[i] = (ri, k)
    known = labels.get(stem, []) + EXTRA.get(stem, [])
    man = MANUAL.get(stem, {})
    for d in man.get('drop_labels', []):
        if d in known:
            known.remove(d)
    order = sorted(range(len(known)), key=lambda i: -len(norm(known[i])))
    assigned = set()
    elements = []

    def spans_in_row(ri):
        r = rows[ri]
        out = []
        for i in range(len(r)):
            for j in range(i + 1, len(r) + 1):
                ids = r[i:j]
                if any(x in assigned for x in ids):
                    break
                out.append((i, j, ids))
        return out

    for li in order:
        lab = known[li]; nl = norm(lab)
        if not nl:
            continue
        best = None
        for ri in range(len(rows)):
            for i, j, ids in spans_in_row(ri):
                t = norm(text_of(words, ids))
                if not (0.6 * len(nl) <= len(t) <= 1.5 * len(nl) + 2):
                    if len(t) > 0.95 * len(nl) or j < len(rows[ri]):
                        continue
                rt = difflib.SequenceMatcher(None, t, nl).ratio()
                if best is None or rt > best[0]:
                    best = (rt, [ids])
                # wrapped continuation: span must end at the row end
                if j == len(rows[ri]) and len(t) < 0.95 * len(nl):
                    hA = np.median([words[x]['h'] for x in ids])
                    bA = box_of(words, ids)
                    for rj in range(ri + 1, len(rows)):
                        r2 = rows[rj]
                        bB0 = words[r2[0]]['box']
                        gap = bB0[1] - bA[3]
                        if gap > 1.4 * hA:
                            continue
                        if gap < -0.3 * hA:
                            continue
                        for j2 in range(1, len(r2) + 1):
                            ids2 = r2[:j2]
                            if any(x in assigned for x in ids2):
                                break
                            bB = box_of(words, ids2)
                            if min(bA[2], bB[2]) - max(bA[0], bB[0]) <= 0 and abs((bA[0] + bA[2]) / 2 - (bB[0] + bB[2]) / 2) > 0.6 * max(bA[2] - bA[0], bB[2] - bB[0]):
                                continue
                            t2 = t + norm(text_of(words, ids2))
                            if len(t2) > 1.5 * len(nl) + 2:
                                break
                            rt2 = difflib.SequenceMatcher(None, t2, nl).ratio()
                            if rt2 > best[0]:
                                best = (rt2, [ids, ids2])
                            # third line
                            if j2 == len(r2) and len(t2) < 0.95 * len(nl):
                                for rk in range(rj + 1, len(rows)):
                                    r3 = rows[rk]
                                    gap3 = words[r3[0]]['box'][1] - bB[3]
                                    if gap3 > 1.4 * hA or gap3 < -0.3 * hA:
                                        continue
                                    for j3 in range(1, len(r3) + 1):
                                        ids3 = r3[:j3]
                                        if any(x in assigned for x in ids3):
                                            break
                                        t3 = t2 + norm(text_of(words, ids3))
                                        if len(t3) > 1.5 * len(nl) + 2:
                                            break
                                        rt3 = difflib.SequenceMatcher(None, t3, nl).ratio()
                                        if rt3 > best[0]:
                                            best = (rt3, [ids, ids2, ids3])
        thr = 0.8 if len(nl) > 4 else 0.86
        if best and best[0] >= thr:
            for ids in best[1]:
                assigned.update(ids)
            spans = [list(ids) for ids in best[1]]
            en_ = lab
            # leading bullet/number drawn apart from the text ("1   Three adjectives") stays untouched
            first = spans[0]
            if len(first) > 1 and BULLET.match(words[first[0]]['text']) and lab.split(' ')[0] == words[first[0]]['text']:
                g = words[first[1]]['box'][0] - words[first[0]]['box'][2]
                if g > 0.45 * (words[first[1]]['box'][3] - words[first[1]]['box'][1]):
                    spans[0] = first[1:]
                    en_ = lab.split(' ', 1)[1]
            # a circled number drawn as artwork beside the text is not part of the OCR span -> not part of the element
            if re.match(r'^[①-⑳]\s', en_) and not re.match(r'^\W', words[spans[0][0]]['text']):
                en_ = en_[2:]
            elements.append(dict(kind='label', label=lab, en=en_, lines=[box_of(words, ids) for ids in spans],
                                 ocr=' / '.join(text_of(words, ids) for ids in spans), ratio=round(best[0], 2),
                                 src=sorted({words[i]['src'] for ids in spans for i in ids})))
    missing = [known[i] for i in range(len(known)) if not any(e['kind'] == 'label' and e['en'] == known[i] for e in elements)]
    # duplicates: count per label
    cnt = {}
    for e in elements:
        cnt[e.get('label', e['en'])] = cnt.get(e.get('label', e['en']), 0) + 1
    need = {}
    for k in known:
        need[k] = need.get(k, 0) + 1
    missing = []
    for k, c in need.items():
        if cnt.get(k, 0) < c:
            missing += [k] * (c - cnt.get(k, 0))
    # left-over words: numbers / acronyms
    noise = []
    for ri, r in enumerate(rows):
        seg = []
        for i in r + [None]:
            if i is not None and i not in assigned:
                seg.append(i); continue
            if seg:
                toks = [words[x] for x in seg]
                txt = ' '.join(t['text'] for t in toks)
                good = all((NUMERIC.match(t['text']) or ACRO.match(t['text']) or t['text'] in (':', '–', '-', '—', '~', '/', '·', '×'))
                           and (t['conf'] >= 70 or NUMERIC.match(t['text'])) for t in toks)
                if good and re.search(r'[A-Za-z0-9]', txt):
                    elements.append(dict(kind='token', en=txt, lines=[box_of(words, seg)], ocr=txt, ratio=None,
                                         src=sorted({t['src'] for t in toks}), conf=round(float(np.mean([t['conf'] for t in toks])), 1)))
                else:
                    noise.append(dict(text=txt, box=[int(v) for v in box_of(words, seg)], conf=round(float(np.mean([t['conf'] for t in toks])), 1)))
                seg = []
    # manual elements / fixes
    for m in man.get('add', []):
        elements.append(dict(kind='manual', en=m['en'], lines=m['lines'], ocr='', ratio=None, src=['manual'], **{k: v for k, v in m.items() if k not in ('en', 'lines')}))
        if m['en'] in missing:
            missing.remove(m['en'])
    drop = man.get('drop', [])
    elements = [e for e in elements if not any(iou_box(e['lines'][0], d) > 0.5 for d in drop)]
    for fx in man.get('fix', []):
        for e in elements:
            if iou_box(e['lines'][0], fx['box']) > 0.5:
                e.update({k: v for k, v in fx.items() if k != 'box'})
    # ---- merge wrapped sentences split into two labels ("A mix with tension" / "creates a world")
    def colour_of(e):
        bg_, _ = ring_bg(a, e['lines'][-1])
        return colour(a, ink, e['lines'][-1], bg_)
    changed = True
    while changed:
        changed = False
        elements.sort(key=lambda e: (e['lines'][0][1], e['lines'][0][0]))
        for e1 in elements:
            if e1['kind'] != 'label' or re.search(r'[.!?:]$', e1['en']):
                continue
            l1 = e1['lines'][-1]; h1 = l1[3] - l1[1]
            for e2 in elements:
                if e2 is e1 or e2['kind'] != 'label' or not re.match(r'^[a-z(]', e2['en']):
                    continue
                l2 = e2['lines'][0]; h2 = l2[3] - l2[1]
                gap = l2[1] - l1[3]
                if not (-2 <= gap < 1.0 * max(h1, h2)):
                    continue
                c1, c2 = (l1[0] + l1[2]) / 2, (l2[0] + l2[2]) / 2
                if not (abs(c1 - c2) < 0.15 * max(l1[2] - l1[0], l2[2] - l2[0]) or abs(l1[0] - l2[0]) < 6):
                    continue
                if sum(abs(p - q) for p, q in zip(colour_of(e1), colour_of(e2))) > 60:
                    continue
                e1['en'] = e1['en'] + ' ' + e2['en']
                e1['lines'] = e1['lines'] + e2['lines']
                e1['ocr'] = e1['ocr'] + ' / ' + e2['ocr']
                e1.setdefault('merged_labels', [e1.get('label', '')]).append(e2.get('label', e2['en']))
                elements.remove(e2)
                changed = True
                break
            if changed:
                break
    # ---- style, alignment, room
    elements.sort(key=lambda e: (e['lines'][0][1], e['lines'][0][0]))
    for k, e in enumerate(elements):
        e['id'] = k
    # late additions keep the ids of everything above stable
    for m in man.get('late_add', []):
        elements.append(dict(kind='manual', en=m['en'], lines=m['lines'], ocr='', ratio=None, src=['manual'], id=len(elements),
                             **{k: v for k, v in m.items() if k not in ('en', 'lines')}))
    for e in elements:
        e['lines'] = [[int(round(v)) for v in b] for b in e['lines']]
        bs = e['lines']
        e['box'] = [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]
        # per-line text split of the truth for template fitting
        if len(bs) == 1:
            lt = [e['en']]
        else:
            ocr_lines = e['ocr'].split(' / ')
            tw = e['en'].split(' ')
            counts = [len(x.split(' ')) for x in ocr_lines]
            if sum(counts) == len(tw):
                lt, q = [], 0
                for c in counts:
                    lt.append(' '.join(tw[q:q + c])); q += c
            else:
                lt = ocr_lines
        e['ltexts'] = lt
        bg, bgstd = ring_bg(a, e['lines'][0])
        e['bg'], e['bgstd'] = bg, max(ring_bg(a, b)[1] for b in bs)
        if 'color' not in e:
            e['color'] = colour(a, ink, e['lines'][0], bg)
        aa = np.array(pil.rotate(e['rot'], expand=True)) if e.get('rot') else a
        if e.get('rot'):
            bg, _ = ring_bg(aa, e['lines'][0]); e['bg'] = bg
            e['color'] = colour(aa, None, e['lines'][0], bg)
        sts = [fit_style(aa, b, t, ring_bg(aa, b)[0], e['color']) for b, t in zip(bs, lt)]
        ok = [s for s in sts if s]
        if ok:
            wts = {}
            for s_ in ok:
                wts[s_['weight']] = wts.get(s_['weight'], 0) + 1 + s_['score']
            e.setdefault('weight', max(wts, key=wts.get))
            e.setdefault('size', round(float(np.median([s_['size'] for s_ in ok])), 2))
            e['baselines'] = [s_['baseline'] if s_ else None for s_ in sts]
            e['xs'] = [s_['x'] if s_ else None for s_ in sts]
            e['inkboxes'] = [s_['inkbox'] if s_ else None for s_ in sts]
            bl = [s_['baseline'] for s_ in ok]
            e['pitch'] = round(float(np.median(np.diff(bl))), 1) if len(bl) > 1 else None
            e['fitscore'] = round(float(np.mean([s_['score'] for s_ in ok])), 2)
    for e in elements:
        if 'align' in e:
            e['align_src'] = 'manual'; continue
        if len(e['lines']) > 1:
            L = [b[0] for b in e['lines']]; R = [b[2] for b in e['lines']]; C = [(b[0] + b[2]) / 2 for b in e['lines']]
            sp = {'left': max(L) - min(L), 'right': max(R) - min(R), 'center': max(C) - min(C)}
            e['align'] = min(sp, key=sp.get); e['align_src'] = 'lines'
            continue
        x0, y0, x1, y1 = e['box']; cx = (x0 + x1) / 2; h = y1 - y0
        votes = {'left': 0, 'right': 0, 'center': 0}
        above = below = None
        for o in elements:
            if o is e:
                continue
            ox0, oy0, ox1, oy1 = o['box']
            if min(x1, ox1) - max(x0, ox0) <= 0:
                continue
            if oy1 <= y0 + 2:
                g = y0 - oy1
                if above is None or g < above[0]:
                    above = (g, o)
            elif oy0 >= y1 - 2:
                g = oy0 - y1
                if below is None or g < below[0]:
                    below = (g, o)
        for nb in (above, below):
            if nb is None:
                continue
            g, o = nb
            ox0, oy0, ox1, oy1 = o['box']
            if g > 6 * max(h, oy1 - oy0):
                continue
            dd = {'left': abs(ox0 - x0), 'right': abs(ox1 - x1), 'center': abs((ox0 + ox1) / 2 - cx)}
            srt = sorted(dd.items(), key=lambda kv: kv[1])
            dw = abs((ox1 - ox0) - (x1 - x0))
            if dw >= 6 and srt[0][1] <= 4 and srt[0][1] <= 0.5 * srt[1][1] and srt[1][1] >= 2.5:
                votes[srt[0][0]] += 1
        if max(votes.values()) > 0:
            e['align'] = max(votes, key=votes.get); e['align_src'] = 'neighbours'
        elif abs(cx - W / 2) < 0.02 * W and (x1 - x0) > 0.3 * W:
            e['align'] = 'center'; e['align_src'] = 'page'
        else:
            e['align'] = None
    g_ = cv2.GaussianBlur(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), (3, 3), 0).astype(float)
    gx_ = np.zeros_like(g_); gy_ = np.zeros_like(g_)
    gx_[:, 2:-2] = np.abs(g_[:, 4:] - g_[:, :-4]); gy_[2:-2, :] = np.abs(g_[4:, :] - g_[:-4, :])
    struct = ink | (np.maximum(gx_, gy_) > 8)
    for e in elements:
        if e.get('rot'):
            inkr, _ = ink_mask(np.array(pil.rotate(e['rot'], expand=True)))
            e['room'] = free_room(inkr, e['box'], e['lines'])
            continue
        # artwork + frame edges, with the text itself (all text lines) removed
        st_ = struct.copy()
        for o in elements:
            for b in o['lines']:
                hh = b[3] - b[1]; pp = max(4, int(0.3 * hh))
                st_[max(0, b[1] - pp):b[3] + pp, max(0, b[0] - pp):b[2] + pp] = ink[max(0, b[1] - pp):b[3] + pp, max(0, b[0] - pp):b[2] + pp] & False
        e['room'] = free_room(st_, e['box'], e['lines'])
        if e.get('align') is None:
            r = e['room']
            if r['lb'] and r['rb'] and abs(r['left'] - r['right']) <= 0.12 * (r['left'] + r['right']) + 6:
                e['align'] = 'center'; e['align_src'] = 'container'
            else:
                e['align'] = 'left'; e['align_src'] = 'default'
    res = dict(stem=stem, size=[W, H], elements=elements, missing=missing, noise=noise)
    json.dump(res, open(OUT + stem + '.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    dbg = pil.copy(); dr = ImageDraw.Draw(dbg)
    for e in elements:
        col = {'label': (0, 150, 0), 'token': (0, 0, 255), 'manual': (200, 0, 200)}[e['kind']]
        for b in e['lines']:
            dr.rectangle(b, outline=col, width=2)
        dr.text((e['box'][0], max(0, e['box'][1] - 16)), f"{e['id']}{e['align'][0]}", fill=col, font=font('Bold', 15))
    for nz in noise:
        dr.rectangle(nz['box'], outline=(255, 120, 0), width=1)
    dbg.save(OUT + stem + '_boxes.png')
    return res


if __name__ == '__main__':
    stems = sys.argv[1:] or [os.path.basename(p)[3:-4] for p in sorted(glob.glob(IMG + 'EN-*.png'))]
    for s in stems:
        r = analyze(s)
        nt = sum(e['kind'] == 'token' for e in r['elements'])
        print(f"{s}: labels {sum(e['kind'] == 'label' for e in r['elements'])} tokens {nt} [{' | '.join(e['en'] for e in r['elements'] if e['kind'] == 'token')}] missing {r['missing']}", flush=True)

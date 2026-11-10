"""Find words that overlap other words in a PDF (collisions such as a margin note running over a section number).
usage: python3 pdf_overlap.py file.pdf"""
import re, subprocess, sys, html
pdf = sys.argv[1]
xml = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True, text=True).stdout
pages = xml.split('<page ')[1:]
hits = []
for pi, pg in enumerate(pages):
    ws = [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in
          re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', pg)]
    ws = [w for w in ws if w[4].strip() and (w[2] - w[0]) > 0.5 and (w[3] - w[1]) > 0.5]
    # word boxes from pdftotext include the font's full ascent/descent: compare only the glyph core
    ws = [(a + 0.08 * (c - a), b + 0.3 * (d - b), c - 0.08 * (c - a), d - 0.3 * (d - b), t) for a, b, c, d, t in ws]
    ws.sort()
    for i in range(len(ws)):
        a = ws[i]
        for j in range(i + 1, len(ws)):
            b = ws[j]
            if b[0] >= a[2]:
                break
            ix = min(a[2], b[2]) - max(a[0], b[0]); iy = min(a[3], b[3]) - max(a[1], b[1])
            if ix <= 0 or iy <= 0:
                continue
            sa = (a[2] - a[0]) * (a[3] - a[1]); sb = (b[2] - b[0]) * (b[3] - b[1])
            if ix * iy > 0.2 * min(sa, sb):
                hits.append((pi + 1, a[4], b[4], round(a[0]), round(a[1])))
print(pdf, 'pages', len(pages), 'overlapping word pairs', len(hits))
seen = set()
for h in hits:
    k = (h[0], h[1], h[2])
    if k in seen:
        continue
    seen.add(k)
    print('  p%d  %r / %r  at (%d,%d)' % h)

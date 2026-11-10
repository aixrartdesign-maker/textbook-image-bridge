"""Clean final render: re-render the last book.html with the invisible page-map markers ([[MK:...]]) removed,
verify the pagination is identical to pass2.pdf page by page, then rebuild the deliverable
(covers + body + running-head overlay + metadata).
Usage: python3 finalize_pdf.py <build_dir> <out_pdf> <title> <author>"""
import os, re, subprocess, sys
from pypdf import PdfReader, PdfWriter

d, out, title, author = sys.argv[1:5]
os.chdir(d)
H = open('book.html', encoding='utf-8').read()
n_mk = len(re.findall(r'\[\[MK:[^\]]+\]\]', H))
open('book_final.html', 'w', encoding='utf-8').write(re.sub(r'\[\[MK:[^\]]+\]\]', '', H))
if not os.environ.get('SKIP_RENDER'):
    subprocess.run(['node', 'render.js', 'book_final.html', 'pass_final.pdf'], check=True)


def page_texts(pdf):
    t = subprocess.run(['pdftotext', '-raw', pdf, '-'], capture_output=True, text=True).stdout
    pages = t.split('\f')
    out = []
    for p in pages:
        p = re.sub(r'\s+', '', p)
        p = re.sub(r'\[\[[^\]]{0,60}\]\]', '', p)  # marker text, possibly clipped by the extractor
        out.append(p)
    return out


a, b = page_texts('pass2.pdf'), page_texts('pass_final.pdf')
same = len(a) == len(b) and all(x == y for x, y in zip(a, b))
diff = [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y]
print('markers removed', n_mk, '| pages', len(a), len(b), '| identical pagination', same, '| differing pages', diff[:10])
ok_diff = {int(x) for x in os.environ.get('ACCEPT_DIFF', '').split(',') if x.strip()}
if not same and len(a) == len(b) and set(diff) <= ok_diff:
    same = True
    print('accepting reviewed local differences on pages', diff)
src = 'pass_final.pdf' if same else 'pass2.pdf'
base = PdfReader(src)
over = PdfReader('overlay.pdf')
cov = PdfReader('covers.pdf')
w = PdfWriter()
N = len(base.pages)
for i, page in enumerate(base.pages):
    if i == 0:
        w.add_page(cov.pages[0]); continue
    if i == N - 1:
        w.add_page(cov.pages[1]); continue
    if i < len(over.pages):
        page.merge_page(over.pages[i])
    w.add_page(page)
w.add_metadata({'/Title': title, '/Author': author})
with open(out, 'wb') as f:
    w.write(f)
left = subprocess.run(['pdftotext', out, '-'], capture_output=True, text=True).stdout.count('[[MK:')
print('wrote', out, 'from', src, '| pages', N, '| marker text left', left)

"""QA of re-lettered diagrams.
python3 diag_qa.py <lang> [stem ...]
1) OCR each placed element (tesseract deu/rus) and compare with the intended text.
2) OCR the whole image in English and flag English words of the original labels that are still visible.
3) Contact sheet EN | <lang> per diagram -> qa_<lang>/<stem>.png"""
import difflib, glob, json, os, re, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/ml/diag/'
IMG = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/book_en/img_en/'
lang = sys.argv[1]
TL = {'de': 'deu', 'ru': 'rus'}[lang]
os.makedirs(D + f'qa_{lang}', exist_ok=True)


def norm(s):
    s = s.lower().replace('ё', 'е')
    return re.sub(r'[^0-9a-zäöüßа-я]+', '', s)


def ocr(img, l, psm):
    with tempfile.NamedTemporaryFile(suffix='.png', dir=D) as tf:
        img.save(tf.name)
        return subprocess.run(['tesseract', tf.name, '-', '-l', l, '--psm', psm], capture_output=True, text=True).stdout.strip()


stems = sys.argv[2:] or [os.path.basename(p)[:-12] for p in sorted(glob.glob(D + f'out_{lang}/*_report.json'))]
summary = []
for stem in stems:
    rep = json.load(open(D + f'out_{lang}/{stem}_report.json'))
    inv = json.load(open(D + f'inv3/{stem}.json'))
    out = Image.open(D + f'out_{lang}/{lang.upper()}-{stem}.png').convert('RGB')
    W, H = out.size
    issues = []
    for p in rep['placed']:
        if p.get('rot'):
            continue
        bbs = p['bboxes']
        x0 = min(b[0] for b in bbs); y0 = min(b[1] for b in bbs); x1 = max(b[2] for b in bbs); y1 = max(b[3] for b in bbs)
        pad = 8
        crop = out.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        got = ocr(crop, TL + '+eng', '6' if len(bbs) > 1 else '7')
        r = difflib.SequenceMatcher(None, norm(got), norm(p['text'].replace('\n', ' '))).ratio()
        if r < 0.9:
            issues.append(dict(id=p['id'], want=p['text'], got=got, ratio=round(r, 2)))
    # leftover English
    full = ocr(out, 'eng', '11')
    words_out = set(norm(w) for w in re.findall(r'[A-Za-z]{4,}', full))
    placed_ids = {str(p['id']) for p in rep['placed']}
    tr = json.load(open(D + f'tr_{lang}/{stem}.json')) if os.path.exists(D + f'tr_{lang}/{stem}.json') else {}
    tr_words = set(norm(w) for v in tr.values() for w in re.findall(r'[A-Za-zÄÖÜäöüß]{4,}', v))
    en_words = set()
    for e in inv['elements']:
        if str(e['id']) in placed_ids:
            en_words |= set(norm(w) for w in re.findall(r'[A-Za-z]{4,}', e['en']))
    left = sorted((en_words & words_out) - tr_words)
    summary.append(dict(stem=stem, ocr_issues=issues, english_left=left, failed=rep['failed']))
    # contact sheet
    en = Image.open(IMG + f'EN-{stem}.png').convert('RGB')
    w = 1300
    a = en.resize((w, int(en.height * w / en.width)), Image.LANCZOS)
    b = out.resize((w, int(out.height * w / out.width)), Image.LANCZOS)
    sheet = Image.new('RGB', (w, a.height + b.height + 12), (90, 90, 90))
    sheet.paste(a, (0, 0)); sheet.paste(b, (0, a.height + 12))
    sheet.save(D + f'qa_{lang}/{stem}.png')
    print(f"{stem}: ocr-mismatch {len(issues)} | english-left {left} | failed {[f['id'] for f in rep['failed']]}", flush=True)
    for i in issues:
        print(f"    #{i['id']} want={i['want']!r} got={i['got']!r} r={i['ratio']}")
json.dump(summary, open(D + f'qa_{lang}/summary.json', 'w'), ensure_ascii=False, indent=1)

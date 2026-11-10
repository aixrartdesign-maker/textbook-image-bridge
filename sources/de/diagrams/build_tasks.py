"""Build translator task files tasks/<stem>.json from inv3 + cap."""
import glob, json, os, re
D = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/ml/diag/'
IMG = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/book_en/img_en/'
os.makedirs(D + 'tasks', exist_ok=True)
LOCAL = re.compile(r'\d\.\d|%|\d\s?(m|cm|mm|s|min|fps|nit|fL)\b|\d+[-–]\d+\s?(m|cm|mm|s)\b')
total = 0
for f in sorted(glob.glob(D + 'inv3/*.json')):
    inv = json.load(open(f))
    stem = inv['stem']
    cap = json.load(open(D + f'cap/{stem}.json'))
    W, H = inv['size']
    els = []
    for e in inv['elements']:
        if e['kind'] == 'token' and not LOCAL.search(e['en']):
            continue
        c = cap[str(e['id'])]
        role = 'label'
        if e['box'][1] < 0.12 * H and e['align'] == 'center' and e['box'][2] - e['box'][0] > 0.3 * W:
            role = 'title'
        elif e['box'][3] > 0.85 * H and e['align'] == 'center' and e['box'][2] - e['box'][0] > 0.3 * W:
            role = 'caption'
        elif e['kind'] == 'token':
            role = 'number'
        en = e['en']
        if e['kind'] == 'token':
            en = re.sub(r'(\d)-(\d)', r'\1–\2', en)
            en = re.sub(r'^(\d+\.\d+):(\d+)$', r'\1 : \2', en)
        els.append(dict(id=str(e['id']), en=en, role=role,
                        fits=dict(chars_per_line_now=c['chars_line_now'], chars_per_line_max=max(c['chars_line_now'], c['chars_line_max']),
                                  chars_per_line_if_shrunk=max(c['chars_line_now'], c['chars_line_max_shrunk']),
                                  lines_now=c['lines'], lines_max=max(c['lines'], c['lines_max']))))
    json.dump(dict(stem=stem, image=IMG + f'EN-{stem}.png', elements=els), open(D + f'tasks/{stem}.json', 'w'), ensure_ascii=False, indent=1)
    total += len(els)
    print(stem, len(els))
print('total', total)

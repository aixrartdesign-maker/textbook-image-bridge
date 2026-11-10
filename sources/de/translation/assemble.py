"""Reassemble translated parts: skel + out_<lang> -> book_<lang>/parts/*.html
usage: python3 assemble.py de|ru  (missing translations are reported and left in English, marked)"""
import glob, json, os, re, sys

S = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad'
ML = S + '/ml/'
lang = sys.argv[1]
tr = {}
for f in sorted(glob.glob(ML + f'out_{lang}/b*_p*.json')):
    for x in json.load(open(f)):
        tr[x['key']] = x[lang]
fixp = ML + f'tr_fixed_{lang}.json'
if os.path.exists(fixp):
    tr.update(json.load(open(fixp)))
runs = json.load(open(ML + 'runs_en.json'))
dst = S + f'/book_{lang}/parts/'
os.makedirs(dst, exist_ok=True)
missing = []
sys.path.insert(0, ML)
from raw_l10n import MAP as RAW
import figfix
fig_rep = []
raw_hits = [0]; raw_miss = []
for name, rs in runs.items():
    skel = json.load(open(ML + f'skel/{name}.json'))
    out = []
    for kind, v in skel:
        if kind == 'RAW':
            out.append(v); continue
        en = rs[v]
        key = f'{name}#{v}'
        t = tr.get(key)
        if t is None:
            missing.append(key); out.append(en); continue
        lead = re.match(r'^\s*', en).group(0); trail = re.search(r'\s*$', en).group(0)
        out.append(lead + t.strip(' \t\n\r') + trail)
    html_ = ''.join(out)
    # numbers and units in text nodes the translation skipped (figure labels)
    for old_, pair in RAW.get(name, {}).items():
        new_ = pair[0 if lang == 'de' else 1]
        if new_ is None:
            continue
        html_, n_ = re.subn(r'>(\s*)' + re.escape(old_) + r'(\s*)<', lambda m: '>' + m.group(1) + new_ + m.group(2) + '<', html_)
        if n_ == 0:
            raw_miss.append((name, old_))
        raw_hits[0] += n_
    html_, frep = figfix.apply(html_, name, lang)
    fig_rep.extend(frep)
    open(dst + name, 'w', encoding='utf-8').write(html_)
print(lang, 'files', len(runs), 'translations', len(tr), 'missing', len(missing), missing[:10])
print(lang, 'figure labels localised', raw_hits[0], '| not found', raw_miss)
print(lang, 'figure layout fixes problems:', fig_rep or 'none')

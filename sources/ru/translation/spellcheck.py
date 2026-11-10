"""Spell check translated text with Hunspell dictionaries (spylls).
usage: python3 spellcheck.py de|ru [--diag]   -> spell_<lang>.json {word: {"n": count, "keys": [...]}}
Words accepted: dictionary words, ё-forms whose е-form is known (ru), words in ml/spell_ok_<lang>.txt,
acronyms/brands (ALL CAPS, mixed case with digits), Latin-script words in the Russian text (names, codes)."""
import glob, json, os, re, sys
S = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad'
sys.path.insert(0, S + '/tools_ext/spylls')
from spylls.hunspell import Dictionary

lang = sys.argv[1]
diag = '--diag' in sys.argv
d = Dictionary.from_files(S + ('/tools_ext/lodict/de/de_DE_frami' if lang == 'de' else '/tools_ext/lodict/ru_RU/ru_RU'))
okf = S + f'/ml/spell_ok_{lang}.txt'
OK = set(l.strip() for l in open(okf, encoding='utf-8')) if os.path.exists(okf) else set()
TAGS = re.compile(r'<[^>]+>')
ENT = re.compile(r'&[a-z]+;|&#\d+;')
if lang == 'de':
    WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
else:
    WORD = re.compile(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*")
cache = {}


def known(w):
    if w in cache:
        return cache[w]
    r = False
    if w in OK or w.lower() in OK:
        r = True
    elif d.lookup(w):
        r = True
    elif lang == 'ru' and 'ё' in w.lower() and d.lookup(w.replace('ё', 'е').replace('Ё', 'Е')):
        r = True
    elif w[:1].isupper() and d.lookup(w.lower()):
        r = True
    cache[w] = r
    return r


texts = []
if diag:
    for f in sorted(glob.glob(S + f'/ml/diag/tr_{lang}/*.json')):
        for k, v in json.load(open(f)).items():
            texts.append((os.path.basename(f)[:-5] + '#' + k, v))
else:
    for f in sorted(glob.glob(S + f'/ml/out_{lang}/b*_p*.json')):
        for x in json.load(open(f)):
            texts.append((x['key'], x[lang]))
bad = {}
for key, t in texts:
    vis = ENT.sub(' ', TAGS.sub(' ', t))
    for m in WORD.finditer(vis):
        whole = m.group(0)
        parts = [whole] if known(whole) else whole.split('-')
        for w in parts:
            if not w or len(w) < 2:
                continue
            if w.isupper() and len(w) <= 6:
                continue
            if not known(w):
                b = bad.setdefault(w, dict(n=0, keys=[]))
                b['n'] += 1
                if len(b['keys']) < 3:
                    b['keys'].append(key)
out = S + f'/ml/spell_{lang}{"_diag" if diag else ""}.json'
json.dump(dict(sorted(bad.items(), key=lambda kv: -kv[1]['n'])), open(out, 'w'), ensure_ascii=False, indent=0)
print(lang, 'texts', len(texts), 'unique words checked', len(cache), 'unknown', len(bad), '->', out)

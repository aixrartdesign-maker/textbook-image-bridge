"""Apply regex replacements across all translated chunks of a language.
usage: python3 global_fix.py de|ru 'pattern' 'replacement' [--dry]"""
import glob, json, re, sys
ML = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/ml/'
lang, pat, rep = sys.argv[1], sys.argv[2], sys.argv[3]
dry = '--dry' in sys.argv
TAGS = re.compile(r'<[^>]+>')
n = 0
for f in sorted(glob.glob(ML + f'out_{lang}/b*_p*.json')):
    arr = json.load(open(f)); ch = False
    for x in arr:
        new = re.sub(pat, rep, x[lang])
        if new != x[lang]:
            assert TAGS.findall(new) == TAGS.findall(x[lang]), x['key']
            print(f"  {x['key']}: …{re.sub(r'<[^>]+>', '', x[lang])[:0]}{re.search(pat, x[lang]).group(0)!r} -> {re.sub(pat, rep, re.search(pat, x[lang]).group(0))!r}")
            n += 1
            if not dry:
                x[lang] = new; ch = True
    if ch:
        json.dump(arr, open(f, 'w'), ensure_ascii=False, indent=0)
print(lang, 'replaced in', n, 'items', '(dry)' if dry else '')

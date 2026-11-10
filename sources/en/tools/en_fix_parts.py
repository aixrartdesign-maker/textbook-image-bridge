"""Rebuild book_en/parts from the pre-fix backup and apply the reviewed corrections (figures, 8K, minus signs)."""
import sys, re, glob, os, shutil
S = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad'
sys.path.insert(0, S + '/ml')
import figfix
B = S + '/book_en/'
COPYFIT = [
    ('The field has accumulated a vast body of practice', 'The field has a vast body of practice'),
    ('That stitching is hardest for the beginner, because knowing what to learn first already demands considerable knowledge.',
     'That stitching is hardest for beginners: knowing what to learn first already takes knowledge.'),
    ('opens with a narrative introduction to set context', 'opens with a narrative introduction for context'),
    ('closes with a one-page summary ready for class use. All plates are monochrome — a practical decision so that nothing is lost',
     'closes with a one-page summary for class. All plates are monochrome, so nothing is lost'),
    ('A word on the handling of examples.', 'A word on examples.'),
    ('figure and equipment drawings and reference images were made with generative image models, with the generation conditions disclosed',
     'drawings and reference images were made with generative image models, their generation conditions disclosed'),
]
changed = []
for f in sorted(glob.glob(S + '/backups/en_before_fix/parts/*.html')):
    name = os.path.basename(f); s = open(f).read(); s0 = s
    if name == 'part04.html':   # minus signs in text content only (never in attributes such as rotate(-45))
        s = re.sub(r'>([^<>]*)<', lambda m: '>' + re.sub(r'(?:(?<=\s)|^)-(?=\d)', '−', m.group(1)) + '<', s)
    if name == 'prologue.html':
        assert s.count('8K 7680×2160') == 1
        s = s.replace('8K 7680×2160', '8K 7680×4320')
    if name == 'part00.html':   # copyfit: at the designed 100 % size the author's note ran two lines onto a new page
        for a, b in COPYFIT:
            assert s.count(a) == 1, a
            s = s.replace(a, b)
    s, rep = figfix.apply(s, name, 'en')
    if rep:
        print(name, rep)
    open(B + 'parts/' + name, 'w').write(s)
    if s != s0:
        changed.append(name)
print('EN parts changed:', changed)

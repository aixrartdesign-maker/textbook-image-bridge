"""Check or apply proofreading corrections.
usage: python3 apply_proof.py de|ru NN [NN ...] [--check]     (--check: validate only, write nothing)
Corrections: ml/proof_<lang>/bNN.json = [{"key","find","replace","why"}]
Applies to ml/out_<lang>/bNN_p*.json in place (once; applied corrections are logged in proof_<lang>/bNN.applied.json)."""
import glob, json, os, re, sys

ML = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/ml/'
lang = sys.argv[1]
check = '--check' in sys.argv
nums = [a for a in sys.argv[2:] if a.isdigit()]
TAGS = re.compile(r'<[^>]+>')
tot_ok = tot_bad = 0
for n in nums:
    b = f'b{int(n):02d}'
    pf = ML + f'proof_{lang}/{b}.json'
    if not os.path.exists(pf):
        print(b, 'no proof file'); continue
    try:
        corr = json.load(open(pf))
    except Exception as e:
        print(b, 'INVALID JSON', e); tot_bad += 1; continue
    files = sorted(glob.glob(ML + f'out_{lang}/{b}_p*.json'))
    data = {f: json.load(open(f)) for f in files}
    where = {}
    for f, arr in data.items():
        for i, x in enumerate(arr):
            where[x['key']] = (f, i)
    src = {x['key']: x['en'] for x in json.load(open(ML + f'batches/{b}.json'))}
    bad = []
    ok = []
    for c in corr:
        k = c.get('key'); fnd = c.get('find', ''); rep = c.get('replace', '')
        if k not in where:
            bad.append((c, 'unknown key')); continue
        f, i = where[k]
        cur = data[f][i][lang]
        cnt = cur.count(fnd) if fnd else 0
        if cnt != 1:
            bad.append((c, f'find occurs {cnt}x')); continue
        new = cur.replace(fnd, rep, 1)
        if TAGS.findall(new) != TAGS.findall(src[k]):
            bad.append((c, 'tags differ from English')); continue
        ok.append(c)
        if not check:
            data[f][i][lang] = new
    for c, why in bad:
        print(f'  REJECTED {c.get("key")}: {why} | find={c.get("find","")[:60]!r}')
    if not check and ok:
        for f, arr in data.items():
            json.dump(arr, open(f, 'w'), ensure_ascii=False, indent=0)
        os.rename(pf, ML + f'proof_{lang}/{b}.applied.json')
    kinds = {}
    for c in ok:
        w = (c.get('why') or 'other').split()[0].strip(':,;').lower()
        kinds[w] = kinds.get(w, 0) + 1
    print(f'{b}: {"valid" if check else "applied"} {len(ok)} | rejected {len(bad)} | {kinds}')
    tot_ok += len(ok); tot_bad += len(bad)
print('total', tot_ok, 'ok', tot_bad, 'rejected')

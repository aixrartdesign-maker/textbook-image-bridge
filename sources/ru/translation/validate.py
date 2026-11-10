"""Validate translated chunks.  usage: python3 validate.py de|ru [NN ...]
Checks per batch: JSON validity, completeness and key order, identical inline-tag sequence,
untranslated runs, leftover English words, wrong quote style, decimal points in measurements."""
import glob, json, os, re, sys

ML = '/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/ml'
lang = sys.argv[1]
want = [f'b{int(x):02d}' for x in sys.argv[2:]] or sorted(os.path.basename(p)[:3] for p in glob.glob(ML + '/batches/b*.json'))
TAGS = re.compile(r'<[^>]+>')
EN_STOP = re.compile(r'\b(the|and|with|your|you|this|that|from|which|when|what|into|than|then|them|they|their|there|here|only|also|each|every|about|before|after|should|would|could|must|will|make|takes?|shot|shots|cut|cuts|light|frame|frames|scene|camera)\b', re.I)
ALLOW_LATIN = set('''iso lut ppm ots els ls fs ks ms bs cu ecu dop ad led xr ar vr mr rgb cmyk hdr sdr hd uhd nd fps sns cta kpi ott ctr raw log mp mov prores h hevc avc srt wav aac mp3 mp4 png jpg tiff psd ai pdf url qr gpt llm ui ux api cpu gpu ram ssd sd cf usb hdmi sdi xlr db dbfs lufs nit fl k s m mm cm km kg g w kw v hz khz mhz gb mb tb px dpi lpi f t
premiere pro after effects davinci resolve youtube shorts instagram reels tiktok higgsfield kling midjourney runway sora veo firefly photoshop illustrator lightroom final cut capcut canva figma blender unreal unity cinema 4d max notion slack zoom google drive docs sheets chatgpt claude gemini netflix disney apple iphone galaxy samsung sony canon nikon panasonic blackmagic arri red dji gopro aputure godox nanlite zeiss sigma tamron rode sennheiser zoom tascam shure adobe stock behance vimeo linkedin wanted saramin jobkorea worknet upwork fiverr kmong youtube studio meta facebook threads x twitter naver kakao coupang shopify wix
size move n se cut ref sync m storyboard take showreel portfolio timecode codec chroma key b roll color grading greenscreen spotlight'''.split())
QUOTE_BAD = {'de': re.compile(r'[”«»]|"(?=\w)|(?<=\w)"'), 'ru': re.compile(r'[”]|"(?=\w)|(?<=\w)"')}


def quote_problem(lang, v):
    if QUOTE_BAD[lang].search(v):
        return True
    if lang == 'de':
        return v.count('„') != v.count('“')
    return v.count('«') != v.count('»') or v.count('„') != v.count('“')
DEC = re.compile(r'(?<![\d.:/])\d+\.\d+(?=\s?(?:mm|m|cm|s|с|м|мм|см|%|×|x|:1|K|К|fps|кадр|нит|nit|fL|Min|мин|Std|ч)\b)')
total_bad = 0
for b in want:
    src = json.load(open(f'{ML}/batches/{b}.json'))
    out = []
    bad_json = []
    for f in sorted(glob.glob(f'{ML}/out_{lang}/{b}_p*.json')):
        try:
            out += json.load(open(f))
        except Exception as e:
            bad_json.append(f'{os.path.basename(f)}: {e}')
    keys = [x['key'] for x in src]
    okeys = [x.get('key') for x in out]
    complete = okeys == keys
    m = {x['key']: x.get(lang, '') for x in out}
    s = {x['key']: x['en'] for x in src}
    tagbad = [k for k in m if k in s and TAGS.findall(m[k]) != TAGS.findall(s[k])]
    def name_like(t):
        ws = re.findall(r"[A-Za-z][A-Za-z0-9&;.'-]*", TAGS.sub(' ', t))
        return bool(ws) and all(w[0].isupper() or w.lower() in ALLOW_LATIN or w in ('amp', 'and') for w in ws)
    same_all = [k for k in m if k in s and m[k] == s[k] and re.search(r'[a-z]{3,}', TAGS.sub(' ', s[k]))]
    same = [k for k in same_all if not name_like(s[k])]
    names = [k for k in same_all if name_like(s[k])]
    eng = []
    for k, v in m.items():
        vis = TAGS.sub(' ', v)
        if lang == 'ru':
            words = [w for w in re.findall(r'[A-Za-z]{2,}', vis) if w.lower() not in ALLOW_LATIN and not w.isupper()]
            if words:
                eng.append((k, words[:4]))
        else:
            hits = EN_STOP.findall(vis)
            if hits:
                eng.append((k, hits[:4]))
    quotes = [k for k, v in m.items() if quote_problem(lang, TAGS.sub(' ', v))]
    decs = [(k, DEC.findall(TAGS.sub(' ', v))[:3]) for k, v in m.items() if DEC.search(TAGS.sub(' ', v))]
    missing = len(src) - len(out)
    nbad = len(bad_json) + (0 if complete else 1) + len(tagbad) + len(same)
    total_bad += nbad
    print(f'{b}: {len(out)}/{len(src)} {"complete" if complete else "INCOMPLETE"} | tags {len(tagbad)} | untranslated {len(same)} (+{len(names)} names kept) | english? {len(eng)} | quotes {len(quotes)} | decimal-dot {len(decs)}')
    for x in bad_json[:3]:
        print('   BAD JSON', x)
    if not complete and out:
        first = next((i for i, (a, c) in enumerate(zip(keys, okeys)) if a != c), min(len(keys), len(okeys)))
        print('   first key mismatch at index', first, keys[first] if first < len(keys) else None)
    for k in tagbad[:5]:
        print('   TAGS', k, '| en:', TAGS.findall(s[k])[:6], '| out:', TAGS.findall(m[k])[:6])
    for k in same[:5]:
        print('   UNTRANSLATED', k, s[k][:80])
    for k, w in eng[:8]:
        print('   ENGLISH?', k, w)
    for k in quotes[:5]:
        print('   QUOTES', k, TAGS.sub(' ', m[k])[:90])
    for k, d in decs[:5]:
        print('   DECIMAL', k, d)
print('blocking problems:', total_bad)

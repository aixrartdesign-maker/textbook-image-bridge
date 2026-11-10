import re
def is_meas(s, start, end):
    """True when the d.d token at s[start:end] is a measurement/version, not a section reference."""
    before=re.sub(r'<[^>]+>','',s[max(0,start-60):start]); after=re.sub(r'<[^>]+>','',s[end:end+30])
    if re.match(r'\s*~\s*\d', after) and re.match(r'\s*~\s*[\d.]+\s*(m\b|m²|cm|mm|배|초|분|%|x|×|K|lux|lm|이상|이하|,|\s*장초점)', after): return True
    if re.match(r'\s*~\s*[\d.]+\s*(m|배|초)', after): return True
    if re.search(r'[×x]\s*$', before): return True
    if re.search(r'F\d[\d.]*,(\s*[\d.]+,)*\s*$', before): return True
    if re.search(r'f/\s*$', before): return True
    if re.search(r'[A-Za-z]{2,}\s$', before) and not re.search(r'(PART|Part|Section|section|Exercise|Figure|Plate)\s$', before): return True
    if re.match(r'\s*(이상|이하|배(?![가-힣])|배로|초(?![가-힣])|%|:\d)', after): return True
    if re.search(r'(표준|단초점|장초점|눈높이|바닥|최소|최대|높이의|대각의|시간 ×)\s*$', before) or re.search(r'(^|[\s(|])약\s*$', before): return True
    return False

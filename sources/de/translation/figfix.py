"""Layout fixes for figures whose labels did not fit (all three editions share the SVG geometry).
apply(html, part_name, lang) -> (html, report)"""
import re
from html import escape

NB = ' '


def _svgs_after(html, fig_id):
    """spans (start, end) of every <svg>…</svg> inside the element with id=fig_id (up to the next id="s…"/"f…" section)"""
    i = html.find(f'id="{fig_id}"')
    if i < 0:
        return []
    nxt = re.compile(r'id="(?:s\d|f-)[^"]*"').search(html, i + 5)
    end = nxt.start() if nxt else len(html)
    out = []
    k = html.find('<svg', i)
    while 0 <= k < end:
        j = html.find('</svg>', k) + 6
        out.append((k, j))
        k = html.find('<svg', j)
    return out


def _edit_svg(html, fig_id, nth, fn, rep):
    spans = _svgs_after(html, fig_id)
    if nth >= len(spans):
        rep.append(f'{fig_id}: svg #{nth} not found')
        return html
    a, b = spans[nth]
    new = fn(html[a:b])
    return html[:a] + new + html[b:]


def wrap(svg, content, lines, dy, rep, tag=''):
    """<text …>content</text> -> two or more tspans at the same x"""
    pat = re.compile(r'<text([^>]*)>' + re.escape(escape(content, quote=False)) + r'</text>')
    m = pat.search(svg)
    if not m:
        rep.append(f'{tag}: text not found: {content!r}')
        return svg
    attrs = m.group(1)
    x = re.search(r'\bx="([^"]+)"', attrs).group(1)
    spans = ''.join('<tspan x="%s"%s>%s</tspan>' % (x, '' if i == 0 else ' dy="%s"' % dy, escape(l, quote=False)) for i, l in enumerate(lines))
    return svg[:m.start()] + f'<text{attrs}>{spans}</text>' + svg[m.end():]


# ---------------------------------------------------------------- per-figure data
S2_10 = {  # s2-10: cut counts under the emotion names (end-anchored, 130 units of room) -> two lines
    'en': {'36 cuts · chase · accident · warning': ['36 cuts · chase ·', 'accident · warning'],
           '15 cuts · product intro · vlog': ['15 cuts ·', 'product intro · vlog'],
           '7 cuts · interview · documentary': ['7 cuts · interview ·', 'documentary'],
           '4 cuts · landscape · brand mood': ['4 cuts · landscape ·', 'brand mood']},
    'de': {'36 Schnitte · Verfolgung · Unfall · Warnung': ['36 Schnitte · Verfolgung ·', 'Unfall · Warnung'],
           '15 Schnitte · Produktvorstellung · Vlog': ['15 Schnitte ·', 'Produktvorstellung · Vlog'],
           '7 Schnitte · Interview · Doku': ['7 Schnitte ·', 'Interview · Doku'],
           '4 Schnitte · Landschaft · Markenstimmung': ['4 Schnitte · Landschaft ·', 'Markenstimmung']},
    'ru': {'36 кадров · погоня · авария · предупреждение': ['36 кадров · погоня ·', 'авария · предупреждение'],
           '15 кадров · презентация товара · влог': ['15 кадров ·', 'презентация товара · влог'],
           '7 кадров · интервью · документалистика': ['7 кадров · интервью ·', 'документалистика'],
           '4 кадра · пейзаж · настроение бренда': ['4 кадра · пейзаж ·', 'настроение бренда']},
}

S4_2_BACK = {'en': ('High behind, rims head·shoulders', ['High behind,', 'rims head·shoulders']),
             'de': ('Hinten hoch, säumt Kopf·Schultern', ['Hinten hoch,', 'säumt Kopf·Schultern']),
             'ru': ('Высоко сзади, контур головы·плеч', ['Высоко сзади,', 'контур головы·плеч'])}

S12_10 = {  # CV sample: contact line, job descriptions and skills in two lines; everything from Education down moves 9 units
    'en': {'Video editing · motion graphics | 010-0000-0000 | portfolio.link': ['Video editing · motion graphics', '010-0000-0000 | portfolio.link'],
           'Rough cuts · subtitles · color-correction support for 12 ads. Average revision rounds cut from 3 → 2':
               ['Rough cuts · subtitles · color-correction support for 12 ads.', 'Average revision rounds cut from 3 → 2'],
           'Led planning · shooting · editing in a 4-person team · 120K views · client came back':
               ['Led planning · shooting · editing in a 4-person team ·', '120K views · client came back'],
           '1 video a week for 48 weeks · 3,400 subscribers · thumbnail A/B test log':
               ['1 video a week for 48 weeks · 3,400 subscribers ·', 'thumbnail A/B test log'],
           'Editing Premiere ●●●●○ · AE ●●●○○ · DaVinci ●●●○○ · Camera α7 ●●●○○ · Generative image/video ●●●○○':
               ['Editing Premiere ●●●●○ · AE ●●●○○ · DaVinci ●●●○○ ·', 'Camera α7 ●●●○○ · Generative image/video ●●●○○']},
    'de': {'Videoschnitt · Motion Design | 010-0000-0000 | portfolio.link': ['Videoschnitt · Motion Design', '010-0000-0000 | portfolio.link'],
           'Rohschnitte · Untertitel · Hilfe bei der Farbkorrektur für 12 Spots. Korrekturschleifen im Mittel von 3 → 2 gesenkt':
               ['Rohschnitte · Untertitel · Hilfe bei der Farbkorrektur', 'für 12 Spots. Korrekturschleifen im Mittel von 3 → 2 gesenkt'],
           'Planung · Dreh · Schnitt im 4er-Team geleitet · 120.000 Aufrufe · Folgeauftrag erhalten':
               ['Planung · Dreh · Schnitt im 4er-Team geleitet ·', '120.000 Aufrufe · Folgeauftrag erhalten'],
           '1 Video pro Woche, 48 Wochen lang · 3.400 Abonnenten · Protokoll zu Thumbnail-A/B-Tests':
               ['1 Video pro Woche, 48 Wochen lang · 3.400 Abonnenten ·', 'Protokoll zu Thumbnail-A/B-Tests'],
           'Schnitt Premiere ●●●●○ · AE ●●●○○ · DaVinci ●●●○○ · Kamera α7 ●●●○○ · Generative Bilder/Videos ●●●○○':
               ['Schnitt Premiere ●●●●○ · AE ●●●○○ · DaVinci ●●●○○ ·', 'Kamera α7 ●●●○○ · Generative Bilder/Videos ●●●○○'],
           '12 Spots à 15 s · 40 Kurzvideo-Folgen geschnitten – durchschnittliche Wiedergabedauer 58 %':
               ['12 Spots à 15 s · 40 Kurzvideo-Folgen geschnitten –', 'durchschnittliche Wiedergabedauer 58 %'],
           '○○ Filmfestival, Kurzfilm: lobende Erwähnung · Führerschein · Drohnenführerschein (Klasse 4)':
               ['○○ Filmfestival, Kurzfilm: lobende Erwähnung ·', 'Führerschein · Drohnenführerschein (Klasse 4)']},
    'ru': {'Видеомонтаж · моушн-графика | 010-0000-0000 | portfolio.link': ['Видеомонтаж · моушн-графика', '010-0000-0000 | portfolio.link'],
           'Черновой монтаж · субтитры · помощь с цветокоррекцией для 12 роликов. Среднее число кругов правок: 3 → 2':
               ['Черновой монтаж · субтитры · помощь с цветокоррекцией', 'для 12 роликов. Среднее число кругов правок: 3 → 2'],
           'Вёл планирование · съёмку · монтаж в команде из 4 · 120 тыс. просмотров · повторный заказ':
               ['Вёл планирование · съёмку · монтаж в команде из 4 ·', '120 тыс. просмотров · повторный заказ'],
           '48 недель по 1 видео в неделю · 3400 подписчиков · журнал A/B-тестов обложек':
               ['48 недель по 1 видео в неделю · 3400 подписчиков ·', 'журнал A/B-тестов обложек'],
           'Монтаж Premiere ●●●●○ · AE ●●●○○ · DaVinci ●●●○○ · Камера α7 ●●●○○ · Генерация фото/видео ●●●○○':
               ['Монтаж Premiere ●●●●○ · AE ●●●○○ · DaVinci ●●●○○ ·', 'Камера α7 ●●●○○ · Генерация фото/видео ●●●○○'],
           'Монтаж 12 роликов по 15 с · 40 выпусков коротких видео — среднее удержание 58 %':
               ['Монтаж 12 роликов по 15 с · 40 выпусков коротких видео —', 'среднее удержание 58 %'],
           'Кинофестиваль ○○, короткий метр: поощрительный приз · водительские права · права на дрон (4 кл.)':
               ['Кинофестиваль ○○, короткий метр: поощрительный приз ·', 'водительские права · права на дрон (4 кл.)']},
}

S12_8 = {  # youth employment chart: labels left of the bars, values inside, donut captions inside the frame
    'en': dict(title='Change in employed youth (ages 15–29) — 2022.6 → 2026.6, Bank of Korea analysis',
               c=['All ages 15–29', 'ICT · publishing (SW · web design)', 'Computer programming', 'Employed in their 50s'],
               v=['−285,000', '−27.4%', '−16.6%', 'Up'], d=['94%', '65.6%'],
               cap1=['Share of the drop in highly', 'AI-exposed industries'],
               cap2=['Ages 19–34 who fear "AI cuts', 'entry-level work, so fewer', 'chances to grow" (FKI)'],
               s=['What disappears is not the profession', "but the ladder's bottom rungs"]),
    'de': dict(title='Veränderung junger Erwerbstätiger (15–29 Jahre) – 06/2022 → 06/2026, Analyse der Bank of Korea',
               c=['Gesamt 15–29', 'IKT · Verlage (SW · Webdesign)', 'Programmierung', 'Erwerbstätige 50–59'],
               v=['−285.000', '−27,4' + NB + '%', '−16,6' + NB + '%', 'Plus'], d=['94' + NB + '%', '65,6' + NB + '%'],
               cap1=['Rückgangsanteil in stark', 'KI-exponierten Branchen'],
               cap2=['19–34-Jährige mit der Sorge', '„KI kürzt Einstiegsjobs, somit', 'weniger Chancen zu wachsen“ (FKI)'],
               s=['Was verschwindet, ist nicht der Beruf,', 'sondern die untersten Sprossen']),
    'ru': dict(title='Изменение числа занятой молодёжи (15–29 лет) — 06.2022 → 06.2026, анализ Банка Кореи',
               c=['Все 15–29 лет', 'ИКТ · издательства (ПО · веб-дизайн)', 'Программирование', 'Занятые 50–59 лет'],
               v=['−285' + NB + '000', '−27,4' + NB + '%', '−16,6' + NB + '%', 'Рост'], d=['94' + NB + '%', '65,6' + NB + '%'],
               cap1=['Доля спада в отраслях,', 'сильно затронутых ИИ'],
               cap2=['Боятся (19–34 года), что ИИ', 'урежет работу новичков', 'и шансы на рост (FKI)'],
               s=['Исчезает не профессия,', 'а нижние ступени лестницы']),
}


def s12_8_svg(L):
    e = lambda t: escape(t, quote=False)
    bars = [(190, 110, '#7A1C2B'), (204, 96, '#7A1C2B'), (236, 64, '#7A1C2B')]
    out = ['<svg viewBox="0 0 560 258" xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans CJK KR" font-size="9.5">',
           '<rect width="560" height="258" fill="#F6F5F3"/>',
           f'<text x="14" y="20" font-weight="600" fill="#1B1B1D">{e(L["title"])}</text>']
    for i, (x, w, col) in enumerate(bars):
        y = 40 + 30 * i
        out.append(f'<text x="14" y="{y + 13}" fill="#1B1B1D">{e(L["c"][i])}</text>')
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="18" fill="{col}"/>')
        out.append(f'<text x="{x + 6}" y="{y + 13}" fill="#fff" font-weight="600">{e(L["v"][i])}</text>')
    out.append(f'<text x="14" y="143" fill="#1B1B1D">{e(L["c"][3])}</text>')
    out.append('<rect x="300" y="130" width="44" height="18" fill="#8E8A82"/>')
    out.append(f'<text x="350" y="143" fill="#8E8A82" font-weight="600">{e(L["v"][3])}</text>')
    out.append('<line x1="300" y1="36" x2="300" y2="160" stroke="#1B1B1D"/>')
    for cx, end, val, cap in ((385, '375.4,165.8', L['d'][0], L['cap1']), (500, '478.4,204.5', L['d'][1], L['cap2'])):
        out.append(f'<circle cx="{cx}" cy="190" r="26" fill="none" stroke="#E5E3DE" stroke-width="7"/>')
        out.append(f'<path d="M{cx},164 A26,26 0 1,1 {end}" fill="none" stroke="#7A1C2B" stroke-width="7"/>')
        out.append(f'<text x="{cx}" y="194" text-anchor="middle" font-weight="600" fill="#1B1B1D" font-size="10">{e(val)}</text>')
        for k, line in enumerate(cap):
            out.append(f'<text x="{cx}" y="{230 + 10 * k}" text-anchor="middle" fill="#3C3C40" font-size="7.6">{e(line)}</text>')
    out.append(f'<text x="14" y="200" fill="#1B1B1D" font-weight="500" font-size="9">{e(L["s"][0])}</text>')
    out.append(f'<text x="14" y="213" fill="#7A1C2B" font-weight="600" font-size="9">{e(L["s"][1])}</text>')
    out.append('</svg>')
    return ''.join(out)


S12_2 = {
    'en': dict(t1='Traditional — one way', flow=['Planning', 'Storyboard', 'Booking · shoot', 'Edit', 'Revise', 'Delivery'],
               n1='No undo after the shoot — decide before it; costs peak on shoot day', t2='Generative — loop',
               nodes=['Prompt', 'Generate', 'Select', 'Revise'], center=['Dozens', 'of times'],
               boxes=[(['Lock'], ['Open to the end']), (['Correct ·', 'composite'], ['Most human handwork']),
                      (['QC · delivery'], ['Rights · facts · quality'])],
               n2='The shooting bottleneck is gone; selection and quality control become the bottleneck — "post-production is the new pre-production"'),
    'de': dict(t1='Klassisch – Einbahnstraße', flow=['Planung', 'Storyboard', 'Buchung · Dreh', 'Schnitt', 'Korrektur', 'Abgabe'],
               n1='Nach dem Dreh kein Zurück – vorher entscheiden; Kostenspitze am Drehtag', t2='Generativ – Schleife',
               nodes=['Prompt', 'Generieren', 'Auswählen', 'Anpassen'], center=['Dutzende', 'Male'],
               boxes=[(['Fixieren'], ['Bis zuletzt offen']), (['Korrektur ·', 'Compositing'], ['Meiste Handarbeit']),
                      (['QC · Abgabe'], ['Rechte · Fakten ·', 'Qualität'])],
               n2='Der Engpass Dreh entfällt; Auswahl und Qualitätskontrolle werden zum Engpass – „Postproduktion ist die neue Vorproduktion“'),
    'ru': dict(t1='Традиционно — в одну сторону', flow=['Планирование', 'Раскадровка', 'Бронь · съёмка', 'Монтаж', 'Правки', 'Сдача'],
               n1='Отмены после съёмки нет — решать до неё; пик затрат — в день съёмки', t2='Генеративно — цикл',
               nodes=['Промпт', 'Генерация', 'Отбор', 'Правка'], center=['Десятки', 'раз'],
               boxes=[(['Фиксация'], ['Открыто до конца']), (['Правка ·', 'композитинг'], ['Пик ручной работы']),
                      (['QC · сдача'], ['Права · факты ·', 'качество'])],
               n2='Узкое место съёмки исчезло; узким местом стали отбор и контроль качества — «постпродакшн — это новый препродакшн»'),
}


def s12_2_svg(L):
    """Traditional pipeline vs generative loop. The loop nodes are large enough for their labels, and the three
    finishing boxes take two-line titles/notes, so no white text runs outside its dark shape."""
    import math
    e = lambda t: escape(t, quote=False)
    o = ['<svg viewBox="0 0 560 282" xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans CJK KR" font-size="9.5">',
         '<rect width="560" height="282" fill="#F6F5F3"/>',
         f'<text x="20" y="24" font-weight="600" fill="#1B1B1D" font-size="11">{e(L["t1"])}</text>']
    for i, (lab, op) in enumerate(zip(L['flow'], ('.85', '.80', '.75', '.70', '.65', '.60'))):
        x = 20 + 90 * i
        o.append(f'<rect x="{x}" y="36" width="78" height="34" rx="3" fill="#B9B5AC" opacity="{op}"/>')
        o.append(f'<text x="{x + 39}" y="57" text-anchor="middle" fill="#3C3C40" font-weight="500">{e(lab)}</text>')
        if i < 5:
            a = x + 80
            o.append(f'<polygon points="{a},53 {a + 8},53 {a + 4},49 {a + 8},53 {a + 4},57" fill="#1B1B1D"/>')
    o.append(f'<text x="20" y="90" fill="#7A7A80" font-size="8.5">{e(L["n1"])}</text>')
    o.append(f'<text x="20" y="124" font-weight="600" fill="#1B1B1D" font-size="11">{e(L["t2"])}</text>')
    cx, cy, rr, nr = 172, 194, 48, 22
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="#7A1C2B" stroke-width="2.5"/>')
    for deg in (45, 135, 225, 315):           # direction marks between the nodes (clockwise)
        t = math.radians(deg)
        px, py = cx + rr * math.cos(t), cy + rr * math.sin(t)
        tx, ty = -math.sin(t), math.cos(t)
        nx, ny = math.cos(t), math.sin(t)
        pts = [(px + 5 * tx, py + 5 * ty), (px - 4 * tx + 4 * nx, py - 4 * ty + 4 * ny), (px - 4 * tx - 4 * nx, py - 4 * ty - 4 * ny)]
        o.append('<polygon points="%s" fill="#7A1C2B"/>' % ' '.join('%.1f,%.1f' % p for p in pts))
    for (nx_, ny_), lab in zip(((cx, cy - rr), (cx + rr, cy), (cx, cy + rr), (cx - rr, cy)), L['nodes']):
        o.append(f'<circle cx="{nx_}" cy="{ny_}" r="{nr}" fill="#7A1C2B"/>')
        o.append(f'<text x="{nx_}" y="{ny_ + 2.6:g}" text-anchor="middle" fill="#fff" font-size="7.4" font-weight="500">{e(lab)}</text>')
    o.append(f'<text x="{cx}" y="{cy - 3}" text-anchor="middle" fill="#3C3C40" font-size="8">{e(L["center"][0])}</text>')
    o.append(f'<text x="{cx}" y="{cy + 7}" text-anchor="middle" fill="#3C3C40" font-size="8">{e(L["center"][1])}</text>')
    o.append(f'<line x1="248" y1="{cy}" x2="272" y2="{cy}" stroke="#1B1B1D" stroke-width="1.5"/>')
    o.append(f'<polygon points="272,{cy - 5} 282,{cy} 272,{cy + 5}" fill="#1B1B1D"/>')
    H = 43
    y0 = cy - H / 2
    for i, ((tl, sl), op) in enumerate(zip(L['boxes'], ('.85', '.70', '.55'))):
        x = 288 + 92 * i
        c = x + 42
        o.append(f'<rect x="{x}" y="{y0:g}" width="84" height="{H}" rx="3" fill="#1B1B1D" opacity="{op}"/>')
        content = 11 * len(tl) + 9 * len(sl)
        top = y0 + (H - content) / 2
        for j, t in enumerate(tl):
            o.append(f'<text x="{c}" y="{top + 8 + 11 * j:g}" text-anchor="middle" fill="#fff" font-weight="500" font-size="9">{e(t)}</text>')
        for j, t in enumerate(sl):
            o.append(f'<text x="{c}" y="{top + 11 * len(tl) + 7 + 9 * j:g}" text-anchor="middle" fill="#fff" font-size="7.2">{e(t)}</text>')
    o.append(f'<text x="20" y="274" fill="#7A7A80" font-size="8.5">{e(L["n2"])}</text>')
    o.append('</svg>')
    return ''.join(o)


def _shift_y(svg, ymin, d):
    def f(m):
        v = float(m.group(2))
        return f'{m.group(1)}="{v + d:g}"' if v >= ymin else m.group(0)
    return re.sub(r'\b(y|y1|y2)="([\d.]+)"', f, svg)


def fit_rrow(html, fig_id, rep):
    """Rows of aspect-ratio frames (.rrow): every image keeps its true proportions (no stretching to the label width),
    images of one row stay bottom-aligned (top padding), labels may wrap below them, and the items may shrink down to
    their image width so a row never runs past the text block."""
    i = html.find(f'id="{fig_id}"')
    if i < 0:
        rep.append(f'{fig_id}: not found'); return html
    a = html.find('<div class="rrow', i)
    end = html.find('</figure>', a)
    if a < 0 or end < 0:
        rep.append(f'{fig_id}: rrow not found'); return html
    fig = html[a:end]
    pieces = re.split(r'(?=<div class="rrow)', fig)
    out = []
    total = 0
    for seg in pieces:
        hs = [float(x) for x in re.findall(r'class="rb(?: eq)?" style="height:([\d.]+)mm"', seg)]
        if not hs:
            out.append(seg); continue
        H = max(hs)
        seg = re.sub(r'<div class="rrow([^"]*)">', r'<div class="rrow\1" style="align-items:flex-start">', seg, count=1)

        def rb(m):
            h = float(m.group(1))
            return (f'<div class="rb" style="height:auto;padding-top:{H - h:g}mm;flex:0 1 auto;min-width:auto;overflow-wrap:normal">'
                    f'<img src="{m.group(2)}" style="height:{h - 9:g}mm;align-self:flex-start">')
        seg, n = re.subn(r'<div class="rb" style="height:([\d.]+)mm"><img src="([^"]+)"[^>]*>', rb, seg)

        def rbeq(m):  # the panorama cell keeps filling the rest of the row; its picture gets the row's image height
            h = float(m.group(1))
            return (f'<div class="rb eq" style="height:auto;padding-top:{H - h:g}mm">'
                    f'<div class="eqw" style="height:{h - 9:g}mm;flex:none">')
        seg, n2 = re.subn(r'<div class="rb eq" style="height:([\d.]+)mm"><div class="eqw">', rbeq, seg)
        n += n2
        if n != len(hs):
            rep.append(f'{fig_id}: rb rewrite {n}/{len(hs)}')
        total += n
        out.append(seg)
    if not total:
        rep.append(f'{fig_id}: nothing rewritten')
    return html[:a] + ''.join(out) + html[end:]

def move_note_before(html, fig_id, note_marker, before_tag, rep, style='break-inside:avoid'):
    """Move a margin note (aside) that contains note_marker to just before the first before_tag in the same section,
    so the float has room in the margin and cannot be pushed onto the next section's opener."""
    reg = _regions(html, fig_id)
    if not reg:
        rep.append(f'{fig_id}: not found'); return html
    a0, b0 = reg
    seg = html[a0:b0]
    m = re.search(r'<aside class="note">(?:(?!</aside>).)*?' + re.escape(note_marker) + r'.*?</aside>\s*', seg, re.S)
    if not m:
        rep.append(f'{fig_id}: note {note_marker!r} not found'); return html
    note = m.group(0).strip()
    seg = seg[:m.start()] + seg[m.end():]
    k = seg.find(before_tag)
    if k < 0:
        rep.append(f'{fig_id}: {before_tag!r} not found'); return html
    note = note.replace('<aside class="note">', f'<aside class="note" style="{style}">', 1)
    seg = seg[:k] + note + '\n' + seg[k:]
    return html[:a0] + seg + html[b0:]


def apply(html, name, lang):
    """name = part file name, or None to apply every fix to a whole book.html"""
    rep = []
    if name in ('part02.html', None):
        # s2-20: the subtitle moves under the title, so the title needs no shrinking
        for n in range(6):
            html = _edit_svg(html, 's2-20', n, lambda s: s.replace('<text x="56" y="26" font-size="10" fill="#7A7A80">',
                                                                     '<text x="14" y="43" font-size="10" fill="#7A7A80">'), rep)
        if lang in S2_10:
            def f(s):
                for k, v in S2_10[lang].items():
                    s = wrap(s, k, v, 12, rep, 's2-10')
                return s
            html = _edit_svg(html, 's2-10', 1, f, rep)
    if name in ('part03.html', None):
        html = fit_rrow(html, 's3-7', rep)
        if lang == 'de':   # the long German 360° note did not fit beside the exercise and fell onto the 3.12 opener
            html = move_note_before(html, 's3-11', 'dünnbeiniges Stativ', '<ol class="rule">', rep)
    if name in ('feature_storyboard.html', None):
        html = fit_rrow(html, 'f-sb-ratio', rep)
    if name in ('part04.html', None):
        def g(s):
            k, v = S4_2_BACK[lang]
            s = wrap(s, k, v, 9.5, rep, 's4-2')
            if lang == 'ru':
                s = wrap(s, 'Напротив рисующего · ½–¼ от рисующего', ['Напротив рисующего ·', '½–¼ от рисующего'], 9.5, rep, 's4-2')
            return s
        html = _edit_svg(html, 's4-2', 0, g, rep)
    if name in ('part12.html', None):
        html = _edit_svg(html, 's12-8', 0, lambda s: s12_8_svg(S12_8[lang]), rep)
        html = _edit_svg(html, 's12-2', 0, lambda s: s12_2_svg(S12_2[lang]), rep)

        def h(s):
            for k, v in S12_10[lang].items():
                s = wrap(s, k, v, 10, rep, 's12-10')
            # skills take two lines: Education and everything below move down 9 units; in German and Russian the
            # first summary line wraps as well, so everything from the second summary line to the awards moves 10 more
            def f(m):
                v = float(m.group(2)); d = 9 if v >= 265 else 0
                if lang != 'en' and 97 <= v < 370:
                    d += 10
                return f'{m.group(1)}="{v + d:g}"' if d else m.group(0)
            return re.sub(r'\b(y|y1|y2)="([\d.]+)"', f, s)
        html = _edit_svg(html, 's12-10', 0, h, rep)
    html = rules_apply(html, name, lang, rep)
    return html, rep


# ====================================================================== rule engine for small per-figure fixes
from tw import tw as _tw


def _regions(html, fig_id):
    i = html.find(f'id="{fig_id}"')
    if i < 0:
        return None
    nxt = re.compile(r'id="(?:s\d|f-|tpl-)[^"]*"').search(html, i + 5)
    return i, (nxt.start() if nxt else len(html))


def _text_re(content):
    return re.compile(r'<text([^>]*)>' + re.escape(escape(content, quote=False)) + r'</text>')


def _set_attrs(attrs, changes):
    for k, v in changes.items():
        if re.search(r'\s' + re.escape(k) + r'="[^"]*"', attrs):
            attrs = re.sub(r'(\s' + re.escape(k) + r'=")[^"]*(")', lambda m: m.group(1) + str(v) + m.group(2), attrs, count=1)
        else:
            attrs += f' {k}="{v}"'
    return attrs


def op_attr(svg, content, changes):
    m = _text_re(content).search(svg)
    if not m:
        return svg, False
    return svg[:m.start()] + f'<text{_set_attrs(m.group(1), changes)}>' + svg[m.end() - len('</text>') - len(escape(content, quote=False)):], True


def op_text(svg, old, new):
    m = _text_re(old).search(svg)
    if not m:
        return svg, False
    return svg[:m.start()] + f'<text{m.group(1)}>{escape(new, quote=False)}</text>' + svg[m.end():], True


def op_wrap(svg, content, lines, dy, changes=None):
    m = _text_re(content).search(svg)
    if not m:
        return svg, False
    attrs = _set_attrs(m.group(1), changes or {})
    x = re.search(r'\bx="([^"]+)"', attrs).group(1)
    spans = ''.join('<tspan x="%s"%s>%s</tspan>' % (x, '' if i == 0 else ' dy="%s"' % dy, escape(l, quote=False)) for i, l in enumerate(lines))
    return svg[:m.start()] + f'<text{attrs}>{spans}</text>' + svg[m.end():], True


def op_sub(svg, old, new):
    if old not in svg:
        return svg, False
    return svg.replace(old, new), True


def op_vbh(svg, old_h, new_h):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m or float(m.group(2)) != float(old_h):
        return svg, False
    w = m.group(1)
    svg = svg.replace(m.group(0), f'viewBox="0 0 {w} {new_h:g}"', 1)
    svg = re.sub(r'(<rect width="%s" height=")%s(")' % (re.escape(w), re.escape(m.group(2))), lambda mm: mm.group(1) + f'{new_h:g}' + mm.group(2), svg, count=1)
    return svg, True


OPS = {'attr': op_attr, 'text': op_text, 'wrap': op_wrap, 'sub': op_sub, 'vbh': op_vbh}
L3 = ('en', 'de', 'ru')


def _per(en, de, ru):
    return {'en': en, 'de': de, 'ru': ru}


RULES = []


def R(part, fig, langs, op, *args, nth=None, all_=False):
    RULES.append(dict(part=part, fig=fig, langs=langs, op=op, args=args, nth=nth, all_=all_))


def RL(part, fig, op, per, *rest, nth=None, all_=False):
    """per-language first argument"""
    for l, a in per.items():
        if a is not None:
            R(part, fig, (l,), op, a, *rest, nth=nth, all_=all_)


# s0-2 resolution boxes: the HD label sits half outside its dark box -> dark text
R('prologue.html', 's0-2', L3, 'attr', 'HD 1280×720', {'fill': '#1B1B1D'})
# s2-10: white text on the light 4.5 s pill
RL('part02.html', 's2-10', 'attr', _per('4.5 s', '4,5 s', '4,5 с'), {'fill': '#1B1B1D'})
# s4-2: camera label beside the camera (below it, it collided with the key-light note and had to shrink to ~60 %)
R('part04.html', 's4-2', ('ru',), 'vbh', 230, 240, nth=0)
RL('part04.html', 's4-2', 'attr', _per('Camera', 'Kamera', 'Камера'), {'x': '178', 'y': '211', 'text-anchor': 'start'}, nth=0)
# s4-3: descenders of the bottom labels were cut by the viewBox
R('part04.html', 's4-3', L3, 'vbh', 120, 124, all_=True)
# s4-8: danger note in two lines, second row lower; Russian dialogue note in two lines
R('part04.html', 's4-8', ('en',), 'wrap', "Danger — touch 0 and it's gone", ['Danger — touch 0', "and it's gone"], 9.5)
R('part04.html', 's4-8', ('de',), 'wrap', 'Gefahr – bei 0 ist es verloren', ['Gefahr – bei 0', 'ist es verloren'], 9.5)
R('part04.html', 's4-8', ('ru',), 'wrap', 'Опасно — коснётесь 0, и звук потерян', ['Опасно — коснётесь 0,', 'и звук потерян'], 9.5)
for t in (_per('Quiet parts · room tone', 'Leise Stellen · Raumton', 'Тихие места · фон помещения'),
          _per('Peak zone allowed', 'Spitzen erlaubt', 'Допустимая зона пиков')):
    RL('part04.html', 's4-8', 'attr', t, {'y': '104'})
R('part04.html', 's4-8', ('ru',), 'wrap', 'Реплики: в среднем от −18 до −12', ['Реплики: в среднем', 'от −18 до −12'], 9.5)
# s4-9: hook subtitle fits its box, long narration lines in two lines, sound-logo label in two lines (ru),
# and the closing sentence (it lay outside the viewBox) becomes visible in two lines
R('part04.html', 's4-9', ('en',), 'text', 'Stop them in the first 3 seconds', 'Stop them in 3 seconds')
R('part04.html', 's4-9', ('de',), 'text', 'In den ersten 3 Sekunden fesseln', 'In 3 Sekunden fesseln')
R('part04.html', 's4-9', ('ru',), 'text', 'Остановить за первые 3 секунды', 'Зацепить за 3 секунды')
R('part04.html', 's4-9', ('de',), 'wrap', 'Auch heute, Marke', ['Auch heute,', 'Marke'], 9, {'y': '69.5', 'font-size': '8'})
R('part04.html', 's4-9', ('ru',), 'wrap', 'Ваш день начинается', ['Ваш день', 'начинается'], 9, {'y': '69.5', 'font-size': '8'})
R('part04.html', 's4-9', ('ru',), 'wrap', 'И сегодня — Бренд', ['И сегодня —', 'Бренд'], 9, {'y': '69.5', 'font-size': '8'})
R('part04.html', 's4-9', ('ru',), 'wrap', 'Звуковой логотип', ['Звуковой', 'логотип'], 10, {'y': '202'})
R('part04.html', 's4-9', L3, 'vbh', 250, 284)
R('part04.html', 's4-9', ('en',), 'wrap', "When there's speech, the music comes down; when there isn't, the effects breathe. If all four layers are loud at once, nothing is heard.",
  ["When there's speech, the music comes down; when there isn't, the effects breathe.", 'If all four layers are loud at once, nothing is heard.'], 12.5)
R('part04.html', 's4-9', ('de',), 'wrap', 'Wenn gesprochen wird, geht die Musik zurück; wenn nicht, atmen die Effekte. Sind alle vier Ebenen gleichzeitig laut, hört man nichts.',
  ['Wenn gesprochen wird, geht die Musik zurück; wenn nicht, atmen die Effekte.', 'Sind alle vier Ebenen gleichzeitig laut, hört man nichts.'], 12.5)
R('part04.html', 's4-9', ('ru',), 'wrap', 'Когда звучит речь, музыка уходит вниз; когда речи нет, дышат эффекты. Если все четыре слоя громкие одновременно, не слышно ничего.',
  ['Когда звучит речь, музыка уходит вниз; когда речи нет, дышат эффекты.', 'Если все четыре слоя громкие одновременно, не слышно ничего.'], 12.5)
# s4-6 (ru): the magenta-gel note was shrunk to 64 %
R('part04.html', 's4-6', ('ru',), 'text', 'Пурпурный фильтр — гасит зелёный спилл', 'Пурпурный фильтр от спилла')
# s6-14: interviewer label beside its dot, interviewee label beside the subject (no dashed line through it)
RL('part06.html', 's6-14', 'attr', _per('Interviewer', 'Interviewer', 'Интервьюер'), {'x': '106', 'y': '171', 'text-anchor': 'end'})
RL('part06.html', 's6-14', 'attr', _per('Interviewee', 'Befragter', 'Герой'), {'x': '166', 'y': '84', 'text-anchor': 'start'})
# s7-5: the viewer dot is large enough for its label; German "Sie" (like Russian "Вы")
R('part07.html', 's7-5', L3, 'sub', '<circle cx="280" cy="292" r="14" fill="#7A1C2B"/>', '<circle cx="280" cy="292" r="16" fill="#7A1C2B"/>')
R('part07.html', 's7-5', ('de',), 'text', 'Betrachter', 'Sie')
# s8-2: dark text on the light middle segment; German/Russian bold note in two lines
RL('part08.html', 's8-2', 'attr', _per('Development — problem → product → in use', 'Hauptteil – Problem → Produkt → Anwendung', 'Развитие — проблема → продукт → в деле'), {'fill': '#1B1B1D'})
R('part08.html', 's8-2', ('de',), 'wrap', 'Zwei Türen, durch die Zuschauer gehen: 1,5 s (Scrollen) und 6 s (Überspringen-Button). Setzen Sie vor die erste Tür einen Kniff, vor die zweite ein Versprechen.',
  ['Zwei Türen, durch die Zuschauer gehen: 1,5 s (Scrollen) und 6 s (Überspringen-Button).', 'Setzen Sie vor die erste Tür einen Kniff, vor die zweite ein Versprechen.'], 11.5, {'y': '112'})
R('part08.html', 's8-2', ('de',), 'attr', 'Gehen Sie bei Kurzvideos im Hochformat davon aus, dass 0–1,5 s über alles entscheiden, und zeigen Sie ab 0 s eine Zeile Untertitel.', {'y': '138'})
R('part08.html', 's8-2', ('ru',), 'wrap', 'Две двери, через которые уходит зритель: 1,5 с (прокрутка) и 6 с (кнопка «Пропустить»). Перед первой дверью поставьте приём, перед второй — обещание.',
  ['Две двери, через которые уходит зритель: 1,5 с (прокрутка) и 6 с (кнопка «Пропустить»).', 'Перед первой дверью поставьте приём, перед второй — обещание.'], 11.5, {'y': '112'})
R('part08.html', 's8-2', ('ru',), 'attr', 'В вертикальных коротких видео считайте, что всё решают 0–1,5 с, и держите на экране одну строку титров с нулевой секунды.', {'y': '138'})
# s8-3: last funnel step in wine (white text on the pale step ran over its edges), metrics in two lines, note full width
RL('part08.html', 's8-3', 'attr', _per('Conversion', 'Conversion', 'Конверсия'), {'fill': '#7A1C2B', 'font-size': '11'})
S8_3 = {'en': {'Clicks · saves · shares': ['Clicks · saves ·', 'shares'], 'Purchases · conversion rate · CPA': ['Purchases · CPA ·', 'conversion rate']},
        'de': {'Reichweite · Aufrufe': ['Reichweite ·', 'Aufrufe'], 'Klicks · Speichern · Teilen': ['Klicks ·', 'Speichern · Teilen'],
               'Käufe · Conversion-Rate · CPA': ['Käufe · CPA ·', 'Conversion-Rate']},
        'ru': {'Охват · просмотры': ['Охват ·', 'просмотры'], 'Ср. время просмотра': ['Ср. время', 'просмотра'],
               'Клики · сохранения · репосты': ['Клики · репосты ·', 'сохранения'], 'Покупки · конверсия · CPA': ['Покупки · CPA ·', 'конверсия']}}
for l, d in S8_3.items():
    for k, v in d.items():
        R('part08.html', 's8-3', (l,), 'wrap', k, v, 10, {'_dy0': '-5'})
RL('part08.html', 's8-3', 'attr', _per('Top: many · short, bottom: few · long — no single video does all four stages.',
                                       'Oben: viele · kurz, unten: wenige · lang – kein einzelnes Video schafft alle vier Stufen.',
                                       'Вверху: много · коротко, внизу: мало · длинно — ни одно видео не закроет все четыре этапа.'), {'x': '14'})
# s11-4: light block label in dark text; the two narrow blocks get two-line notes
RL('part11.html', 's11-4', 'attr', _per('Main C', 'Teil C', 'Блок C'), {'fill': '#1B1B1D'})
for l, d in {'en': {'Interview · doc — a breather': ['Interview · doc —', 'a breather'], 'Best cut again + name · contact': ['Best cut again +', 'name · contact']},
             'de': {'Interview · Doku – Atempause': ['Interview · Doku –', 'Atempause'], 'Bester Clip erneut + Name · Kontakt': ['Bester Clip erneut', '+ Name · Kontakt']},
             'ru': {'Интервью · док — передышка': ['Интервью · док —', 'передышка'], 'Лучший кадр + имя · контакты': ['Лучший кадр +', 'имя · контакты']}}.items():
    for k, v in d.items():
        R('part11.html', 's11-4', (l,), 'wrap', k, v, 9.5)
# f-lt-modifier (ru): headings in two lines instead of 58 % type
R('feature_lighting.html', 'f-lt-modifier', ('ru',), 'wrap', 'Малый источник · далеко → жёстко', ['Малый источник ·', 'далеко → жёстко'], 10, {'y': '91', 'x': '75'})
# left panel labels further from the edge, so they keep the size of the right ones
RL('feature_lighting.html', 'f-lt-modifier', 'attr', _per('Small source · far → hard', 'Kleine Quelle · weit → hart', None), {'x': '75'})
RL('feature_lighting.html', 'f-lt-modifier', 'attr', _per('Razor-sharp shadow edge', 'Messerscharfe Schattenkante', 'Очень резкий край тени'), {'x': '75'})
R('feature_lighting.html', 'f-lt-modifier', ('ru',), 'wrap', 'Большой источник · близко → мягко', ['Большой источник ·', 'близко → мягко'], 10, {'y': '91'})
# f-ppm (ru): shorter title so the 50× label keeps its size
R('feature_ppm.html', 'f-ppm', ('ru',), 'text', 'Одно и то же изменение может стоить до 50 раз дороже — смотря когда его внести',
  'Изменение может стоить до 50 раз дороже — всё решает момент')
# f-ppm-location: camera C2 label above the camera (it collided with the longer tube-light label)
R('feature_ppm.html', 'f-ppm-location', ('de', 'ru'), 'attr', 'C2 · 03', {'y': '114'})
R('feature_ppm.html', 'f-ppm-location', ('ru',), 'sub', '<text x="312" y="54">K Рисующий LED 600 Вт</text>',
  '<text x="312" y="49">K Рисующий<tspan x="320.7" dy="11">LED 600 Вт</tspan></text>')
R('feature_ppm.html', 'f-ppm-location', ('ru',), 'attr', 'Лестница', {'font-size': '7'})
# s4-8: closing sentence a little lower (the second label row moved down); Russian in two lines
R('part04.html', 's4-8', ('en', 'de'), 'vbh', 120, 126)
R('part04.html', 's4-8', ('en',), 'attr', 'By the peak meter — dialogue dances around −12 and never passes −6. Digital audio is cut off the moment it passes 0 (clipping).', {'y': '122'})
R('part04.html', 's4-8', ('de',), 'attr', 'Gemessen am Spitzenpegel – Dialog pendelt um −12 und überschreitet nie −6. Digitaler Ton wird abgeschnitten, sobald er 0 überschreitet (Clipping).', {'y': '122'})
R('part04.html', 's4-8', ('ru',), 'vbh', 120, 137)
R('part04.html', 's4-8', ('ru',), 'wrap', 'По пиковому индикатору: реплики пляшут около −12 и никогда не заходят за −6. Цифровой звук обрезается в тот же миг, как переходит 0 (клиппинг).',
  ['По пиковому индикатору: реплики пляшут около −12 и никогда не заходят за −6.', 'Цифровой звук обрезается в тот же миг, как переходит 0 (клиппинг).'], 11.5, {'y': '122'})
# s4-6 (ru): fill-light label in two lines
R('part04.html', 's4-6', ('ru',), 'wrap', 'Заполняющий (отражатель)', ['Заполняющий', '(отражатель)'], 11, {'y': '228'})
# s8-7 (de): shorter CC note
R('part08.html', 's8-7', ('de',), 'text', '„Kostenlos“ und „kommerzielle Nutzung erlaubt“ sind zweierlei – lesen Sie die 4 Bedingungen in Kombination',
  '„Kostenlos“ und „kommerziell nutzbar“ sind zweierlei – lesen Sie die 4 Bedingungen zusammen')
# templates: the note under each template sheet lost its descenders at the bottom edge
for _i in range(1, 9):
    R('templates.html', f'tpl-{_i}', L3, 'sub', '<text x="0" y="1178" font-size="8"', '<text x="0" y="1175" font-size="8"')


def rules_apply(html, name, lang, rep):
    for r in RULES:
        if lang not in r['langs'] or (name is not None and r['part'] != name):
            continue
        reg = _regions(html, r['fig'])
        if not reg:
            rep.append(f"{r['fig']}: figure not found"); continue
        a0, b0 = reg
        spans = []
        k = html.find('<svg', a0)
        while 0 <= k < b0:
            j = html.find('</svg>', k) + 6
            spans.append((k, j)); k = html.find('<svg', j)
        if r['nth'] is not None:
            spans = spans[r['nth']:r['nth'] + 1]
        done = False
        for a, b in reversed(spans):
            svg = html[a:b]
            args = list(r['args'])
            if r['op'] == 'wrap' and len(args) >= 4 and args[3] and '_dy0' in args[3]:
                ch = dict(args[3]); dy0 = float(ch.pop('_dy0'))
                m = _text_re(args[0]).search(svg)
                if m:   # first line moves up so the block stays centred on the old baseline
                    y0 = float(re.search(r'\by="([^"]+)"', m.group(1)).group(1))
                    ch['y'] = '%g' % (y0 + dy0)
                args[3] = ch
            new, ok = OPS[r['op']](svg, *args)
            if ok:
                html = html[:a] + new + html[b:]
                done = True
                if not r['all_']:
                    break
        if not done:
            rep.append(f"{r['fig']}/{lang}: {r['op']} {str(r['args'][0])[:40]!r} not applied")
    return html

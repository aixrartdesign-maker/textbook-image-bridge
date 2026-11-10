# Translating the text inside the book's diagrams

The textbook "Video Production: A Practical Textbook" has 40 explanatory diagrams (PNG images) whose text is English.
Each diagram will be re-lettered: the English text is removed and your translation is typeset in the same place,
same font, weight, colour and size. Your job is the wording. The translation is printed as is, so it must be free of
typos and grammar errors, and it has to fit the space.

## Input
For every diagram there is a task file `tasks/<stem>.json`:
```
{"stem": "...", "image": "/abs/path/EN-<stem>.png",
 "elements": [{"id": "7", "en": "Overcast window light · low contrast", "role": "label",
               "fits": {"chars_per_line_now": 36, "chars_per_line_max": 44, "chars_per_line_if_shrunk": 54,
                        "lines_now": 1, "lines_max": 1}}, ...]}
```
- `en` is the English text as printed in the image (separators like " · " and " — " are part of it).
- `fits` describes the space: the English uses `chars_per_line_now` characters per line on `lines_now` lines.
  A line can hold about `chars_per_line_max` characters at the same type size, and about `chars_per_line_if_shrunk`
  if the renderer shrinks the type to 82 % (allowed, but less nice). More lines than `lines_max` do not fit.
  The numbers are estimates in characters; capital letters and W/M/Ш/Щ/Ж/Ю are wider than average.
- Always open the image with the Read tool before translating it: the picture shows what each label refers to
  (an axis end, a column heading, a step in a flow…), which decides the right word and grammatical form.

## Output
Write `tr_<lang>/<stem>.json` (lang = de or ru) with the Write tool, one file per diagram:
```
{"0": "translation of element 0", "1": "...", ...}
```
- One entry for every element id of the task file, nothing else. Valid JSON, UTF-8, no comments.
- If an element must stay exactly as it is (a pure number, an acronym, a brand), repeat the English string unchanged.
- The renderer wraps text by itself where `lines_max` > 1. Put an explicit line break `\n` only if a particular
  break point matters (e.g. a two-line heading that must break after a specific word); otherwise do not use `\n`.

## Rules
1. Same terminology as the book. Read the "Fixed terms" and "Typography" sections of
   `/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/ml/INSTRUCTIONS_<LANG>.md`
   (DE or RU) and use exactly those terms (shot sizes, angles, roles, stages of production, etc.).
2. Fit first: prefer the shortest natural wording that keeps the meaning. Labels and table cells are terse
   (noun phrases, no articles in German labels unless natural, infinitive or noun style in lists). Captions and titles
   can be full sentences but must stay within `chars_per_line_max` × `lines_max`. Use standard abbreviations when
   needed (DE: z. B., ca., max., min., Min., Std., Abb.; RU: напр., ок., макс., мин., с, мин, ч). Never truncate words.
3. Keep the structure of the English string: separators " · ", " — ", "→", "+", "=", numbering, parentheses.
4. Numbers: decimal comma (DE/RU) — 2,39 : 1, f/2,8, 0,04–0,1 s; ranges with an en dash and no spaces (50–85);
   a space between number and unit: DE 50–85 mm, 4–6 s, 30 m, 2 Min.; RU 50–85 мм, 4–6 с, 30 м, 2 мин;
   percent with a space: 50 %. Years, ratios like 16:9, resolutions (4K, FHD+) and acronyms stay as they are.
   Keep the exact spacing of ratios as printed (e.g. "2.39 : 1" → "2,39 : 1").
5. Capitalisation: German nouns capitalised, otherwise sentence case; Russian sentence case. Keep ALL CAPS only for
   acronyms. Keep sentence-final punctuation as in the English (usually none in labels).
6. Quotation marks: DE „…“, RU «…».
7. Russian: Cyrillic everywhere except acronyms/brands/codes (ELS, LS, CU, PPM, VFX, LED, XR, 4K, YouTube…);
   use ё consistently; correct case/gender agreement with the noun the label describes.
8. Elements that are parts of one picture must read consistently (e.g. the two ends of an axis: "Kalt"/"Warm";
   "Холодный"/"Тёплый"; list items in the same grammatical form).

## When done
Check every file you wrote: valid JSON (run `python3 -c "import json,sys; [json.load(open(f)) for f in sys.argv[1:]]" tr_<lang>/*.json`
on your files), every id present, no English left where a translation is needed, no typos.
Reply with one line per diagram: `<stem>: N elements` and, if any, the ids where you could not fit the meaning into the
space (with a short note).

# Proofreading a translated textbook batch (German or Russian)

You are the final proofreader of a printed textbook ("Video Production: A Practical Textbook", translated from English).
The text will be printed exactly as it is. Your job is to find and fix real errors — not to restyle.

## Input
- Source batch: `ml/batches/bNN.json` — array of {"key", "en"} (HTML fragments).
- Translation: `ml/out_<lang>/bNN_p*.json` — arrays of {"key", "<lang>"} (same keys, same order).
- Style guide with fixed terms and typography: `ml/INSTRUCTIONS_<LANG>.md` (DE or RU). Read it first.
(All paths are relative to /tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/.)

Read source and translation side by side, in order, in parts (e.g. 100 items at a time).

## What to fix (only these)
1. Typos, misspellings, wrong letters, doubled or missing words, wrong ё/е (RU: ё must be used consistently), ß/ss (DE).
2. Grammar: case, gender, number, agreement, verb forms, word order errors; wrong prepositions.
3. Mistranslations: meaning differs from the English, a sentence or clause missing, numbers or units changed.
4. English left untranslated where it should be translated (names of products/brands/works, acronyms and template
   labels like SIZE, MOVE, CUT legitimately stay).
5. Terminology that contradicts the fixed terms of the style guide, or the same thing named differently in
   neighbouring items.
6. Typography rules of the style guide: quotation marks (DE „…“, RU «…»), dashes (DE " – ", RU " — "), decimal comma,
   space before units and %, thousands separators, sentence-final punctuation consistent with the English.
7. Broken HTML: tags must be identical to the English item (same tags, same order, same attributes). Never change tags.

Do NOT report: stylistic preferences, synonyms that are equally correct, word order that is correct, sentence length.

## Output
Write ONE file with the Write tool: `ml/proof_<lang>/bNN.json` — a JSON array of corrections:
```
[{"key": "part02.html#17", "find": "exact substring of the current translation", "replace": "corrected substring", "why": "typo"}]
```
- `find` must occur exactly once in that item's current translation (include enough context to make it unique);
  keep it short (the smallest unique span containing the error).
- `replace` is the corrected text for that span. Keep all HTML tags/entities inside the span unchanged.
- `why` is one of: typo, grammar, meaning, untranslated, term, typography, other (+ a few words).
- If an item is badly wrong overall, you may use the whole item text as `find` and give the full corrected item.
- Empty array `[]` if the batch is clean.

Then run: `python3 ml/apply_proof.py <lang> NN --check` — it verifies that every `find` occurs exactly once and that
tags are preserved; fix any entry it rejects. Reply with one line: `bNN: N corrections (typo X, grammar Y, …)`.

Video Production: A Practical Textbook — English edition sources v2.1

Changes in v2.1
- The build now pads the end of the book with NOTE pages to a multiple of 8 pages (the printer imposes in 8-page
  signatures; the count includes the covers: p1 front cover, last page back cover). The PDF is unchanged:
  v2 already has 560 pages = 8 x 70, and part openers stay on odd pages.

Changes from v1 to v2
- Figures corrected: crumb "PART 07–08 wrap-up" (was 07–09), 8K resolution 7680×4320 (was 7680×2160),
  youth-employment chart (labels were hidden behind the bars, captions cut off), one-page CV sample (lines ran out of the page),
  storyboard aspect-ratio rows (photos were stretched), generative-loop pipeline (white text ran outside its boxes),
  sound-timeline closing sentence (was outside the figure), funnel metrics, small labels that had to shrink, minus signs.
- The page now renders at the designed 100 % size. In v1 one figure (aspect-ratio row, 3.7) was 8 mm wider than the text block,
  so the browser shrank every page to 95 %; this edition has 560 pages (v1: 540).
  The author's note was tightened by a few words (tools/en_fix_parts.py, COPYFIT) so it still fits on one page.

book_en/          typesetting sources (English HTML parts, CSS, build script)
book_en/img_en    the 40 diagrams re-lettered in English
tools/            figure fixes applied to the parts (figfix.py, en_fix_parts.py) and the QA scripts used for this edition

Photos and illustrations shared with the Korean edition are not duplicated here:
extract the Korean source package (v9.6) next to this one and point book_en/img -> book/img
and book_en/img_new -> book/img_new before building.
Build: in book_en/, run  python3 build_en.py   then   python3 tools/finalize_pdf.py book_en <out.pdf> "<title>" "<author>"
(Playwright/Chromium, pdftotext, pypdf; fonts Lora + Inter + Noto CJK)

Videoproduktion: Ein Praxislehrbuch — German edition sources v1.1

v1.1: four more NOTIZEN pages at the end, so that the whole PDF (covers included) is a multiple of 8 pages for the
printer's 8-page signatures: 596 -> 600 pages. Text, figures, page numbers and part openers (all on odd pages) are
unchanged. build_ml.py now pads to a multiple of 8 (SIG=8).

book_de/parts       the German HTML parts (assembled from the translation memory below)
book_de/img_de      the 40 diagrams re-lettered in German
build/              build script (build_ml.py + lang_strings.py) and finalize_pdf.py
translation/        translation memory (out_de/*.json: key -> German), fixed strings, figure-label localisation,
                    figure layout fixes, assembly, validation and spell-check scripts
diagrams/           re-lettering tools for the diagrams (inventory, translations tr_de/, manual fixes, overrides)

Conventions: „…“ quotes, spaced en dash ( – ), decimal comma, 50 %, formal address (Sie).
Photos shared with the Korean edition are not duplicated: extract the Korean source package (v9.6) next to this one and
point book_de/img -> book/img and book_de/img_new -> book/img_new; the English sources (book_en) supply the skeleton.
Build: python3 translation/assemble.py de ; python3 build/build_ml.py de ; python3 build/finalize_pdf.py book_de <out.pdf> "<title>" "<author>"

Видеопроизводство: практический учебник — Russian edition sources v1.1

v1.1: four more ЗАМЕТКИ pages at the end, so that the whole PDF (covers included) is a multiple of 8 pages for the
printer's 8-page signatures: 604 -> 608 pages. Text, figures, page numbers and part openers (all on odd pages) are
unchanged. build_ml.py now pads to a multiple of 8 (SIG=8).

book_ru/parts       the Russian HTML parts (assembled from the translation memory below)
book_ru/img_ru      the 40 diagrams re-lettered in Russian
build/              build script (build_ml.py + lang_strings.py) and finalize_pdf.py
translation/        translation memory (out_ru/*.json: key -> Russian), fixed strings, figure-label localisation,
                    figure layout fixes, assembly, validation and spell-check scripts
diagrams/           re-lettering tools for the diagrams (inventory, translations tr_ru/, manual fixes, overrides)

Conventions: «…» quotes (inner „…“), spaced em dash ( — ), decimal comma, 12 000, ё used consistently, address with «вы».
Photos shared with the Korean edition are not duplicated: extract the Korean source package (v9.6) next to this one and
point book_ru/img -> book/img and book_ru/img_new -> book/img_new; the English sources (book_en) supply the skeleton.
Build: python3 translation/assemble.py ru ; python3 build/build_ml.py ru ; python3 build/finalize_pdf.py book_ru <out.pdf> "<title>" "<author>"

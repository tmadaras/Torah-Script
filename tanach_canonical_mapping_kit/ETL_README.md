
# Canonical Mapping ETL — 39 → 24, Per-Token

Inputs: OSHB (tokens+lemma+Strong), BHSA (root/features), paleo_reference (paleo data), books_39_to_24.csv.

Steps:
1) Load books_39_to_24.csv → books_map_39_to_24.
2) Extract OSHB → oshb_tokens(source_book_39, chapter, verse, position, hebrew_surface, hebrew_lemma, strong_number).
3) Join BHSA features to get root; join paleo_reference by (book/chapter/verse/position) else fallback by (lemma/root).
4) Map source_book_39 → canon_book_24 (use table).
5) Copy chapter/verse/position to canon_* unless a custom resequence is desired.
6) Compute benner_mechanical → final_mech via rules; store compiled_definitions and decision_notes.
7) Insert into tanach_canonical_map; ensure uq_source and uq_canon hold.
Validation: run qa_sql.sql → all zeros.

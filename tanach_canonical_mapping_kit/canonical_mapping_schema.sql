
BEGIN;
CREATE TABLE IF NOT EXISTS books_map_39_to_24 (
  source_book_39 TEXT PRIMARY KEY,
  canon_book_24  TEXT NOT NULL,
  canon_section  TEXT NOT NULL,
  notes          TEXT
);
CREATE TABLE IF NOT EXISTS tanach_canonical_map (
  id BIGSERIAL PRIMARY KEY,
  source_book_39 TEXT NOT NULL,
  source_chapter INT NOT NULL,
  source_verse   INT NOT NULL,
  source_word_position INT NOT NULL,
  canon_book_24 TEXT NOT NULL,
  canon_chapter INT NOT NULL,
  canon_verse   INT NOT NULL,
  canon_word_position INT NOT NULL,
  hebrew_surface TEXT NOT NULL,
  hebrew_lemma   TEXT NOT NULL,
  paleo_hebrew   TEXT,
  pictographic_paleo TEXT,
  transliteration_sbl TEXT,
  root TEXT,
  root_definition_concrete TEXT,
  benner_mechanical TEXT,
  final_mech TEXT,
  english_word_final TEXT,
  compiled_definitions TEXT,
  strong_number TEXT,
  bhsa_lexeme_id TEXT,
  decision_notes TEXT,
  review_status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_source UNIQUE (source_book_39, source_chapter, source_verse, source_word_position),
  CONSTRAINT uq_canon  UNIQUE (canon_book_24, canon_chapter, canon_verse, canon_word_position),
  CONSTRAINT chk_review CHECK (review_status IN ('approved','pending','needs_review'))
);
CREATE OR REPLACE FUNCTION tanach_canonical_map_touch() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at := NOW(); RETURN NEW; END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_tanach_canonical_map_touch ON tanach_canonical_map;
CREATE TRIGGER trg_tanach_canonical_map_touch BEFORE UPDATE ON tanach_canonical_map
FOR EACH ROW EXECUTE FUNCTION tanach_canonical_map_touch();
CREATE OR REPLACE VIEW v_tanach_canonical_tokens AS
SELECT
  canon_book_24 AS book,
  canon_chapter AS chapter,
  canon_verse AS verse,
  canon_word_position AS position,
  hebrew_surface,
  hebrew_lemma,
  paleo_hebrew,
  transliteration_sbl,
  final_mech,
  english_word_final,
  root, root_definition_concrete,
  strong_number, bhsa_lexeme_id
FROM tanach_canonical_map;
COMMIT;

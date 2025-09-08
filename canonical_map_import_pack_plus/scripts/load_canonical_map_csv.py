
import os, csv, sys, json
from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text

def load_schema(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def to_row_types(row):
    int_fields = ['source_chapter','source_verse','source_word_position','canon_chapter','canon_verse','canon_word_position']
    casted = {}
    for k,v in row.items():
        if k in int_fields:
            casted[k] = int(v) if v != '' else None
        else:
            casted[k] = v if v is not None else ''
    return casted

UPSERT_SQL = """
INSERT INTO tanach_canonical_map (
  source_book_39, source_chapter, source_verse, source_word_position,
  canon_book_24, canon_chapter, canon_verse, canon_word_position,
  hebrew_surface, hebrew_lemma, paleo_hebrew, pictographic_paleo,
  transliteration_sbl, root, root_definition_concrete, benner_mechanical,
  final_mech, english_word_final, compiled_definitions, strong_number,
  bhsa_lexeme_id, decision_notes, review_status
) VALUES (
  :source_book_39, :source_chapter, :source_verse, :source_word_position,
  :canon_book_24, :canon_chapter, :canon_verse, :canon_word_position,
  :hebrew_surface, :hebrew_lemma, :paleo_hebrew, :pictographic_paleo,
  :transliteration_sbl, :root, :root_definition_concrete, :benner_mechanical,
  :final_mech, :english_word_final, :compiled_definitions, :strong_number,
  :bhsa_lexeme_id, :decision_notes, :review_status
)
ON CONFLICT (source_book_39, source_chapter, source_verse, source_word_position)
DO UPDATE SET
  canon_book_24=EXCLUDED.canon_book_24,
  canon_chapter=EXCLUDED.canon_chapter,
  canon_verse=EXCLUDED.canon_verse,
  canon_word_position=EXCLUDED.canon_word_position,
  hebrew_surface=EXCLUDED.hebrew_surface,
  hebrew_lemma=EXCLUDED.hebrew_lemma,
  paleo_hebrew=EXCLUDED.paleo_hebrew,
  pictographic_paleo=EXCLUDED.pictographic_paleo,
  transliteration_sbl=EXCLUDED.transliteration_sbl,
  root=EXCLUDED.root,
  root_definition_concrete=EXCLUDED.root_definition_concrete,
  benner_mechanical=EXCLUDED.benner_mechanical,
  final_mech=EXCLUDED.final_mech,
  english_word_final=EXCLUDED.english_word_final,
  compiled_definitions=EXCLUDED.compiled_definitions,
  strong_number=EXCLUDED.strong_number,
  bhsa_lexeme_id=EXCLUDED.bhsa_lexeme_id,
  decision_notes=EXCLUDED.decision_notes,
  review_status=EXCLUDED.review_status;
"""

def main(csv_path, schema_path, dry_run=False):
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('DATABASE_URL env var is required')
        return 2

    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)

    engine = create_engine(db_url, future=True)
    invalid = 0; total = 0
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, raw in enumerate(reader, start=2):
            total += 1
            row = to_row_types(raw)
            errs = sorted(validator.iter_errors(row), key=lambda e: e.path)
            if errs:
                invalid += 1
                print(f"Row {i}: INVALID")
                for e in errs:
                    print("  -", e.message, "at", list(e.path))
            else:
                rows.append(row)

    if invalid:
        print(f"\nFAILED: {invalid}/{total} rows invalid. Aborting load.")
        return 1

    if dry_run:
        print(f"DRY RUN: {len(rows)} rows valid. No DB changes made.")
        return 0

    with engine.begin() as conn:
        for r in rows:
            conn.execute(text(UPSERT_SQL), r)

    print(f"OK: {len(rows)} rows upserted into tanach_canonical_map.")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python load_canonical_map_csv.py <mapping.csv> <schema.json> [--dry-run]')
        sys.exit(2)
    dry = '--dry-run' in sys.argv
    sys.exit(main(sys.argv[1], sys.argv[2], dry))

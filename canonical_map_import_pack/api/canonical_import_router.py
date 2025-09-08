
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import csv, io, os, json
from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text

router = APIRouter(prefix='/admin/canonical', tags=['admin'])

def get_engine():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise HTTPException(500, 'DATABASE_URL not configured')
    return create_engine(db_url, future=True)

class ImportResult(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    dry_run: bool
    errors: list

@router.post('/import', response_model=ImportResult)
async def import_csv(file: UploadFile = File(...), dry_run: bool = Form(False)):
    schema_path = os.environ.get('CANONICAL_ROW_SCHEMA', 'schema/mapping_row.schema.json')
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except Exception as e:
        raise HTTPException(500, f'Cannot load schema: {e}')

    validator = Draft202012Validator(schema)

    content = await file.read()
    text_stream = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(text_stream)

    int_fields = {'source_chapter','source_verse','source_word_position','canon_chapter','canon_verse','canon_word_position'}
    rows = []
    errors = []
    total = 0
    for i, raw in enumerate(reader, start=2):
        total += 1
        row = {k: (int(v) if k in int_fields and v != '' else v) for k,v in raw.items()}
        errs = list(validator.iter_errors(row))
        if errs:
            errors.append({'row': i, 'messages': [e.message for e in errs], 'fields': [list(e.path) for e in errs]})
        else:
            rows.append(row)

    if dry_run:
        return ImportResult(total_rows=total, valid_rows=len(rows), invalid_rows=len(errors), dry_run=True, errors=errors)

    if errors:
        raise HTTPException(400, detail={'message':'Validation failed','errors':errors})

    engine = get_engine()
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

    with engine.begin() as conn:
        for r in rows:
            conn.execute(text(UPSERT_SQL), r)

    return ImportResult(total_rows=total, valid_rows=len(rows), invalid_rows=0, dry_run=False, errors=[])

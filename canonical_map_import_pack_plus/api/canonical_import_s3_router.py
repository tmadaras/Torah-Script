
from fastapi import APIRouter, HTTPException, Query
import os, io, csv, json, boto3
from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

router = APIRouter(prefix='/admin/canonical', tags=['admin'])

def get_engine():
    url = os.environ.get('DATABASE_URL')
    if not url: raise HTTPException(500, 'DATABASE_URL not configured')
    return create_engine(url, future=True)

def fetch_s3_object(url: str) -> bytes:
    p = urlparse(url)
    if p.scheme != 's3' or not p.netloc or not p.path:
        raise HTTPException(400, 'Invalid s3 url, expected s3://bucket/key')
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=p.netloc, Key=p.path.lstrip('/'))
    return obj['Body'].read()

@router.post('/import_s3')
def import_s3(url: str = Query(..., description='s3://bucket/key'), dry_run: bool = False):
    schema_path = os.environ.get('CANONICAL_ROW_SCHEMA', 'schema/mapping_row.schema.json')
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except Exception as e:
        raise HTTPException(500, f'Cannot load schema: {e}')

    validator = Draft202012Validator(schema)

    data = fetch_s3_object(url)
    reader = csv.DictReader(io.StringIO(data.decode('utf-8')))

    int_fields = {'source_chapter','source_verse','source_word_position','canon_chapter','canon_verse','canon_word_position'}
    rows = []; errors = []; total = 0
    for i, raw in enumerate(reader, start=2):
        total += 1
        row = {k: (int(v) if k in int_fields and v != '' else v) for k,v in raw.items()}
        errs = list(validator.iter_errors(row))
        if errs:
            errors.append({'row': i, 'messages': [e.message for e in errs]})
        else:
            rows.append(row)

    if dry_run:
        return {'total_rows': total, 'valid_rows': len(rows), 'invalid_rows': len(errors), 'errors': errors, 'dry_run': True}

    if errors:
        raise HTTPException(400, detail={'message': 'Validation failed', 'errors': errors})

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

    with get_engine().begin() as conn:
        for r in rows:
            conn.execute(text(UPSERT_SQL), r)

    return {'total_rows': total, 'valid_rows': len(rows), 'invalid_rows': 0, 'errors': [], 'dry_run': False}

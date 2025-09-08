
from scripts.validate_csv import validate_row, load_schema

def test_validate_row_ok():
    schema = load_schema('schema/mapping_row.schema.json')
    row = {
        'source_book_39':'Genesis','source_chapter':'1','source_verse':'1','source_word_position':'1',
        'canon_book_24':'Bereshit','canon_chapter':'1','canon_verse':'1','canon_word_position':'1',
        'hebrew_surface':'ברא','hebrew_lemma':'ברא','paleo_hebrew':'','pictographic_paleo':'',
        'transliteration_sbl':'bara','root':'ברא','root_definition_concrete':'',
        'benner_mechanical':'cut/shape','final_mech':'carve/create',
        'english_word_final':'create','compiled_definitions':'','strong_number':'H1254',
        'bhsa_lexeme_id':'','decision_notes':'','review_status':'approved'
    }
    casted, errs = validate_row(row, schema)
    assert not errs

def test_validate_row_bad():
    schema = load_schema('schema/mapping_row.schema.json')
    row = {k:'' for k in [
        'source_book_39','source_chapter','source_verse','source_word_position',
        'canon_book_24','canon_chapter','canon_verse','canon_word_position',
        'hebrew_surface','hebrew_lemma','transliteration_sbl','root','final_mech','english_word_final','review_status'
    ]}
    casted, errs = validate_row(row, schema)
    assert errs

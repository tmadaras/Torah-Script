
import io, csv
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.canonical_import_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def build_csv(rows):
    import io, csv
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=[
        'source_book_39','source_chapter','source_verse','source_word_position',
        'canon_book_24','canon_chapter','canon_verse','canon_word_position',
        'hebrew_surface','hebrew_lemma','paleo_hebrew','pictographic_paleo',
        'transliteration_sbl','root','root_definition_concrete','benner_mechanical',
        'final_mech','english_word_final','compiled_definitions','strong_number',
        'bhsa_lexeme_id','decision_notes','review_status'
    ])
    writer.writeheader()
    for r in rows: writer.writerow(r)
    return buf.getvalue().encode('utf-8')

def test_import_dry_run_valid(monkeypatch):
    rows = [{
        'source_book_39':'Genesis','source_chapter':'1','source_verse':'1','source_word_position':'1',
        'canon_book_24':'Bereshit','canon_chapter':'1','canon_verse':'1','canon_word_position':'1',
        'hebrew_surface':'ברא','hebrew_lemma':'ברא','paleo_hebrew':'','pictographic_paleo':'',
        'transliteration_sbl':'bara','root':'ברא','root_definition_concrete':'',
        'benner_mechanical':'cut/shape','final_mech':'carve/create',
        'english_word_final':'create','compiled_definitions':'','strong_number':'H1254',
        'bhsa_lexeme_id':'','decision_notes':'','review_status':'approved'
    }]
    files = {'file': ('test.csv', build_csv(rows), 'text/csv')}
    resp = client.post('/admin/canonical/import', data={'dry_run':'true'}, files=files)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload['dry_run'] is True
    assert payload['invalid_rows'] == 0

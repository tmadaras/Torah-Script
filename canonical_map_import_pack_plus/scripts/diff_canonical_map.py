
import os, sys, csv, json
from collections import namedtuple, defaultdict
from sqlalchemy import create_engine, text

KEY = ('source_book_39','source_chapter','source_verse','source_word_position')

COMPARE_FIELDS = [
  'canon_book_24','canon_chapter','canon_verse','canon_word_position',
  'hebrew_surface','hebrew_lemma','paleo_hebrew','pictographic_paleo',
  'transliteration_sbl','root','root_definition_concrete','benner_mechanical',
  'final_mech','english_word_final','compiled_definitions','strong_number',
  'bhsa_lexeme_id','decision_notes','review_status'
]

def load_csv(path):
    out = {}
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            key = tuple(row[k] for k in KEY)
            out[key] = row
    return out

def fetch_db(engine):
    sql = text("""
      SELECT source_book_39, source_chapter::text, source_verse::text, source_word_position::text,
             canon_book_24, canon_chapter::text, canon_verse::text, canon_word_position::text,
             hebrew_surface, hebrew_lemma, paleo_hebrew, pictographic_paleo,
             transliteration_sbl, root, root_definition_concrete, benner_mechanical,
             final_mech, english_word_final, compiled_definitions, strong_number,
             bhsa_lexeme_id, decision_notes, review_status
      FROM tanach_canonical_map
    """)
    out = {}
    with engine.begin() as conn:
        for row in conn.execute(sql):
            row = dict(row._mapping)
            key = tuple(row[k] for k in KEY)
            out[key] = row
    return out

def diff_rows(old, new):
    changes = {}
    for f in COMPARE_FIELDS:
        if (old.get(f) or '') != (new.get(f) or ''):
            changes[f] = {'old': old.get(f, ''), 'new': new.get(f, '')}
    return changes

def main(csv_path, out_json='diff_report.json', limit=50):
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('DATABASE_URL is required'); return 2
    engine = create_engine(db_url, future=True)
    csv_map = load_csv(csv_path)
    db_map = fetch_db(engine)

    added = []
    removed = []
    changed = []

    for k,row in csv_map.items():
        if k not in db_map:
            added.append({'key': k, 'row': row})
        else:
            ch = diff_rows(db_map[k], row)
            if ch:
                changed.append({'key': k, 'changes': ch})

    for k,row in db_map.items():
        if k not in csv_map:
            removed.append({'key': k})

    report = {
        'summary': {'added': len(added), 'changed': len(changed), 'removed': len(removed)},
        'samples': {
            'added': added[:limit],
            'changed': changed[:limit],
            'removed': removed[:limit]
        }
    }
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report['summary'], indent=2))
    print(f"Report written to {out_json}")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python diff_canonical_map.py <mapping.csv> [out.json]')
        sys.exit(2)
    out = sys.argv[2] if len(sys.argv) > 2 else 'diff_report.json'
    sys.exit(main(sys.argv[1], out))

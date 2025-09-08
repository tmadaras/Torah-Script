
import os, csv, sys, json
from sqlalchemy import create_engine, text

UPSERT_KEYS = ['source_book_39','source_chapter','source_verse','source_word_position']

def main(csv_path):
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('DATABASE_URL env var required')
        return 2

    engine = create_engine(db_url, future=True)

    # Load CSV into memory
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = {tuple(row[k] for k in UPSERT_KEYS): row for row in reader}

    with engine.begin() as conn:
        db_rows = {tuple(map(str,[r['source_book_39'],r['source_chapter'],r['source_verse'],r['source_word_position']])): dict(r)
                   for r in conn.execute(text("SELECT * FROM tanach_canonical_map"))}

    added = [r for k,r in csv_rows.items() if k not in db_rows]
    removed = [r for k,r in db_rows.items() if k not in csv_rows]
    changed = []
    for k,row in csv_rows.items():
        if k in db_rows:
            diffs = {col:(row[col], db_rows[k][col]) for col in row if col in db_rows[k] and str(row[col])!=str(db_rows[k][col])}
            if diffs:
                changed.append({'key':k,'diffs':diffs})

    print(json.dumps({'added':len(added),'removed':len(removed),'changed':len(changed)}, indent=2, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    if len(sys.argv)<2:
        print('Usage: python diff_csv_vs_db.py <mapping.csv>')
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

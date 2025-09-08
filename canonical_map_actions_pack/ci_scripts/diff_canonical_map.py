
# Fallback diff (simplified): compares CSV vs DB and outputs basic summary.
import os, sys, csv, json
from sqlalchemy import create_engine, text
KEY=('source_book_39','source_chapter','source_verse','source_word_position')
def load_csv(p):
    out={}
    with open(p, newline='', encoding='utf-8') as f:
        r=csv.DictReader(f)
        for row in r:
            out[tuple(row[k] for k in KEY)]=row
    return out
def fetch_db(db):
    e=create_engine(db, future=True)
    sql=text("""SELECT source_book_39, source_chapter::text, source_verse::text, source_word_position::text FROM tanach_canonical_map""")
    out=set()
    with e.begin() as c:
        for row in c.execute(sql):
            out.add(tuple(row))
    return out
def main(csv_path, out_json):
    db=os.environ.get('DATABASE_URL'); 
    if not db: print("DATABASE_URL required"); return 2
    csv_map=load_csv(csv_path)
    db_keys=fetch_db(db)
    added=[{'key':k} for k in csv_map.keys() if k not in db_keys]
    removed=[{'key':k} for k in db_keys if k not in csv_map.keys()]
    rep={'summary':{'added':len(added),'removed':len(removed)},'samples':{'added':added[:50],'removed':removed[:50]}}
    with open(out_json,'w',encoding='utf-8') as f: json.dump(rep,f,indent=2,ensure_ascii=False)
    print(json.dumps(rep['summary'],indent=2))
if __name__=='__main__':
    if len(sys.argv)<3: print("Usage: python diff_canonical_map.py <csv> <out.json>"); sys.exit(2)
    main(sys.argv[1], sys.argv[2])

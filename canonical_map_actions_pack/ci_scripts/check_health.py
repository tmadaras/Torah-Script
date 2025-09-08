
import os, sys, json
from sqlalchemy import create_engine, text

def main():
    db = os.environ.get('DATABASE_URL')
    if not db:
        print("DATABASE_URL required", file=sys.stderr); return 2
    engine = create_engine(db, future=True)
    queries = {
        'missing_map': text("""
            SELECT COUNT(*) FROM oshb_tokens t
            LEFT JOIN tanach_canonical_map m
            ON (m.source_book_39=t.source_book_39 AND m.source_chapter=t.chapter AND m.source_verse=t.verse AND m.source_word_position=t.position)
            WHERE m.id IS NULL
        """),
        'canon_duplicates': text("""
            SELECT COALESCE(SUM(c),0) FROM (
              SELECT COUNT(*) c
              FROM tanach_canonical_map
              GROUP BY canon_book_24, canon_chapter, canon_verse, canon_word_position
              HAVING COUNT(*)>1
            ) x
        """),
        'paleo_fallback_count': text("""
            SELECT COUNT(*)
            FROM tanach_canonical_map m
            WHERE (paleo_hebrew IS NULL OR paleo_hebrew='')
              AND hebrew_lemma IN (SELECT hebrew_word FROM paleo_reference WHERE book IS NULL)
        """),
        'judges_9_9_dup': text("""
            SELECT COUNT(*)
            FROM tanach_canonical_map
            WHERE canon_book_24='Shoftim' AND canon_chapter=9 AND canon_verse=9
              AND hebrew_surface='וַיַּעַשׂ הָרַע'
        """),
    }
    out = {}
    with engine.begin() as conn:
        for k,q in queries.items():
            out[k] = int(conn.execute(q).scalar_one())
    print(json.dumps(out))
    # Hard fail if duplicates or missing_map > 0
    if out['canon_duplicates'] > 0 or out['missing_map'] > 0:
        print("Health check failed: duplicates or missing maps detected", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

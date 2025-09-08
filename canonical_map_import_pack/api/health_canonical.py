
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
import os

router = APIRouter(prefix='/health/canonical', tags=['health'])

def get_engine():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise HTTPException(500, 'DATABASE_URL not configured')
    return create_engine(db_url, future=True)

@router.get('/counters')
def counters():
    engine = get_engine()
    queries = {
        'missing_map': """
            SELECT COUNT(*) FROM oshb_tokens t
            LEFT JOIN tanach_canonical_map m
            ON (m.source_book_39=t.source_book_39 AND m.source_chapter=t.chapter AND m.source_verse=t.verse AND m.source_word_position=t.position)
            WHERE m.id IS NULL;""",
        'canon_duplicates': """
            SELECT COUNT(*) FROM (
              SELECT canon_book_24, canon_chapter, canon_verse, canon_word_position, COUNT(*) c
              FROM tanach_canonical_map GROUP BY 1,2,3,4 HAVING COUNT(*)>1
            ) d;""",
        'paleo_fallback_count': """
            SELECT COUNT(*) FROM tanach_canonical_map
            WHERE (paleo_hebrew IS NULL OR paleo_hebrew='')
              AND hebrew_lemma IN (SELECT hebrew_word FROM paleo_reference WHERE book IS NULL);""",
        'judges_9_9_dup': """
            SELECT COUNT(*) FROM tanach_canonical_map
            WHERE canon_book_24='Shoftim' AND canon_chapter=9 AND canon_verse=9
              AND hebrew_surface='וַיַּעַשׂ הָרַע';"""
    }
    results = {}
    with engine.begin() as conn:
        for k,q in queries.items():
            results[k] = conn.execute(text(q)).scalar()
    return results

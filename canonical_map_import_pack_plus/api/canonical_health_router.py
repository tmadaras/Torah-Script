
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
import os

router = APIRouter(prefix='/admin/canonical', tags=['admin'])

def engine():
    url = os.environ.get('DATABASE_URL')
    if not url: raise HTTPException(500, 'DATABASE_URL not configured')
    return create_engine(url, future=True)

@router.get('/health')
def health():
    q_missing = text("""
      SELECT COUNT(*) AS c
      FROM oshb_tokens t
      LEFT JOIN tanach_canonical_map m
      ON (m.source_book_39=t.source_book_39 AND m.source_chapter=t.chapter AND m.source_verse=t.verse AND m.source_word_position=t.position)
      WHERE m.id IS NULL
    """)
    q_dupe = text("""
      SELECT COALESCE(SUM(c),0) AS s FROM (
        SELECT COUNT(*) c
        FROM tanach_canonical_map
        GROUP BY canon_book_24, canon_chapter, canon_verse, canon_word_position
        HAVING COUNT(*)>1
      ) x
    """)
    q_paleo = text("""
      SELECT COUNT(*) AS c
      FROM tanach_canonical_map m
      WHERE (paleo_hebrew IS NULL OR paleo_hebrew='')
        AND hebrew_lemma IN (SELECT hebrew_word FROM paleo_reference WHERE book IS NULL)
    """)
    q_judges = text("""
      SELECT COUNT(*) AS c
      FROM tanach_canonical_map
      WHERE canon_book_24='Shoftim' AND canon_chapter=9 AND canon_verse=9
        AND hebrew_surface='וַיַּעַשׂ הָרַע'
    """)

    with engine().begin() as conn:
        missing = conn.execute(q_missing).scalar_one()
        dupe = conn.execute(q_dupe).scalar_one()
        paleo = conn.execute(q_paleo).scalar_one()
        judges = conn.execute(q_judges).scalar_one()

    return {
        'missing_map': int(missing),
        'canon_duplicates': int(dupe),
        'paleo_fallback_count': int(paleo),
        'judges_9_9_dup': int(judges)
    }


SELECT COUNT(*) AS missing_map
FROM oshb_tokens t
LEFT JOIN tanach_canonical_map m
ON (m.source_book_39=t.source_book_39 AND m.source_chapter=t.chapter AND m.source_verse=t.verse AND m.source_word_position=t.position)
WHERE m.id IS NULL;

SELECT COUNT(*) AS canon_duplicates
FROM (
  SELECT canon_book_24, canon_chapter, canon_verse, canon_word_position, COUNT(*) c
  FROM tanach_canonical_map
  GROUP BY 1,2,3,4 HAVING COUNT(*)>1
) d;

SELECT COUNT(*) AS paleo_fallback_count
FROM tanach_canonical_map
WHERE (paleo_hebrew IS NULL OR paleo_hebrew='')
  AND hebrew_lemma IN (SELECT hebrew_word FROM paleo_reference WHERE book IS NULL);

SELECT COUNT(*) AS judges_9_9_dup
FROM tanach_canonical_map
WHERE canon_book_24='Shoftim' AND canon_chapter=9 AND canon_verse=9
AND hebrew_surface='וַיַּעַשׂ הָרַע';

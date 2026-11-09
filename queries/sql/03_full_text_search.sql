-- Full-text search over the review texts (PostgreSQL tsvector / tsquery).

-- GIN index to speed up full-text search on review texts
CREATE INDEX idx_reviews_text_fts
ON reviews
USING GIN (to_tsvector('english', text));


-- 1) Reviews about slow service and waiting, with the XPointer to the exact keyword
SELECT
    k.review_id,
    r.brand,
    k.keyword,
    k.xpointer,
    r.text,
    ts_rank(to_tsvector('english', r.text), to_tsquery('slow & wait')) AS rank
FROM keywords k
JOIN reviews r ON k.review_id = r.review_id
WHERE to_tsvector('english', r.text) @@ to_tsquery('slow & wait')
  AND (k.keyword ILIKE '%slow%' OR k.keyword ILIKE '%wait%')
ORDER BY rank DESC, k.review_id DESC
LIMIT 10;


-- 2) Most subjective staff-attitude mentions that praise friendly, helpful or kind staff
SELECT
    s.review_id,
    s.keyword,
    s.sub_aspect,
    s.subjectivity,
    ts_rank(to_tsvector('english', r.text), to_tsquery('friend:* | helpful:* | kind:*')) AS rank
FROM service_subaspects s
JOIN reviews r ON s.review_id = r.review_id
WHERE s.sub_aspect = 'STAFF_ATTITUDE'
  AND to_tsvector('english', r.text) @@ to_tsquery('friend:* | helpful:* | kind:*')
  AND s.keyword ILIKE ANY (ARRAY['%friendly%', '%helpful%', '%kind%'])
ORDER BY s.subjectivity DESC, rank DESC
LIMIT 10;

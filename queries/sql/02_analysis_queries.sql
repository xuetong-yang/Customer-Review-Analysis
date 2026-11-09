-- Analysis queries used to compare the two brands.

-- 1) Share of positive and negative ratings per brand and aspect
--    Percentages are relative to all 50 reviews per brand, including n/a.
SELECT
    rv.brand,
    ra.aspect,
    COUNT(*) FILTER (WHERE ra.rating = 'good') AS positive_count,
    ROUND(COUNT(*) FILTER (WHERE ra.rating = 'good') * 100.0 / COUNT(*), 1) AS positive_percentage,
    COUNT(*) FILTER (WHERE ra.rating = 'bad') AS negative_count,
    ROUND(COUNT(*) FILTER (WHERE ra.rating = 'bad') * 100.0 / COUNT(*), 1) AS negative_percentage
FROM ratings ra
JOIN reviews rv ON ra.review_id = rv.review_id
GROUP BY rv.brand, ra.aspect
ORDER BY positive_percentage DESC;


-- 2) Top 5 negative keywords per brand (window function)
SELECT brand, keyword, count
FROM (
    SELECT
        r.brand,
        k.keyword,
        COUNT(*) AS count,
        ROW_NUMBER() OVER (PARTITION BY r.brand ORDER BY COUNT(*) DESC) AS rank
    FROM keywords k
    JOIN reviews r ON k.review_id = r.review_id
    WHERE k.rating = 'bad'
    GROUP BY r.brand, k.keyword
) ranked
WHERE rank <= 5
ORDER BY brand, count DESC;


-- 3) Most frequent staff-attitude keywords and their average subjectivity
SELECT
    keyword,
    COUNT(*) AS freq,
    ROUND(AVG(subjectivity)::numeric, 2) AS avg_subjectivity
FROM service_subaspects
WHERE sub_aspect = 'STAFF_ATTITUDE'
GROUP BY keyword
ORDER BY freq DESC;

-- Relational schema for the annotated reviews (PostgreSQL).
-- The nested XML is split into four tables linked by review_id.

CREATE TABLE reviews (
    review_id VARCHAR(128) PRIMARY KEY,
    brand     VARCHAR(128),
    text      TEXT
);

-- One row per review and aspect (service, foodQuality, environment, price)
CREATE TABLE ratings (
    review_id VARCHAR(128) REFERENCES reviews(review_id),
    aspect    VARCHAR(128),
    rating    VARCHAR(128)          -- good / bad / neutral / n/a
);

-- One row per annotated keyword, with an XPointer back into the review text
CREATE TABLE keywords (
    keyword_id SERIAL PRIMARY KEY,
    review_id  VARCHAR(128) REFERENCES reviews(review_id),
    aspect     VARCHAR(128),
    rating     VARCHAR(128),
    keyword    TEXT,
    xpointer   TEXT
);

-- Service keywords grouped into sub-aspects, with a subjectivity score (0 = objective, 1 = subjective)
CREATE TABLE service_subaspects (
    id           SERIAL PRIMARY KEY,
    review_id    VARCHAR(128) REFERENCES reviews(review_id),
    keyword      VARCHAR(128),
    sub_aspect   VARCHAR(128),      -- TIMELINESS / STAFF_ATTITUDE / ORDER_ACCURACY / STAFFING_LEVELS
    subjectivity FLOAT
);

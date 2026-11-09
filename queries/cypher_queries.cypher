// Cypher queries on the Neo4j knowledge graph built in notebooks/build_knowledge_graph.ipynb.
// Nodes: Brand, Review, Sentiment, Aspect (service sub-aspect), Keyword. Reviews carry a subjectivity score.

// 1. Average, min and max subjectivity per brand and service sub-aspect
MATCH (b:Brand)-[:HAS_REVIEW]->(r:Review)-[:RELATES_TO_ASPECT]->(a:Aspect)
WHERE b.name IN ['BK', 'MC']
  AND a.name IN ['TIMELINESS', 'STAFF_ATTITUDE', 'ORDER_ACCURACY', 'STAFFING_LEVELS', 'OTHER']
RETURN b.name AS Brand,
       a.name AS Aspect,
       avg(r.subjectivity) AS AverageSubjectivity,
       min(r.subjectivity) AS MinSubjectivity,
       max(r.subjectivity) AS MaxSubjectivity
ORDER BY Brand, Aspect;

// 2. Average, min and max subjectivity per brand
MATCH (b:Brand)-[:HAS_REVIEW]->(r:Review)
WHERE b.name IN ['BK', 'MC']
RETURN b.name AS Brand,
       avg(r.subjectivity) AS AverageSubjectivity,
       min(r.subjectivity) AS MinSubjectivity,
       max(r.subjectivity) AS MaxSubjectivity
ORDER BY Brand;

// 3. Visualize how reviews link keywords and sentiments
MATCH p = ()<-[:CONTAINS_KEYWORD]-(r:Review)-[:EXPRESSES_SENTIMENT]->()
RETURN p
LIMIT 25;

// 4. Subjectivity of reviews by sentiment
MATCH (b:Brand)-[:HAS_REVIEW]->(r:Review)-[:EXPRESSES_SENTIMENT]->(s:Sentiment)
WHERE b.name IN ['BK', 'MC']
  AND s.type IN ['good', 'bad', 'neutral']
RETURN b.name AS Brand,
       s.type AS Sentiment,
       avg(r.subjectivity) AS AverageSubjectivity,
       min(r.subjectivity) AS MinSubjectivity,
       max(r.subjectivity) AS MaxSubjectivity
ORDER BY Brand, Sentiment;

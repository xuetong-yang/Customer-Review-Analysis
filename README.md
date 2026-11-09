# Customer Review Analysis: From Reviews to Advertising Strategy

How can unstructured customer reviews guide advertising decisions?
This project turns 100 Yelp reviews of Burger King and McDonald's into structured data, stores it in PostgreSQL and a knowledge graph, and derives brand-level marketing recommendations.

*Text Technology project, Institute for Natural Language Processing (IMS), University of Stuttgart, summer 2025.*

---

## Project story

We act as a marketing agency comparing customer reviews of two competing fast-food brands.
The goal is to uncover what customers praise and criticize, and to turn that into data-driven advertising recommendations.

## Pipeline

```
Collect                      Prepare                          Access
───────────────────────      ───────────────────────────      ─────────────────────────────
Yelp Open Dataset (JSON)  →  XML + XML Schema validation   →  PostgreSQL: statistics,
Filter: 2 brands, 5 stores,  XPath to explore aspects          window functions,
10 most useful reviews each  XPointer to anchor keywords        full-text search
Manual annotation:           Keyword normalization              Neo4j knowledge graph
4 aspects x sentiment        (tokenization, lemmatization)      SPARQL query to Wikidata
+ supporting keywords        Service sub-aspects + subjectivity
```

- **Collect.** For each brand, we took the 5 most-reviewed stores and the 10 reviews per store with the most "useful" votes. Each review was annotated by hand for four aspects: service, food quality, environment and price. Each aspect got a rating (good, neutral, bad or n/a) plus keywords as evidence.
- **Prepare.** The annotations were stored as XML and validated against an XML Schema. XPointer links each keyword to its exact position in the review text. Service keywords were normalized and grouped into four sub-aspects: timeliness, staff attitude, order accuracy and staffing levels. Each got a subjectivity score.
- **Access.** The hierarchical XML was flattened into four relational tables in PostgreSQL. SQL queries compare the brands, and full-text search finds specific service issues. A Neo4j knowledge graph shows how brands, reviews, sentiments and keywords connect.

## Key findings

- **Service is the key differentiator.** 82% of McDonald's reviews criticize the service and only 6% praise it. At Burger King, 32% of reviews praise the service, mainly for friendly staff.
- **Burger King also does better on food quality.** 18% of its reviews praise the food, compared with 2% for McDonald's. Negative food ratings still outnumber positive ones for both brands.
- **Staff attitude is the most emotionally charged sub-aspect.** It has the highest subjectivity scores.

Percentages are relative to all 50 reviews per brand. A review that does not mention an aspect counts as n/a.

**Recommendation:** Burger King should lead its advertising with friendly staff. McDonald's should prioritize improving service, its most criticized area.

## Repository structure

```
├── README.md
├── requirements.txt
├── annotation/
│   └── annotation_guideline.md       # Aspect and sentiment labels with examples
├── schema/
│   └── reviews.xsd                   # XML Schema for annotated reviews
├── data/
│   └── sample_reviews.xml            # Two synthetic reviews showing the annotation format
├── scripts/
│   ├── csv_to_xml.py                 # Annotation spreadsheet → XML, validated against the XSD
│   ├── add_xpointer.py               # Anchors each keyword to its position in the review text
│   └── import_to_postgres.py         # Flattens the XML into relational tables and loads them
├── notebooks/
│   ├── keyword_normalization.ipynb   # Tokenize, lemmatize, assign service sub-aspects, score subjectivity
│   └── build_knowledge_graph.ipynb   # Loads Neo4j and exports the same graph as RDF (Turtle)
├── queries/
│   ├── xpath_queries.sh              # Explore aspects and ratings, export keywords per brand
│   ├── sql/
│   │   ├── 01_create_tables.sql      # Relational schema
│   │   ├── 02_analysis_queries.sql   # Brand comparison, top keywords (window function), sub-aspects
│   │   └── 03_full_text_search.sql   # GIN index and full-text search
│   ├── cypher_queries.cypher         # Subjectivity by brand, sub-aspect and sentiment
│   └── sparql_query.rq               # Local review graph + company data from Wikidata
└── docs/
    └── presentation.pdf              # Final project presentation
```

## Database schema

| Table | One row per | Columns |
|---|---|---|
| `reviews` | review | review_id, brand, text |
| `ratings` | review and aspect | review_id, aspect, rating |
| `keywords` | annotated keyword | keyword_id, review_id, aspect, rating, keyword, xpointer |
| `service_subaspects` | service keyword | id, review_id, keyword, sub_aspect, subjectivity |

All tables are linked by `review_id`. Splitting the data this way keeps each keyword queryable on its own, instead of losing it inside one flattened cell.

## Example query

Top 5 negative keywords per brand, using a window function:

```sql
SELECT brand, keyword, count
FROM (
    SELECT r.brand, k.keyword, COUNT(*) AS count,
           ROW_NUMBER() OVER (PARTITION BY r.brand ORDER BY COUNT(*) DESC) AS rank
    FROM keywords k
    JOIN reviews r ON k.review_id = r.review_id
    WHERE k.rating = 'bad'
    GROUP BY r.brand, k.keyword
) ranked
WHERE rank <= 5
ORDER BY brand, count DESC;
```

More queries are in [`queries/`](queries/), including Cypher for the knowledge graph and a federated SPARQL query.

## Linking to public data

In the RDF graph, each brand is a Wikidata entity (Burger King = `wd:Q177054`, McDonald's = `wd:Q38076`).
This lets one SPARQL query combine our review sentiment with company data from Wikidata, such as total assets and net income.
The query needs an endpoint that supports SPARQL 1.1 federation, for example Apache Jena Fuseki with `review_kg.ttl` loaded.

## How to run

The original reviews come from the [Yelp Open Dataset](https://www.yelp.com/dataset) and are **not included**, in line with its terms of use. The relational part of the pipeline can be tried on the synthetic sample.

```bash
pip install -r requirements.txt

# 1. Anchor keywords with XPointer
python scripts/add_xpointer.py data/sample_reviews.xml data/sample_reviews_with_xpointer.xml

# 2. Create the tables (PostgreSQL)
psql -d <database> -f queries/sql/01_create_tables.sql

# 3. Load the data. Credentials come from environment variables.
export PGDATABASE=<database> PGUSER=<user> PGPASSWORD=<password>
python scripts/import_to_postgres.py data/sample_reviews_with_xpointer.xml

# 4. Run the analysis
psql -d <database> -f queries/sql/02_analysis_queries.sql
psql -d <database> -f queries/sql/03_full_text_search.sql
```

With the full annotated data, the complete order is:

1. `scripts/csv_to_xml.py`: annotation spreadsheet → validated XML
2. `scripts/add_xpointer.py`: add XPointer anchors
3. `queries/xpath_queries.sh`: explore the XML and export keywords into `keywords/`
4. `notebooks/keyword_normalization.ipynb`: service sub-aspects and subjectivity → `keywords_dict_expanded.parquet`
5. `scripts/import_to_postgres.py <xml> keywords_dict_expanded.parquet`, then the SQL files
6. `notebooks/build_knowledge_graph.ipynb` (set `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`), then the Cypher and SPARQL queries

## My contribution

This was a three-person project with Qianyue Li and Qianru Qian.

**My part:**

- Wrote the annotation guideline and annotated one third of the reviews
- Designed the PostgreSQL schema
- Built the Python pipeline that flattens the XML and loads it into PostgreSQL (`scripts/import_to_postgres.py`, `scripts/add_xpointer.py`)
- Wrote the SQL analysis and full-text search queries (`queries/sql/`)

**My teammates' part:** Qianyue Li built the XML conversion and the Neo4j knowledge graph with its Cypher queries. The XPath exploration, the keyword normalization and the SPARQL extension were done by my teammates.
Their code is included here, with local paths and credentials removed, so the full pipeline can be followed.

## Authors

- Xuetong Yang
- Qianyue Li
- Qianru Qian


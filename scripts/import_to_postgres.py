"""Flatten the annotated review XML into relational tables and load them into PostgreSQL.

The hierarchical XML (review -> aspect -> rating + keywords) is split into three tables:
  - reviews:  one row per review
  - ratings:  one row per review and aspect
  - keywords: one row per keyword, with its XPointer back into the review text

Optionally, a fourth table, service_subaspects, is loaded from a parquet file that
groups service keywords into sub-aspects (e.g. STAFF_ATTITUDE, TIMELINESS) with a
subjectivity score.

Database credentials are read from environment variables, never from the code:
    PGDATABASE, PGUSER, PGPASSWORD, PGHOST (default localhost), PGPORT (default 5432)

Usage:
    python scripts/import_to_postgres.py <reviews_with_xpointer.xml> [service_subaspects.parquet]

Create the tables first with sql/01_create_tables.sql.
"""

import logging
import os
import sys
import xml.etree.ElementTree as ET

import pandas as pd

REVIEWS_NS = "http://tt-project.com/reviews"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
NS = {"ns": REVIEWS_NS}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_xml_to_dataframes(xml_path: str):
    """Flatten the nested XML into three DataFrames: reviews, ratings and keywords."""
    root = ET.parse(xml_path).getroot()
    reviews, ratings, keywords = [], [], []

    for review in root.findall("ns:review", NS):
        review_id = review.get("review_id")
        text_elem = review.find("ns:text", NS)
        reviews.append({
            "review_id": review_id,
            "brand": review.get("brand"),
            "text": text_elem.text if text_elem is not None else "",
        })

        for aspect_elem in review.find("ns:annotations", NS):
            aspect = aspect_elem.tag.replace(f"{{{REVIEWS_NS}}}", "")
            rating_elem = aspect_elem.find("ns:rating", NS)
            rating = rating_elem.text if rating_elem is not None else None
            ratings.append({"review_id": review_id, "aspect": aspect, "rating": rating})

            for keyword_elem in aspect_elem.findall("ns:keyword", NS):
                keywords.append({
                    "review_id": review_id,
                    "aspect": aspect,
                    "rating": rating,
                    "keyword": keyword_elem.text,
                    "xpointer": keyword_elem.get(XLINK_HREF),
                })

    return pd.DataFrame(reviews), pd.DataFrame(ratings), pd.DataFrame(keywords)


def load_service_subaspects(parquet_path: str, df_keywords: pd.DataFrame) -> pd.DataFrame:
    """Attach review_id to the sub-aspect table by matching keywords back to the XML."""
    df_sub = pd.read_parquet(parquet_path).rename(columns=str.upper)
    keyword_map = (
        df_keywords[["review_id", "keyword"]]
        .drop_duplicates()
        .rename(columns={"keyword": "KEYWORDS"})
    )
    merged = pd.merge(df_sub, keyword_map, on="KEYWORDS", how="left")
    logging.info("Matched %d of %d sub-aspect keywords to a review",
                 merged["review_id"].notna().sum(), len(merged))
    return (
        merged.dropna(subset=["review_id"])[["review_id", "KEYWORDS", "ASPECT", "SUBJECTIVITY"]]
        .rename(columns={"KEYWORDS": "keyword", "ASPECT": "sub_aspect", "SUBJECTIVITY": "subjectivity"})
    )


def insert_dataframe(conn, df: pd.DataFrame, table: str, columns: list) -> None:
    """Insert a DataFrame into a table in one transaction; roll back on error."""
    from psycopg2.extras import execute_batch

    placeholders = ", ".join(f"%({col})s" for col in columns)
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    with conn.cursor() as cur:
        try:
            execute_batch(cur, sql, df[columns].to_dict("records"))
            conn.commit()
            logging.info("Inserted %d rows into %s", len(df), table)
        except Exception as error:
            conn.rollback()
            logging.error("Failed to insert into %s: %s", table, error)
            raise


def main() -> None:
    if len(sys.argv) not in (2, 3):
        sys.exit("Usage: python scripts/import_to_postgres.py <reviews.xml> [service_subaspects.parquet]")
    xml_path = sys.argv[1]
    parquet_path = sys.argv[2] if len(sys.argv) == 3 else None

    df_reviews, df_ratings, df_keywords = parse_xml_to_dataframes(xml_path)
    logging.info("Parsed %d reviews, %d ratings, %d keywords",
                 len(df_reviews), len(df_ratings), len(df_keywords))

    import psycopg2

    conn = psycopg2.connect(
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
    )
    try:
        insert_dataframe(conn, df_reviews, "reviews", ["review_id", "brand", "text"])
        insert_dataframe(conn, df_ratings, "ratings", ["review_id", "aspect", "rating"])
        insert_dataframe(conn, df_keywords, "keywords",
                         ["review_id", "aspect", "rating", "keyword", "xpointer"])
        if parquet_path:
            df_sub = load_service_subaspects(parquet_path, df_keywords)
            insert_dataframe(conn, df_sub, "service_subaspects",
                             ["review_id", "keyword", "sub_aspect", "subjectivity"])
    finally:
        conn.close()

    logging.info("Import finished")


if __name__ == "__main__":
    main()

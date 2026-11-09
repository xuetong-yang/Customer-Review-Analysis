"""Convert the annotation spreadsheet (CSV) to XML and validate it against the XSD schema.

Expected CSV columns: review_id, brand, text, and for each aspect
(service, foodQuality, environment, price) an <aspect>_rating and an <aspect>_keyword column.
Empty ratings become "n/a".

Usage:
    python scripts/csv_to_xml.py <reviews.csv> <output.xml> [schema/reviews.xsd]
"""
import sys

import pandas as pd
from lxml import etree

NAMESPACE = "http://tt-project.com/reviews"
ASPECTS = ["service", "foodQuality", "environment", "price"]


def create_dimension(parent, name, row):
    """Add one aspect element with a <rating> and an optional <keyword>."""
    dim = etree.SubElement(parent, f"{{{NAMESPACE}}}{name}")

    rating = etree.SubElement(dim, f"{{{NAMESPACE}}}rating")
    rating_val = row.get(f"{name}_rating")
    rating.text = str(rating_val) if pd.notna(rating_val) and rating_val != "" else "n/a"

    keyword_val = row.get(f"{name}_keyword")
    if pd.notna(keyword_val) and keyword_val != "":
        keyword = etree.SubElement(dim, f"{{{NAMESPACE}}}keyword")
        keyword.text = str(keyword_val)


def create_xml(csv_path, xml_path):
    df = pd.read_csv(csv_path, dtype=str, encoding="latin-1", engine="python").fillna("")
    print(f"Read {len(df)} rows from {csv_path}")

    root = etree.Element(f"{{{NAMESPACE}}}reviews", nsmap={None: NAMESPACE})
    for _, row in df.iterrows():
        review = etree.SubElement(root, f"{{{NAMESPACE}}}review")
        review.set("review_id", str(row.get("review_id", "")))
        review.set("brand", str(row.get("brand", "")))

        text = etree.SubElement(review, f"{{{NAMESPACE}}}text")
        text.text = str(row.get("text", ""))

        annotations = etree.SubElement(review, f"{{{NAMESPACE}}}annotations")
        for aspect in ASPECTS:
            create_dimension(annotations, aspect, row)

    etree.ElementTree(root).write(xml_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
    print(f"Wrote {xml_path}")


def validate(xml_path, xsd_path):
    schema = etree.XMLSchema(etree.parse(xsd_path))
    if schema.validate(etree.parse(xml_path)):
        print("Validation successful.")
        return True
    print("Validation failed:")
    for error in schema.error_log:
        print(f"  - Line {error.line}, Column {error.column}: {error.message}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    csv_file, xml_file = sys.argv[1], sys.argv[2]
    xsd_file = sys.argv[3] if len(sys.argv) > 3 else "schema/reviews.xsd"
    create_xml(csv_file, xml_file)
    sys.exit(0 if validate(xml_file, xsd_file) else 1)

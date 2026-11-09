"""Anchor each annotated keyword to its exact position in the review text.

For every <keyword>, the script adds:
  - start / end: character offsets of the keyword in the review text (-1 if not found)
  - xlink:href:  an XPointer string-range that points to the keyword in its review

Usage:
    python scripts/add_xpointer.py <input.xml> <output.xml>
"""

import sys
import xml.etree.ElementTree as ET

REVIEWS_NS = "http://tt-project.com/reviews"
XLINK_NS = "http://www.w3.org/1999/xlink"
NS = {"ns": REVIEWS_NS}


def add_xpointers(input_path: str, output_path: str) -> None:
    ET.register_namespace("", REVIEWS_NS)
    ET.register_namespace("xlink", XLINK_NS)

    tree = ET.parse(input_path)
    root = tree.getroot()

    found, missing = 0, 0
    for review in root.findall("ns:review", NS):
        review_id = review.attrib["review_id"]
        text_elem = review.find("ns:text", NS)
        annotations = review.find("ns:annotations", NS)
        if text_elem is None or text_elem.text is None or annotations is None:
            continue
        text = text_elem.text

        for aspect in annotations:
            for keyword_elem in aspect.findall("ns:keyword", NS):
                keyword = keyword_elem.text
                if not keyword:
                    continue
                start = text.find(keyword)
                if start == -1:
                    keyword_elem.set("start", "-1")
                    keyword_elem.set("end", "-1")
                    missing += 1
                    continue
                keyword_elem.set("start", str(start))
                keyword_elem.set("end", str(start + len(keyword)))
                keyword_elem.set(
                    f"{{{XLINK_NS}}}href",
                    f"#xpointer(string-range(//review[@review_id='{review_id}']/text,'{keyword}'))",
                )
                found += 1

    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"Anchored {found} keywords, {missing} not found in text. Saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/add_xpointer.py <input.xml> <output.xml>")
    add_xpointers(sys.argv[1], sys.argv[2])

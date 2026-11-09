#!/usr/bin/env bash
# XPath queries used to explore the annotated reviews (requires the `xpath` command, e.g. from libxml-xpath-perl).
# Usage: bash queries/xpath_queries.sh <reviews.xml> [output_dir]
#
# Note: "McDonald's" contains an apostrophe, which breaks quoting in XPath attribute tests,
# so contains(@brand, 'McDonald') is used instead.

XML="${1:?Usage: bash queries/xpath_queries.sh <reviews.xml> [output_dir]}"
OUT="${2:-keywords}"
mkdir -p "$OUT"

BK='@brand="Burger King"'
MC="contains(@brand, 'McDonald')"

# Task 1: how many reviews rate each aspect (not n/a)? Shows which aspects matter most.
for aspect in service foodQuality environment price; do
  echo "BK $aspect:  $(xpath -q -e "count(//review[$BK]//$aspect[rating!='n/a'])" "$XML")"
  echo "MC $aspect:  $(xpath -q -e "count(//review[$MC]//$aspect[rating!='n/a'])" "$XML")"
done

# Task 2: rating distribution for the two most rated aspects
for aspect in service foodQuality; do
  for rating in good bad neutral; do
    echo "BK $aspect $rating: $(xpath -q -e "count(//review[$BK]//$aspect[rating='$rating'])" "$XML")"
    echo "MC $aspect $rating: $(xpath -q -e "count(//review[$MC]//$aspect[rating='$rating'])" "$XML")"
  done
done

# Task 3: export the keywords for each brand, aspect and rating for further processing
for aspect in service foodQuality; do
  for rating in good bad neutral; do
    xpath -q -e "//review[$BK]//$aspect[rating='$rating']/keyword" "$XML" > "$OUT/BK_${aspect}_${rating}.txt"
    xpath -q -e "//review[$MC]//$aspect[rating='$rating']/keyword" "$XML" > "$OUT/MC_${aspect}_${rating}.txt"
  done
done

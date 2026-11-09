# Annotation Guideline

## Purpose

Manually annotate the sentiment of Yelp user reviews of Burger King and McDonald's on four aspects: **SERVICE**, **FOOD_QUALITY**, **ENVIRONMENT** and **PRICE**.

Each aspect gets a sentiment label: **good**, **neutral** or **bad**. If an aspect is not mentioned, it is labeled **n/a**.
Annotators also select keywords from the original text as evidence for each label.

## General principles

- One review may contain mixed sentiment across different aspects.
- Only annotate an aspect if it is clearly mentioned or implied.
- Avoid over-annotation. If something is not clearly evaluative, label it n/a.

## Label definitions and examples

### SERVICE

The behavior, attitude, speed or helpfulness of the staff, including correct processing of orders.

| Label | Example |
|---|---|
| good | "The staff was super friendly." / "Service was fast and efficient." |
| bad | "Horrible service in the drive-through!" / "The food took forever." |
| neutral | "Nothing to complain about." |

### FOOD_QUALITY

The taste, freshness and temperature of the food or drinks served.

| Label | Example |
|---|---|
| good | "The chicken was crispy and juicy." / "Delicious burger and fresh fries." |
| bad | "Taste was really bland and the hash browns even tasted a little old." / "My sandwich was cold and dry." |
| neutral | "I can't say I liked it or disliked it." |

### ENVIRONMENT

The physical setting of the restaurant, including cleanliness, noise level, seating, safety and location.

| Label | Example |
|---|---|
| good | "Nice and clean dining area." |
| bad | "The place was dirty and smelled awful." / "Too noisy, hard to enjoy my meal." |
| neutral | "Restaurant fine." |

### PRICE

Whether users are satisfied with the value for money.

| Label | Example |
|---|---|
| good | "For the money, you get a decent shake." / "Affordable and worth every penny." |
| bad | "Overpriced for what you get." / "Way too expensive for fast food." |
| neutral | "The prices are normal." |

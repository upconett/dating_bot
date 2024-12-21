FULL_RECOMENDATION = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
sex_filtered AS (
    SELECT *
    FROM active_cards
    WHERE sex = {seek_sex}
),
city_filtered AS (
    SELECT *
    FROM sex_filtered
    WHERE city = '{target_city}'
),
age_filtered AS (
    SELECT *
    FROM city_filtered
    WHERE age BETWEEN {seek_age_from} AND {seek_age_to}
),
interests_filtered AS (
    SELECT *,
        (interests & {interests}) AS common_bits,
        LENGTH(REPLACE(HEX((interests & {interests})), '0', '')) AS common_count
    FROM age_filtered
    WHERE (interests & {interests}) != 0
    ORDER BY common_count DESC
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM interests_filtered c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""

RECOMENDATION_NO_CITY = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
sex_filtered AS (
    SELECT *
    FROM active_cards
    WHERE sex = {seek_sex}
),
age_filtered AS (
    SELECT *
    FROM sex_filtered
    WHERE age BETWEEN {seek_age_from} AND {seek_age_to}
),
interests_filtered AS (
    SELECT *,
        (interests & {interests}) AS common_bits,
        LENGTH(REPLACE(HEX((interests & {interests})), '0', '')) AS common_count
    FROM age_filtered
    WHERE (interests & {interests}) != 0
    ORDER BY common_count DESC
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM interests_filtered c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""

RECOMENDATION_NO_AGE = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
sex_filtered AS (
    SELECT *
    FROM active_cards
    WHERE sex = {seek_sex}
),
city_filtered AS (
    SELECT *
    FROM sex_filtered
    WHERE city = '{target_city}'
),
interests_filtered AS (
    SELECT *,
        (interests & {interests}) AS common_bits,
        LENGTH(REPLACE(HEX((interests & {interests})), '0', '')) AS common_count
    FROM city_filtered
    WHERE (interests & {interests}) != 0
    ORDER BY common_count DESC
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM interests_filtered c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""

RECOMENDATION_NO_CITY_AGE = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
sex_filtered AS (
    SELECT *
    FROM active_cards
    WHERE sex = {seek_sex}
),
interests_filtered AS (
    SELECT *,
        (interests & {interests}) AS common_bits,
        LENGTH(REPLACE(HEX((interests & {interests})), '0', '')) AS common_count
    FROM sex_filtered
    WHERE (interests & {interests}) != 0
    ORDER BY common_count DESC
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM interests_filtered c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""

RECOMENDATION_NO_INTERESTS = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
sex_filtered AS (
    SELECT *
    FROM active_cards
    WHERE sex = {seek_sex}
),
city_filtered AS (
    SELECT *
    FROM sex_filtered
    WHERE city = '{target_city}'
),
age_filtered AS (
    SELECT *
    FROM city_filtered
    WHERE age BETWEEN {seek_age_from} AND {seek_age_to}
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM age_filtered c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""

RECOMENDATION_BY_SEX = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
sex_filtered AS (
    SELECT *
    FROM active_cards
    WHERE sex = {seek_sex}
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM sex_filtered c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""

RECOMENDATION_UNSEEN = """
WITH active_cards AS (
    SELECT *
    from cards
    where active = 1
),
unseen_filtered AS (
    SELECT c.id AS seen
    FROM active_cards c
    CROSS JOIN seen_cards sc
    WHERE sc.user_id = {current_user_id}
    AND SUBSTR(sc.bit_string, c.id, 1) = '0'
)
SELECT * 
FROM unseen_filtered
WHERE seen != {current_id}
LIMIT {limit};
"""
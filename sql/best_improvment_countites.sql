WITH county_years AS (
    SELECT 
        fo.fipscode,
        fo.raw_value,
        fo.year_start,
        MIN(fo.year_start) OVER (PARTITION BY fo.fipscode) AS min_year,
        MAX(fo.year_start) OVER (PARTITION BY fo.fipscode) AS max_year
    FROM fact_observations fo
    JOIN measure m ON fo.measure_id = m.measure_id
    WHERE m.measure_name = 'Premature Death'
    AND fo.raw_value IS NOT NULL
),
first_year AS (
    SELECT fipscode, raw_value FROM county_years WHERE year_start = min_year
),
last_year AS (
    SELECT fipscode, raw_value FROM county_years WHERE year_start = max_year
)
SELECT c.county_name, c.state_name,
    ROUND((first_year.raw_value - last_year.raw_value)::numeric, 2) AS improvement
FROM first_year
JOIN last_year ON first_year.fipscode = last_year.fipscode
JOIN county c ON first_year.fipscode = c.fipscode
ORDER BY improvement DESC
LIMIT 10;
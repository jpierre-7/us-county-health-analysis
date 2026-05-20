SELECT year_start, AVG(raw_value) AS premature_death
FROM fact_observations fo
JOIN measure m ON fo.measure_id = m.measure_id
JOIN county c ON fo.fipscode = c.fipscode
WHERE m.measure_name = 'Premature Death'
GROUP BY year_start
ORDER BY year_start ASC
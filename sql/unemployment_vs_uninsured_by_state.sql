WITH unemployment AS (
    SELECT state_name, AVG(raw_value) AS unemployment_rate
    FROM fact_observations fo
    JOIN measure m ON fo.measure_id = m.measure_id
    JOIN county c ON fo.fipscode = c.fipscode
    WHERE m.measure_name = 'Unemployment' AND fo.year_start = 2008
    GROUP BY state_name
),
uninsured AS (
    SELECT state_name, AVG(raw_value) AS uninsured_rate
    FROM fact_observations fo
    JOIN measure m ON fo.measure_id = m.measure_id
    JOIN county c ON fo.fipscode = c.fipscode
    WHERE m.measure_name = 'Uninsured' AND fo.year_start = 2008
    GROUP BY state_name
)
SELECT u.state_name, u.unemployment_rate, i.uninsured_rate
FROM unemployment u
JOIN uninsured i ON u.state_name = i.state_name
ORDER BY u.unemployment_rate DESC;
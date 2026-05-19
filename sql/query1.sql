SELECT state_name, ROUND(AVG(raw_value)::numeric, 4) AS avg_obesity
FROM fact_observations fo
JOIN measure m ON fo.measure_id = m.measure_id
JOIN county c ON fo.fipscode = c.fipscode
WHERE m.measure_name = 'Adult obesity'
GROUP BY c.state_name
ORDER BY avg_obesity DESC
LIMIT 10;
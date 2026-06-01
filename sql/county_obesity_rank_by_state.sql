SELECT county_name, state_name, raw_value, RANK() OVER (PARTITION BY state_name ORDER BY raw_value DESC) AS obesity_rank
FROM fact_observations fo
JOIN measure m ON fo.measure_id = m.measure_id
JOIN county c ON fo.fipscode = c.fipscode
WHERE m.measure_name = 'Adult obesity' AND fo.year_start = 2008
ORDER BY state_name, obesity_rank
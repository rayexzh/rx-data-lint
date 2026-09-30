-- Dropping negatives is a hypothetical scenario, not recommended cleaning.
SELECT month, COUNT(*) AS records, COUNT(cost_gbp) AS known_cost_records,
 SUM(cost_status='missing') AS missing_cost_records,
 SUM(cost_status='invalid') AS invalid_cost_records,
 SUM(CASE WHEN cost_gbp<0 THEN 1 ELSE 0 END) AS negative_cost_records,
 ROUND(SUM(cost_gbp),2) AS known_net_indicative_cost_gbp,
 ROUND(SUM(CASE WHEN cost_gbp>=0 THEN cost_gbp END),2) AS nonnegative_only_cost_gbp,
 ROUND(SUM(CASE WHEN cost_gbp<0 THEN cost_gbp ELSE 0 END),2) AS negative_component_gbp
FROM records GROUP BY month ORDER BY month;

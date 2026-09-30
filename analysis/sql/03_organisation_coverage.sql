-- Counts describe this file, not hospital performance or complete NHS coverage.
SELECT month, ods_code, COUNT(*) AS records,
 COUNT(DISTINCT NULLIF(product_code,'')) AS observed_products,
 COUNT(cost_gbp) AS known_cost_records,
 SUM(cost_status='missing') AS missing_cost_records,
 SUM(cost_status='invalid') AS invalid_cost_records,
 ROUND(100.0*COUNT(cost_gbp)/COUNT(*),4) AS known_cost_record_percent,
 ROUND(SUM(cost_gbp),2) AS known_net_indicative_cost_gbp
FROM records GROUP BY month,ods_code ORDER BY month,ods_code;

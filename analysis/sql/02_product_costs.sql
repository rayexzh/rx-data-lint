-- Keep all products; set a Top N filter in Power BI if desired.
-- Names may differ for a code: expose the count, use MIN only as a display label.
WITH totals AS (
 SELECT month, product_code, MIN(product_name) AS display_name,
 COUNT(DISTINCT product_name) AS name_variants, COUNT(*) AS records,
 COUNT(cost_gbp) AS known_cost_records,
 COUNT(DISTINCT NULLIF(ods_code,'')) AS observed_organisations,
 SUM(cost_gbp) AS known_net_indicative_cost_gbp
 FROM records GROUP BY month,product_code
)
SELECT *, CASE WHEN known_cost_records>0 THEN
 DENSE_RANK() OVER (PARTITION BY month ORDER BY known_net_indicative_cost_gbp DESC)
 END AS cost_rank
FROM totals ORDER BY month, cost_rank IS NULL, cost_rank, product_code;

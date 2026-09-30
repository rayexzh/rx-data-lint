-- LEFT JOIN keeps findings that do not have a source record.
-- One record can trigger multiple rules; do not add affected counts across rules.
SELECT f.rule, f.severity, COUNT(*) AS findings,
 COUNT(DISTINCT f.row_number) AS affected_records,
 SUM(f.row_number IS NULL) AS unlocated_findings,
 COUNT(DISTINCT NULLIF(r.ods_code,'')) AS observed_organisations
FROM findings f LEFT JOIN records r ON r.row_number=f.row_number
GROUP BY f.rule,f.severity ORDER BY findings DESC,f.rule;

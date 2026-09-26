# Validation rule boundaries

This catalog describes the implementation, not a regulatory specification. Official source for future dataset verification: https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price . No new live-data verification is claimed in this revision.

| Rule | What is checked | Limitations / review guidance |
|---|---|---|
| schema.empty | Header absent | Header-only files produce schema.no_records. |
| schema.required_column | Required project fields absent | Checks depending on absent columns are skipped; present blank values remain errors. |
| schema.legacy_column | Recognized aliases mapped | Alias coverage is limited; Duplicate or ambiguous headers block row checking and normalized export. |
| schema.row_width | Field count differs from header | Extra fields are omitted in normalized export; retain and review the original input. |
| value.year_month | YYYY-MM or YYYYMM month format | Does not verify release dates or submission periods. |
| value.ods_code | 3–5 uppercase alphanumeric characters | Syntax heuristic only; no lookup of real organizations. |
| value.snomed_code | 6–18 digits | No checksum, dm+d lookup, active-status or product-type validation. |
| value.product_name | Nonblank name | Does not verify correspondence to the identifier. |
| value.numeric | Finite floating point number after comma removal | Comma removal is permissive, not locale-aware. Not exact financial arithmetic. |
| value.negative | Negative quantity or cost | Stock adjustments may be legitimate. |
| row.duplicate_key | Same parsed month, ODS and product ID | Candidate duplicates, not automatic deletion instructions. Requires syntactically valid key. |
| series.missing_month | Organization gaps within the file-wide observed range | File filtering, opening/closure or reporting scope may explain gaps; not proof of missing submissions. Skips if fewer than two distinct valid months. |
| series.extreme_quantity | Greater than 20 times product median | Project heuristic, not an official threshold. Requires four positive observations; pools organizations and months, so size differences may explain flags. |

## Report interpretation

The experimental score subtracts fixed penalties per finding and saturates at zero. It is not a correctness percentage or a comparable rate across differently sized files. Distinct affected records exclude findings without row numbers; those findings are counted separately. Logical CSV record numbers include the header and can differ from physical text lines for multiline fields.

SHA-256 identifies the bytes checked, including BOM/newlines. It does not prove who created a file, that its contents are true, or that a report has not been edited. Check time is the local machine's UTC clock, not a trusted timestamp or a tamper-proof audit trail.

## Coverage update

JSON/HTML reports include executed, skipped and not_applicable checks with counts and reasons. Numeric checks are per column. Series counts refer to eligible organization groups or product observations, not all input records. The normalized export is now named normalized-scmd.csv; callers should use the returned paths. Header conflicts and absent headers produce reports only, with all remaining checks explicitly marked skipped.

Each export creates a unique run-* subdirectory inside the selected output directory. Previous exports are preserved, so a blocked run cannot accidentally inherit an earlier CSV. Export is not transactional: an interrupted or failed write may leave an incomplete run directory; only a successful return confirms completion.

CLI exit codes: 0 means a completed assessment without errors (warnings may still exist); 1 means validation errors, blocked/partial assessment or no data; 2 means an input, encoding, CSV parsing or output I/O failure. Exit 0 is not proof of correctness or compliance.

## Missing indicative cost (ruleset 0.2.2)

Blank or whitespace-only INDICATIVE_COST cells are value.missing_cost warnings, not malformed-number errors. Missing required columns remain schema errors; nonblank invalid or nonfinite numbers remain errors. Missing costs are preserved, never imputed as zero. This severity is a project screening decision, not an official declaration that missing costs are acceptable. Cost completeness is reported by record count, not expenditure; the cause of missingness is unknown. A completed assessment or zero errors does not establish fitness for cost analysis.

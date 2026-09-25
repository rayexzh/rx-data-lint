# Validation rule boundaries

This catalog describes the implementation, not a regulatory specification. Official source for future dataset verification: https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price . No new live-data verification is claimed in this revision.

| Rule | What is checked | Limitations / review guidance |
|---|---|---|
| schema.empty | Header absent | A header-only file is not currently flagged as empty data. |
| schema.required_column | Required project fields absent | Row checks currently still execute and may produce consequential errors. |
| schema.legacy_column | Recognized aliases mapped | Alias coverage is limited; duplicate/ambiguous headers need further handling. |
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

# NHS Medicines Analytics — companion case study

[简体中文](README.zh-CN.md)

[SQL walkthrough (Chinese)](SQL_LESSON.zh-CN.md) · [Power BI setup (Chinese, with English summary)](powerbi/START.zh-CN.md).

To reproduce the static PNG/SVG figures, install optional chart dependencies with `python -m pip install -r analysis/requirements-charts.txt`, then run `python analysis/plot_analysis.py analysis/output/202607 --month 2026-07 --output analysis/figures/202607`. The desktop application and SQL pipeline do not require matplotlib. Figure metadata records source provenance. The Power Query import preview has been confirmed in Power BI Desktop by a user-provided screenshot; interactive visuals and a saved PBIX remain pending.

This companion to RxDataLint demonstrates a reproducible CSV → quality review → SQLite → SQL summary workflow. Python 3.10+ is required; no additional packages or paid services are needed. It runs locally. Generated CSVs are ready for Power BI import; a Power BI report is not bundled.

## Run from the repository root

Synthetic example:

```powershell
python analysis/run_analysis.py examples/sample_scmd.csv --output analysis/output/sample --source-url synthetic
```

July 2026 case study (replace the input path if needed):

```powershell
python analysis/run_analysis.py "D:/xiazai/scmd_provisional_202607.csv" --output analysis/output/202607 --source-url "https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753"
```

Choose a **new output folder** for each run. Existing folders are refused to preserve previous results. An interrupted run can leave a partial folder; only use outputs from a successfully completed run with `manifest.json` and `SUMMARY.md` present. Each run builds a snapshot from one input CSV; files are not appended to an existing database. Large files inherit the validator's in-memory processing requirements.

## Questions and outputs

| SQL file | Question / grain |
|---|---|
| 01_monthly_overview.sql | What is represented in each observed month? One row per month. |
| 02_product_costs.sql | Which VMP codes have the highest known net indicative cost? Month × product, with DENSE_RANK. |
| 03_organisation_coverage.sql | How many records/products and known costs appear per organisation? Month × ODS code. |
| 04_findings_by_rule.sql | Which review rules trigger? A LEFT JOIN retains unlocated findings. |
| 05_cost_sensitivity.sql | How would dropping negative cost records change reported totals? Month-level scenario. |

The output contains `medicines.sqlite`, five CSV summaries, a bilingual `SUMMARY.md`, standalone `REPORT.en.html` and `REPORT.zh-CN.html`, and `manifest.json` with input SHA-256, source URL, validator/ruleset versions, time and rule coverage. Query files are readable learning materials. In SQLite, try:

```sql
SELECT month, ods_code, product_code, cost_gbp, cost_status
FROM records ORDER BY row_number LIMIT 10;
```

## Model and metric dictionary

`source` (one input snapshot) → `records` (one logical CSV record, keyed by row number including the header) → `findings` (zero or more review prompts). File-level findings have no row link. Original cell strings and original headers are retained in `raw_json`; identifiers stay TEXT.

- `cost_status`: known finite number, missing blank, or invalid nonblank value. Missing and invalid costs become SQL NULL, never zero. SQL SUM omits NULL; an all-NULL group's sum stays NULL.
- `known_net_indicative_cost_gbp`: sum of available finite costs, including negative values. It is not actual purchasing expenditure or a complete cost estimate. SQL REAL uses floating point; totals are rounded for display, not suitable for ledger reconciliation.
- `known_cost_record_percent`: known-cost record count / total record count × 100. This is **not** coverage by expenditure. Recompute weighted percentages when combining groups.
- Candidate duplicates and records with warnings/errors remain in all summaries. Findings indicate what needs review; no row is automatically certified, deleted or corrected.
- Observed organisation/product counts describe the supplied file. They do not establish national coverage, quality of care, efficiency or market share. Blank codes do not count as distinct codes; nonblank malformed codes remain available for review.
- Quantities are retained with their UDFS units in SQLite and are not summed across products or units.
- Invalid months are retained as a NULL group. July alone cannot establish a trend. Multi-month comparisons also require coverage and comparability review.
- CSV text beginning with spreadsheet formula characters is prefixed with an apostrophe for safer spreadsheet import. SQL values and numeric negatives are unchanged.

## Power BI handoff

Import the five generated CSVs using **Get data → Text/CSV**. Set `month`, `ods_code` and `product_code` to Text (especially long SNOMED identifiers), counts to Whole number, cost to Decimal number, and percentages to Decimal number. These percentages are already on a 0–100 scale: do not apply percentage formatting that multiplies by 100. Keep empty numeric cells null.

Start with two pages: (1) monthly overview, Top N product costs and organisation coverage; (2) missing/invalid costs, rule findings and negative-cost sensitivity. Use each summary as an independent table, avoiding many-to-many joins and summing distinct counts across groups. Keep the month context consistent across visuals; independent tables do not automatically share slicers. Use a single-month selection initially. Display the source, provisional status and metric limitations. No PBIX or live dashboard is claimed in this version.

## Sources and licence

The [NHSBSA July 2026 resource and dictionary](https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753) identify this as provisional SCMD with indicative price, licensed under [OGL v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). Contains public sector information licensed under the Open Government Licence v3.0. Source: NHS Business Services Authority. This independent analysis does not imply NHS/NHSBSA endorsement.

Download the source separately. Local input/output folders and SQLite files are ignored by Git. Source data licensing is separate from the repository's MIT code licence.

## Verify an analysis run

Run `python analysis/verify_analysis.py analysis/output/202607` after generating a new analysis. The manifest records SHA-256 hashes for the database, five CSV summaries, bilingual summary and HTML reports. Missing or changed files produce a nonzero exit code. Older outputs must be regenerated to obtain artifact hashes. This checks consistency with the local manifest; it does not authenticate the manifest, certify source accuracy or establish regulatory compliance.

## Desktop analysis launcher

On Windows, double-click `run_analysis_desktop.bat` in the repository root, or run `python analysis/desktop.py`. Select the SCMD CSV, enter its official source URL (`synthetic` for generated examples), then click **Generate & verify** and choose a parent output folder. Each run creates its own new subfolder, keeping earlier runs intact. Processing runs in the background; the window shows completion or failure and opens the results folder on request. No data is uploaded. Python 3.10+ with Tkinter is required. This launcher is separate from the released checker executable; offline report charts are generated without extra packages; a PBIX is not generated.

## Shareable offline report

Each new run generates Chinese and English HTML reports with monthly cost completeness, an inline cost-sensitivity chart, rule-level findings and review guidance, and source/version metadata. Open either file in a browser; the desktop launcher provides report buttons. All styling and charts are embedded, with no scripts or external assets. Keep both HTML files together to use the language link, or share either one independently. Review source metadata and aggregates before sharing. Browser printing can save a PDF, but PDF layout is not automatically verified.

Reports are included in format-v2 artifact hashes. Previous hashed runs remain checkable, but must be regenerated to obtain the new reports. Null costs and invalid-month groups remain explicit; the report does not automatically correct data or certify compliance.

"""Report and cleaned-data exporters."""

from __future__ import annotations

import csv
import html
import json
import tempfile
from pathlib import Path

from .schema import CANONICAL_COLUMNS
from .validator import ValidationResult


def write_outputs(result: ValidationResult, output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    # A separate run directory prevents stale CSVs from accompanying a new,
    # blocked report, and preserves evidence from previous exports.
    destination = Path(tempfile.mkdtemp(prefix="run-", dir=root))

    json_path = destination / "quality-report.json"
    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    paths = {"json": json_path}
    if not result.export_blocked:
        csv_path = destination / "normalized-scmd.csv"
        with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
            writer.writeheader()
            writer.writerows(result.cleaned_rows)
        paths["csv"] = csv_path

    html_path = destination / "quality-report.html"
    html_path.write_text(_html_report(result), encoding="utf-8")
    paths["html"] = html_path
    return paths


def _html_report(result: ValidationResult) -> str:
    rows = []
    for issue in result.issues:
        rows.append(
            "<tr>"
            f"<td><span class='badge {issue.severity}'>{html.escape(issue.severity)}</span></td>"
            f"<td>{html.escape(issue.rule)}</td>"
            f"<td>{issue.row or ''}</td>"
            f"<td>{html.escape(issue.column or '')}</td>"
            f"<td>{html.escape(issue.message)}</td>"
            f"<td>{html.escape(issue.guidance or '')}</td>"
            "</tr>"
        )
    issue_rows = "".join(rows) or "<tr><td colspan='6'>No issues detected.</td></tr>"
    counts = result.severity_counts
    provenance = result.to_dict()["provenance"]
    evidence = "".join(
        f"<dt>{html.escape(key)}</dt><dd>{html.escape(str(value))}</dd>"
        for key, value in provenance.items()
    )
    coverage = "".join("<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in
        (c.rule, c.column or "", c.status, c.checked_count, c.reason)) + "</tr>" for c in result.checks)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>RxDataLint quality report</title>
<style>
body{{font:15px system-ui,sans-serif;margin:0;background:#f4f7f6;color:#17231f}}main{{max-width:1180px;margin:40px auto;padding:0 24px}}
h1{{margin-bottom:4px}}.meta{{color:#5b6863}}.cards{{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}}
.card{{background:white;border:1px solid #dce5e1;border-radius:12px;padding:18px;min-width:140px}}.score{{font-size:34px;font-weight:700;color:#0b6b50}}
table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:10px;border-bottom:1px solid #e5ebe8;text-align:left;vertical-align:top}}th{{background:#eaf2ef}}
.badge{{padding:3px 8px;border-radius:20px;font-weight:650}}.error{{background:#fee2e2;color:#991b1b}}.warning{{background:#fef3c7;color:#92400e}}.info{{background:#dbeafe;color:#1e40af}}
</style></head><body><main><h1>RxDataLint quality report</h1><p class="meta">{html.escape(result.source)}</p>
<p>No findings means no current rules triggered, not proof of correctness or compliance.
The experimental score is not a percentage of correct records.</p>
<p>Normalized CSV export does not automatically correct flagged values. Row numbers identify logical CSV records, including the header.</p>
<p>Assessment: {result.assessment}. Normalized export available: {not result.export_blocked}.</p>
<div class="cards"><div class="card"><div>Affected records</div><div class="score">{result.affected_row_count}</div></div>
<div class="card"><div>Rows checked</div><div class="score">{result.row_count}</div></div>
<div class="card"><div>Errors</div><div class="score">{counts['error']}</div></div>
<div class="card"><div>Warnings</div><div class="score">{counts['warning']}</div></div></div>
<p>Distinct records with findings: {result.affected_row_count}. Findings without a record number: {sum(issue.row is None for issue in result.issues)}.</p>
<details><summary>Input and execution evidence</summary><dl style="overflow-wrap:anywhere">{evidence}</dl></details>
<table><thead><tr><th>Severity</th><th>Rule</th><th>Row</th><th>Column</th><th>Finding</th><th>Guidance</th></tr></thead>
<tbody>{issue_rows}</tbody></table><h2>Check coverage</h2><p>Counts are records, values or groups depending on the rule. Executed does not mean passed; review findings above.</p><table><tr><th>Rule</th><th>Column</th><th>Status</th><th>Checked</th><th>Reason</th></tr>{coverage}</table></main></body></html>"""

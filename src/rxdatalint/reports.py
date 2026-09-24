"""Report and cleaned-data exporters."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from .schema import CANONICAL_COLUMNS
from .validator import ValidationResult


def write_outputs(result: ValidationResult, output_dir: str | Path) -> dict[str, Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    json_path = destination / "quality-report.json"
    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    csv_path = destination / "cleaned-scmd.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        writer.writerows(result.cleaned_rows)

    html_path = destination / "quality-report.html"
    html_path.write_text(_html_report(result), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "html": html_path}


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
<div class="cards"><div class="card"><div>Quality score</div><div class="score">{result.score}</div></div>
<div class="card"><div>Rows checked</div><div class="score">{result.row_count}</div></div>
<div class="card"><div>Errors</div><div class="score">{counts['error']}</div></div>
<div class="card"><div>Warnings</div><div class="score">{counts['warning']}</div></div></div>
<table><thead><tr><th>Severity</th><th>Rule</th><th>Row</th><th>Column</th><th>Finding</th><th>Guidance</th></tr></thead>
<tbody>{issue_rows}</tbody></table></main></body></html>"""


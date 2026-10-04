"""Review summaries and contextual finding exports; never modify source data."""

from collections import defaultdict
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile

from .validator import ValidationResult, Issue


def record_for(result: ValidationResult, issue: Issue) -> dict[str, str]:
    if issue.row is not None and 0 <= issue.row - 2 < len(result.cleaned_rows):
        return result.cleaned_rows[issue.row - 2]
    return {}


def finding_group(result: ValidationResult, issue: Issue, dimension: str) -> tuple[str, str]:
    """Return a stable key and readable label without guessing missing identities."""
    if dimension == "rule":
        return issue.rule, issue.rule
    if dimension not in ("organisation", "product"):
        raise ValueError(f"Unknown finding group dimension: {dimension}")
    record = record_for(result, issue)
    if not record:
        return "__unlocated__", "(No source row)"
    if dimension == "organisation":
        code = record.get("ODS_CODE", "").strip()
        return (f"ods:{code}", code) if code else ("__missing__", "(Blank ODS_CODE)")
    code = record.get("VMP_SNOMED_CODE", "").strip()
    name = record.get("VMP_PRODUCT_NAME", "").strip()
    if code:
        return f"code:{code}", f"{name or '(Unnamed medicine)'} · {code}"
    if name:
        return f"name:{name}", f"{name} (no product code)"
    return "__missing__", "(Blank product identity)"


def group_findings(result: ValidationResult, issues: list[Issue], dimension: str) -> list[dict]:
    """Count findings and distinct located rows in the supplied review scope."""
    groups: dict[str, dict] = {}
    for issue in issues:
        key, label = finding_group(result, issue, dimension)
        group = groups.setdefault(key, {"key": key, "label": label, "findings": 0,
                                        "rows": set(), "unlocated_findings": 0})
        group["findings"] += 1
        if record_for(result, issue):
            group["rows"].add(issue.row)
        else:
            group["unlocated_findings"] += 1
    return sorted(({key: value for key, value in group.items() if key != "rows"} |
                   {"affected_records": len(group["rows"])} for group in groups.values()),
                  key=lambda group: (-group["findings"], group["label"].casefold()))


def summarise(result: ValidationResult) -> list[dict]:
    groups = defaultdict(list)
    for issue in result.issues:
        groups[issue.rule].append(issue)
    summaries = []
    for rule, issues in sorted(groups.items()):
        records = [record_for(result, i) for i in issues]
        summaries.append({
            "rule": rule, "findings": len(issues),
            "affected_records": len({i.row for i in issues if record_for(result, i)}),
            "unlocated_findings": sum(not record_for(result, i) for i in issues),
            "organisations": len({r.get("ODS_CODE") for r in records if r.get("ODS_CODE")}),
            "products": len({r.get("VMP_SNOMED_CODE") for r in records if r.get("VMP_SNOMED_CODE")}),
        })
    return summaries


def write_filtered_findings(result, issues, output_dir, *, query="", category="all", group_by="", group_key=""):
    """Export one row per selected finding, not a cleaned dataset or full report."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix="findings-", dir=root))
    contextual = [{**asdict(i), "record": record_for(result, i)} for i in issues]
    payload = {
        "scope": "filtered_findings", "query": query, "category": category,
        "group_by": group_by, "group_key": group_key,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": result.source_sha256, "source": result.source,
        "total_findings": len(result.issues), "selected_findings": len(issues),
        "note": "One item per finding. Not a complete quality report. JSON preserves original text; CSV prefixes spreadsheet formula-like text with an apostrophe.",
        "findings": contextual,
    }
    json_path = destination / "filtered-findings.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = destination / "filtered-findings.csv"
    context_fields = ("YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE", "VMP_PRODUCT_NAME")
    issue_fields = ("rule", "severity", "row", "column", "value", "message", "guidance")

    def cell(value):
        if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + value
        return value

    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=(*context_fields, *issue_fields))
        writer.writeheader()
        for item in contextual:
            row = {key: item["record"].get(key, "") for key in context_fields}
            row.update({key: item[key] for key in issue_fields})
            writer.writerow({key: cell(value) for key, value in row.items()})
    return {"json": json_path, "csv": csv_path}

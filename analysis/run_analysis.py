"""Build a reproducible, local SCMD SQLite case study using the RxDataLint rules."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rxdatalint.validator import validate_csv, MONTH_RE, RULESET_VERSION
from rxdatalint import __version__
from rxdatalint.schema import REQUIRED_COLUMNS
from html_report import render_reports


def number(value):
    try:
        result = float(value.replace(",", "").strip())
        return result if math.isfinite(result) else None
    except (ValueError, AttributeError):
        return None


def safe_cell(value):
    # Protect spreadsheet imports of text without changing numeric negatives.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def build(source: Path, output: Path, source_url: str):
    if output.exists():
        raise ValueError("Output folder already exists. Choose a new folder to preserve earlier results.")
    content = source.read_bytes()
    result = validate_csv(source)
    if hashlib.sha256(content).hexdigest() != result.source_sha256:
        raise ValueError("Source changed during validation. Please run again.")
    if result.export_blocked or not result.row_count or set(REQUIRED_COLUMNS) - set(result.columns):
        raise ValueError("CSV structure is blocked or empty. Review it in RxDataLint first.")
    output.mkdir(parents=True)
    db = sqlite3.connect(output / "medicines.sqlite")
    db.execute("PRAGMA foreign_keys=ON")
    try:
        db.executescript((Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))
        db.execute("INSERT INTO source VALUES (1,?,?,?,?,?)", (
            source.name, source_url, result.source_sha256, result.checked_at_utc, result.row_count))
        raw = csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=""))
        for row_number, (original, row) in enumerate(zip(raw, result.cleaned_rows, strict=True), 2):
            match = MONTH_RE.fullmatch(row["YEAR_MONTH"])
            month = f"{match[1]}-{match[2]}" if match else None
            cost = number(row["INDICATIVE_COST"])
            status = "missing" if not row["INDICATIVE_COST"] else "invalid" if cost is None else "known"
            db.execute("INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                row_number, 1, month, row["ODS_CODE"], row["VMP_SNOMED_CODE"],
                row["VMP_PRODUCT_NAME"], cost, status,
                number(row["TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE"]),
                row["VMP_UDFS_UNIT_OF_MEASURE_NAME"], json.dumps(original, ensure_ascii=False)))
        db.executemany("INSERT INTO findings(rule,severity,row_number,column_name,message) VALUES (?,?,?,?,?)",
                       [(i.rule, i.severity, i.row, i.column, i.message) for i in result.issues])
        db.commit()
        metadata = {
            "analysis_format_version": 2,
            "source_file": source.name, "source_url": source_url,
            "source_sha256": result.source_sha256, "checked_at_utc": result.checked_at_utc,
            "tool_version": __version__, "ruleset_version": RULESET_VERSION,
            "row_count": result.row_count, "finding_counts": result.severity_counts,
            "rule_coverage": [asdict(c) for c in result.checks],
            "months": [r[0] for r in db.execute("SELECT DISTINCT month FROM records WHERE month IS NOT NULL ORDER BY month")],
            "policy": "All source rows retained, including duplicate candidates and negatives. Missing/invalid costs remain NULL. SQL REAL totals are approximate, rounded only for presentation. Row numbers include the header. Source data is provisional."
        }
        for query in sorted((Path(__file__).parent / "sql").glob("*.sql")):
            cursor = db.execute(query.read_text(encoding="utf-8"))
            with (output / f"{query.stem}.csv").open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow([c[0] for c in cursor.description])
                writer.writerows([[safe_cell(v) for v in row] for row in cursor])
        monthly = list(db.execute("SELECT month,COUNT(*),COUNT(cost_gbp),SUM(cost_gbp) FROM records GROUP BY month ORDER BY month"))
        lines = ["# SCMD local analysis / 本地分析摘要", "", f"Source: {source.name}", f"Source URL: {source_url}",
                 f"SHA-256: {result.source_sha256}", "", "| Month / 月份 | Records / 记录 | Known cost / 成本有效记录 | Known net indicative cost GBP / 已知净指示性成本 |", "|---|---:|---:|---:|"]
        for month, count, known, net in monthly:
            lines.append(f"| {month or 'Invalid month / 无效月份'} | {count:,} | {known:,} | {net:,.2f} |" if net is not None else f"| {month} | {count:,} | 0 | unavailable |")
        lines += ["", "Only one valid month: no trend conclusion. / 仅一个有效月份，不能得出趋势结论。" if len(metadata["months"]) == 1 else "Monthly totals are descriptive; organisation coverage may change. / 月度总额仅作描述，机构覆盖可能变化。",
                  "", "Known cost excludes missing/invalid amounts and retains negative adjustments; it is not actual procurement expenditure. / 已知成本不含缺失或无效金额，保留负数调整，不代表实际采购支出。",
                  "Findings are review prompts. Candidate duplicates are retained; findings counts are not defective-record counts. / 提示用于复核，疑似重复仍保留，提示数不等于错误记录数。"]
        (output / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        render_reports(db, metadata, output)
        db.close()
        metadata["artifacts"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(output.iterdir()) if p.is_file() and p.name != "manifest.json"}
        (output / "manifest.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        return metadata
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-url", required=True, help="Official resource URL; use synthetic for examples")
    args = parser.parse_args()
    try:
        info = build(args.csv, args.output, args.source_url)
    except (ValueError, OSError, sqlite3.Error, UnicodeError) as exc:
        parser.exit(1, f"Analysis failed: {exc}\n")
    print(f"Created {args.output.resolve()} | {info['row_count']} records | months: {info['months']}")


if __name__ == "__main__":
    main()

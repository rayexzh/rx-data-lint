"""Streaming-friendly validation rules for NHSBSA SCMD CSV files."""

from __future__ import annotations

import csv
import hashlib
import io
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .schema import CANONICAL_COLUMNS, COLUMN_ALIASES, REQUIRED_COLUMNS, normalise_header
from . import __version__

RULESET_VERSION = "0.2.2"

MONTH_RE = re.compile(r"^(\d{4})-?(0[1-9]|1[0-2])$")
ODS_RE = re.compile(r"^[A-Z0-9]{3,5}$")
SNOMED_RE = re.compile(r"^\d{6,18}$")


@dataclass(frozen=True)
class Issue:
    rule: str
    severity: str
    message: str
    row: int | None = None
    column: str | None = None
    value: str | None = None
    guidance: str | None = None


@dataclass
class RuleCheck:
    rule: str
    status: str
    checked_count: int = 0
    reason: str = ""
    column: str | None = None


@dataclass
class ValidationResult:
    source: str
    row_count: int
    columns: list[str]
    issues: list[Issue]
    cleaned_rows: list[dict[str, str]]
    source_sha256: str = ""
    source_size_bytes: int = 0
    checked_at_utc: str = ""
    checks: list[RuleCheck] = field(default_factory=list)
    export_blocked: bool = False

    @property
    def assessment(self) -> str:
        if self.export_blocked:
            return "blocked"
        if not self.row_count:
            return "no_data"
        if any(c.status == "skipped" for c in self.checks):
            return "partial"
        return "completed"

    @property
    def affected_row_count(self) -> int:
        return len({issue.row for issue in self.issues if issue.row is not None})

    @property
    def severity_counts(self) -> dict[str, int]:
        counts = Counter(issue.severity for issue in self.issues)
        return {level: counts.get(level, 0) for level in ("error", "warning", "info")}

    @property
    def score(self) -> int:
        weights = {"error": 12, "warning": 4, "info": 1}
        penalty = sum(weights[issue.severity] for issue in self.issues)
        return max(0, 100 - min(100, penalty))

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "assessment": self.assessment,
            "normalized_export_available": not self.export_blocked,
            "checks": [asdict(check) for check in self.checks],
            "provenance": {
                "tool_version": __version__,
                "ruleset_version": RULESET_VERSION,
                "source_sha256": self.source_sha256,
                "source_size_bytes": self.source_size_bytes,
                "checked_at_utc": self.checked_at_utc,
            },
            "affected_row_count": self.affected_row_count,
            "cost_completeness": self.cost_completeness,
            "non_row_finding_count": sum(issue.row is None for issue in self.issues),
            "interpretation": "No findings means no current rules triggered, not proof of correctness or compliance. Exported CSV is normalized, not automatically corrected. Row numbers are logical CSV records including the header.",
            "row_count": self.row_count,
            "columns": self.columns,
            "quality_score": self.score,
            "severity_counts": self.severity_counts,
            "issues": [asdict(issue) for issue in self.issues],
        }

    @property
    def cost_completeness(self) -> dict:
        available = not self.export_blocked and "INDICATIVE_COST" in self.columns and self.row_count > 0
        missing = sum(not row["INDICATIVE_COST"] for row in self.cleaned_rows) if available else None
        return {
            "assessed": available,
            "missing_rows": missing,
            "missing_percent": round(100 * missing / self.row_count, 4) if available else None,
            "note": "Missing cost is not zero. Nonblank costs may still be invalid; review findings. Completeness by record count is not coverage by expenditure.",
        }


def _parse_number(value: str) -> float | None:
    try:
        number = float(value.replace(",", "").strip())
        return number if math.isfinite(number) else None
    except (AttributeError, ValueError):
        return None


def _month_index(value: str) -> int | None:
    match = MONTH_RE.fullmatch(value.strip())
    if not match:
        return None
    return int(match.group(1)) * 12 + int(match.group(2)) - 1


def _canonicalise(row: dict[str, str], header_map: dict[str, str]) -> dict[str, str]:
    output = {column: "" for column in CANONICAL_COLUMNS}
    for original, value in row.items():
        if original is None:
            continue
        canonical = header_map.get(original, normalise_header(original))
        if canonical in output:
            output[canonical] = (value or "").strip()
    return output


def validate_csv(path: str | Path) -> ValidationResult:
    source = Path(path)
    issues: list[Issue] = []
    cleaned_rows: list[dict[str, str]] = []
    # Hash and parse the same byte snapshot, including BOM and original newlines.
    content = source.read_bytes()
    provenance = {
        "source_sha256": hashlib.sha256(content).hexdigest(),
        "source_size_bytes": len(content),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    checks = []
    counts = Counter()
    dependencies = {
        "value.year_month": ["YEAR_MONTH"],
        "value.ods_code": ["ODS_CODE"],
        "value.snomed_code": ["VMP_SNOMED_CODE"],
        "value.product_name": ["VMP_PRODUCT_NAME"],
        "value.missing_cost": ["INDICATIVE_COST"],
        "row.duplicate_key": ["YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE"],
        "series.missing_month": ["YEAR_MONTH", "ODS_CODE"],
        "series.extreme_quantity": ["VMP_SNOMED_CODE", "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE"],
    }
    numeric_columns = ["TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE", "TOTAL_QUANTITY_IN_VMP_UNIT_DOSE_UNIT_OF_MEASURE", "INDICATIVE_COST"]
    def blocked_checks(reason, completed):
        schema_rules = ("schema.empty", "schema.header_conflict", "schema.required_column",
                        "schema.legacy_column", "schema.row_width", "schema.no_records")
        return [RuleCheck(rule, "skipped", reason=reason) for rule in schema_rules if rule not in completed] + [RuleCheck(rule, "skipped", reason=reason) for rule in dependencies] + [
            RuleCheck(rule, "skipped", reason=reason, column=column)
            for column in numeric_columns for rule in ("value.numeric", "value.negative")]

    with io.StringIO(content.decode("utf-8-sig"), newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return ValidationResult(str(source), 0, [], [Issue(
                "schema.empty", "error", "The CSV has no header row."
            )], [], **provenance, checks=[RuleCheck("schema.empty", "executed", 1)] + blocked_checks("No header", {"schema.empty"}), export_blocked=True)

        header_map = {name: normalise_header(name) for name in reader.fieldnames}
        canonical_headers = list(dict.fromkeys(header_map.values()))
        conflicts = [name for name, count in Counter(normalise_header(n) for n in reader.fieldnames).items() if count > 1]
        checks.extend([RuleCheck("schema.empty", "executed", 1), RuleCheck("schema.header_conflict", "executed", len(reader.fieldnames))])
        if conflicts:
            issues.extend(Issue("schema.header_conflict", "error", f"Multiple headers map to {name}.", column=name,
                                guidance="Resolve duplicate headers before checking or exporting.") for name in conflicts)
            return ValidationResult(str(source), 0, canonical_headers, issues, [], **provenance,
                                    checks=checks + blocked_checks("Ambiguous headers", {c.rule for c in checks}), export_blocked=True)
        missing = [column for column in REQUIRED_COLUMNS if column not in canonical_headers]
        for column in missing:
            issues.append(Issue(
                "schema.required_column",
                "error",
                f"Required SCMD column is missing: {column}",
                column=column,
                guidance="Check the NHSBSA release schema or map the source column to this field.",
            ))

        checks.extend([RuleCheck("schema.required_column", "executed", len(REQUIRED_COLUMNS)), RuleCheck("schema.legacy_column", "executed", len(reader.fieldnames))])
        for old, new in COLUMN_ALIASES.items():
            if old in (name.strip().upper() for name in reader.fieldnames):
                issues.append(Issue(
                    "schema.legacy_column",
                    "info",
                    f"Legacy column {old} was mapped to {new}.",
                    column=old,
                    guidance="The alias is supported, but new exports should use the June 2026 schema.",
                ))

        duplicate_keys: dict[tuple[str, str, str], int] = {}
        months_by_org: dict[str, set[int]] = defaultdict(set)
        quantities_by_product: dict[str, list[tuple[int, float]]] = defaultdict(list)

        for row_number, raw in enumerate(reader, start=2):
            if None in raw or any(value is None for value in raw.values()):
                issues.append(Issue(
                    "schema.row_width", "error", "Record has a different number of fields than the header.",
                    row_number, guidance="Review the original record. Extra fields are not included in the normalized export.",
                ))
            row = _canonicalise(raw, header_map)
            cleaned_rows.append(row)

            month = row["YEAR_MONTH"]
            month_idx = _month_index(month)
            if "YEAR_MONTH" in canonical_headers and month_idx is None:
                issues.append(Issue(
                    "value.year_month", "error", "YEAR_MONTH must use YYYY-MM or YYYYMM.",
                    row_number, "YEAR_MONTH", month,
                ))

            ods = row["ODS_CODE"].upper()
            row["ODS_CODE"] = ods
            if "ODS_CODE" in canonical_headers and not ODS_RE.fullmatch(ods):
                issues.append(Issue(
                    "value.ods_code", "error", "ODS_CODE is missing or has an unexpected format.",
                    row_number, "ODS_CODE", ods,
                ))
            elif month_idx is not None and ODS_RE.fullmatch(ods):
                months_by_org[ods].add(month_idx)

            snomed = row["VMP_SNOMED_CODE"]
            if "VMP_SNOMED_CODE" in canonical_headers and not SNOMED_RE.fullmatch(snomed):
                issues.append(Issue(
                    "value.snomed_code", "error", "VMP_SNOMED_CODE should contain 6 to 18 digits.",
                    row_number, "VMP_SNOMED_CODE", snomed,
                ))

            if "VMP_PRODUCT_NAME" in canonical_headers and not row["VMP_PRODUCT_NAME"]:
                issues.append(Issue(
                    "value.product_name", "error", "VMP_PRODUCT_NAME is blank.",
                    row_number, "VMP_PRODUCT_NAME", "",
                ))

            key = (str(month_idx), ods, snomed)
            if month_idx is not None and ODS_RE.fullmatch(ods) and SNOMED_RE.fullmatch(snomed):
                counts["row.duplicate_key"] += 1
                if key in duplicate_keys:
                    issues.append(Issue(
                        "row.duplicate_key", "warning",
                        f"Possible duplicate of row {duplicate_keys[key]} for month, trust and VMP.",
                        row_number,
                        guidance="Confirm whether rows represent distinct records before aggregating.",
                    ))
                else:
                    duplicate_keys[key] = row_number

            for column in (
                "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE",
                "TOTAL_QUANTITY_IN_VMP_UNIT_DOSE_UNIT_OF_MEASURE",
                "INDICATIVE_COST",
            ):
                if column not in canonical_headers:
                    continue
                value = row[column]
                if column == "INDICATIVE_COST" and not value:
                    issues.append(Issue(
                        "value.missing_cost", "warning", "Indicative cost is missing; cost analysis is incomplete.",
                        row_number, column, value,
                        "Do not replace missing cost with zero or discard other usable fields. "
                        "Report missing-cost coverage when aggregating. The reason for missingness is unknown. "
                        "参考费用缺失：不要补零或直接删除整行；费用汇总需披露缺失情况，缺失原因尚未确认。",
                    ))
                    continue
                if not value and column == "TOTAL_QUANTITY_IN_VMP_UNIT_DOSE_UNIT_OF_MEASURE":
                    continue
                counts[("value.numeric", column)] += 1
                number = _parse_number(value)
                if number is not None:
                    counts[("value.negative", column)] += 1
                if number is None:
                    issues.append(Issue(
                        "value.numeric", "error", f"{column} is not numeric.",
                        row_number, column, value,
                    ))
                elif number < 0:
                    issues.append(Issue(
                        "value.negative", "warning", f"{column} contains a negative value.",
                        row_number, column, value,
                        "Negative stock-control adjustments can be valid, but may distort aggregates.",
                    ))
                elif column == "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE" and SNOMED_RE.fullmatch(snomed):
                    quantities_by_product[snomed].append((row_number, number))

        _add_missing_month_issues(months_by_org, issues)
        _add_outlier_issues(quantities_by_product, issues)

    checks.append(RuleCheck("schema.row_width", "executed" if cleaned_rows else "not_applicable", len(cleaned_rows), "" if cleaned_rows else "No data records"))
    checks.append(RuleCheck("schema.no_records", "executed", 1))
    if not cleaned_rows:
        issues.append(Issue("schema.no_records", "warning", "The file has a header but no data records."))
    counts["series.missing_month"] = len(months_by_org) if len(set().union(*months_by_org.values()) if months_by_org else set()) >= 2 else 0
    counts["series.extreme_quantity"] = sum(len(obs) for obs in quantities_by_product.values() if sum(v > 0 for _, v in obs) >= 4)
    for rule, required in dependencies.items():
        absent = [c for c in required if c not in canonical_headers]
        count = len(cleaned_rows) if rule.startswith("value.") else counts[rule]
        status = "skipped" if absent else ("executed" if count else "not_applicable")
        reason = "Missing columns: " + ", ".join(absent) if absent else ("" if count else "No eligible records/groups; see rule prerequisites")
        checks.append(RuleCheck(rule, status, 0 if absent else count, reason))
    for column in numeric_columns:
        for rule in ("value.numeric", "value.negative"):
            count = counts[(rule, column)]
            absent = column not in canonical_headers
            optional = column not in REQUIRED_COLUMNS
            status = ("not_applicable" if optional else "skipped") if absent else ("executed" if count else "not_applicable")
            checks.append(RuleCheck(rule, status, count, "Column absent" if absent else ("" if count else "No eligible values"), column))
    return ValidationResult(
        str(source), len(cleaned_rows), canonical_headers, issues, cleaned_rows, **provenance, checks=checks
    )


def _add_missing_month_issues(months_by_org: dict[str, set[int]], issues: list[Issue]) -> None:
    all_months = set().union(*months_by_org.values()) if months_by_org else set()
    if len(all_months) < 2:
        return
    low, high = min(all_months), max(all_months)
    expected = set(range(low, high + 1))
    for ods, observed in months_by_org.items():
        missing = sorted(expected - observed)
        if missing:
            labels = [f"{index // 12:04d}-{index % 12 + 1:02d}" for index in missing]
            issues.append(Issue(
                "series.missing_month", "warning",
                f"{ods} has {len(missing)} missing month(s): {', '.join(labels[:6])}",
                column="YEAR_MONTH",
                guidance="Check submission history before comparing organisations or trends.",
            ))


def _add_outlier_issues(
    quantities_by_product: dict[str, list[tuple[int, float]]], issues: list[Issue]
) -> None:
    for snomed, observations in quantities_by_product.items():
        positive = [value for _, value in observations if value > 0]
        if len(positive) < 4:
            continue
        median = statistics.median(positive)
        if median <= 0:
            continue
        threshold = median * 20
        for row_number, value in observations:
            if value > threshold:
                issues.append(Issue(
                    "series.extreme_quantity", "warning",
                    f"Quantity {value:g} is more than 20x the product median ({median:g}).",
                    row_number,
                    "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE",
                    str(value),
                    "Treat this as a review flag, not proof of an error.",
                ))

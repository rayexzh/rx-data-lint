"""Streaming-friendly validation rules for NHSBSA SCMD CSV files."""

from __future__ import annotations

import csv
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from .schema import CANONICAL_COLUMNS, COLUMN_ALIASES, REQUIRED_COLUMNS, normalise_header

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
class ValidationResult:
    source: str
    row_count: int
    columns: list[str]
    issues: list[Issue]
    cleaned_rows: list[dict[str, str]]

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
            "row_count": self.row_count,
            "columns": self.columns,
            "quality_score": self.score,
            "severity_counts": self.severity_counts,
            "issues": [asdict(issue) for issue in self.issues],
        }


def _parse_number(value: str) -> float | None:
    try:
        return float(value.replace(",", "").strip())
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
        canonical = header_map.get(original, normalise_header(original))
        if canonical in output:
            output[canonical] = (value or "").strip()
    return output


def validate_csv(path: str | Path) -> ValidationResult:
    source = Path(path)
    issues: list[Issue] = []
    cleaned_rows: list[dict[str, str]] = []

    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return ValidationResult(str(source), 0, [], [Issue(
                "schema.empty", "error", "The CSV has no header row."
            )], [])

        header_map = {name: normalise_header(name) for name in reader.fieldnames}
        canonical_headers = list(dict.fromkeys(header_map.values()))
        missing = [column for column in REQUIRED_COLUMNS if column not in canonical_headers]
        for column in missing:
            issues.append(Issue(
                "schema.required_column",
                "error",
                f"Required SCMD column is missing: {column}",
                column=column,
                guidance="Check the NHSBSA release schema or map the source column to this field.",
            ))

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
            row = _canonicalise(raw, header_map)
            cleaned_rows.append(row)

            month = row["YEAR_MONTH"]
            month_idx = _month_index(month)
            if month_idx is None:
                issues.append(Issue(
                    "value.year_month", "error", "YEAR_MONTH must use YYYY-MM or YYYYMM.",
                    row_number, "YEAR_MONTH", month,
                ))

            ods = row["ODS_CODE"].upper()
            row["ODS_CODE"] = ods
            if not ODS_RE.fullmatch(ods):
                issues.append(Issue(
                    "value.ods_code", "error", "ODS_CODE is missing or has an unexpected format.",
                    row_number, "ODS_CODE", ods,
                ))
            elif month_idx is not None:
                months_by_org[ods].add(month_idx)

            snomed = row["VMP_SNOMED_CODE"]
            if not SNOMED_RE.fullmatch(snomed):
                issues.append(Issue(
                    "value.snomed_code", "error", "VMP_SNOMED_CODE should contain 6 to 18 digits.",
                    row_number, "VMP_SNOMED_CODE", snomed,
                ))

            if not row["VMP_PRODUCT_NAME"]:
                issues.append(Issue(
                    "value.product_name", "error", "VMP_PRODUCT_NAME is blank.",
                    row_number, "VMP_PRODUCT_NAME", "",
                ))

            key = (month, ods, snomed)
            if all(key):
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
                value = row[column]
                if not value and column == "TOTAL_QUANTITY_IN_VMP_UNIT_DOSE_UNIT_OF_MEASURE":
                    continue
                number = _parse_number(value)
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
                elif column == "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE" and snomed:
                    quantities_by_product[snomed].append((row_number, number))

        _add_missing_month_issues(months_by_org, issues)
        _add_outlier_issues(quantities_by_product, issues)

    return ValidationResult(
        str(source), len(cleaned_rows), canonical_headers, issues, cleaned_rows
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

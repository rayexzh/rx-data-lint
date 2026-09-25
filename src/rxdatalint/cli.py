"""Command-line interface for RxDataLint."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .reports import write_outputs
from .validator import validate_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check NHS SCMD CSV data quality locally.")
    parser.add_argument("csv_file", type=Path, help="Path to an SCMD CSV file")
    parser.add_argument("--output", "-o", type=Path, default=Path("outputs/report"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = validate_csv(args.csv_file)
        paths = write_outputs(result, args.output)
    except (OSError, UnicodeError, csv.Error) as error:
        print(f"Unable to complete check/export: {error}", file=sys.stderr)
        return 2
    counts = result.severity_counts
    print(f"Assessment: {result.assessment} | checked {result.row_count} rows | affected records {result.affected_row_count}")
    print(f"Errors {counts['error']} | warnings {counts['warning']} | info {counts['info']}")
    for kind, path in paths.items():
        print(f"{kind}: {path.resolve()}")
    return 1 if counts["error"] or result.assessment != "completed" else 0


if __name__ == "__main__":
    raise SystemExit(main())

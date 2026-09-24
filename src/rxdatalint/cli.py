"""Command-line interface for RxDataLint."""

from __future__ import annotations

import argparse
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
    result = validate_csv(args.csv_file)
    paths = write_outputs(result, args.output)
    counts = result.severity_counts
    print(f"Checked {result.row_count} rows | score {result.score}/100")
    print(f"Errors {counts['error']} | warnings {counts['warning']} | info {counts['info']}")
    for kind, path in paths.items():
        print(f"{kind}: {path.resolve()}")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())


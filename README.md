# RxDataLint

[English](README.md) | [简体中文](README.zh-CN.md)

[![Tests](https://github.com/rayexzh/rx-data-lint/actions/workflows/tests.yml/badge.svg)](https://github.com/rayexzh/rx-data-lint/actions/workflows/tests.yml)

RxDataLint is a local-first data quality workbench for NHS medicines datasets.
The first adapter checks NHSBSA Secondary Care Medicines Data (SCMD) CSV files
before they are used for trend analysis, benchmarking, or Power BI reporting.

This repository is an early, testable prototype. It is not affiliated with the
NHS, NHSBSA, or OpenPrescribing, and a clean report is not proof that data is
clinically or financially correct.

## Why this project exists

Public medicines data can be highly useful and still be easy to misread. Schema
changes, negative stock adjustments, missing submissions, duplicate rows, and
extreme values can materially change a trend or benchmark. RxDataLint adds an
explainable review step between an NHSBSA download and downstream analysis.

The project combines pharmaceutical quality thinking with practical Python and
data-analysis workflows. It aims to help analysts, educators, and learners find
potential problems early without uploading their data to a third-party service.

> **Alpha software:** use only public, synthetic, or appropriately governed
> data. Validate findings against the source documentation before acting on
> them.

## What the prototype checks

- the current NHSBSA SCMD schema and selected pre-June-2026 column aliases;
- invalid months, ODS codes, SNOMED codes, names, and numeric values (including
  both `YYYY-MM` documented dates and `YYYYMM` values returned by the API);
- negative quantities and indicative costs;
- possible duplicate month/trust/product records;
- missing months by Trust in combined files; and
- extreme product quantities using a transparent 20x-median review rule.

It exports a canonical CSV plus JSON and standalone HTML quality reports. All
processing stays on the user's computer.

The desktop interface starts in Chinese and includes an English switch for UK
users. Findings are colour coded, the table scrolls horizontally, and selecting
a finding shows its complete value and guidance below the table.

## Run the desktop program

Python 3.10 or later is required. No third-party runtime dependency is needed.
On Windows, double-click `run_desktop.bat` to launch the program without an
installation step.

In PyCharm, open the repository folder and run the root-level `app.py` file.

Alternatively, install the commands locally:

```powershell
python -m pip install -e .
rx-data-lint-gui
```

Choose `examples/sample_scmd.csv` to see the prototype identify deliberate
quality problems.

## Run from the command line

```powershell
python -m pip install -e .
rx-data-lint examples/sample_scmd.csv --output outputs/demo
```

Each export is saved in a new `run-*` subfolder of your chosen output directory; the application shows the actual file paths. Previous reports are preserved. Header conflicts or missing headers produce HTML/JSON reports without a normalized CSV. CLI exit codes are `0` for completed checks without errors (warnings may exist), `1` for errors or incomplete/no-data assessments, and `2` for input/output failures.

The command exits with status 1 when errors are present, so it can later be
used in automated data pipelines.

Run the dependency-free test suite with:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Project direction

The next release should be driven by user interviews and real SCMD files. The
initial product hypothesis is that analysts need a portable, explainable check
between raw NHSBSA downloads and analysis tools. Candidate additions include
provisional-versus-final comparisons, schema-change detection, product-level
submission anomalies, dm+d validation, and Power BI star-schema export.

## Current limitations

- Rules are screening checks and do not establish that a value is incorrect.
- The score is experimental and is not a clinical, financial, or regulatory
  assessment.
- Large multi-month files are currently processed in memory and may take time.
- dm+d reference validation and provisional-versus-final comparison are not yet
  implemented.

## Data source

SCMD is published by the NHS Business Services Authority under the Open
Government Licence. Refer to the official dataset documentation before drawing
conclusions, especially the caveats around provisional submissions, negative
stock adjustments, and indicative rather than net acquisition costs:

https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price

## Contributing

Bug reports, anonymised examples, proposed validation rules, and documentation
improvements are welcome. Each validation rule should explain what it detects,
why the finding matters, and when a flagged value may still be valid.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and data
handling rules.

## Licence

MIT

## Development progress

See [rule boundaries](docs/RULES.md) and the [v0.2 checklist](docs/V0.2-PLAN.zh-CN.md). Reports now include input SHA-256, byte size, check time, version metadata and distinct affected-record counts. These identify the checked input; they are not a compliance certificate. Processing remains in memory.


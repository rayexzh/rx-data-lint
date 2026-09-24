# Contributing to RxDataLint

RxDataLint is an early open-source prototype. Contributions are welcome from
data analysts, pharmacists, students, developers, and people who work with NHS
medicines data.

## Useful contributions

- reproducible bug reports;
- anonymised or public examples of data-quality problems;
- proposed SCMD validation rules with an authoritative source;
- accessibility, documentation, and translation improvements; and
- performance improvements for large CSV files.

Never submit confidential NHS, patient, staff, supplier, or commercially
sensitive data. Use public or synthetic examples.

## Development

Python 3.10 or later is required. The core has no third-party runtime
dependencies.

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python app.py
```

Each validation rule should state what it detects, why it matters, when the
finding may be valid, and how it is tested. A flag should not be presented as
proof that the source data is wrong.

## Pull requests

Keep changes focused, add or update meaningful tests, and explain any effect on
the exported report. By contributing, you agree that your contribution is
licensed under the MIT License.


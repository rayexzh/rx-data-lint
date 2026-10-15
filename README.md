# RxDataLint

Check an NHS medicines CSV before using it for analysis.

RxDataLint reads NHSBSA hospital medicines data (SCMD) and lists missing costs, invalid values, possible duplicates and other records worth reviewing. Open a finding to see its source row. You can also build local SQL summaries and export reports.

[Windows download](https://github.com/rayexzh/rx-data-lint/releases/tag/v0.4.0-alpha.5) · [中文](README.zh-CN.md) · [Guides](docs/INDEX.md)

## Try it

1. Download and fully extract the ZIP.
2. Open `Start-Checker.bat` and click **Try sample**.
3. Open a finding, check the source row, then export the report if needed.
4. For SQL summaries, open `Start-Analysis.bat`, choose **Use sample**, then **Generate and verify**.

![CSV checker](docs/screenshots/checker-en.png)

A negative quantity may be a stock adjustment. A blank cost is not zero. The app flags these for review; it does not decide that the source is wrong or silently repair it. Indicative cost is not actual purchasing expenditure.

Files are processed on your computer. No account or paid API is needed. Large files are held in memory. The current checks are for SCMD, not every kind of medicines data. The project is independent of the NHS and NHSBSA.

## Run from source

Python 3.10+ with Tkinter:

```powershell
python app.py
python analysis/desktop.py
```

[Check rules](docs/RULES.md) · [SQL guide](analysis/README.md) · [Public-data example](analysis/CASE_STUDY.md) · [Changes](CHANGELOG.md) · [MIT licence](LICENSE)

[BatchScope](https://github.com/rayexzh/batchscope) is a separate app for learning with synthetic batch-quality records.

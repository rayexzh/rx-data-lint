# Two-minute walkthrough / 两分钟上手

For the v0.3 two-program suite, start with [Windows suite guide](WINDOWS-SUITE.md). / v0.3 两个程序的运行包请先阅读[便携包启动说明](WINDOWS-SUITE.md)。

## 简体中文

### 启动
将 Windows ZIP **全部解压**，双击其中的 `RxDataLint.exe`。不要只把 exe 拖出来，它需要旁边的 `_internal` 文件夹。不需要另外安装 Python。当前运行包未签名，属于 Alpha 预发布版。

### 0:00–0:30：载入示例
点击“选择 SCMD CSV”，在解压目录的 `examples` 文件夹选择 `sample_scmd.csv`。不要双击 CSV（那可能打开 Excel）。示例有 8 条记录，故意包含数据问题；程序不是在报告自身运行错误。

### 0:30–1:00：理解问题
点击“问题概览”，查看各规则的提示数、关联记录数、机构数和药品数。一个记录可能触发多条规则，各组不能直接相加。双击规则进入对应列表（会清除先前搜索）。点击一条提示，在下方滚动查看药品、机构编码、月份、原值和处理建议。

### 1:00–1:30：搜索和复核
选择“负数”分类，在搜索框输入药品名或机构编码，按回车。多个词须全部匹配。切换 English 后结果保持一致。搜索仅针对问题及关联记录，不是全部药品目录。负数可能涉及调整，提示并不证明原始数据错误。

### 1:30–2:00：选择正确的导出
- “导出完整报告”：保存全文件检查的 HTML、JSON 和可用时的规范化 CSV，不受筛选影响。
- “导出当前筛选的问题”：保存单独的 CSV 和 JSON，一条提示一行，附药品、机构和月份。JSON 记录搜索条件、选中数量、总提示数与输入哈希。没有匹配项时按钮不可用。
- 每次导出保存到独立文件夹。筛选 CSV 为便于表格软件安全打开，对公式样式文本加前置单引号；JSON 保留原始文本。筛选文件不等同于完整质量报告，也不代表已修复的数据。

等待导出成功后再关闭程序。真实大文件仍在内存中处理。活动条不是完成百分比，不能据此判断剩余时间。

## English

### Launch
Extract the **entire** Windows ZIP and double-click `RxDataLint.exe`. Keep `_internal` beside it; do not copy the executable alone. Python installation is not required. The package is unsigned and is an alpha prerelease.

### 0:00–0:30: Load the example
Click **Choose SCMD CSV**, then select `examples/sample_scmd.csv` inside the extracted folder. Do not double-click the CSV, which may open Excel. It contains 8 records with deliberate data problems; findings are not application crashes.

### 0:30–1:00: Understand findings
Open **Finding overview** for rule-level counts of findings, associated records, organisations and products. Record counts overlap between rules and must not be added. Double-click a rule to inspect it (clears any search). Select a finding and scroll through its medicine, organisation code, month, source value and guidance.

### 1:00–1:30: Search and review
Choose **Negative**, enter a medicine name or organisation code and press Enter. All space-separated terms must match. Switching languages preserves results. Search covers findings and their associated records, not a complete medicine catalogue. Negative values may represent adjustments; a flag does not prove a source error.

### 1:30–2:00: Choose an export
- **Export full report** writes whole-file HTML, JSON and, when available, normalized CSV, regardless of filters.
- **Export filtered findings** writes separate CSV and JSON files, one item per finding with medicine, organisation and month. JSON records the search, category, selected/total counts and source hash. No matches disables this button.
- Each export uses its own folder. Formula-like text in the filtered CSV is prefixed with an apostrophe for spreadsheet use; JSON preserves the original text. Filtered files are neither full quality reports nor corrected datasets.

Wait for export confirmation before closing. Large files are still processed in memory. The activity bar is not a percentage or an estimate of time remaining.

## Build from source / 从源码打包

On Windows with Python and Tkinter / 在含 Tkinter 的 Windows Python 环境中：

```powershell
python -m pip install pyinstaller==6.22.3
python tools/build_windows_suite.py
```

Output / 输出：`dist/RxDataLint-Windows-x64-v0.3.0-alpha.1.zip` and its SHA-256 file. The build script runs a packaged smoke test before creating the ZIP. Test on another Windows computer before calling the package broadly compatible.

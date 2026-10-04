# Windows portable suite / Windows 便携运行包

## 简体中文

新版运行包包含两个本地程序，不需要另行安装 Python。将 ZIP **全部解压**，保留每个程序旁边的 `_internal` 文件夹。

| 入口 | 用途 |
|---|---|
| `Start-Checker.bat` 或 `Checker/RxDataLint.exe` | 检查 SCMD CSV，搜索提示，查看概览，导出完整或筛选结果 |
| `Start-Analysis.bat` 或 `Analysis/RxDataLintAnalysis.exe` | 生成数据库、五份 SQL 汇总、中英文 HTML 报告并自动校验文件 |

第一次使用：

1. 打开数据检查程序，选择运行包中的 `examples/sample_scmd.csv`，查看故意设置的问题。样例有 8 条记录，不是真实药品数据。
2. 打开数据分析程序，选择同一个 CSV；来源栏填 `synthetic`。
3. 点击“生成并校验”，选择一个可写的保存位置。每次创建独立结果文件夹，不覆盖旧结果。
4. 完成后点击“中文报告”或“English report”。报告是本地导出文件，在浏览器打开；不需要联网，不是托管网页。
5. 换成真实 SCMD 文件时，填写对应的官方来源链接。数据只在本机处理。

分析失败时不要使用部分输出；修正输入后可以重新运行。请等待任务完成再关闭窗口。大文件仍在内存中处理，活动条不表示完成百分比。

这是未签名的 Alpha 运行包。两个程序和解压后的示例流程在打包电脑上验证，测试时移除了 Python 环境变量并使用只含系统目录的 PATH；尚未在独立、没有 Python 的 Windows 虚拟机或其他电脑验证。检查提示不是药品质量认证，指示性成本不是实际采购支出。负数处理差额不是节省金额。

校验下载：在 PowerShell 中运行 `Get-FileHash <ZIP文件路径> -Algorithm SHA256`，与同一发行页面的 `.zip.sha256` 文件比较。

## English

Extract the **entire** ZIP. The suite includes two local Windows programs and their Python runtime; a separate Python installation is not required by design. Keep each `_internal` folder beside its executable.

- **Start-Checker.bat / Checker/RxDataLint.exe:** review SCMD CSVs, search findings and export full/filtered quality reports.
- **Start-Analysis.bat / Analysis/RxDataLintAnalysis.exe:** generate SQLite, five SQL summaries, Chinese/English offline HTML reports and verify output hashes.

Start with `examples/sample_scmd.csv` (8 deliberately problematic synthetic records). In the analysis program, enter `synthetic` as the source, select **Generate & verify**, and choose a writable parent folder. Each run creates a new output subfolder. On success, use the report buttons to open a local HTML file in your default browser. For real data, enter the corresponding official source URL.

Data stays on the computer. Failed runs may leave partial outputs; do not use them. Wait for completion before closing. Large files are still processed in memory. Findings are review prompts, not clinical/quality/compliance certification; indicative cost is not actual procurement expenditure and the cost-sensitivity difference is not savings.

This is an unsigned alpha package. Built and ZIP-extracted executables were tested on the build machine with Python environment variables removed and a system-only PATH. An independent clean Windows VM/other-machine test has not been performed. Report-button path handling was tested with an intercepted open call; generated HTML rendering was separately inspected locally.

Verify the downloaded ZIP using `Get-FileHash <ZIP-path> -Algorithm SHA256` and compare with the release's `.zip.sha256` file.

## Build from source / 源码打包

Use 64-bit Python on Windows with Tkinter / 使用 Windows 64 位 Python（含 Tkinter）：

```powershell
python -m pip install pyinstaller==6.22.3
python tools/build_windows_suite.py
```

The build refuses existing versioned output folders, runs both packaged diagnostics, extracts the ZIP into a path containing spaces and Chinese characters, repeats the checks, then writes the checksum and validation summary. Output: `dist/RxDataLint-Windows-x64-v0.4.0-alpha.4.zip`.


## First example / 第一个示例

Checker: **Try sample / 打开示例** runs the bundled eight-row fictional CSV. Analysis: **Use sample / 使用示例** also fills source `synthetic`; click Generate and verify and choose an output folder. Theme/font/language changes affect display only. / 示例按钮免去找文件；界面设置不改变数据。

BatchScope is downloaded separately from [its own releases](https://github.com/rayexzh/batchscope/releases). / BatchScope 请单独下载。

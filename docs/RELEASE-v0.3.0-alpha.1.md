# v0.3.0-alpha.1 — Windows analysis suite / Windows 分析运行包

## English

This prerelease packages the CSV-to-SQL analysis workflow alongside the existing data checker. The ZIP includes two independent local programs:

- **Start-Checker.bat → Checker/RxDataLint.exe:** review SCMD CSVs, inspect/search findings, export full or filtered quality reports.
- **Start-Analysis.bat → Analysis/RxDataLintAnalysis.exe:** select a CSV and its source, generate SQLite and five SQL summaries, create Chinese/English offline HTML reports, and verify output hashes.

Download **RxDataLint-Windows-x64-v0.3.0-alpha.1.zip**, extract the entire folder, then choose either launcher. Keep each `_internal` directory beside its executable. A separate Python installation is not required by design. Start with the included `examples/sample_scmd.csv`; enter `synthetic` in the analysis source field. Each analysis creates a new result folder.

The release also includes a SHA-256 checksum and a machine-readable validation summary. Compare `Get-FileHash <ZIP-path> -Algorithm SHA256` against the `.zip.sha256` file before using the package.

Validation: 32 desktop tests and 8 analysis tests passed locally. Both executables passed packaged workflow checks before and after ZIP extraction, including extraction under a path with spaces and Chinese characters. Analysis checks cover background execution, SQL resource loading, bilingual reports, file verification, tamper detection, failed-input recovery and preservation of earlier runs. Report buttons were tested with an intercepted OS open call; report HTML was separately rendered and inspected locally.

Scope: tested on the Windows 11 x64 build machine with Python environment variables removed and a system-only PATH. No independent clean Windows VM/other-machine test has been performed. This is an unsigned alpha package, not a production-qualified system. Large CSVs remain memory-bound. Partial outputs from failed runs must not be used. Findings do not certify clinical, financial or regulatory correctness. Indicative costs are not actual procurement spending, and negative-cost sensitivity is not savings. Power BI PBIX and AI chat are not included.

## 简体中文

此次预发布将数据分析流程打包成独立程序，与原有检查程序一起提供：

- **Start-Checker.bat → Checker/RxDataLint.exe：** 检查 SCMD CSV、搜索和复核问题、导出完整或筛选检查报告。
- **Start-Analysis.bat → Analysis/RxDataLintAnalysis.exe：** 选择 CSV 和来源，生成数据库及五份 SQL 汇总，生成中英文离线 HTML 报告，并自动校验输出文件。

下载 **RxDataLint-Windows-x64-v0.3.0-alpha.1.zip** 后完整解压，再选择入口。不要单独移动 EXE，应保留旁边的 `_internal` 文件夹。按设计不需要另外安装 Python。先用包内 `examples/sample_scmd.csv`；分析窗口来源填写 `synthetic`。每次分析使用独立结果文件夹，不覆盖旧结果。

发行附件还提供 SHA-256 校验文件和验证摘要。本地通过 32 项桌面测试及 8 项分析测试；两个 EXE 在打包目录及 ZIP 解压后均通过流程检查，包含空格和中文路径。验证了后台分析、SQL 资源、中英文报告、文件校验、修改检测、失败恢复和旧结果保留。报告按钮测试拦截了系统打开操作，HTML 报告另外在本地浏览器检查了排版。

验证范围为打包电脑 Windows 11 x64，测试移除了 Python 环境变量，PATH 仅含系统目录；尚未在独立干净虚拟机或其他电脑验证。这是未签名 Alpha 版，尚非生产验证系统。大 CSV 仍在内存中处理；失败产生的部分输出不可使用。问题提示不证明临床、财务或合规正确，指示性成本不等于实际采购支出，负数处理差额不代表节省。此次不包含 Power BI PBIX 或 AI 聊天功能。

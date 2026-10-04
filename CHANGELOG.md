# Change log / 更新日志

## v0.4.0-alpha.4 (2026-10-04) — Safer CSV and source switching / CSV 与文件切换修复

- Reject truncated quoted CSV records instead of silently treating them as valid data. / 拒绝引号未闭合的截断 CSV，避免误读为有效数据。
- Close source-specific review windows after a successful file change; keep them after a failed load. / 成功切换文件时关闭旧复核窗口，加载失败则保留旧结果。
- Verified with a malformed fixture and the public July 2026 provisional SCMD file; synthetic role-play is not external validation. / 用异常样本与公开数据验证；模拟岗位试用不等于外部验收。

## v0.4.0-alpha.3 (2026-10-04) — Group findings / 分组复核

- Group the current findings by rule, organisation or medicine and open a group to inspect its source row. / 按规则、机构或药品汇总当前提示，并定位到原始行。
- Keep exact group identity in filtered JSON exports; full reports and source CSV remain unchanged. / 筛选导出记录分组范围，完整报告和源 CSV 不变。
- Verified against the public July 2026 provisional SCMD file and the portable checker diagnostics. / 使用公开的 2026 年 7 月临时版 SCMD 和便携版自检验证。

## v0.4.0-alpha.2 (2026-10-01) — Readable controls and report identity / 布局与报告对应关系

- Keep titles readable and wrap category, export and search controls at small window sizes and large fonts. / 窄窗口、大字体下完整显示标题与操作按钮。
- SQL reports show their original input and source; edited inputs display a pending-analysis notice without deleting previous results. / 区分新输入与旧报告。
- Validation: 35 checker tests and 15 analysis tests passed; the new regressions also run in the packaged diagnostics. / 本地 50 项源码测试通过，EXE 自检增加对应检查。
- Findings came from scripted native-interface simulation, not external user research. The alpha.1 animation remains a labelled earlier-version walkthrough. / 明确模拟试用与旧演示版本。

## v0.4.0-alpha.1 (2026-10-01) — Clear desktop workflow / 清晰桌面流程

- Rx keeps its SCMD checker and SQL analysis; BatchScope is maintained in its own repository. Old release history is retained. / 更新独立项目边界，保留历史。
- Added local sample buttons, light/dark palettes, adjustable fonts, language controls, workflow guidance and scrollable pages. Double-click/Enter reaches complete record context. / 新增示例、主题、字号、语言和详情定位。
- Added an animated English walkthrough with Chinese highlights, real desktop states and disclosed synthetic narration. / 动画讲解明确来源与合成配音。
- Validation: 34 checker tests and 13 analysis tests passed locally. Packaged checks and limits are attached to the release. / 本地 47 项测试通过，运行包证据见附件。

## v0.3.0-alpha.2 (2026-09-30) — Analysis boundary fixes / 分析边界修复

- Reject malformed manifests, unsupported versions, unsafe artifact names and invalid hash formats with actionable errors. / 校验文件异常时给出明确错误。
- Stop non-finite SQL aggregates before writing a completion manifest; label missing cost and invalid months explicitly. / 数值汇总溢出时停止，不生成完成清单；明确显示缺失成本和无效月份。
- Improved packaged error diagnostics. Local verification: 32 checker tests and 12 analysis tests passed. See the release validation attachment for executable checks and limits. / 改进 EXE 错误诊断，本地 44 项测试通过，EXE 测试范围见发布附件。

## v0.3.0-alpha.1 (2026-09-30) — Portable analysis suite / 便携分析运行包

- Added self-contained Chinese and English HTML analysis reports with per-month completeness, cost-sensitivity charts, review guidance and provenance. No extra runtime dependencies or network access are required.
- Added artifact hashes and file verification, preserving compatibility with previous hashed runs. Reports show NULL costs and invalid-month groups explicitly; differences are not presented as savings.
- Added a separate desktop analysis launcher with background processing, unique result folders and report-opening buttons. The portable suite now includes Checker/RxDataLint.exe and Analysis/RxDataLintAnalysis.exe.
- Documented the portfolio scope and a planned synthetic quality-operations project; planned work is not represented as completed functionality.
- Local validation: 32 desktop tests and 8 analysis tests passed; the complete 319,345-record July file produced matching report totals and verified artifacts. Report layout was inspected in a local browser. Check GitHub Actions for this commit's CI status. Both executables passed built and ZIP-extracted diagnostics with a system-only PATH; no independent clean VM/other-machine test was performed.

- 新增可独立打开的中英文 HTML 报告，展示各月完整率、成本处理差异图、复核建议和来源；无额外运行依赖、无需联网。
- 新增文件哈希与校验，仍支持旧版已记录哈希的输出。报告保留未知成本和无效月份，差额不描述为节省。
- 新增独立桌面分析入口：后台运行、独立结果文件夹和报告按钮；运行包包含 Checker/RxDataLint.exe 和 Analysis/RxDataLintAnalysis.exe。
- 记录作品集范围和下一项模拟质量业务项目；规划不表示功能已实现。
- 本地验证：32 项桌面测试和 8 项分析测试通过；完整 319,345 条七月记录的报告数字已核对，输出文件校验通过，并检查了本地浏览器排版。当前提交的远端状态请查看 GitHub Actions；两个 EXE 在打包目录及 ZIP 解压后均通过诊断，PATH 仅含系统目录。尚未在独立干净虚拟机或其他电脑验证。

## v0.2.0-alpha.1 (2026-09-28) — Review workflow and Windows package / 复核流程与 Windows 运行包

### English

- Added whole-file rule summaries with finding, distinct associated-record, organisation and product counts. Double-click a rule to inspect it. Unlocated findings are counted separately.
- Finding details now show medicine name/code, organisation code and month, with a scrollbar for long explanations.
- Added a separate filtered-findings CSV/JSON export with search scope and source hash; full-report exports remain unchanged. Spreadsheet formula-like text is quoted in the filtered CSV; JSON preserves source text.
- Added a Windows x64 portable build script, packaged application smoke test, SHA-256 checksum and bilingual two-minute walkthrough. Portable ZIPs are unsigned and have only been verified on the build machine; this is an alpha prerelease.
- 32 local automated tests pass. Packaged smoke testing covers Tk startup, sample validation, search, language switching, overview and both export formats.

### 简体中文

- 新增全文件问题概览：按规则统计提示数、去重的关联记录数、机构数和药品数。双击规则查看问题；未定位到记录的提示单独计数。
- 问题详情增加药品名称及编码、机构编码、月份，并提供滚动条。
- 新增独立的筛选问题 CSV/JSON 导出，记录搜索范围和输入哈希；原有完整报告不变。筛选 CSV 的公式样式文本会加单引号，JSON 保留原始文本。
- 新增 Windows x64 便携打包脚本、打包程序冒烟测试、SHA-256 校验文件和双语两分钟上手说明。运行包未签名，目前仅在打包电脑验证；此次作为 Alpha 预发布版提供。
- 本地 32 项自动化测试通过。打包后的程序验证了 Tk 启动、示例检查、搜索、语言切换、概览和两类导出。

## 2026-09-28 — Desktop responsiveness / 桌面响应优化

### English

- CSV validation and report export now run in a background thread. An animated activity bar indicates work in progress; it is not a completion percentage.
- Import, search, language and export controls are temporarily disabled during background work to prevent overlapping operations. Failed loads preserve the previous successful result and restore controls.
- Findings are inserted into the table in batches of 200. Starting another search cancels pending display batches so old results cannot reappear.
- Chinese finding searches remain consistent when switching between Chinese and English.
- Filtered views still export the complete validation result, including findings not currently visible.

Validation: 28 local automated tests passed, including UI event-loop responsiveness, duplicate-load prevention, recovery after a failed load, search/language consistency and complete exports after filtering. A local end-to-end check of the July 2026 provisional SCMD file loaded 319,345 records, displayed 21,563 findings and exported all findings after filtering. These are checks of this implementation and input, not a guarantee for all files or machines. The raw dataset is not included in this update.

Limitations: files are still processed in memory; this change improves responsiveness rather than guaranteeing faster validation or lower memory use. Search and some display preparation still run on the UI thread. Wait for export success before exiting; closing during export can leave an incomplete output folder. This is a source update, not a tagged release or compliance certification.

### 简体中文

- CSV 检查和报告导出改为后台线程执行。动态活动条表示任务正在处理，不表示完成百分比。
- 后台处理期间暂停导入、搜索、语言切换和导出，避免任务重叠。读取失败会保留上一次成功的结果，并恢复按钮。
- 问题列表每批显示 200 条。发起新搜索会取消尚未完成的旧列表加载，避免旧结果重新出现。
- 修复使用中文搜索问题后，切换英文导致搜索结果消失的问题。
- 筛选只影响显示；导出仍包含完整检查结果，包括当前未显示的问题。

验证：本地 28 项自动化测试全部通过，覆盖处理期间界面响应、避免重复导入、读取失败恢复、搜索与语言切换，以及筛选后完整导出。使用 2026 年 7 月暂定 SCMD 文件进行本地完整流程验证：载入 319,345 条记录、显示 21,563 条提示，并在筛选后成功导出全部提示。这仅验证当前实现与该输入，不代表所有文件和电脑上的保证。本次更新不包含原始数据集。

限制：仍在内存中处理文件；此次优化旨在改善响应，不保证检查更快或内存更少。搜索和部分界面准备工作仍在主线程执行。请等待导出成功后再退出，导出中关闭程序可能留下不完整的文件夹。本次为源代码更新，尚非带标签的正式发行版，也不代表合规认证。

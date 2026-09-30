# Change log / 更新日志

## Unreleased — Analysis reports / 分析报告（2026-09-30）

- Added self-contained Chinese and English HTML analysis reports with per-month completeness, cost-sensitivity charts, review guidance and provenance. No extra runtime dependencies or network access are required.
- Added artifact hashes and file verification, preserving compatibility with previous hashed runs. Reports show NULL costs and invalid-month groups explicitly; differences are not presented as savings.
- Added a separate desktop analysis launcher with background processing, unique result folders and report-opening buttons. It is not yet included in the published checker EXE.
- Documented the portfolio scope and a planned synthetic quality-operations project; planned work is not represented as completed functionality.
- Local validation: 32 desktop tests and 8 analysis tests passed; the complete 319,345-record July file produced matching report totals and verified artifacts. Report layout was inspected in a local browser. Check GitHub Actions for this commit's CI status; the published checker EXE does not include this source update.

- 新增可独立打开的中英文 HTML 报告，展示各月完整率、成本处理差异图、复核建议和来源；无额外运行依赖、无需联网。
- 新增文件哈希与校验，仍支持旧版已记录哈希的输出。报告保留未知成本和无效月份，差额不描述为节省。
- 新增独立桌面分析入口：后台运行、独立结果文件夹和报告按钮；尚未包含在已发布检查程序的 EXE 中。
- 记录作品集范围和下一项模拟质量业务项目；规划不表示功能已实现。
- 本地验证：32 项桌面测试和 8 项分析测试通过；完整 319,345 条七月记录的报告数字已核对，输出文件校验通过，并检查了本地浏览器排版。当前提交的远端状态请查看 GitHub Actions；已发布的检查程序 EXE 尚不包含此次源码更新。

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

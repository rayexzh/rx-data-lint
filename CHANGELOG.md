# Change log / 更新日志

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

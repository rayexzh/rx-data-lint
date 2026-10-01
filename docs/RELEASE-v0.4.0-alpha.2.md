# RxDataLint v0.4.0-alpha.2 / 布局与报告对应关系修复

Download **RxDataLint-Windows-x64-v0.4.0-alpha.2.zip**, extract fully and run **Start-Checker.bat** or **Start-Analysis.bat**. No Python or paid API required. / 下载、完整解压后运行；无需安装 Python。

- Small-window/large-font titles, categories, exports and search controls remain readable; extra controls wrap to another row. / 小窗口、大字体下按钮自动换行。
- SQL results name their original input/source. Changing inputs displays **not analysed yet** while preserving previous reports. / 显示报告原输入，区分待分析的新文件。
- Business rules, source data and SQL calculations are unchanged. / 不改变业务规则、原数据和计算口径。

**Checks:** 35 checker + 15 analysis source tests passed locally. Both built and ZIP-extracted EXEs must pass diagnostics, including sample loading, changed-input context and small-window controls. See the attached versioned validation JSON and checksum. Checks use the build host with Python variables removed/system-only PATH; no separate clean-machine trial. The executables are unsigned. / 本地 50 项源码测试通过；EXE 验证条件与结果见附件，程序未签名。

This patch follows an [AI-scripted native desktop review](https://github.com/rayexzh/rx-data-lint/blob/main/docs/SIMULATED-USABILITY-REVIEW.md), not independent user testing. / 修复来自模拟试用，不能作为外部采用证据。

[Animated tutorial recorded on alpha.1](https://github.com/rayexzh/rx-data-lint/releases/download/v0.4.0-alpha.1/RxDataLint-Animated-Walkthrough.mp4) remains available. Its layout predates this patch; the workflow still applies. Narration is locally synthesized, not the maintainer's own voice. / 保留上一版动画，明确版本与合成旁白。

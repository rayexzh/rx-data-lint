# v0.3.0-alpha.2 — Boundary-case fixes / 边界问题修复

## English

This patch keeps the two-program portable suite and repairs analysis verification and numeric boundary cases:

- Malformed manifest roots, unsupported format versions, unsafe artifact names and invalid SHA-256 digests now produce clear verification failures.
- SQL aggregates that overflow the finite numeric range stop the run before a completion manifest is written. Partial outputs must not be used.
- Markdown summaries identify invalid months and unavailable costs explicitly instead of displaying `None`.
- Packaged diagnostics include the analysis error message to make failures easier to diagnose.

Download **RxDataLint-Windows-x64-v0.3.0-alpha.2.zip**, extract the complete folder, and start **Start-Checker.bat** or **Start-Analysis.bat**. Keep each `_internal` folder beside its executable. Previous releases remain available.

Validation: 32 checker tests and 12 analysis tests passed locally. Both executables passed sample diagnostics before and after ZIP extraction, with Python environment variables removed and a system-only PATH. Complete-file executable results are recorded in the attached validation summary. Testing was performed on the build machine, not an independent clean Windows VM. Report-opening calls were intercepted during diagnostics.

The package is unsigned and remains an Alpha prerelease. Data findings are review prompts, not clinical decisions, GMP/CSV certification or batch-release decisions. Hashes detect changes relative to the manifest; they do not authenticate a publisher. Indicative costs are not actual procurement expenditure.

## 中文

本次修订保留检查与分析两个本地程序，重点修复边界问题：

- 校验清单结构损坏、格式版本不支持、文件名不安全或 SHA-256 格式错误时，提供明确失败提示。
- SQL 汇总超出有限数值范围时停止运行，不生成完成清单；不应使用部分生成的结果。
- Markdown 摘要明确显示无效月份与不可用成本，不再出现 `None`。
- EXE 自检记录具体的分析错误，便于排查问题。

下载并完整解压 **RxDataLint-Windows-x64-v0.3.0-alpha.2.zip**，启动 **Start-Checker.bat** 或 **Start-Analysis.bat**。保留 EXE 旁的 `_internal` 文件夹。历史版本继续保留。

本地 32 项检查测试和 12 项分析测试通过；两个 EXE 在打包目录及 ZIP 解压目录的小样本自检均通过。完整数据的 EXE 结果见附件校验摘要。本次在打包电脑测试，尚未在独立干净 Windows 虚拟机验证；报告打开操作以拦截调用的方式检查。

仍为未签名 Alpha 预发布版。检查提示不代表临床判断、GMP/CSV 合规认证或批次放行；文件哈希不是发布者身份认证；指示性成本不代表实际采购支出。

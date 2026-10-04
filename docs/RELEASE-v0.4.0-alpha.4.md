# RxDataLint v0.4.0-alpha.4 — Safer CSV review / 更稳妥的 CSV 复核

**English.** Download and fully extract the Windows ZIP, then run `Start-Checker.bat`. A truncated quoted CSV record now stops the check instead of appearing as valid data. When a different file loads successfully, the old finding, group and coverage windows close; a failed load leaves the previous result available. The public July 2026 provisional SCMD file still produces 319,345 rows and 21,563 review prompts. These prompts are not confirmed errors. Tests and packaged diagnostics are described in the release assets. The EXE is unsigned and has not been tested on an independent Windows computer.

**中文。** 下载并完整解压 Windows ZIP，再运行 `Start-Checker.bat`。CSV 记录引号未闭合时，程序会中止检查，不会将截断内容当成有效数据。成功切换文件时，旧的问题、分组与覆盖情况窗口会关闭；加载失败则保留上一份结果。公开的 2026 年 7 月临时版 SCMD 文件仍得到 319,345 行、21,563 条待复核提示；提示不等于已确认错误。测试和打包自检记录见发布附件。EXE 未签名，尚未在独立 Windows 电脑测试。

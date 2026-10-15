# RxDataLint v0.4.0-alpha.5

Malformed separators such as `1,2` stay invalid instead of becoming a different amount. The checker and SQL analysis share one numeric parser. Extreme quantities are compared within the same product and supplied unit identity; unknown units are excluded.

错误分隔符（如 `1,2`）保留为无效值，不再变成另一个金额；检查器与 SQL 分析共用数值解析。极端数量只在同药品、同单位标识内比较，未知单位不参与。

The analysis CLI reports truncated CSV failures without creating completed results. Builds can use a fresh artifact folder and preserve earlier candidates.

分析命令行明确提示截断 CSV 失败，不生成完成结果；打包可指定新的产物目录，保留之前构建。

59 source tests passed. Built and ZIP-extracted Checker and Analysis executables passed diagnostics on the build machine with a system-only PATH. An independent clean-machine test has not been performed. See the validation attachment on the release page.

59 项源码测试通过；检查器与分析 EXE 在构建后及 ZIP 解压后均通过诊断，使用仅含系统目录的 PATH。尚未在另一台全新机器验证，详细证据见发布附件。

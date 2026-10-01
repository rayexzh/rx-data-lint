# RxDataLint v0.4.0-alpha.1 / 独立药品数据复核项目

## Download and first run / 下载与第一次运行

Download **RxDataLint-Windows-x64-v0.4.0-alpha.1.zip**, extract the entire archive, open **Start-Checker.bat** and click **Try sample / 打开示例**. Open **Start-Analysis.bat** for SQL summaries; **Use sample / 使用示例** also sets the source label to synthetic. Python installation and paid APIs are not needed. Keep the _internal folders beside both executables.

下载便携 ZIP，完整解压。检查器和分析器是同一个 Rx 项目的两步流程，样例按钮免去寻找 CSV。BatchScope 是另一个独立项目，需从[其发布页](https://github.com/rayexzh/batchscope/releases)单独下载。

## Changes / 本次变化

- Shared light/dark palettes, native DPI awareness, adjustable fonts, language switching and responsive/scrollable content. / 统一主题、字号、语言与页面布局。
- One-click example entry points and full record context reached by double-click/Enter. Source values and calculations are unchanged. / 示例入口与直达详情，不改变复核规则与数值。
- Bilingual homepages, project boundaries and documentation navigation. Existing commits/releases remain available. / 独立介绍与导航，保留历史。
- [Animated English walkthrough](https://github.com/rayexzh/rx-data-lint/releases/download/v0.4.0-alpha.1/RxDataLint-Animated-Walkthrough.mp4), **2:59.83**, 1080p, with English captions and Chinese chapter highlights. / 约三分钟动画视频。
- [Complete video pack](https://github.com/rayexzh/rx-data-lint/releases/download/v0.4.0-alpha.1/RxDataLint-Demo-Pack.zip) includes narration, script, subtitles, manifest and checks.

## Verification / 核对

34 checker tests and 13 analysis tests passed locally. Both built and ZIP-extracted executables passed self-tests with Python variables removed and a Windows-only PATH. Checks include bundled sample loading, language/theme/font controls, exports, SQL, bilingual reports, hashes and failure recovery. See **validation-v0.4.0-alpha.1.json** and the ZIP SHA-256 attachment. This was on the build host, not an independent clean-machine test. The package is unsigned.

本地 47 项源码测试通过；构建后与解压后的两个 EXE 都完成自检，运行环境移除 Python PATH。尚未进行独立纯净机器测试，程序未签名。

## Demo method and scope / 视频制作与边界

The video combines real native desktop states and explanatory animation; it is not uninterrupted raw recording. English narration is locally synthesized Microsoft Zira Desktop, not the maintainer speaking. Chinese highlights are summaries, not verbatim translations. Example inputs are synthetic. No adoption, measured learning benefit, financial savings, clinical correctness or regulatory validation is claimed. See [production notes](https://github.com/rayexzh/rx-data-lint/blob/main/docs/DEMO_VIDEO.md).

视频采用实际桌面画面与讲解动画，旁白为合成声音。空白费用、非数值费用和负数分开理解；规范化不会自动修正异常。

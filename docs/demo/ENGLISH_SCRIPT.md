# RxDataLint — animated English walkthrough

Version v0.4.0-alpha.1. Edited real application captures, explanatory animation and Microsoft Zira Desktop synthetic narration; not the author speaking or an uninterrupted screen recording. All displayed examples are synthetic. Chinese captions are chapter highlights, not a verbatim translation.

## 00:00:00 — A CSV is not a conclusion

RxDataLint adds a review step before turning medicines data into a chart. This walkthrough uses the bundled synthetic example, not patient or company records. Open a CSV, understand the findings, and export evidence before analysing totals.

中文要点：先检查，再解释，最后分析。

## 00:00:14 — Start with a safe example

Extract the Windows ZIP and open Start Checker. Click Try sample to load eight fictional records. For public SCMD data, use Choose CSV. Processing stays on your computer, and the desktop remains responsive during checks.

中文要点：点击示例即可体验，不需要账号。

## 00:00:29 — Count records, not just messages

The sample produces six errors and nine warnings, but only four affected records. One row can trigger several rules, so fifteen findings do not mean fifteen bad rows. These counts are not a regulatory or clinical verdict.

中文要点：同一条记录可能触发多个提示。

## 00:00:42 — A negative value needs context

Choose Negative to focus on quantities and costs below zero. A stock adjustment can legitimately be negative. Source values stay intact: the program does not delete them, turn them positive, or decide they are wrong. Review their context.

中文要点：负数可能是调整记录，不要直接删除。

## 00:00:57 — Follow a finding back to its record

Select a finding and double click, or press Enter, to reach its full explanation. Details link the finding to its medicine, organisation, month and original value. You have a specific record to investigate, instead of a vague dashboard number.

中文要点：查看药品、机构、月份与原始值。

## 00:01:11 — Check what actually ran

Check coverage shows which rules ran, which were skipped, and why. Executed does not mean passed. No findings does not mean every possible quality issue was tested. Read the coverage and guidance together.

中文要点：了解哪些规则执行了、跳过了。

## 00:01:24 — Find the records you need

Search an organisation, medicine, month, or rule while using a category filter. Here, R two B leaves six negative findings. Category totals describe the unsearched file; the visible count describes your current view. Clear the search to widen your review.

中文要点：分类加搜索，定位需要复核的记录。

## 00:01:40 — Choose the right export

Export full report keeps all findings even when the screen is filtered. It creates HTML, JSON evidence, and a normalized CSV when the schema permits. Export filtered findings creates a smaller follow up list. Normalization does not correct flagged records.

中文要点：完整报告保留全部结果，筛选导出用于跟进。

## 00:01:56 — Move from checking to analysis

Open Start Analysis for SQL summaries. Use the sample with source synthetic, or provide the official URL for public data. Generate and verify builds SQLite summaries and bilingual offline reports, then checks the exported files.

中文要点：同一项目的分析入口生成 SQL 汇总。

## 00:02:10 — Missing is not zero

Blank costs stay unknown; malformed costs are separate problems. The missing cost card counts blanks only, so zero percent missing does not mean every cost is valid. Excluding negatives changes totals. That difference is not a saving.

中文要点：空白、非数值、负数费用必须分开理解。

## 00:02:25 — Make the review easier to read

Switch language, choose a theme, and adjust font size. These controls change presentation, not data or findings. Scroll on smaller screens and open details for long fields. The analysis launcher has the same display controls.

中文要点：主题与字号只改变显示，不改变结果。

## 00:02:39 — Two focused, independent projects

RxDataLint reviews medicines data. BatchScope is a separate synthetic manufacturing quality project, with its own repository and Windows release. Both are educational alpha tools. This demo combines real application captures, explanatory animation, and a synthetic English voice. Start with the example and review the evidence.

中文要点：两个项目、两套版本，各自有清晰用途。
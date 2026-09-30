# RxDataLint + NHS 药品数据分析作品集

[English](PORTFOLIO.md)

**用本地数据检查工具和可复现 SQL 案例，说明数据处理方式如何改变药品指示性成本汇总。**

| 项目内容 | 已完成的证据 |
|---|---|
| 业务问题 | 缺失成本和负数成本怎样影响分析？ |
| 真实数据 | NHSBSA 2026 年 7 月临时发布 SCMD，共 319,345 条记录 |
| 关键发现 | 排除负数成本后，已知成本汇总增加 £10,317,563.30 |
| 使用技术 | Python、SQLite、SQL、Tkinter、matplotlib；Power Query 导入预览已确认 |
| 当前阶段 | 桌面 Alpha 版已发布，单月分析完成；外部采用情况尚未验证 |

## 问题与实现

负数可能需要检查，但不能因此直接删除；缺失成本也不能当作已经测量得到的零。处理决定会影响汇总和完整率。

项目提供中英文桌面复核工具，支持搜索、问题概览、关联记录及完整/筛选结果导出。SQLite 保存原始内容、行号和检查提示，运行记录包含来源、SHA-256、工具版本与规则覆盖情况。

五组 SQL 查询包含月度概览、药品成本排名、机构记录覆盖、规则提示和成本处理场景，展示 GROUP BY、CTE、LEFT JOIN 和排名窗口函数；两张可复现 PNG/SVG 图表解释结果。

## 结果与业务含义

![按记录数计算的成本完整率](../analysis/figures/202607/cost_completeness.png)

**12,473 条记录缺失成本，记录完整率为 96.0942%。** 这不意味着掌握了相同比例的支出，也无法据此估算未知金额。

![排除负数成本的影响](../analysis/figures/202607/negative_cost_impact.png)

保留负数时，已知净指示性成本为 **£2,425,349,659.23**；排除 2,340 条负数成本记录后为 **£2,435,667,222.53**。差额 **£10,317,563.30** 展示的是处理方式的影响，不能写成“为 NHS 节省了 1,031 万英镑”。负数实际含义仍需复核。

## 验证与当前边界

- 完整数据已运行，独立 Decimal 计算核对记录数、净成本和负数金额，结果与 SQL 一致。
- 本地通过 32 项原有测试及 3 项分析测试。当前提交的远端检查状态请查看 GitHub Actions；本地测试通过不代表远端检查已通过。
- 你的 Power BI 截图显示一行月度预览，记录数、机构数、药品数和已知成本记录数正确。交互图表和 PBIX 尚未完成。
- 没有声称药厂部署、合规认证、外部客户采用或已实现节省时间。

数据只有一个临时发布月份，不能得出趋势、因果或医院效率结论。指示性成本不等于实际采购支出，警告记录和疑似重复记录仍保留在汇总中。

## 怎样介绍自己的贡献

项目连接药品质量与安全背景、电子经济学习和数据工具。开发使用 AI 辅助；你提出业务方向、推动迭代，并实际试用了桌面程序和 Power Query 导入。展示时应能解释关键规则和指标；项目不代表已经获得 GMP 系统验证经验。

英文简历表述：

> Developed an AI-assisted, local medicines-data review tool and a reproducible Python/SQLite analysis of 319,345 NHSBSA records, preserving source traceability and demonstrating how negative-cost handling changes reported totals.

英文面试介绍：

> I built a local review workflow for public NHS medicines data. In the July 2026 snapshot, excluding negative costs increased the known indicative-cost sum by £10.32 million. I retained those records and made the processing choice explicit. The figure is a sensitivity result, not a claimed saving.

## 查看与复现

- [分析运行说明和指标口径](../analysis/README.zh-CN.md)
- [详细中英文案例及文件哈希](../analysis/CASE_STUDY.md)
- [第一条 SQL 中文讲解](../analysis/SQL_LESSON.zh-CN.md)
- [桌面程序已发布版本](https://github.com/rayexzh/rx-data-lint/releases/tag/v0.2.0-alpha.1)

来源：[NHSBSA 2026 年 7 月 SCMD 页面及字典](https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753)。Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). 独立项目，不表示 NHS/NHSBSA 背书。

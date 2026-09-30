# July 2026 SCMD: how data handling changes a cost summary

## English

![Cost completeness](figures/202607/cost_completeness.png)

![Negative-cost sensitivity](figures/202607/negative_cost_impact.png)

Question: what happens if an analyst removes negative costs before reporting?

The locally supplied July 2026 provisional NHSBSA SCMD file was checked with RxDataLint, retained in SQLite with review findings and analysed with the queries in `sql/`. These are descriptive results from that file, not estimates of actual NHS procurement expenditure.

| Metric | Observed result |
|---|---:|
| Records | 319,345 |
| Distinct nonblank ODS codes | 192 |
| Distinct nonblank VMP codes | 8,366 |
| Records with known finite costs | 306,872 |
| Records with missing costs | 12,473 |
| Records with invalid nonblank costs | 0 |
| Cost completeness by record count | 96.0942% |
| Records with negative costs | 2,340 |
| Known net indicative cost, including negatives | £2,425,349,659.23 |
| Sum after excluding negative costs | £2,435,667,222.53 |
| Difference caused by excluding negatives | £10,317,563.30 |

Interpretation: treating every negative cost as an error and deleting those records would increase this summary by £10.32 million. This is a sensitivity calculation, not proof that all negative entries are valid. Review their meaning before choosing a treatment. Missing costs remain unavailable: the observed sum does not estimate their value.

The validator produced 12,473 missing-cost prompts, 7,142 negative-value prompts across 2,401 records, and 1,948 extreme-quantity prompts. The negative-value rule checks quantities as well as costs: its count is therefore different from the 2,340 negative-cost records. Multiple prompts may refer to one record. An extreme quantity is a review signal, not a demonstrated error.

Only July 2026 is present. No growth, decline, spending efficiency, treatment demand or national completeness conclusion follows from this snapshot. Product rankings depend on known costs, coverage and the retained records.

Verification: counts and rounded net/negative totals were independently recalculated directly from the CSV with Python Decimal and matched the SQL exports. This confirms the aggregation against the supplied input; it does not independently validate the source's clinical or financial accuracy. The local run manifest records the exact input SHA-256 and validator version.

## 简体中文

本案例的问题是：分析人员如果把负数成本全部删掉，成本汇总会变化多少？

本地文件包含 319,345 条记录，192 个非空 ODS 代码和 8,366 个非空 VMP 代码。12,473 条记录缺失成本，按记录数计算的成本完整率为 96.0942%；这一比例不是支出覆盖率。

保留负数时，已知净指示性成本为 **£2,425,349,659.23**；排除 2,340 条负数成本后为 **£2,435,667,222.53**，增加 **£10,317,563.30**。因此，负数的处理方式会明显影响汇总。是否调整这些记录需要业务复核，不能看到警告就自动删除。缺失金额始终保留为空，不估算为零。

7,142 条负数提示包含数量字段的提示，对应 2,401 条记录，与 2,340 条负数成本记录是不同指标。同一记录可能有多条提示。1,948 条极端数量提示也不表示已经确认错误。

当前仅有 2026 年 7 月，不能推断增长或下降；指示性成本不等于实际采购支出。已通过独立的 Decimal 计算核对记录数及金额汇总，但这不构成对原始数据业务正确性的证明。

## Source / 来源

[NHSBSA provisional SCMD July 2026, resource and dictionary](https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753).

Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). Source: NHS Business Services Authority. Independent analysis; no NHS/NHSBSA endorsement. Results refer to the supplied snapshot; later revisions may differ. Reproduce using the commands in the companion README.

Input SHA-256: `58e1975007eb2272a0845c01ed621d437b732242bebc9602af3f2cdf372bd427`

Validator: `0.2.0a1`; ruleset: `0.2.2`; checked at: `2026-09-29T18:04:48.728798+00:00`.

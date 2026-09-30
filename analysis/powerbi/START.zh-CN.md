# Power BI Desktop：第一张报告

本阶段已通过 Power BI Desktop 导入预览：截图中的月份、记录数、机构数、药品数和已知成本记录数与 SQL 输出一致。度量值、交互图表和保存的 PBIX 尚未完成。

## 导入

1. 打开 Power BI Desktop，新建空白报告。
2. 在“获取数据”中选择“空白查询”（可能需先点“更多”）。
3. 进入 Power Query 编辑器，打开“高级编辑器”。
4. 打开本目录 `MonthlyReview.pq`，复制全部内容到高级编辑器。将顶部 `Folder` 改为你实际输出文件夹，以反斜杠结尾。M 字符串中的反斜杠不需要写成双反斜杠。
5. 将查询命名为 **MonthlyReview**。确认没有错误，再“关闭并应用”。

本机已另行生成 `analysis/output/202607/MonthlyReview.local.pq`，填好了文件夹路径，可以直接复制其中内容。公开的 `.pq` 模板不包含本机个人路径。

导入成功应有 1 行，month 为 `2026-07`，records 为 `319345`。先核对 known_cost_records 为 `306872`，missing_cost_records 为 `12473`。如果不存在对应输出文件夹，请先按分析 README 运行脚本。

## 指标

在“新建度量值”中逐条创建（每次仅粘贴一个公式）：

```dax
Records = SUM(MonthlyReview[records])
```

```dax
Known Cost Records = SUM(MonthlyReview[known_cost_records])
```

```dax
Missing Cost Records = SUM(MonthlyReview[missing_cost_records])
```

```dax
Cost Completeness = DIVIDE([Known Cost Records], [Records])
```

```dax
Known Net Cost = SUM(MonthlyReview[known_net_indicative_cost_gbp])
```

```dax
Nonnegative Only Cost = SUM(MonthlyReview[nonnegative_only_cost_gbp])
```

```dax
Negative Exclusion Impact = [Nonnegative Only Cost] - [Known Net Cost]
```

`Cost Completeness` 设为百分比，两位小数；金额设 GBP/英镑，两位小数。这是 0–1 的度量值，与原 CSV 已经是 0–100 的百分数列不同。

## 报告布局

- 顶部：标题 `NHS Medicines Data Review | July 2026 (Provisional)`；使用 month 做单选切片器。
- 第一排：总记录数、缺失成本记录数、成本完整率、已知净指示性成本四张卡片。
- 第二排：簇状条形图，数值使用 `Known Net Cost` 和 `Nonnegative Only Cost`；数值轴起点设为 0，打开数据标签。旁边放 `Negative Exclusion Impact` 卡片。
- 底部文本框：`Source: NHSBSA provisional SCMD, OGL v3.0. Missing costs are unavailable. Indicative cost is not actual procurement expenditure. Excluding negatives is a hypothetical scenario.`

当前应显示：319,345 条记录；12,473 条缺失；96.09%；£2,425,349,659.23；排除负数后的差额为 £10,317,563.30。将文件保存为 `NHS_Medicines_Review.pbix` 到本项目 `analysis/output/202607/`。

月份切片器在同一张 MonthlyReview 表上工作，两组数字会同步筛选。如果以后增加月份，机构数和产品数不可直接跨月相加当作唯一机构或产品数；本页保持单月选择。

## English summary

Create a Blank Query, paste `MonthlyReview.pq` into Advanced Editor, set the local output folder and name the query MonthlyReview. It merges the two monthly exports by month and checks uniqueness and record counts. Add the measures above; format the completeness measure as a percentage. Use a single-month slicer and keep the cost chart's value axis starting at zero. The Power Query preview has been confirmed by a user-provided screenshot; measures, interactive visuals and a saved PBIX remain pending.

References: [Power Query Editor and Advanced Editor](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-query-overview), [Csv.Document](https://learn.microsoft.com/en-us/powerquery-m/csv-document), [Table.NestedJoin](https://learn.microsoft.com/en-us/powerquery-m/table-nestedjoin).

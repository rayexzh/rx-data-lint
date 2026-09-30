# NHS 药品数据分析案例

[English](README.md)

下一步：[第一条 SQL 中文讲解](SQL_LESSON.zh-CN.md) · [Power BI Desktop 导入和制图步骤](powerbi/START.zh-CN.md)。

图表可复现：安装可选依赖 `python -m pip install -r analysis/requirements-charts.txt`，然后执行 `python analysis/plot_analysis.py analysis/output/202607 --month 2026-07 --output analysis/figures/202607`。生成 PNG、SVG 及来源记录，原有分析程序不需要这些绘图依赖。

这是 RxDataLint 的配套分析：CSV → 数据检查 → SQLite 数据库 → 五组 SQL 汇总。使用 Python 3.10 及以上版本，不需要安装第三方库。现阶段提供可导入 Power BI 的 CSV 和操作说明，尚未制作 PBIX 仪表盘。

## 怎么运行

在 PyCharm 打开原项目，下方打开“终端”，复制以下命令。先运行自带模拟数据：

```powershell
python analysis/run_analysis.py examples/sample_scmd.csv --output analysis/output/sample --source-url synthetic
```

运行你的真实文件：

```powershell
python analysis/run_analysis.py "D:/xiazai/scmd_provisional_202607.csv" --output analysis/output/202607 --source-url "https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753"
```

每次使用新的输出文件夹，例如把 `202607` 改成 `202607_review2`。程序会拒绝覆盖已有文件夹。中断运行可能留下不完整文件，只有成功结束且生成 `manifest.json` 和 `SUMMARY.md` 后才使用结果。一个输入 CSV 对应一个数据库快照，不会追加到已有数据库。检查过程仍在内存中处理数据。

## 会得到什么

- `medicines.sqlite`：原始单元格内容、规范字段、来源信息、检查提示。
- `01_monthly_overview.csv`：月度记录数、机构数、药品数及已知净指示性成本。
- `02_product_costs.csv`：按月、药品代码汇总和排名，展示窗口函数。
- `03_organisation_coverage.csv`：按月、ODS 机构代码统计可见记录和成本完整率。
- `04_findings_by_rule.csv`：通过 LEFT JOIN 汇总规则提示，保留没有行号的提示。
- `05_cost_sensitivity.csv`：保留负数与排除负数的假设对比。
- `SUMMARY.md`：中英文摘要；`manifest.json`：来源、SHA-256、检查时间及规则版本。

学习时先读 `sql/01_monthly_overview.sql`，理解 GROUP BY；接着看第三、第四条查询，理解分组与 JOIN；最后看第二条中的 CTE 和 DENSE_RANK。

## 分析口径

1. 指示性成本不等于医院实际采购支出。缺失和无效金额保留 NULL，不补零；全组都没有有效成本时，合计也为空。浮点汇总仅用于分析展示。
2. 保留负数、疑似重复和其他带提示记录，不自动删除。排除负数的金额仅是一个假设场景，不是推荐清洗方案。
3. 成本完整率 = 有效成本记录数 / 全部记录数，不代表支出覆盖率。合并分组时应用总分子除以总分母，不平均百分比。
4. 一条记录可能出现多项提示，因此提示数不等于问题记录数，各规则的受影响记录数不可直接相加。
5. 机构记录少不代表漏报或表现差，没有完整参照名录时只描述当前文件。当前仅一个月，不能得出增长或下降趋势。
6. 药品数量保留单位，不跨药品、跨单位直接相加；药品代码按文本保存，避免长数字精度损失。
7. `raw_json` 保存原始字段和值；SQL 的行号包含表头。无效月份单独保留为空组。CSV 中可能被识别为公式的文本加单引号，数据库原值不变。

## 接入 Power BI

“获取数据 → 文本/CSV”导入汇总文件。月份、ODS、药品代码设为文本；记录数为整数；金额和完整率为小数。完整率已经是 0–100，不要再用自动乘以 100 的百分比格式。

先做“月度概览”和“数据质量及分析限制”两页。各汇总表先独立使用，避免直接关联造成重复汇总；独立表的月份筛选器不会自动联动，第一版应明确选择同一个月。机构数、药品数等去重指标不能跨分组直接求和。

## 数据来源

[NHSBSA 2026 年 7 月临时发布 SCMD 及字段字典](https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753)。该页面标注 [OGL 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)。

Contains public sector information licensed under the Open Government Licence v3.0. Source: NHS Business Services Authority.

本项目为独立分析，不表示 NHS/NHSBSA 背书。代码采用仓库 MIT 许可，数据许可单独适用。真实原始文件和生成的数据库、汇总结果暂留本地，不加入 Git。

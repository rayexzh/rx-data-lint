# 第一课：从药品记录到月度汇总

目标：自己解释并修改 `sql/01_monthly_overview.sql`。先看结果，再读查询。

2026 年 7 月：319,345 条记录，其中 306,872 条有有效成本，12,473 条缺失成本。

## 先读这条简化查询

```sql
SELECT
    month,
    COUNT(*) AS records,
    COUNT(cost_gbp) AS known_cost_records,
    ROUND(100.0 * COUNT(cost_gbp) / COUNT(*), 4) AS known_cost_record_percent,
    ROUND(SUM(cost_gbp), 2) AS known_net_indicative_cost_gbp
FROM records
GROUP BY month
ORDER BY month;
```

| 写法 | 具体含义 |
|---|---|
| FROM records | 从刚导入的药品记录表读取数据 |
| GROUP BY month | 把同一个月的记录放在一起计算 |
| COUNT(*) | 数全部记录，即使成本为空也计数 |
| COUNT(cost_gbp) | 只数成本不为空的记录，负数和零都计数 |
| SUM(cost_gbp) | 汇总已知成本，保留负数，跳过空值 |
| ROUND(..., 2) | 展示时保留两位小数 |
| AS ... | 给输出列取一个容易理解的名字 |
| ORDER BY month | 按月份排列输出 |

这里的 `100.0` 使用小数运算。`306872 / 319345 * 100 = 96.0942%`：这是记录完整率，并不说明我们知道了 96.0942% 的总支出。

## 为什么不能把空值全部改成零

如果三条记录成本分别为 `100`、`NULL`、`-20`：

- `COUNT(*)` 是 3，`COUNT(cost_gbp)` 是 2。
- `SUM(cost_gbp)` 是 80，只代表已知部分。
- 把 NULL 改成 0 后，总和仍是 80，但完整率会被错误地变成 100%。
- 把负数那条删除，总和变成 100。这是处理方式造成的变化。

## 怎么亲自运行

在项目根目录的终端输入 `python`，进入 Python 后逐行输入：

```python
import sqlite3
from pathlib import Path
db = sqlite3.connect("file:analysis/output/202607/medicines.sqlite?mode=ro", uri=True)
sql = Path("analysis/sql/01_monthly_overview.sql").read_text(encoding="utf-8")
cursor = db.execute(sql)
print([column[0] for column in cursor.description])
print(cursor.fetchall())
db.close()
exit()
```

只读连接不会修改数据库。注意应在项目根目录执行，路径不存在会报错。

## 两个小练习

1. 把简化查询中的 GROUP BY 改成 `GROUP BY month, ods_code`，同时在 SELECT 中加入 `ods_code`。解释为什么输出变成了机构级汇总。
2. 加上 `WHERE cost_gbp < 0`（放在 FROM 后、GROUP BY 前）。解释为什么这时的 COUNT(*) 不是全部记录数。

做完后用自己的话说：**“我的汇总保留了负数，并单独展示缺失成本；这些数字只描述已知的指示性成本。”**

英文练习：

> I retained negative values and reported missing costs separately. The total represents known indicative costs, not actual procurement expenditure.

## 对应的两张图

![成本完整率](figures/202607/cost_completeness.png)

![负数成本影响](figures/202607/negative_cost_impact.png)

第一张图展示记录完整率；第二张图展示删除负数对同一份数据的影响。第二张图的横轴从零开始，避免把相对较小的差异画得夸张。它们是同月的处理场景对比，不是月度趋势。

# RxDataLint

检查 NHS 药品 CSV，查看需要复核的记录，再生成本地 SQL 汇总。

Check NHS medicines CSVs, inspect flagged records, and build local SQL summaries. [Full English README](README.md)

[下载 Windows 版](https://github.com/rayexzh/rx-data-lint/releases/tag/v0.4.0-alpha.2) · [文档目录](docs/INDEX.md) · [操作视频](docs/DEMO_VIDEO.md)

**当前版本：v0.4.0-alpha.2。** 在本机运行，不需要付费 API。

## 解决什么问题

RxDataLint 面向 NHSBSA 发布的医院药品数据（SCMD）。在做统计或导入 Power BI 前，先检查 CSV 中有哪些记录值得复核。

例如，负数量可能来自库存调整，空白费用不能直接当作零，重复记录也可能影响汇总。软件会列出检查规则、对应单元格和原始记录，方便你查清楚后再分析。

适合使用 SCMD 的分析人员，也可用于学习药品数据分析。它目前不是通用的医药数据检查器。

![桌面检查工具](docs/screenshots/checker-en.png)

## 两个入口，分别做什么

| 工具 | 操作 | 输出 |
|---|---|---|
| **数据检查** | 打开 SCMD CSV，搜索检查结果，查看对应原始记录。 | 检查说明、覆盖情况，以及完整报告或当前筛选范围的报告。 |
| **SQL 分析** | 选择 CSV，生成一次新的分析快照。 | SQLite 数据库、五张 CSV 汇总表、中英文离线 HTML 报告。 |

检查项包括必需字段、日期、编码、数值格式、疑似重复记录、负值和极端数量。缺失月份检查用于合并后的多月数据。搜索针对检查结果及其关联记录，不是搜索文件中的所有药品。

SQL 汇总回答：每月包含多少记录、哪些产品的已知指示性费用较高、各机构包含哪些数据、哪些规则触发较多，以及排除负费用后总额会怎样变化。空白或无效费用不会被填成零，不同产品或单位的数量也不会混加。

## 先试一次

1. 下载 Windows ZIP，**完整解压整个文件夹**。
2. 打开 **Start-Checker.bat**，点击 **Try sample／试用示例**。
3. 选中一条检查结果，查看原始记录，再选择导出完整报告或当前筛选报告。
4. 打开 **Start-Analysis.bat**，点击 **Use sample／使用示例**，然后 **Generate and verify／生成并验证**。
5. 打开生成的报告，或查看 CSV 汇总表。

故意设置了问题的示例包含 **8 条记录、4 条受影响记录、6 个错误、9 个警告**。一条记录可能触发多个检查项。这是功能演示，不代表 NHS 数据的整体质量。

使用真实公开文件时，可参考[公开数据案例](analysis/CASE_STUDY.md)，核对来源和临时发布状态。更换输入后需要重新运行，已完成的报告不会自动更新。

## 结果怎么理解

检查项是复核线索，不等于原始数据一定错误。负值可能合理；极端数量使用基于中位数的阈值，不是临床风险预测。字段标准化也不会自动修复异常记录。

指示性费用不是实际采购支出、销售额或节省金额。没有触发检查项，不代表临床正确或合规认证。大文件在内存中处理；参考编码验证及部分跨发布版本对比尚未实现。详细口径见[检查规则](docs/RULES.md)和 [SQL 指标说明](analysis/README.zh-CN.md)。

项目与 NHS、NHSBSA 无隶属关系。公开数据保留其原有许可；软件采用 [MIT 许可证](LICENSE)。

## 从源码运行

需要 Python 3.10 或以上版本。桌面工具使用 Python 标准库。

```powershell
python app.py
python analysis/desktop.py
```

命令行用法：

```powershell
python -m pip install -e .
rx-data-lint examples/sample_scmd.csv --output outputs/demo
```

## 更多资料

- [启动与 Windows 打包说明](docs/WINDOWS-SUITE.md)
- [SQL 查询、输出文件与 Power BI 导入](analysis/README.zh-CN.md)
- [更新记录](CHANGELOG.md)、[贡献说明](CONTRIBUTING.md)、[安全说明](SECURITY.md)
- [脚本化试用记录](docs/SIMULATED-USABILITY-REVIEW.md)：自动化检查，并非外部用户反馈。

操作视频展示较早版本的界面，制作方式见视频说明。[BatchScope](https://github.com/rayexzh/batchscope) 是另一个独立项目，处理模拟生产质量记录，有自己的下载和版本。

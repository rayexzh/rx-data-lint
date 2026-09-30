# 作品集主线 / Portfolio roadmap

这份文件记录项目取舍和下一步计划，不表示以下项目已完成，也不承诺开源支持申请或英国求职结果。

## 两个目标，分别积累证据

近期目标是争取 Codex for Open Source 支持。RxDataLint 继续公开维护，收集真实使用反馈、修复问题、发布可复现结果；申请材料仅写可以核查的事实，不虚构下载、用户、行业采用或节省金额。

长期目标是英国生命科学行业的数据分析、质量数字化或业务分析工作。作品集要连接药品质量与安全、电子经济和实际数据技能，同时让项目作者能独立解释数据模型、SQL、规则和业务限制。

功能数量不是进度指标。每个项目应回答一个具体业务问题，并留下输入、处理逻辑、结果、检查方法和使用反馈。

## 项目组合

| 项目 | 定位与证据 | 当前状态 | 下一步结束条件 |
|---|---|---|---|
| RxDataLint + NHS Medicines Analytics | 公开药品数据复核、Python/SQL、来源追溯、处理方式对成本汇总的影响 | 桌面 Alpha 版已发布；SQL 案例已上传；v0.3 运行包提供检查和分析两个 EXE、文件校验与离线报告 | 从新环境完成示例分析；至少开展一次外部试用并记录实际反馈；随后转为维护 |
| Quality Operations Analytics | 模拟药企检验、偏差及措施数据，体现质量业务问题和关系建模 | 规划阶段，尚未开发 | 完成可复现模拟数据、数据库、3 个分析问题和报告；解释全部指标 |
| RFM Customer Segmentation | 与本科论文关联的客户分析，补充商业和经济背景 | 根据论文进度开展，本仓库不声称已实现 | 对分群口径、时间窗口和可执行建议进行解释；完成 SQL/Python 分析 |

## 下一项目：Quality Operations Analytics

先做本地程序和 SQL 分析，不同时建设 CRM、商业销售平台、聊天助手及完整质量管理系统。

### 最小范围

用固定随机种子生成明确标注为 synthetic 的示例数据，并保留少量手工设计、已知预期结果的异常案例。数据不来自实习公司或真实实验记录。

数据库首版四张表：

1. `batches`：批次、产品、生产日期；一个批次可有多条检验结果和偏差。
2. `test_results`：检验类型、数值、单位、测量日期、示例规格上下限和检测方法；不把不同单位直接合并。
3. `deviations`：偏差 ID、关联批次、创建/关闭日期、分类、状态；保留未关闭记录。
4. `actions`：措施 ID、关联偏差、负责人角色、约定到期日、实际完成日、状态。

数据字典明确字段含义、主外键、空值、时间基准及规格来源。示例规格仅用于演示，不声称来自药典或代表真实药品合格标准。

### 首版只回答三个问题

| 问题 | 指标与口径 | 必须说明的边界 |
|---|---|---|
| 哪些示例检验结果超出设定范围？ | 按产品、检验类型、方法和单位计算可判定记录数、超出范围记录数及比例；缺失/无效值单列 | 自动标记是复核线索，不自动认定调查结论或批次放行 |
| 偏差处理哪里出现积压？ | 截至指定日期的未关闭数量及账龄；关闭耗时只统计有效的已关闭记录 | 不用只看已关闭记录的均值掩盖积压；不同偏差类型不可直接比较员工绩效 |
| 哪些措施需要跟进？ | 截至指定日期，未完成且约定到期日早于该日期的措施；未来信息不进入历史快照 | 逾期是跟进线索，不自动代表质量风险大小或措施无效 |

先检查重复主键、孤立外键、关闭早于创建、规格上下限反转、单位不匹配及缺失结果。对这些异常写小规模、可解释的验证案例。

### 交付闭环

固定种子的模拟数据 → SQLite 模型和数据字典 → JOIN/CTE/窗口函数查询 → 双语报告 → 一页业务解释。

Power BI 留作后续展示练习，不作为首版完成的前置条件。AI 解释只有在指标、证据引用和错误处理可以验证后再加入。

## 每一步都与学习结合

- 项目作者应能解释一条 SQL：它的记录粒度、JOIN 是否重复计数、分子分母及空值口径。
- 每周选择一个小改动自己完成，如新增过滤条件、检查规则或报告指标，并解释前后结果。
- 用英文准备一个两分钟案例：问题、方法、结果、限制。面试时明确 AI 辅助开发与自己的实际贡献。
- 收集真实使用反馈，区分操作反馈与专业规则审查；教师或同学试用不等于药企采用或业务验证。

## English summary

The portfolio serves two goals: a near-term open-source support application and a longer-term UK life-sciences data/quality-digitalisation career. RxDataLint contributes public-data review, Python/SQL analysis and source traceability. After the current usability work and an external trial, it should move to maintenance rather than continuous feature expansion.

The next planned project is **Quality Operations Analytics**, using reproducible synthetic data and four related tables: batches, test results, deviations and actions. Its first version answers three questions: which example measurements fall outside configured ranges, where deviation backlogs accumulate, and which actions are overdue as of an explicit date. Range flags are review prompts, not batch-release decisions; synthetic specifications are not represented as regulatory standards.

A separate RFM project supports the degree thesis and commercial-analysis story. Each project needs a narrow question, documented metrics, reproducible results and an explanation the owner can deliver independently. Planned work is not evidence of completed experience, adoption, regulatory validation or guaranteed application success.

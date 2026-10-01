# Project boundaries / 项目边界

| | RxDataLint | BatchScope |
|---|---|---|
| Repository / 仓库 | [rayexzh/rx-data-lint](https://github.com/rayexzh/rx-data-lint) | [rayexzh/batchscope](https://github.com/rayexzh/batchscope) |
| Domain / 业务 | Public NHS SCMD medicines data / NHS 公开药品数据 | Synthetic manufacturing quality / 模拟制造质量流程 |
| Inputs / 输入 | SCMD CSV; sample or publicly sourced data / SCMD 文件 | Four fictional tables plus synthetic declaration / 四表模拟数据 |
| Questions / 问题 | What needs review before aggregation? What does a cost-processing choice change? / 汇总前需复核什么？处理口径如何影响成本？ | What is outside a fictional range? Which deviations/actions need follow-up at a date? / 检验、偏差与措施如何跟进？ |
| Run / 启动 | Checker + analysis launchers inside one Rx workflow / 同一流程的检查与分析入口 | BatchScope.exe / 独立程序 |
| Downloads / 下载 | [Rx releases](https://github.com/rayexzh/rx-data-lint/releases) | [BatchScope releases](https://github.com/rayexzh/batchscope/releases) |

Each project builds and runs independently. There is no import, submodule or shared installed runtime between repositories. Cross-links are navigation only. Rx's SQL analysis remains here because it consumes the same SCMD input and review rules; it is not BatchScope.

两个项目独立构建、独立运行，没有互相导入、子模块或共同安装依赖。链接仅用于导航。Rx 的 SQL 分析继续保留，因为它使用相同的 SCMD 输入和复核规则，不属于 BatchScope。

Existing commits and releases remain as historical records. The previous portfolio roadmap called the quality project “planned”; it has been replaced with current ownership links. No historical Git commits were rewritten and no released files were deleted.

保留历史提交和旧版本。旧路线文档中“质量项目尚未开发”的描述已更新；不改写 Git 历史、不删除旧发布文件。

# RxDataLint

[English](README.md) | [简体中文](README.zh-CN.md)

[![Tests](https://github.com/rayexzh/rx-data-lint/actions/workflows/tests.yml/badge.svg)](https://github.com/rayexzh/rx-data-lint/actions/workflows/tests.yml)

RxDataLint 是一个本地运行的开源药品数据质量检查工具。第一版面向英国
NHSBSA 发布的 Secondary Care Medicines Data（SCMD），帮助用户在趋势分析、
机构比较或导入 Power BI 之前发现潜在的数据问题。

程序不会把数据上传到服务器。它可以导出标准化 CSV、JSON 检查结果和独立
HTML 报告。

本项目仍处于 Alpha 阶段，与 NHS、NHSBSA 和 OpenPrescribing 没有关联。
“未发现问题”不代表数据在临床、财务或监管意义上一定正确。

## 为什么开发这个项目

公开药品数据很有价值，但也很容易被错误解读。字段结构变化、负数库存调整、
缺失提交、重复记录和极端数值，都可能改变趋势和机构比较的结论。

RxDataLint 希望在“下载原始数据”和“制作分析结果”之间增加一个透明、可解释的
质量检查步骤。项目结合药品质量管理思维、Python 数据处理和商业分析流程，目标
用户包括医药数据分析人员、教师、学生以及希望学习英国医药数据的人。

## 当前功能

- 支持 NHSBSA 当前 SCMD 字段结构；
- 兼容部分 2026 年 6 月前的旧字段名；
- 检查月份、ODS Code、SNOMED Code、药品名称和数值字段；
- 标记负数药品数量和负数指示成本；
- 发现疑似重复的“月份—Trust—药品”记录；
- 检查合并数据中 Trust 缺失的月份；
- 通过透明的 20 倍中位数规则标记极端用量；
- 提供中英文桌面界面；
- 导出清洗后的 CSV、JSON 和 HTML 报告；
- 所有数据处理均在用户电脑本地完成。

## Windows 桌面程序

需要 Python 3.10 或更高版本，不需要安装第三方运行库。最简单的方法是双击：

```text
run_desktop.bat
```

在 PyCharm 中，可以打开整个项目文件夹，然后运行项目根目录的 `app.py`。

也可以在 PowerShell 中运行：

```powershell
python -m pip install -e .
rx-data-lint-gui
```

## 测试示例

启动程序后选择：

```text
examples/sample_scmd.csv
```

这份合成数据故意包含负数、重复记录、错误日期、错误代码、缺失月份和极端数量，
用于确认检查规则能够正常工作。示例不包含患者数据。

## 命令行使用

```powershell
python -m pip install -e .
rx-data-lint examples/sample_scmd.csv --output outputs/demo
```

当报告包含 error 时，命令以状态码 1 退出，因此未来可以接入自动化数据流程。

## 自动化测试

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

GitHub Actions 会在多个 Python 版本上自动运行测试。

## 当前限制

- 检查结果属于筛查提示，不代表原始数据一定错误；
- 质量分仍是实验性指标，不属于临床、财务或监管结论；
- 多月份大型文件目前会在内存中处理，可能需要等待；
- dm+d 参考数据验证尚未实现；
- 暂定数据与最终数据的自动回溯比较尚未实现。

## 后续方向

- 比较 provisional 与 finalised SCMD；
- 自动识别新的字段结构变化；
- 检查产品级提交异常；
- 加入 dm+d 参考数据验证；
- 提高大型 CSV 的处理速度；
- 导出适合 Power BI 的星型数据模型；
- 根据真实用户反馈增加规则。

## 数据来源

SCMD 由 NHS Business Services Authority 发布，并使用英国 Open Government
Licence。使用数据前应阅读官方说明，尤其要注意暂定数据、负数库存调整以及
indicative cost 不等于医院实际采购净成本。

官方数据页面：

https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price

## 参与贡献

欢迎提交错误报告、公开或合成的数据示例、验证规则建议、中文或英文文档改进，
以及大型数据文件的性能优化。请勿在公开 issue 中上传患者数据、医院内部数据或
商业敏感数据。

详细要求参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT

## 开发进度

参见 [v0.2 改进清单](docs/V0.2-PLAN.zh-CN.md) 与 [规则及适用边界](docs/RULES.md)。报告已增加输入文件 SHA-256、字节数、检查时间、版本和受影响记录数；这些信息用于复查，不代表合规认证。当前仍在内存中处理数据。


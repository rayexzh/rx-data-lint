"""Create offline, self-contained analysis reports from the SQLite summaries."""
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


REPORT_FILES = ("REPORT.zh-CN.html", "REPORT.en.html")
NHSBSA_JULY_RESOURCE = "https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price/resource/4112eed6-b93a-4cfd-9582-c216d4416753"

TEXT = {
    "en": {
        "title": "Medicines data review", "subtitle": "SCMD analysis · review before interpretation",
        "other": "简体中文", "other_file": REPORT_FILES[0],
        "records": "Records", "known": "Known costs", "missing": "Missing costs", "invalid": "Invalid nonblank costs",
        "orgs": "Observed organisations", "products": "Observed products",
        "months": "Valid months", "overview": "File overview", "month": "Month",
        "invalid_month": "Invalid month (retained)", "coverage": "Cost completeness by record count",
        "coverage_note": "Completeness describes records, not expenditure coverage. Missing and invalid costs remain unavailable, never zero.",
        "costs": "What changes if negative costs are excluded?",
        "including": "Including negatives", "excluding": "Excluding negatives (hypothetical)",
        "negative": "Negative-cost records", "component": "Negative component", "delta": "Change in reported sum",
        "money_note": "Known indicative costs in GBP. These are not actual procurement expenditures. The change is a processing sensitivity, not savings or a recommendation to delete negatives.",
        "unavailable": "Unavailable", "empty_scenario": "A sum remains unavailable when its group has no matching known amounts.",
        "review": "Review findings", "rule": "Rule", "severity": "Level", "findings": "Findings",
        "affected": "Associated records", "unlocated": "Unlocated findings", "action": "Suggested review",
        "error": "Error", "warning": "Warning", "info": "Information",
        "finding_note": "One record can trigger multiple rules. Do not add affected-record counts across rules. Warning records and duplicate candidates remain in the analysis.",
        "no_findings": "No findings under the implemented rules. This does not certify data accuracy.",
        "fallback": "Review the original record and the source dictionary in the desktop checker.",
        "limits": "Scope and limits", "single": "Only one valid month is present: this report cannot establish trends.",
        "multiple": "Monthly totals are descriptive. Check organisation coverage, units and release comparability before comparing months.",
        "zero_months": "No valid months are present. Review the retained invalid-month group before interpreting totals.",
        "general_limits": "All source rows are retained, including candidate duplicates. Quantities across products or units are not summed. This report does not establish clinical correctness, hospital performance or regulatory compliance. SQL floating-point totals are rounded for presentation and are unsuitable for ledger reconciliation.",
        "trace": "Source and reproducibility", "file": "Input file", "source": "Source supplied by user",
        "time": "Checked at (UTC)", "version": "Tool / ruleset", "hash": "Input SHA-256",
        "verify": "The run manifest records hashes for this report, the database and summaries. Run the file verification command before relying on copied outputs. Hash matching checks consistency, not the authenticity of the manifest or source accuracy.",
        "sharing": "This report contains aggregate results and source metadata; inspect it before sharing. It is an offline report, not a hosted dashboard. Open it in a browser or use the browser’s Print function to save a PDF.",
        "credit": "Declared source: NHS Business Services Authority, provisional July 2026 SCMD. Contains public sector information licensed under the Open Government Licence v3.0. Independent analysis; no NHS/NHSBSA endorsement.",
    },
    "zh-CN": {
        "title": "药品数据分析报告", "subtitle": "SCMD 数据复核 · 先检查，再解释",
        "other": "English", "other_file": REPORT_FILES[1],
        "records": "记录数", "known": "已知成本记录", "missing": "缺失成本记录", "invalid": "非空无效成本记录",
        "orgs": "观察到的机构", "products": "观察到的药品", "months": "有效月份", "overview": "文件概览",
        "month": "月份", "invalid_month": "无效月份（仍保留）", "coverage": "按记录数计算的成本完整率",
        "coverage_note": "完整率描述记录数量，不等于支出覆盖率。缺失和无效成本保持未知，不按零处理。",
        "costs": "排除负数成本后，汇总会怎样变化？", "including": "保留负数成本",
        "excluding": "排除负数成本（假设场景）", "negative": "负数成本记录", "component": "负数成本合计",
        "delta": "汇总差额", "money_note": "金额单位为英镑，表示已知指示性成本，并非实际采购支出。差额体现处理方式的影响，不是节省金额，也不建议据此删除负数。",
        "unavailable": "无法计算", "empty_scenario": "当某个场景没有符合条件的已知金额时，SQL 合计保持未知。",
        "review": "问题复核", "rule": "规则", "severity": "级别", "findings": "提示数",
        "affected": "关联记录数", "unlocated": "未定位提示", "action": "建议怎样复核",
        "error": "错误", "warning": "警告", "info": "信息",
        "finding_note": "同一条记录可能触发多条规则，请勿将各规则关联记录数相加。警告记录和疑似重复记录仍参与分析。",
        "no_findings": "现有规则未发现问题；这不代表数据已被认证为准确。",
        "fallback": "在桌面检查程序中查看原始记录，并对照来源字典复核。",
        "limits": "检查范围与限制", "single": "只有一个有效月份，不能据此得出趋势结论。",
        "multiple": "月度合计仅作描述。跨月比较前应复核机构覆盖、计量单位和发布口径是否一致。",
        "zero_months": "没有有效月份。解释汇总前，应先复核保留的无效月份分组。",
        "general_limits": "保留全部源记录，包括疑似重复；不跨药品或单位累加用量。报告不证明临床正确性、医院绩效或合规认证。SQL 浮点合计仅在展示时四舍五入，不适用于财务账目核对。",
        "trace": "来源与复现", "file": "输入文件", "source": "用户填写的来源", "time": "检查时间（UTC）",
        "version": "工具版本 / 规则版本", "hash": "输入 SHA-256",
        "verify": "运行记录包含本报告、数据库和摘要的文件哈希。使用复制的输出前，请运行文件校验。哈希匹配只说明文件与运行记录一致，不验证运行记录真实性或源数据准确性。",
        "sharing": "本报告包含汇总指标和来源信息，分享前请检查内容。这是离线报告，不是托管仪表盘。可在浏览器打开，也可使用浏览器打印功能保存为 PDF。",
        "credit": "声明的来源：NHS Business Services Authority，2026 年 7 月临时发布 SCMD。Contains public sector information licensed under the Open Government Licence v3.0. 独立分析，不表示 NHS/NHSBSA 背书。",
    },
}

GUIDANCE = {
    "value.missing_cost": ("Check whether the source release lacks a usable indicative price. Report known sums with the missing-record count; do not fill missing costs with zero.", "核对发布字典中缺失价格的含义；展示已知成本时同时说明缺失记录数，不将其填为零。"),
    "value.negative": ("Inspect original cost/quantity and adjustment context. Negative values can represent adjustments; do not automatically delete or take absolute values.", "查看原始成本、用量及调整背景。负数可能是调整记录，不自动删除或取绝对值。"),
    "row.duplicate_key": ("Confirm whether matching month/organisation/product keys represent distinct records before any deduplication.", "核对相同月份、机构和药品编码的记录是否有不同业务含义，再决定是否去重。"),
    "series.extreme_quantity": ("Check product units and organisation context. A 20×-median flag is a review heuristic, not proof of an error.", "核对药品单位和机构背景；超过中位数 20 倍仅是复核线索，不证明记录错误。"),
    "series.missing_month": ("Check submission history and organisation coverage before interpreting a gap as zero use.", "先核对提交历史和机构覆盖，不将缺月直接理解为零用量。"),
    "value.numeric": ("Inspect the original numeric string and source conventions; invalid amounts remain NULL in SQL.", "核对原始数值字符串及来源格式，无效金额在 SQL 中保持 NULL。"),
    "value.year_month": ("Confirm the release month and date format; invalid months remain in a separate group.", "确认发布月份和日期格式，无效月份仍保留为单独分组。"),
}

CSS = """
:root{color-scheme:light;font-family:Segoe UI,Microsoft YaHei,Arial,sans-serif;color:#243a34;background:#f3f6f4}
*{box-sizing:border-box}body{margin:0}main{max-width:1060px;margin:auto;padding:38px 24px 60px}
header{border-top:6px solid #176b58;padding:24px 0}h1{font-size:34px;margin:10px 0}h2{font-size:22px;margin:0 0 18px}
h3{font-size:17px;margin:18px 0 10px}p{line-height:1.7}a{color:#176b58}small,.muted{color:#566b63}
.brand{font-size:13px;letter-spacing:2px;font-weight:700}.switch{float:right}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.card{background:white;padding:20px;border:1px solid #dbe5df;border-radius:8px}
.card strong{display:block;font-size:28px;margin-bottom:8px}.card span{font-size:14px}.context{margin:18px 0}
section{background:white;border:1px solid #dbe5df;border-radius:8px;padding:26px;margin:20px 0}
.note{background:#f4f7f5;border-left:3px solid #8ba99b;padding:12px 16px;font-size:14px}.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:870px;font-size:14px}th,td{text-align:left;padding:12px 10px;border-bottom:1px solid #e3eae5;vertical-align:top}
th:first-child{width:205px}th:nth-child(2){width:65px}th:nth-child(3){width:75px}th:nth-child(4),th:nth-child(5){width:100px}th:not(:last-child),.severity{white-space:nowrap}
th{background:#edf3ef}td.numeric{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}code{font-size:12px;overflow-wrap:anywhere}
.stack{display:flex;height:28px;border-radius:4px;overflow:hidden;background:#edf3ef;margin:12px 0}.legend{display:flex;gap:24px;flex-wrap:wrap;font-size:14px}
.known{background:#176b58}.missing{background:#c98b22}.invalid{background:#a3434b}.dot{display:inline-block;width:10px;height:10px;margin-right:6px}
.metrics{display:flex;gap:28px;flex-wrap:wrap;margin:12px 0}.metrics strong{display:block;margin:6px 0;font-size:19px}
.costchart{width:100%;max-width:620px;height:auto;display:block}.costmonth{border-bottom:1px solid #e3eae5;padding-bottom:18px;margin-bottom:18px}
dl{display:grid;grid-template-columns:170px minmax(0,1fr);gap:12px;font-size:14px}dt{color:#566b63}dd{margin:0;overflow-wrap:anywhere}.severity{font-weight:600}
@media(max-width:650px){main{padding:18px 12px}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}section{padding:18px}h1{font-size:28px}dl{grid-template-columns:1fr;gap:6px}dd{margin-bottom:8px}}
@media print{body{background:white}main{padding:0;max-width:none}.switch{display:none}section{break-inside:avoid;border-radius:0}.tablewrap{overflow:visible}table{font-size:11px}a{color:inherit}h1{font-size:26px}.card strong{font-size:22px}}
"""


def query_rows(db, name):
    cursor = db.execute((Path(__file__).parent / "sql" / name).read_text(encoding="utf-8"))
    columns = [c[0] for c in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def money(value, text):
    return text["unavailable"] if value is None else f"£{value:,.2f}"


def cost_chart(values, text):
    if any(v is None for v in values):
        return f'<p class="muted">{text["empty_scenario"]}</p>'
    low, high = min(0, *values), max(0, *values)
    span = high - low or 1
    scale = lambda value: 8 + 580 * (value - low) / span
    zero = scale(0)
    bars = []
    for value, label, colour, y in zip(values, (text["including"], text["excluding"]), ("#176b58", "#c98b22"), (28, 94)):
        end = scale(value)
        bars.append(f'<text x="8" y="{y-7}" font-size="13">{escape(label)}</text>'
                    f'<rect x="{min(zero,end):.3f}" y="{y}" width="{abs(end-zero):.3f}" height="22" fill="{colour}"/>'
                    f'<text x="588" y="{y-7}" text-anchor="end" font-size="13">{money(value,text)}</text>')
    return ('<svg class="costchart" viewBox="0 0 600 132" role="img" xmlns="http://www.w3.org/2000/svg">'
            f'<title>{escape(text["costs"])}</title><line x1="{zero:.3f}" x2="{zero:.3f}" y1="28" y2="117" stroke="#53685e"/>'
            + ''.join(bars) + '</svg>')


def render_reports(db, metadata, output):
    monthly = query_rows(db, "01_monthly_overview.sql")
    costs = query_rows(db, "05_cost_sensitivity.sql")
    findings = query_rows(db, "04_findings_by_rule.sql")
    counts = {key: sum(r[key] for r in monthly) for key in ("records", "known_cost_records", "missing_cost_records", "invalid_cost_records")}
    orgs, products = db.execute("SELECT COUNT(DISTINCT NULLIF(ods_code,'')), COUNT(DISTINCT NULLIF(product_code,'')) FROM records").fetchone()
    for language, filename in zip(("zh-CN", "en"), REPORT_FILES):
        t = TEXT[language]
        month_label = lambda value: escape(value) if value else t["invalid_month"]
        cards = ''.join(f'<div class="card"><strong>{counts[key]:,}</strong><span>{t[label]}</span></div>'
                        for key, label in (("records", "records"), ("known_cost_records", "known"), ("missing_cost_records", "missing"), ("invalid_cost_records", "invalid")))
        coverage = []
        for row in monthly:
            legend, segments = [], []
            for key, label in (("known_cost_records", "known"), ("missing_cost_records", "missing"), ("invalid_cost_records", "invalid")):
                pct = 100 * row[key] / row["records"]
                segments.append(f'<span class="{label}" style="width:{pct:.6f}%"></span>')
                legend.append(f'<span><i class="dot {label}"></i>{t[label]}: {row[key]:,} ({pct:.2f}%)</span>')
            coverage.append(f'<h3>{month_label(row["month"])}</h3><div class="stack" aria-hidden="true">{"".join(segments)}</div><div class="legend">{"".join(legend)}</div>')
        cost_sections = []
        for row in costs:
            net, nonnegative = row["known_net_indicative_cost_gbp"], row["nonnegative_only_cost_gbp"]
            delta = nonnegative - net if net is not None and nonnegative is not None else None
            metrics = ''.join(f'<div>{t[key]}<strong>{value}</strong></div>' for key, value in (
                ("negative", f'{row["negative_cost_records"]:,}'), ("component", money(row["negative_component_gbp"], t)), ("delta", money(delta, t))))
            cost_sections.append(f'<div class="costmonth"><h3>{month_label(row["month"])}</h3>{cost_chart((net,nonnegative),t)}<div class="metrics">{metrics}</div></div>')
        finding_rows = []
        for row in findings:
            guidance = GUIDANCE.get(row["rule"])
            action = guidance[language == "zh-CN"] if guidance else t["fallback"]
            finding_rows.append('<tr>' + f'<td><code>{escape(row["rule"])}</code></td><td class="severity">{escape(t.get(row["severity"], row["severity"]))}</td>'
                                + ''.join(f'<td class="numeric">{row[key]:,}</td>' for key in ("findings", "affected_records", "unlocated_findings"))
                                + f'<td>{escape(action)}</td></tr>')
        finding_table = ('<div class="tablewrap"><table><thead><tr>'
                         + ''.join(f'<th scope="col">{t[key]}</th>' for key in ("rule", "severity", "findings", "affected", "unlocated", "action"))
                         + '</tr></thead><tbody>' + ''.join(finding_rows) + '</tbody></table></div>') if findings else f'<p>{t["no_findings"]}</p>'
        url = metadata["source_url"]
        try:
            parsed = urlsplit(url)
            linkable = parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except ValueError:
            linkable = False
        source = f'<a href="{escape(url,quote=True)}" rel="noreferrer">{escape(url)}</a>' if linkable else escape(url)
        credit = (f'<p>{t["credit"]} <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/">OGL v3.0</a></p>'
                  if url.rstrip("/") == NHSBSA_JULY_RESOURCE else "")
        trace = ''.join(f'<dt>{t[key]}</dt><dd>{value}</dd>' for key, value in (
            ("file", escape(metadata["source_file"])), ("source", source), ("time", escape(metadata["checked_at_utc"])),
            ("version", escape(f'{metadata["tool_version"]} / {metadata["ruleset_version"]}')),
            ("hash", f'<code>{escape(metadata["source_sha256"])}</code>')))
        months = len(metadata["months"])
        limit = t["single"] if months == 1 else t["zero_months"] if months == 0 else t["multiple"]
        html = f'''<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>RxDataLint — {t['title']}</title><style>{CSS}</style></head><body><main>
<header><a class="switch" href="{t['other_file']}" lang="{'en' if language == 'zh-CN' else 'zh-CN'}">{t['other']}</a><div class="brand">RxDataLint</div><h1>{t['title']}</h1><p class="muted">{t['subtitle']}</p></header>
<h2>{t['overview']}</h2><div class="cards">{cards}</div><p class="context">{t['orgs']}: {orgs:,} · {t['products']}: {products:,} · {t['months']}: {months}</p>
<section><h2>{t['coverage']}</h2>{''.join(coverage)}<p class="note">{t['coverage_note']}</p></section>
<section><h2>{t['costs']}</h2>{''.join(cost_sections)}<p class="note">{t['money_note']}</p></section>
<section><h2>{t['review']}</h2>{finding_table}<p class="note">{t['finding_note']}</p></section>
<section><h2>{t['limits']}</h2><p>{limit}</p><p>{t['general_limits']}</p></section>
<section><h2>{t['trace']}</h2><dl>{trace}</dl><p>{t['verify']}</p><code>python analysis/verify_analysis.py &lt;output-folder&gt;</code></section>
<footer>{credit}<p class="muted">{t['sharing']}</p></footer></main></body></html>
'''
        (output / filename).write_text(html, encoding="utf-8")

"""Dependency-free desktop interface using Tkinter."""

from __future__ import annotations

import tkinter as tk
from queue import Empty, Queue
from threading import Thread
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .reports import write_outputs
from .review import record_for, summarise, write_filtered_findings
from .validator import Issue, validate_csv


TEXT = {
    "zh": {
        "title": "RxDataLint",
        "subtitle": "在分析前检查 NHS 医院药品数据（SCMD）的质量",
        "choose": "选择 SCMD CSV",
        "export": "导出完整报告",
        "language": "English",
        "no_file": "尚未选择文件",
        "checking": "正在检查数据，请稍候…",
        "score": "受影响记录数",
        "rows": "检查行数",
        "errors": "错误",
        "warnings": "警告",
        "missing_cost": "费用缺失（记录占比）",
        "passed": "已执行的检查未发现问题，请查看检查覆盖情况",
        "review": "发现需要检查的问题",
        "severity": "级别",
        "rule": "检查规则",
        "row": "行号",
        "column": "字段",
        "finding": "发现的问题",
        "details": "问题详情",
        "select_hint": "点击上方任意问题，可在这里查看完整说明。",
        "no_issues": "未发现问题",
        "export_title": "选择报告保存文件夹",
        "exported": "报告导出成功",
        "created": "已生成 3 个文件：\nquality-report.html\nquality-report.json\nnormalized-scmd.csv\n\n保存位置：\n{path}",
        "open_error": "无法检查文件",
        "export_error": "无法导出报告",
        "status_ready": "就绪",
        "status_loaded": "已完成：{name}",
        "error": "错误",
        "warning": "警告",
        "info": "提示",
        "guidance": "处理建议",
        "value": "原始值",
        "score_note": "受影响记录数按记录去重。请结合检查覆盖情况阅读结果；已执行不等于通过，规范化导出不会自动修正异常。",
    },
    "en": {
        "title": "RxDataLint",
        "subtitle": "Review NHS Secondary Care Medicines Data before analysis",
        "choose": "Choose SCMD CSV",
        "export": "Export full report",
        "language": "中文",
        "no_file": "No file selected",
        "checking": "Checking data…",
        "score": "Affected records",
        "rows": "Rows checked",
        "errors": "Errors",
        "warnings": "Warnings",
        "missing_cost": "Missing cost (% of records)",
        "passed": "No findings in executed checks; review coverage",
        "review": "Findings need review",
        "severity": "Severity",
        "rule": "Rule",
        "row": "Row",
        "column": "Column",
        "finding": "Finding",
        "details": "Finding details",
        "select_hint": "Select a finding above to read the complete explanation.",
        "no_issues": "No issues found",
        "export_title": "Choose a report folder",
        "exported": "Report exported",
        "created": "Created 3 files:\nquality-report.html\nquality-report.json\nnormalized-scmd.csv\n\nSaved to:\n{path}",
        "open_error": "Could not validate file",
        "export_error": "Could not export report",
        "status_ready": "Ready",
        "status_loaded": "Complete: {name}",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "guidance": "Guidance",
        "value": "Source value",
        "score_note": "Affected records are counted once. Review check coverage: executed does not mean passed, and normalized exports do not correct findings.",
    },
}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = "zh"
        self.search_query = ""
        self.active_filter = "all"
        self.result = None
        self.busy = False
        self._poll_id = None
        self._render_id = None
        self.source_path: Path | None = None
        self.issue_by_item: dict[str, Issue] = {}
        self.title("RxDataLint — NHS medicines data quality")
        self.geometry("1180x850")
        self.minsize(900, 800)
        self.configure(background="#f3f7f5")
        self._configure_styles()
        self._build()
        self._refresh_text()

    @property
    def t(self) -> dict[str, str]:
        return TEXT[self.language]

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f3f7f5")
        style.configure("Header.TFrame", background="#123c32")
        style.configure("Title.TLabel", background="#123c32", foreground="white", font=("Microsoft YaHei UI", 23, "bold"))
        style.configure("Subtitle.TLabel", background="#123c32", foreground="#d8ebe5", font=("Microsoft YaHei UI", 10))
        style.configure("Primary.TButton", font=("Microsoft YaHei UI", 10, "bold"), padding=(14, 8))
        style.configure("Toolbar.TButton", font=("Microsoft YaHei UI", 9), padding=(11, 7))
        style.configure("MetricCard.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Metric.TLabel", background="white", foreground="#17372f", font=("Microsoft YaHei UI", 19, "bold"))
        style.configure("MetricName.TLabel", background="white", foreground="#64756f", font=("Microsoft YaHei UI", 9))
        style.configure("Passed.TLabel", background="#dff5e8", foreground="#14633c", font=("Microsoft YaHei UI", 11, "bold"), padding=10)
        style.configure("Review.TLabel", background="#fff0dc", foreground="#8a4b08", font=("Microsoft YaHei UI", 11, "bold"), padding=10)
        style.configure("Treeview", rowheight=29, font=("Microsoft YaHei UI", 9), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"), background="#dce9e4", foreground="#17372f")

    def _build(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame", padding=(26, 12))
        header.pack(fill="x")
        self.title_label = ttk.Label(header, style="Title.TLabel")
        self.title_label.pack(anchor="w")
        self.subtitle_label = ttk.Label(header, style="Subtitle.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(3, 0))

        content = ttk.Frame(self, style="App.TFrame", padding=14)
        content.pack(fill="both", expand=True)

        toolbar = ttk.Frame(content, style="App.TFrame")
        toolbar.pack(fill="x", pady=(0, 14))
        self.choose_button = ttk.Button(toolbar, style="Primary.TButton", command=self.choose_file)
        self.choose_button.pack(side="left")
        self.export_button = ttk.Button(toolbar, style="Toolbar.TButton", command=self.export_report, state="disabled")
        self.export_button.pack(side="left", padx=8)
        self.language_button = ttk.Button(toolbar, style="Toolbar.TButton", command=self.toggle_language)
        self.language_button.pack(side="right")
        self.file_label = ttk.Label(toolbar, background="#f3f7f5", foreground="#42554f")
        self.file_label.pack(side="left", padx=12)
        self.progress = ttk.Progressbar(content, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))

        metrics = ttk.Frame(content, style="App.TFrame")
        metrics.pack(fill="x", pady=(0, 12))
        self.metric_widgets: dict[str, tuple[ttk.Label, ttk.Label]] = {}
        for key in ("score", "rows", "errors", "warnings", "missing_cost"):
            card = ttk.Frame(metrics, padding=(16, 11), style="MetricCard.TFrame")
            card.pack(side="left", fill="x", expand=True, padx=(0, 9))
            value = ttk.Label(card, text="—", style="Metric.TLabel")
            value.pack(anchor="w")
            name = ttk.Label(card, style="MetricName.TLabel")
            name.pack(anchor="w")
            self.metric_widgets[key] = (value, name)

        review_bar = ttk.Frame(content, style="App.TFrame")
        review_bar.pack(fill="x", pady=(0, 8))
        self.coverage_button = ttk.Button(review_bar, command=self.show_coverage)
        self.coverage_button.pack(side="left", padx=(0, 8))
        self.summary_button = ttk.Button(review_bar, command=self.show_summary)
        self.summary_button.pack(side="left")
        self.filtered_export_button = ttk.Button(review_bar, command=self.export_filtered, state="disabled")
        self.filtered_export_button.pack(side="left", padx=8)
        self.filter_bar = ttk.Frame(content, style="App.TFrame")
        self.filter_bar.pack(fill="x", pady=(0, 8))
        self.filter_buttons = {}
        for key in ("all", "value.missing_cost", "value.negative", "series.extreme_quantity", "other"):
            button = ttk.Button(self.filter_bar, command=lambda k=key: self.select_filter(k))
            button.pack(side="left", padx=(0, 6))
            self.filter_buttons[key] = button
        search_bar = ttk.Frame(content, style="App.TFrame")
        search_bar.pack(fill="x", pady=(0, 8))
        self.search_label = ttk.Label(search_bar, background="#f3f7f5")
        self.search_label.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=8)
        self.search_entry.bind("<Return>", self.apply_search)
        self.search_button = ttk.Button(search_bar, command=self.apply_search)
        self.search_button.pack(side="left")
        self.clear_button = ttk.Button(search_bar, command=self.clear_search)
        self.clear_button.pack(side="left", padx=(6, 0))
        self.filter_note = ttk.Label(content, background="#f3f7f5")
        self.filter_note.pack(anchor="w", pady=(0, 6))
        self.result_banner = ttk.Label(content, style="Passed.TLabel")

        table_frame = ttk.Frame(content)
        table_frame.pack(fill="both", expand=True)
        columns = ("severity", "rule", "row", "column", "finding")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        widths = (90, 180, 65, 290, 560)
        for column, width in zip(columns, widths):
            self.tree.column(column, width=width, minwidth=55, stretch=column == "finding")
        self.tree.tag_configure("error", background="#fff0f0", foreground="#8e1b1b")
        self.tree.tag_configure("warning", background="#fff8e8", foreground="#7b4800")
        self.tree.tag_configure("info", background="#eef6ff", foreground="#215a86")
        self.tree.tag_configure("passed", background="#eefbf3", foreground="#14633c")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.show_selected_issue)

        self.details_frame = ttk.LabelFrame(content, padding=10)
        self.details_frame.pack(fill="x", side="bottom", pady=(12, 0))
        self.details = tk.Text(
            self.details_frame, height=5, wrap="word", borderwidth=0, background="#ffffff",
            foreground="#263832", font=("Microsoft YaHei UI", 9), padx=6, pady=4,
        )
        detail_scroll = ttk.Scrollbar(self.details_frame, command=self.details.yview)
        detail_scroll.pack(side="right", fill="y")
        self.details.configure(yscrollcommand=detail_scroll.set)
        self.details.pack(fill="both", expand=True)
        self.details.configure(state="disabled")
        # Reserve the details panel before allocating remaining space to the table.
        table_frame.pack_forget()
        table_frame.pack(fill="both", expand=True)

        self.status = ttk.Label(self, anchor="w", padding=(12, 5), background="#e3ebe8", foreground="#40514b")
        self.status.pack(fill="x", side="bottom", before=content)

    def _refresh_text(self) -> None:
        self.refresh_filters()
        self.coverage_button.configure(text="检查覆盖情况" if self.language == "zh" else "Check coverage")
        self.summary_button.configure(text="问题概览" if self.language == "zh" else "Finding overview")
        self.filtered_export_button.configure(text="导出当前筛选的问题" if self.language == "zh" else "Export filtered findings")
        self.title_label.configure(text=self.t["title"])
        self.subtitle_label.configure(text=self.t["subtitle"])
        self.choose_button.configure(text=self.t["choose"])
        self.export_button.configure(text=self.t["export"])
        self.language_button.configure(text=self.t["language"])
        self.file_label.configure(text=self.source_path.name if self.source_path else self.t["no_file"])
        for key, (_, name) in self.metric_widgets.items():
            name.configure(text=self.t[key])
        for key, title in {
            "severity": self.t["severity"], "rule": self.t["rule"], "row": self.t["row"],
            "column": self.t["column"], "finding": self.t["finding"],
        }.items():
            self.tree.heading(key, text=title)
        self.details_frame.configure(text=self.t["details"])
        self._set_details(self.t["select_hint"])
        self.status.configure(text=self.t["status_loaded"].format(name=self.source_path.name) if self.source_path else self.t["status_ready"])
        if self.result:
            self._render_result()

    def toggle_language(self) -> None:
        self.language = "en" if self.language == "zh" else "zh"
        self._refresh_text()

    def choose_file(self) -> None:
        if self.busy:
            return
        selected = filedialog.askopenfilename(
            title=self.t["choose"], filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not selected:
            return
        candidate = Path(selected)

        def loaded(result):
            self.source_path = candidate
            self.result = result
            self.search_query = ""
            self.search_var.set("")
            self.active_filter = "all"
            self.export_button.configure(state="normal")
            self._render_result()

        self._run_background(lambda: validate_csv(candidate), loaded,
                             self.t["checking"] + " " + candidate.name, self.t["open_error"])

    def _run_background(self, operation, completed, status, error_title):
        """Workers exchange plain Python values; all Tk calls stay on the UI thread."""
        if self.busy:
            return
        self.busy = True
        for widget in (self.choose_button, self.export_button, self.language_button,
                       self.filtered_export_button, self.summary_button,
                       self.search_entry, self.search_button, self.clear_button,
                       *self.filter_buttons.values()):
            widget.configure(state="disabled")
        self.progress.start(15)
        self.status.configure(text=status)
        mailbox = Queue(maxsize=1)

        def work():
            try:
                mailbox.put((True, operation()))
            except Exception as exc:
                mailbox.put((False, str(exc)))

        def poll():
            self._poll_id = None
            try:
                success, value = mailbox.get_nowait()
            except Empty:
                self._poll_id = self.after(50, poll)
                return
            self.busy = False
            self.progress.stop()
            self.progress.configure(value=0)
            for widget in (self.choose_button, self.language_button, self.search_entry,
                           self.search_button, self.clear_button, self.summary_button):
                widget.configure(state="normal")
            self.export_button.configure(state="normal" if self.result else "disabled")
            self.refresh_filters()
            self.status.configure(text=self.t["status_loaded"].format(name=self.source_path.name)
                                  if self.source_path else self.t["status_ready"])
            if success:
                completed(value)
            else:
                messagebox.showerror(error_title, value)

        Thread(target=work, daemon=True).start()
        self._poll_id = self.after(50, poll)

    def destroy(self):
        for callback in (self._poll_id, self._render_id):
            if callback is not None:
                self.after_cancel(callback)
        self._poll_id = self._render_id = None
        super().destroy()

    def _render_result(self) -> None:
        if self._render_id is not None:
            self.after_cancel(self._render_id)
            self._render_id = None
        if not self.result:
            return
        self.file_label.configure(text=self.source_path.name if self.source_path else self.result.source)
        counts = self.result.severity_counts
        values = {
            "score": str(self.result.affected_row_count), "rows": str(self.result.row_count),
            "errors": str(counts["error"]), "warnings": str(counts["warning"]),
        }
        cost = self.result.cost_completeness
        values["missing_cost"] = f"{cost['missing_percent']:.2f}%" if cost['assessed'] else "—"
        self.refresh_filters()
        for key, value in values.items():
            self.metric_widgets[key][0].configure(text=value)

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.issue_by_item.clear()
        if self.result.issues:
            findings = self.filtered_issues()

            def insert_batch(offset=0):
                self._render_id = None
                for issue in findings[offset:offset + 200]:
                    item = self.tree.insert("", "end", values=(
                        self.t[issue.severity], self.rule_label(issue.rule), issue.row or "", issue.column or "", self.finding_text(issue)
                    ), tags=(issue.severity,))
                    self.issue_by_item[item] = issue
                if offset + 200 < len(findings):
                    self._render_id = self.after(1, insert_batch, offset + 200)

            insert_batch()
            if not findings:
                self.tree.insert("", "end", values=("", "", "", "", "没有匹配的问题，请调整搜索或分类。" if self.language == "zh" else "No matching findings. Change search or category."))
            self.result_banner.configure(text=f"⚠  {self.t['review']}", style="Review.TLabel")
        else:
            self.tree.insert("", "end", values=("✓", "", "", "", self.t["no_issues"]), tags=("passed",))
            self.result_banner.configure(text=f"✓  {self.t['passed']}", style="Passed.TLabel")
        self.result_banner.pack(fill="x", pady=(0, 12), before=self.tree.master)
        labels = {"executed": "已执行", "skipped": "已跳过", "not_applicable": "不适用"} if self.language == "zh" else {}
        self._set_details(self.t["score_note"] + "\n" + "\n".join(
            f"{c.rule} {c.column or ''}: {labels.get(c.status, c.status)} ({c.checked_count}) {c.reason}"
            for c in self.result.checks))
        self.status.configure(text=self.t["status_loaded"].format(name=self.source_path.name if self.source_path else self.result.source))

    def filtered_issues(self):
        issues = self.result.issues if self.result else []
        primary = {"value.missing_cost", "value.negative", "series.extreme_quantity"}
        return [i for i in issues if (self.active_filter == "all" or
                (self.active_filter == "other" and i.rule not in primary) or i.rule == self.active_filter)
                and self.matches_search(i)]

    def matches_search(self, issue):
        if not self.search_query:
            return True
        record = {}
        if self.result and issue.row and 0 <= issue.row - 2 < len(self.result.cleaned_rows):
            record = self.result.cleaned_rows[issue.row - 2]
        text = " ".join(str(v) for v in (
            issue.rule, issue.row or "", issue.column or "", issue.value or "",
            issue.message, issue.guidance or "",
            self.rule_label(issue.rule, language="zh"), self.finding_text(issue, language="zh"),
            *record.values(),
        )).casefold()
        return all(term in text for term in self.search_query.casefold().split())

    def apply_search(self, _event=None):
        if self.busy:
            return
        self.search_query = self.search_var.get().strip()
        self._render_result()

    def clear_search(self):
        self.search_var.set("")
        self.apply_search()

    def rule_label(self, rule, language=None):
        if (language or self.language) == "zh":
            return {"value.missing_cost": "费用缺失", "value.negative": "负数，需复核",
                    "series.extreme_quantity": "数量偏高，需复核"}.get(rule, rule)
        return rule

    def finding_text(self, issue, language=None):
        if (language or self.language) == "zh":
            return {
                "value.missing_cost": "参考费用为空，费用分析需披露缺失；不要补零。",
                "value.negative": f"发现负数 {issue.value}，可能涉及调整；需核查，勿直接删除或取绝对值。",
                "series.extreme_quantity": "数量超过同药品正数中位数的 20 倍；机构差异可能影响比较，不代表已证实错误。",
            }.get(issue.rule, issue.message)
        return issue.message

    def select_filter(self, key):
        self.active_filter = key
        self._render_result()

    def refresh_filters(self):
        self.search_label.configure(text="搜索问题" if self.language == "zh" else "Search findings")
        self.search_button.configure(text="搜索 / 回车" if self.language == "zh" else "Search / Enter")
        self.clear_button.configure(text="清除" if self.language == "zh" else "Clear")
        labels = (["全部", "费用缺失", "负数", "数量偏高", "其他"] if self.language == "zh"
                  else ["All", "Missing cost", "Negative", "High quantity", "Other"])
        issues = self.result.issues if self.result else []
        primary = {"value.missing_cost", "value.negative", "series.extreme_quantity"}
        for (key, button), label in zip(self.filter_buttons.items(), labels):
            count = sum(key == "all" or i.rule == key or (key == "other" and i.rule not in primary) for i in issues)
            button.configure(text=f"{label} ({count:,})", state="disabled" if key == self.active_filter else "normal")
        count = len(self.filtered_issues())
        self.filtered_export_button.configure(state="normal" if count and not self.busy else "disabled")
        query = self.search_query
        self.filter_note.configure(text=(f"显示 {count:,} 条提示｜搜索：{query or '无'}｜分类计数为搜索前总数；完整报告不受筛选影响。" if self.language == "zh"
                                        else f"Showing {count:,} findings | Search: {query or 'none'} | Category totals are unsearched; full reports ignore filters."))

    def show_summary(self):
        if not self.result or self.busy:
            return
        window = tk.Toplevel(self)
        window.title("问题概览 / Finding overview")
        window.geometry("950x440")
        note = ("全文件汇总；各规则记录数分别去重，不能直接相加。双击规则查看对应问题（清除搜索）。"
                if self.language == "zh" else
                "Whole-file summary. Record counts overlap across rules; do not add them. Double-click a rule to review it (clears search).")
        ttk.Label(window, text=note, wraplength=900, padding=12).pack(fill="x")
        columns = ("rule", "findings", "affected_records", "unlocated_findings", "organisations", "products")
        table = ttk.Treeview(window, columns=columns, show="headings")
        titles = (["规则", "提示数", "关联记录数", "未定位到记录", "机构数", "药品数"] if self.language == "zh"
                  else ["Rule", "Findings", "Records", "Unlocated", "Organisations", "Products"])
        for col, title in zip(columns, titles):
            table.heading(col, text=title)
            table.column(col, width=290 if col == "rule" else 115, minwidth=70)
        scroll = ttk.Scrollbar(window, command=table.yview)
        scroll.pack(side="right", fill="y")
        table.configure(yscrollcommand=scroll.set)
        table.pack(fill="both", expand=True, padx=12, pady=12)
        for item in summarise(self.result):
            table.insert("", "end", iid=item["rule"], values=(self.rule_label(item["rule"]), *(item[k] for k in columns[1:])))
        if not self.result.issues:
            ttk.Label(window, text=self.t["passed"], padding=12).pack()

        def review(_event):
            if table.selection() and not self.busy:
                self.search_query = ""
                self.search_var.set("")
                self.select_filter(table.selection()[0])
                window.destroy()
        table.bind("<Double-1>", review)

    def export_filtered(self):
        if self.busy or not self.result:
            return
        issues = self.filtered_issues()
        if not issues:
            return
        selected = filedialog.askdirectory(title="保存筛选问题 / Save filtered findings")
        if not selected:
            return
        result, query, category = self.result, self.search_query, self.active_filter
        self._run_background(
            lambda: write_filtered_findings(result, issues, selected, query=query, category=category),
            lambda paths: messagebox.showinfo(self.t["exported"], "\n".join(str(p) for p in paths.values())),
            "正在导出筛选问题…" if self.language == "zh" else "Exporting filtered findings…",
            self.t["export_error"],
        )

    def show_coverage(self) -> None:
        if not self.result:
            return
        window = tk.Toplevel(self)
        window.title("检查覆盖情况 / Check coverage")
        window.geometry("920x500")
        area = tk.Text(window, wrap="word")
        scroll = ttk.Scrollbar(window, command=area.yview)
        area.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        area.pack(fill="both", expand=True)
        labels = {"executed": "已执行", "skipped": "已跳过", "not_applicable": "不适用"} if self.language == "zh" else {}
        note = "计数单位按规则为记录、数值或机构组。已执行不等于通过。\n" if self.language == "zh" else "Counts represent records, values or organization groups. Executed does not mean passed.\n"
        area.insert("end", note + "\n".join(
            f"{c.rule} {c.column or ''}\n  {labels.get(c.status, c.status)} | {c.checked_count} | {c.reason}"
            for c in self.result.checks))
        area.configure(state="disabled")

    def show_selected_issue(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected or selected[0] not in self.issue_by_item:
            return
        issue = self.issue_by_item[selected[0]]
        lines = [f"[{self.t[issue.severity]}] {self.finding_text(issue)}", f"Rule: {issue.rule}", issue.message]
        record = record_for(self.result, issue)
        for key, zh, en in (("VMP_PRODUCT_NAME", "药品", "Medicine"), ("ODS_CODE", "机构编码", "Organisation code"),
                            ("YEAR_MONTH", "月份", "Month"), ("VMP_SNOMED_CODE", "药品编码", "Product code")):
            lines.append(f"{zh if self.language == 'zh' else en}: {record.get(key) or '—'}")
        if issue.row:
            lines.append(f"{self.t['row']}: {issue.row}")
        if issue.column:
            lines.append(f"{self.t['column']}: {issue.column}")
        if issue.value is not None:
            lines.append(f"{self.t['value']}: {issue.value}")
        if issue.guidance:
            lines.append(f"{self.t['guidance']}: {issue.guidance}")
        self._set_details("\n".join(lines))

    def _set_details(self, text: str) -> None:
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def export_report(self) -> None:
        if self.busy or not self.result:
            return
        selected = filedialog.askdirectory(title=self.t["export_title"])
        if not selected:
            return
        result = self.result
        self._run_background(
            lambda: write_outputs(result, selected),
            lambda paths: messagebox.showinfo(self.t["exported"], "\n".join(str(path) for path in paths.values())),
            "正在导出完整报告…" if self.language == "zh" else "Exporting complete reports…",
            self.t["export_error"],
        )


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()

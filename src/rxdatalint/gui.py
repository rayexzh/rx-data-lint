"""Dependency-free desktop interface using Tkinter."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .reports import write_outputs
from .validator import Issue, validate_csv


TEXT = {
    "zh": {
        "title": "RxDataLint",
        "subtitle": "在分析前检查 NHS 医院药品数据（SCMD）的质量",
        "choose": "选择 SCMD CSV",
        "export": "导出报告",
        "language": "English",
        "no_file": "尚未选择文件",
        "checking": "正在检查数据，请稍候…",
        "score": "实验性质量分",
        "rows": "检查行数",
        "errors": "错误",
        "warnings": "警告",
        "passed": "基础检查通过：未发现错误或警告",
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
        "created": "已生成 3 个文件：\nquality-report.html\nquality-report.json\ncleaned-scmd.csv\n\n保存位置：\n{path}",
        "open_error": "无法检查文件",
        "export_error": "无法导出报告",
        "status_ready": "就绪",
        "status_loaded": "已完成：{name}",
        "error": "错误",
        "warning": "警告",
        "info": "提示",
        "guidance": "处理建议",
        "value": "原始值",
        "score_note": "质量分是原型阶段的筛查指标，用于帮助排序问题，不代表临床、财务或监管结论。",
    },
    "en": {
        "title": "RxDataLint",
        "subtitle": "Review NHS Secondary Care Medicines Data before analysis",
        "choose": "Choose SCMD CSV",
        "export": "Export report",
        "language": "中文",
        "no_file": "No file selected",
        "checking": "Checking data…",
        "score": "Experimental score",
        "rows": "Rows checked",
        "errors": "Errors",
        "warnings": "Warnings",
        "passed": "Basic checks passed: no errors or warnings found",
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
        "created": "Created 3 files:\nquality-report.html\nquality-report.json\ncleaned-scmd.csv\n\nSaved to:\n{path}",
        "open_error": "Could not validate file",
        "export_error": "Could not export report",
        "status_ready": "Ready",
        "status_loaded": "Complete: {name}",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "guidance": "Guidance",
        "value": "Source value",
        "score_note": "The score is an early screening aid. It is not a clinical, financial, or regulatory conclusion.",
    },
}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = "zh"
        self.result = None
        self.source_path: Path | None = None
        self.issue_by_item: dict[str, Issue] = {}
        self.title("RxDataLint — NHS medicines data quality")
        self.geometry("1180x760")
        self.minsize(900, 620)
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
        header = ttk.Frame(self, style="Header.TFrame", padding=(26, 20))
        header.pack(fill="x")
        self.title_label = ttk.Label(header, style="Title.TLabel")
        self.title_label.pack(anchor="w")
        self.subtitle_label = ttk.Label(header, style="Subtitle.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(3, 0))

        content = ttk.Frame(self, style="App.TFrame", padding=22)
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

        metrics = ttk.Frame(content, style="App.TFrame")
        metrics.pack(fill="x", pady=(0, 12))
        self.metric_widgets: dict[str, tuple[ttk.Label, ttk.Label]] = {}
        for key in ("score", "rows", "errors", "warnings"):
            card = ttk.Frame(metrics, padding=(16, 11), style="MetricCard.TFrame")
            card.pack(side="left", fill="x", expand=True, padx=(0, 9))
            value = ttk.Label(card, text="—", style="Metric.TLabel")
            value.pack(anchor="w")
            name = ttk.Label(card, style="MetricName.TLabel")
            name.pack(anchor="w")
            self.metric_widgets[key] = (value, name)

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
        self.details_frame.pack(fill="x", pady=(12, 0))
        self.details = tk.Text(
            self.details_frame, height=5, wrap="word", borderwidth=0, background="#ffffff",
            foreground="#263832", font=("Microsoft YaHei UI", 9), padx=6, pady=4,
        )
        self.details.pack(fill="x")
        self.details.configure(state="disabled")

        self.status = ttk.Label(self, anchor="w", padding=(12, 5), background="#e3ebe8", foreground="#40514b")
        self.status.pack(fill="x", side="bottom")

    def _refresh_text(self) -> None:
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
        selected = filedialog.askopenfilename(
            title=self.t["choose"], filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not selected:
            return
        self.status.configure(text=self.t["checking"])
        self.update_idletasks()
        try:
            self.source_path = Path(selected)
            self.result = validate_csv(self.source_path)
        except Exception as exc:  # GUI boundary: show readable error instead of closing.
            messagebox.showerror(self.t["open_error"], str(exc))
            self.status.configure(text=self.t["status_ready"])
            return
        self.export_button.configure(state="normal")
        self._render_result()

    def _render_result(self) -> None:
        if not self.result:
            return
        self.file_label.configure(text=self.source_path.name if self.source_path else self.result.source)
        counts = self.result.severity_counts
        values = {
            "score": f"{self.result.score}/100", "rows": str(self.result.row_count),
            "errors": str(counts["error"]), "warnings": str(counts["warning"]),
        }
        for key, value in values.items():
            self.metric_widgets[key][0].configure(text=value)

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.issue_by_item.clear()
        if self.result.issues:
            for issue in self.result.issues:
                item = self.tree.insert("", "end", values=(
                    self.t[issue.severity], issue.rule, issue.row or "", issue.column or "", issue.message
                ), tags=(issue.severity,))
                self.issue_by_item[item] = issue
            self.result_banner.configure(text=f"⚠  {self.t['review']}", style="Review.TLabel")
        else:
            self.tree.insert("", "end", values=("✓", "", "", "", self.t["no_issues"]), tags=("passed",))
            self.result_banner.configure(text=f"✓  {self.t['passed']}", style="Passed.TLabel")
        self.result_banner.pack(fill="x", pady=(0, 12), before=self.tree.master)
        self._set_details(self.t["score_note"])
        self.status.configure(text=self.t["status_loaded"].format(name=self.source_path.name if self.source_path else self.result.source))

    def show_selected_issue(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected or selected[0] not in self.issue_by_item:
            return
        issue = self.issue_by_item[selected[0]]
        lines = [f"[{self.t[issue.severity]}] {issue.message}"]
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
        if not self.result:
            return
        selected = filedialog.askdirectory(title=self.t["export_title"])
        if not selected:
            return
        try:
            write_outputs(self.result, selected)
        except Exception as exc:
            messagebox.showerror(self.t["export_error"], str(exc))
            return
        messagebox.showinfo(self.t["exported"], self.t["created"].format(path=selected))


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()

"""Local desktop launcher for the companion SQL analysis (no extra packages)."""
from pathlib import Path
import os
import queue
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from run_analysis import build
from verify_analysis import verify


class AnalysisWindow:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        self.output = None
        root.title("RxDataLint — SQL Analysis / 数据分析")
        root.geometry("790x510")
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="NHS medicines analysis / NHS 药品数据分析", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="CSV → SQLite → SQL summaries → HTML report → verification", padding=(0, 8)).pack(anchor="w")
        self.csv = tk.StringVar()
        self.source = tk.StringVar()
        ttk.Label(frame, text="SCMD CSV 文件").pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=5)
        ttk.Entry(row, textvariable=self.csv).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="选择 / Browse", command=self.choose).pack(side="right", padx=8)
        ttk.Label(frame, text="官方来源链接 / Source URL（模拟数据填写 synthetic）").pack(anchor="w", pady=(12, 0))
        ttk.Entry(frame, textvariable=self.source).pack(fill="x", pady=5)
        self.run_button = ttk.Button(frame, text="生成并校验 / Generate & verify", command=self.start)
        self.run_button.pack(anchor="w", pady=14)
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x")
        self.status = tk.StringVar(value="请选择文件并填写来源。 / Choose a CSV and enter its source.")
        ttk.Label(frame, textvariable=self.status, wraplength=700).pack(anchor="w", pady=10)
        actions = ttk.Frame(frame)
        actions.pack(anchor="w")
        self.open_button = ttk.Button(actions, text="打开文件夹 / Open folder", command=self.open_output, state="disabled")
        self.open_button.pack(side="left")
        self.report_button = ttk.Button(actions, text="中文报告", command=lambda: self.open_report("zh-CN"), state="disabled")
        self.report_button.pack(side="left", padx=8)
        self.english_button = ttk.Button(actions, text="English report", command=lambda: self.open_report("en"), state="disabled")
        self.english_button.pack(side="left")
        ttk.Label(frame, text="本地处理；不上传数据。结果不代表实际采购支出或合规认证。", wraplength=700).pack(anchor="w", pady=12)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(150, self.poll)

    def choose(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.csv.set(path)

    def start(self):
        if self.busy:
            return
        source = Path(self.csv.get().strip())
        url = self.source.get().strip()
        if not source.is_file() or not url:
            messagebox.showerror("检查输入 / Check input", "请选择存在的 CSV 并填写来源。 / Select a CSV and enter its source.")
            return
        parent = filedialog.askdirectory(title="选择结果保存位置 / Choose output parent folder")
        if not parent:
            return
        self.busy = True
        self.run_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.report_button.configure(state="disabled")
        self.english_button.configure(state="disabled")
        self.progress.start()
        self.status.set("正在分析，请稍候… / Analysing, please wait…")
        threading.Thread(target=self.worker, args=(source, Path(parent), url), daemon=True).start()

    def worker(self, source, parent, url):
        output = None
        try:
            # Reserve a unique parent so existing results are never overwritten.
            reserved = Path(tempfile.mkdtemp(prefix="RxDataLint-analysis-", dir=parent))
            output = reserved / "results"
            info = build(source, output, url)
            failures = verify(output)
            if failures:
                raise ValueError("; ".join(failures))
            self.events.put((True, output, f"完成并校验通过 / Verified: {info['row_count']:,} records\n{output}"))
        except Exception as exc:
            self.events.put((False, output, f"失败 / Failed: {exc}\n部分输出不能作为完整结果使用。 / Partial outputs must not be used."))

    def poll(self):
        try:
            ok, output, text = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.progress.stop()
            self.run_button.configure(state="normal")
            self.output = output if ok else None
            self.open_button.configure(state="normal" if ok else "disabled")
            self.report_button.configure(state="normal" if ok else "disabled")
            self.english_button.configure(state="normal" if ok else "disabled")
            self.status.set(text)
        self.root.after(150, self.poll)

    def open_output(self):
        if self.output:
            try:
                os.startfile(self.output)
            except (OSError, AttributeError) as exc:
                messagebox.showinfo("Results / 结果", f"{self.output}\n{exc}")

    def open_report(self, language):
        if self.output:
            try:
                os.startfile(self.output / f"REPORT.{language}.html")
            except (OSError, AttributeError) as exc:
                messagebox.showinfo("Report / 报告", f"{self.output}\n{exc}")

    def close(self):
        if self.busy:
            messagebox.showinfo("正在运行 / Running", "请等待分析结束再关闭窗口。 / Wait for the analysis to finish.")
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    AnalysisWindow(root)
    root.mainloop()

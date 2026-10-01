"""Local desktop launcher for the companion SQL analysis (no extra packages)."""
from pathlib import Path
import os
import sys
import queue
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rxdatalint.presentation import configure_theme, enable_dpi_awareness, sample_path

from run_analysis import build
from verify_analysis import verify


class AnalysisWindow:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        self.output = None
        self.completed_inputs = self.running_inputs = None
        self.completed_text = ""
        self.language, self.theme, self.font_size = "zh", "light", 10
        configure_theme(root, self.theme, self.font_size)
        root.title("RxDataLint — SQL Analysis / 数据分析")
        root.geometry("950x650")
        root.minsize(800, 600)
        header = ttk.Frame(root, style="Header.TFrame", padding=22)
        header.pack(fill="x")
        controls = ttk.Frame(header, style="Header.TFrame")
        self.language_button = ttk.Button(controls, command=self.toggle_language)
        self.language_button.pack(side="left", padx=4)
        self.theme_button = ttk.Button(controls, command=self.toggle_theme)
        self.theme_button.pack(side="left", padx=4)
        ttk.Button(controls, text="A−", width=3, command=lambda: self.adjust_font(-1)).pack(side="left", padx=2)
        ttk.Button(controls, text="A+", width=3, command=lambda: self.adjust_font(1)).pack(side="left", padx=2)
        self.title = ttk.Label(header, text="RxDataLint", style="Title.TLabel")
        self.title.pack(anchor="w")
        self.subtitle = ttk.Label(header, style="Subtitle.TLabel")
        self.subtitle.pack(anchor="w", pady=6)
        controls.pack(fill="x", pady=(4,0))
        header.bind("<Configure>", lambda e: self.subtitle.configure(wraplength=max(200,e.width-44)))
        body = ttk.Frame(root)
        body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(body, highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(fill="both", expand=True)
        frame = ttk.Frame(self.canvas, padding=22)
        item = self.canvas.create_window((0,0), window=frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(item,width=e.width))
        frame.bind("<Configure>", self.resize_content)
        self.root.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 if e.delta>0 else 1,"units"), add="+")
        self.workflow = ttk.Label(frame, style="Muted.TLabel")
        self.workflow.pack(fill="x", pady=(0,12))
        self.csv, self.source = tk.StringVar(), tk.StringVar()
        self.csv_label = ttk.Label(frame)
        self.csv_label.pack(anchor="w")
        row = ttk.Frame(frame);row.pack(fill="x", pady=5)
        ttk.Entry(row, textvariable=self.csv).pack(side="left", fill="x", expand=True)
        self.browse_button = ttk.Button(row, command=self.choose)
        self.browse_button.pack(side="right", padx=8)
        self.sample_button = ttk.Button(row, command=self.use_sample)
        self.sample_button.pack(side="right")
        self.source_label = ttk.Label(frame)
        self.source_label.pack(anchor="w", pady=(12,0))
        ttk.Entry(frame, textvariable=self.source).pack(fill="x", pady=5)
        self.run_button = ttk.Button(frame, style="Primary.TButton", command=self.start)
        self.run_button.pack(anchor="w", pady=14)
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.status = tk.StringVar(value="请选择文件并填写来源。 / Choose a CSV and enter its source.")
        self.status_label = ttk.Label(frame, textvariable=self.status, wraplength=820)
        self.status_label.pack(anchor="w", pady=10)
        actions = ttk.Frame(frame);actions.pack(anchor="w")
        self.open_button = ttk.Button(actions, command=self.open_output, state="disabled")
        self.open_button.pack(side="left")
        self.report_button = ttk.Button(actions, text="中文报告", command=lambda: self.open_report("zh-CN"), state="disabled")
        self.report_button.pack(side="left", padx=8)
        self.english_button = ttk.Button(actions, text="English report", command=lambda: self.open_report("en"), state="disabled")
        self.english_button.pack(side="left")
        self.scope_label = ttk.Label(frame, style="Muted.TLabel", wraplength=820)
        self.scope_label.pack(fill="x", pady=16)
        self.apply_view()
        for variable in (self.csv, self.source):
            variable.trace_add("write", self.refresh_result_context)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll_id = root.after(150, self.poll)
        root.bind("<Destroy>", self.on_destroy, add="+")

    def apply_view(self):
        colors = configure_theme(self.root, self.theme, self.font_size)
        self.canvas.configure(background=colors["background"])
        en = self.language == "en"
        for widget,zh,text in (
            (self.subtitle,"药品数据 · SQL 分析与离线报告","Medicines data · SQL analysis and offline reports"),
            (self.workflow,"① 选择 CSV 和来源 → ② 生成并校验 → ③ 打开离线报告","1. Choose CSV and source → 2. Generate and verify → 3. Open offline report"),
            (self.csv_label,"SCMD CSV 文件","SCMD CSV file"),
            (self.browse_button,"选择文件","Browse"),
            (self.sample_button,"使用示例","Use sample"),
            (self.source_label,"官方来源链接（示例填写 synthetic）","Official source URL (use synthetic for the sample)"),
            (self.run_button,"生成并校验","Generate and verify"),
            (self.open_button,"结果文件夹","Results folder"),
            (self.scope_label,"本地处理，不上传输入。NULL 费用保留为未知；处理差额不代表节省或实际采购支出。","Local processing. NULL cost remains unknown. Processing differences are not savings or actual acquisition spending."),
        ):
            widget.configure(text=text if en else zh)
        self.language_button.configure(text="中文" if en else "English")
        self.theme_button.configure(text=("Light" if self.theme == "dark" else "Dark") if en else ("浅色" if self.theme == "dark" else "深色"))
        self.refresh_result_context()

    def resize_content(self, event):
        width = max(200, event.width-44)
        for label in (self.workflow, self.status_label, self.scope_label, self.source_label):
            label.configure(wraplength=width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def refresh_result_context(self, *args):
        if self.busy or not self.output or not self.completed_inputs:
            return
        source, provenance = self.completed_inputs
        en = self.language == "en"
        text = self.completed_text + ("\nReport input: " if en else "\n报告对应输入：") + source
        text += ("\nSource: " if en else "\n来源：") + provenance
        if (self.csv.get().strip(), self.source.get().strip()) != self.completed_inputs:
            notice = ("Input changed — not analysed yet. Buttons below open the previous report."
                      if en else "输入已变更，尚未重新分析。下方按钮打开的是上次报告。")
            text = notice + "\n" + text
        self.status.set(text)

    def toggle_language(self):
        self.language = "en" if self.language == "zh" else "zh"
        self.apply_view()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_view()

    def adjust_font(self, delta):
        self.font_size = min(12, max(10, self.font_size + delta))
        self.apply_view()

    def use_sample(self):
        if not self.busy:
            self.csv.set(str(sample_path()))
            self.source.set("synthetic")

    def on_destroy(self, event):
        if event.widget is self.root and self.poll_id is not None:
            try:
                self.root.after_cancel(self.poll_id)
            except tk.TclError:
                pass
            self.poll_id = None

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
        self.running_inputs = (self.csv.get().strip(), url)
        self.run_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.report_button.configure(state="disabled")
        self.english_button.configure(state="disabled")
        self.sample_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.progress.pack(fill="x", before=self.run_button)
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
            self.progress.pack_forget()
            self.sample_button.configure(state="normal")
            self.browse_button.configure(state="normal")
            self.run_button.configure(state="normal")
            self.output = output if ok else None
            self.completed_inputs = self.running_inputs if ok else None
            self.completed_text = text if ok else ""
            self.open_button.configure(state="normal" if ok else "disabled")
            self.report_button.configure(state="normal" if ok else "disabled")
            self.english_button.configure(state="normal" if ok else "disabled")
            self.status.set(text)
            self.refresh_result_context()
        self.poll_id = self.root.after(150, self.poll)

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


def main():
    enable_dpi_awareness()
    root = tk.Tk()
    AnalysisWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

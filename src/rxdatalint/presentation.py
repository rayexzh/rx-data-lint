"""Shared native desktop presentation; no data or network operations."""
import ctypes
import sys
import tkinter.font as tkfont
from tkinter import ttk
from pathlib import Path

PALETTES = {
    "light": {"background":"#eef5f2", "surface":"#ffffff", "text":"#183b31", "muted":"#48665c", "header":"#123c32", "border":"#bdd1c8", "accent":"#166b54", "selection":"#14634e", "entry":"#ffffff", "error_bg":"#fff0f0", "error_fg":"#8e1b1b", "warning_bg":"#fff4de", "warning_fg":"#794300", "info_bg":"#eaf4ff", "info_fg":"#215a86", "passed_bg":"#e2f3e8", "passed_fg":"#14633c"},
    "dark": {"background":"#15251f", "surface":"#20372d", "text":"#e8f3ed", "muted":"#b4cbc0", "header":"#10291f", "border":"#527562", "accent":"#166b54", "selection":"#237358", "entry":"#20372d", "error_bg":"#472728", "error_fg":"#ffd0cf", "warning_bg":"#433720", "warning_fg":"#ffe1a3", "info_bg":"#233b4e", "info_fg":"#c3e4ff", "passed_bg":"#214b36", "passed_fg":"#c8efda"},
}

def layout_flow(frame, widgets, width=None):
    """Wrap complete controls; never shrink a button until its label disappears."""
    available = max(1, frame.winfo_width() if width is None else width)
    for widget in widgets:
        if widget.winfo_manager() == "pack":
            widget.pack_forget()
    row = column = used = 0
    for widget in widgets:
        required = widget.winfo_reqwidth() + 8
        if column and used + required > available:
            row, column, used = row + 1, 0, 0
        widget.grid(row=row, column=column, sticky="w", padx=(0,8), pady=(0,6))
        column += 1
        used += required

def enable_dpi_awareness():
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass

def sample_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "examples" / "sample_scmd.csv"
    return Path(__file__).resolve().parents[2] / "examples" / "sample_scmd.csv"

def configure_theme(root, name="light", size=10):
    c=PALETTES[name]
    families=set(tkfont.families(root))
    family=next((f for f in ("Microsoft YaHei UI","Segoe UI","Arial") if f in families),"TkDefaultFont")
    for f in ("TkDefaultFont","TkTextFont","TkMenuFont","TkHeadingFont"):
        tkfont.nametofont(f,root).configure(family=family,size=size)
    style=ttk.Style(root);style.theme_use("clam")
    style.configure(".",background=c["background"],foreground=c["text"],font="TkDefaultFont")
    for kind in ("TFrame","App.TFrame"):
        style.configure(kind,background=c["background"])
    style.configure("TLabel",background=c["background"],foreground=c["text"])
    style.configure("Muted.TLabel",foreground=c["muted"])
    style.configure("Header.TFrame",background=c["header"])
    style.configure("Title.TLabel",background=c["header"],foreground="#ffffff",font=(family,size+12,"bold"))
    style.configure("Subtitle.TLabel",background=c["header"],foreground="#d8ebe5",font=(family,size))
    style.configure("TButton",padding=(10,7),background=c["surface"],foreground=c["text"],bordercolor=c["border"])
    style.map("TButton",background=[("active",c["selection"])],foreground=[("disabled",c["muted"]),("active","#ffffff")])
    style.configure("Primary.TButton",background=c["accent"],foreground="#ffffff",font=(family,size,"bold"),padding=(14,9))
    style.map("Primary.TButton",background=[("disabled",c["surface"]),("active",c["selection"])],foreground=[("disabled",c["muted"])])
    style.configure("Toolbar.TButton",padding=(10,7))
    style.configure("MetricCard.TFrame",background=c["surface"],relief="solid",borderwidth=1)
    style.configure("Metric.TLabel",background=c["surface"],foreground=c["text"],font=(family,size+9,"bold"))
    style.configure("MetricName.TLabel",background=c["surface"],foreground=c["muted"],font=(family,size))
    for label,key in (("Passed","passed"),("Review","warning")):
        style.configure(label+".TLabel",background=c[key+"_bg"],foreground=c[key+"_fg"],font=(family,size,"bold"),padding=10)
    for entry in ("TEntry","TCombobox"):
        style.configure(entry,fieldbackground=c["entry"],foreground=c["text"],padding=6,bordercolor=c["border"],arrowcolor=c["text"])
        style.map(entry,fieldbackground=[("readonly",c["entry"])],foreground=[("readonly",c["text"])])
    style.configure("TLabelframe",background=c["background"],bordercolor=c["border"])
    style.configure("TLabelframe.Label",background=c["background"],foreground=c["text"])
    style.configure("Treeview",rowheight=tkfont.nametofont("TkDefaultFont",root).metrics("linespace")+12,background=c["surface"],fieldbackground=c["surface"],foreground=c["text"],font="TkDefaultFont")
    style.map("Treeview",background=[("selected",c["selection"])],foreground=[("selected","#ffffff")])
    style.configure("Treeview.Heading",background=c["border"],foreground=c["text"],font=(family,size,"bold"),padding=8)
    style.configure("Horizontal.TProgressbar",background=c["accent"],troughcolor=c["border"])
    root.configure(background=c["background"])
    return c

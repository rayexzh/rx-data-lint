"""Frozen analysis entry point with a packaged workflow diagnostic."""
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback
import tkinter as tk
from unittest.mock import patch

from desktop import AnalysisWindow, main
from verify_analysis import verify


def self_test(source, diagnostic):
    root = None
    try:
        if not getattr(sys, "frozen", False):
            raise RuntimeError("This diagnostic must run inside the packaged executable.")
        root = tk.Tk()
        root.withdraw()
        app = AnalysisWindow(root)
        app.use_sample()
        assert Path(app.csv.get()).is_file() and app.source.get() == "synthetic"
        app.toggle_language()
        app.toggle_theme()
        app.adjust_font(1)

        def run(csv, parent):
            app.csv.set(str(csv))
            app.source.set("synthetic")
            with patch("desktop.filedialog.askdirectory", return_value=str(parent)):
                app.start()
            assert app.busy
            assert str(app.run_button["state"]) == "disabled"
            deadline = time.monotonic() + 60
            ticks = 0
            while app.busy:
                if time.monotonic() > deadline:
                    raise TimeoutError("Packaged analysis did not finish.")
                root.update()
                ticks += 1
                time.sleep(.01)
            return ticks

        with tempfile.TemporaryDirectory(prefix="RxDataLint-smoke-") as folder:
            parent = Path(folder)
            ticks = run(source, parent)
            first = app.output
            assert first is not None, app.status.get()
            assert verify(first) == []
            info = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            assert info["row_count"] > 0
            assert str(app.report_button["state"]) == "normal"
            opened = []
            with patch("desktop.os.startfile", side_effect=lambda path: opened.append(Path(path))):
                app.open_report("zh-CN")
                app.open_report("en")
                app.open_output()
            assert opened == [first / "REPORT.zh-CN.html", first / "REPORT.en.html", first]
            assert all(path.exists() for path in opened)
            assert "<html lang=\"en\"" in opened[1].read_text(encoding="utf-8")
            report = first / "REPORT.en.html"
            original = report.read_bytes()
            report.write_bytes(original + b"modified")
            assert "Changed: REPORT.en.html" in verify(first)
            report.write_bytes(original)

            invalid = parent / "invalid.csv"
            invalid.write_text("wrong\n1\n", encoding="utf-8")
            run(invalid, parent)
            assert app.output is None and "Failed:" in app.status.get()
            assert str(app.report_button["state"]) == "disabled"

            run(source, parent)
            assert app.output is not None and app.output != first
            assert verify(first) == [] and verify(app.output) == []
            diagnostic.write_text(json.dumps({
                "ok": True, "frozen": True, "rows": info["row_count"],
                "checks": ["Tk startup", "background analysis", "SQL resources", "bilingual reports",
                           "report button paths", "artifact verification", "tamper detection",
                           "failed-input recovery", "previous-run preservation"],
                "event_loop_ticks": ticks,
            }, indent=2), encoding="utf-8")
        return 0
    except Exception:
        diagnostic.write_text(traceback.format_exc(), encoding="utf-8")
        return 1
    finally:
        if root is not None:
            root.destroy()


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test(Path(sys.argv[2]), Path(sys.argv[3])))
    main()

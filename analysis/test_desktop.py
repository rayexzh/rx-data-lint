"""Presentation controls retain completed SQL results and sample provenance."""
from pathlib import Path
import tempfile,time
import tkinter as tk
import unittest
from unittest.mock import patch
from desktop import AnalysisWindow
from verify_analysis import verify

class DesktopPresentationTests(unittest.TestCase):
    def test_input_changes_label_previous_report_and_revert_clears_notice(self):
        root=tk.Tk();root.withdraw()
        app=AnalysisWindow(root)
        try:
            app.use_sample()
            app.toggle_language()
            with tempfile.TemporaryDirectory() as folder:
                with patch("desktop.filedialog.askdirectory",return_value=folder):
                    app.start()
                deadline=time.monotonic()+10
                while app.busy and time.monotonic()<deadline:
                    root.update();time.sleep(.01)
                self.assertFalse(app.busy)
                original=app.output
                source=app.csv.get()
                app.csv.set(str(Path(folder)/"not-yet-analysed.csv"))
                self.assertIn("Input changed",app.status.get())
                self.assertIn(source,app.status.get())
                self.assertEqual(app.output,original)
                self.assertEqual(verify(original),[])
                app.csv.set(source)
                self.assertNotIn("Input changed",app.status.get())
                app.source.set("changed provenance")
                self.assertIn("Input changed",app.status.get())
                app.toggle_language()
                self.assertIn("尚未重新分析",app.status.get())
        finally:
            root.destroy()

    def test_small_window_large_font_keeps_title_and_workflow_readable(self):
        root=tk.Tk();app=AnalysisWindow(root)
        try:
            root.geometry("800x600")
            app.toggle_language();app.adjust_font(2)
            for _ in range(4):root.update()
            self.assertGreaterEqual(app.title.winfo_width(),app.title.winfo_reqwidth())
            self.assertGreaterEqual(app.workflow.winfo_width(),app.workflow.winfo_reqwidth())
        finally:
            root.destroy()

    def test_sample_and_view_controls_preserve_verified_output(self):
        root=tk.Tk();root.withdraw()
        app=AnalysisWindow(root)
        try:
            app.use_sample()
            self.assertEqual(app.source.get(), "synthetic")
            self.assertTrue(Path(app.csv.get()).is_file())
            with tempfile.TemporaryDirectory() as folder:
                with patch("desktop.filedialog.askdirectory",return_value=folder):
                    app.start()
                deadline=time.monotonic()+10
                while app.busy and time.monotonic()<deadline:
                    root.update();time.sleep(.01)
                self.assertFalse(app.busy)
                self.assertEqual(verify(app.output), [])
                original=app.output
                app.toggle_language();app.toggle_theme();app.adjust_font(2)
                self.assertEqual(app.output,original)
                self.assertEqual(app.source.get(),"synthetic")
                self.assertEqual(app.run_button["text"],"Generate and verify")
                self.assertEqual(app.progress.winfo_manager(),"")
        finally:
            root.destroy()

if __name__ == "__main__":
    unittest.main()

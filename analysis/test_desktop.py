"""Presentation controls retain completed SQL results and sample provenance."""
from pathlib import Path
import tempfile,time
import tkinter as tk
import unittest
from unittest.mock import patch
from desktop import AnalysisWindow
from verify_analysis import verify

class DesktopPresentationTests(unittest.TestCase):
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

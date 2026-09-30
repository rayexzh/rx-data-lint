import csv
import json
import queue
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from run_analysis import build, safe_cell
from verify_analysis import verify
from desktop import AnalysisWindow
from html_report import REPORT_FILES


class AnalysisTests(unittest.TestCase):
    def sample(self, path, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE", "VMP_PRODUCT_NAME", "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE", "INDICATIVE_COST"])
            for month, cost in rows:
                writer.writerow([month, "R1A", "123456789", "Example", "1", cost])

    def test_reports_are_hashed_and_explain_cost_sensitivity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root / "sample.csv", [("202607", "100"), ("202607", "-20"), ("202607", "")])
            output = root / "output"
            info = build(root / "sample.csv", output, "synthetic")
            self.assertEqual(info["analysis_format_version"], 2)
            self.assertTrue(set(REPORT_FILES).issubset(info["artifacts"]))
            report = (output / "REPORT.en.html").read_text(encoding="utf-8")
            for phrase in ("£80.00", "£100.00", "£20.00", "66.67%", "Only one valid month", "not savings", "<html lang=\"en\"", "value.missing_cost"):
                self.assertIn(phrase, report)
            self.assertNotIn("<script", report)
            self.assertEqual(verify(output), [])
            (output / REPORT_FILES[0]).write_text("changed", encoding="utf-8")
            self.assertIn(f"Changed: {REPORT_FILES[0]}", verify(output))
            info["artifacts"].pop(REPORT_FILES[0])
            (output / "manifest.json").write_text(json.dumps(info), encoding="utf-8")
            self.assertIn(f"Not recorded: {REPORT_FILES[0]}", verify(output))

    def test_reports_preserve_unavailable_costs_and_invalid_month_group(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root / "sample.csv", [("bad-month", ""), ("202607", "bad"), ("202608", "")])
            output = root / "output"
            build(root / "sample.csv", output, "synthetic")
            report = (output / "REPORT.en.html").read_text(encoding="utf-8")
            self.assertIn("Invalid month (retained)", report)
            self.assertIn("Monthly totals are descriptive", report)
            self.assertIn("no matching known amounts", report)
            self.assertNotIn('<svg class="costchart"', report)
            self.assertNotIn("Only one valid month", report)

    def test_reports_escape_source_metadata_and_reject_script_links(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # This filename is portable on Windows and embeds an HTML entity.
            source = root / "A&B.csv"
            self.sample(source, [("202607", "10")])
            output = root / "output"
            build(source, output, 'javascript:alert("<script>")')
            report = (output / "REPORT.en.html").read_text(encoding="utf-8")
            self.assertIn("A&amp;B.csv", report)
            self.assertIn("&lt;script&gt;", report)
            self.assertNotIn('href="javascript:', report)
            self.assertNotIn("<script>", report)
            self.assertIn("No findings under the implemented rules", report)

    def test_missing_negative_and_duplicate_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "sample.csv"
            with source.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE", "VMP_PRODUCT_NAME", "TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE", "INDICATIVE_COST"])
                for cost in ("100", "", "-20", "bad"):
                    writer.writerow(["202607", "R1A", "123456789", "Example", "1", cost])
                writer.writerow(["202607", "R1A", "987654321", "No cost", "1", ""])
            output = root / "output"
            result = build(source, output, "synthetic")
            self.assertEqual(result["row_count"], 5)
            self.assertEqual(verify(output), [])
            summary = output / "SUMMARY.md"
            original = summary.read_bytes()
            summary.write_bytes(original + b"changed")
            self.assertIn("Changed: SUMMARY.md", verify(output))
            summary.write_bytes(original)
            summary.unlink()
            self.assertIn("Missing or unsupported file: SUMMARY.md", verify(output))
            with closing(sqlite3.connect(output / "medicines.sqlite")) as db:
                self.assertEqual(db.execute("SELECT COUNT(*),COUNT(cost_gbp),SUM(cost_gbp) FROM records").fetchone(), (5, 2, 80))
                self.assertIsNone(db.execute("SELECT SUM(cost_gbp) FROM records WHERE product_code='987654321'").fetchone()[0])
                self.assertEqual(db.execute("SELECT cost_status FROM records WHERE row_number=5").fetchone()[0], "invalid")
                self.assertEqual(db.execute("SELECT COUNT(*) FROM findings WHERE rule='row.duplicate_key'").fetchone()[0], 3)
            with self.assertRaises(ValueError):
                build(source, output, "synthetic")

    def test_desktop_worker_verifies_results_and_preserves_previous_run(self):
        window = object.__new__(AnalysisWindow)
        window.events = queue.Queue()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(__file__).resolve().parents[1] / "examples/sample_scmd.csv"
            window.worker(source, Path(folder), "synthetic")
            ok, first, _ = window.events.get_nowait()
            self.assertTrue(ok)
            self.assertEqual(verify(first), [])
            window.worker(source, Path(folder), "synthetic")
            ok, second, _ = window.events.get_nowait()
            self.assertTrue(ok)
            self.assertNotEqual(first, second)
            self.assertEqual(verify(first), [])

    def test_desktop_worker_reports_failure(self):
        window = object.__new__(AnalysisWindow)
        window.events = queue.Queue()
        with tempfile.TemporaryDirectory() as folder:
            window.worker(Path(folder) / "missing.csv", Path(folder), "synthetic")
            ok, _, message = window.events.get_nowait()
            self.assertFalse(ok)
            self.assertIn("Failed:", message)

    def test_blocked_input_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "bad.csv"
            source.write_text("wrong\n1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build(source, root / "output", "synthetic")
            self.assertFalse((root / "output").exists())

    def test_export_formula_protection_preserves_numeric_negative(self):
        self.assertEqual(safe_cell("=1+1"), "'=1+1")
        self.assertEqual(safe_cell(-20.0), -20.0)


if __name__ == "__main__":
    unittest.main()

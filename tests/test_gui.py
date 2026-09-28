"""Exercise search and export through the desktop interface."""

import json
from pathlib import Path
import tempfile
import time
from threading import Event, get_ident
import unittest
from unittest.mock import patch

from rxdatalint.gui import App
from rxdatalint.validator import validate_csv


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.withdraw()
        self.addCleanup(self.app.destroy)
        self.app.result = validate_csv(
            Path(__file__).parents[1] / "examples" / "sample_scmd.csv"
        )

    def search(self, query):
        self.app.search_var.set(query)
        self.app.apply_search()
        return self.app.filtered_issues()

    def pump_until(self, predicate):
        deadline = time.monotonic() + 5
        while not predicate() and time.monotonic() < deadline:
            self.app.update()
            time.sleep(0.005)
        self.assertTrue(predicate(), "Background task did not finish")

    def test_background_check_keeps_event_loop_live_and_blocks_duplicate_load(self):
        release = Event()
        self.addCleanup(release.set)
        original = self.app.result
        worker_threads = []
        ui_thread = get_ident()

        def slow_check(_path):
            worker_threads.append(get_ident())
            release.wait(3)
            return original

        with patch("rxdatalint.gui.filedialog.askopenfilename", return_value="example.csv") as picker, \
             patch("rxdatalint.gui.validate_csv", side_effect=slow_check):
            self.app.choose_file()
            self.assertTrue(self.app.busy)
            self.assertTrue(self.app.export_button.instate(["disabled"]))
            heartbeat = []
            self.app.after(10, lambda: heartbeat.append(True))
            self.pump_until(lambda: bool(heartbeat))
            self.assertTrue(self.app.busy)
            self.app.choose_file()
            picker.assert_called_once()
            release.set()
            self.pump_until(lambda: not self.app.busy)
        self.assertNotEqual(worker_threads[0], ui_thread)
        self.assertEqual(self.app.source_path, Path("example.csv"))
        self.assertFalse(self.app.export_button.instate(["disabled"]))

    def test_failed_load_preserves_previous_result_and_restores_controls(self):
        previous = self.app.result
        with patch("rxdatalint.gui.filedialog.askopenfilename", return_value="missing.csv"), \
             patch("rxdatalint.gui.validate_csv", side_effect=OSError("Cannot read file")), \
             patch("rxdatalint.gui.messagebox.showerror") as error:
            self.app.choose_file()
            self.pump_until(lambda: not self.app.busy)
            error.assert_called_once()
        self.assertIs(self.app.result, previous)
        self.assertFalse(self.app.choose_button.instate(["disabled"]))

    def test_new_search_cancels_pending_table_batches(self):
        self.app.result.issues *= 100
        self.app._render_result()
        self.assertIsNotNone(self.app._render_id)
        self.assertEqual(self.search("no-such-product-xyz"), [])
        self.app.update()
        self.assertIsNone(self.app._render_id)
        self.assertEqual(self.app.issue_by_item, {})

    def test_chinese_search_survives_language_switch(self):
        before = self.search("负数")
        self.assertTrue(before)
        self.app.toggle_language()
        self.assertEqual(self.app.filtered_issues(), before)
        self.app.toggle_language()
        self.assertEqual(self.app.filtered_issues(), before)

    def test_details_include_associated_medicine_and_month(self):
        self.app._render_result()
        item, issue = next((key, value) for key, value in self.app.issue_by_item.items() if value.row)
        self.app.tree.selection_set(item)
        self.app.show_selected_issue()
        record = self.app.result.cleaned_rows[issue.row - 2]
        details = self.app.details.get("1.0", "end")
        self.assertIn(record["VMP_PRODUCT_NAME"], details)
        self.assertIn(record["ODS_CODE"], details)
        self.assertIn(record["YEAR_MONTH"], details)

    def test_filtered_export_has_only_selected_findings(self):
        expected = self.search("负数")
        self.assertTrue(expected)
        with tempfile.TemporaryDirectory() as directory:
            with patch("rxdatalint.gui.filedialog.askdirectory", return_value=directory), \
                 patch("rxdatalint.gui.messagebox.showinfo") as success:
                self.app.export_filtered()
                self.pump_until(lambda: not self.app.busy)
                success.assert_called_once()
            payload = json.loads(next(Path(directory).glob("findings-*/filtered-findings.json")).read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_findings"], len(expected))
            self.assertTrue(all(i["rule"] == "value.negative" for i in payload["findings"]))
        self.search("no-such-product-xyz")
        self.assertTrue(self.app.filtered_export_button.instate(["disabled"]))

    def test_record_search_and_category_intersect(self):
        issue = next(i for i in self.app.result.issues if i.rule == "value.negative")
        row = self.app.result.cleaned_rows[issue.row - 2]
        query = row["VMP_PRODUCT_NAME"].upper() + " " + row["ODS_CODE"].lower()
        self.app.select_filter("value.negative")
        matches = self.search(query)
        self.assertIn(issue, matches)
        self.assertTrue(all(i.rule == "value.negative" for i in matches))
        self.assertEqual(self.search(query + " no-such-product-xyz"), [])
        self.app.clear_search()
        self.assertEqual(self.app.filtered_issues(), [
            i for i in self.app.result.issues if i.rule == "value.negative"
        ])

    def test_export_after_empty_search_keeps_all_findings(self):
        self.assertEqual(self.search("no-such-product-xyz"), [])
        with tempfile.TemporaryDirectory() as directory:
            with patch("rxdatalint.gui.filedialog.askdirectory", return_value=directory), \
                 patch("rxdatalint.gui.messagebox.showinfo") as success, \
                 patch("rxdatalint.gui.messagebox.showerror") as failure:
                self.app.export_report()
                self.pump_until(lambda: not self.app.busy)
                failure.assert_not_called()
                success.assert_called_once()
            report = next(Path(directory).glob("run-*/quality-report.json"))
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["issues"]), len(self.app.result.issues))
            self.assertEqual(payload["row_count"], self.app.result.row_count)


if __name__ == "__main__":
    unittest.main()

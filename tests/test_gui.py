"""Exercise search and export through the desktop interface."""

import json
from pathlib import Path
import tempfile
import time
from threading import Event, get_ident
import unittest
from unittest.mock import patch
from tkinter import ttk

from rxdatalint.gui import App
from rxdatalint.review import finding_group
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

    def test_theme_and_font_preserve_snapshot_filter_and_selected_issue(self):
        self.app._render_result()
        self.app.select_filter("value.negative")
        item = next(iter(self.app.issue_by_item))
        self.app.tree.selection_set(item)
        before = self.app.result
        rows = self.app.filtered_issues()
        self.app.toggle_theme()
        self.app.adjust_font(2)
        self.assertIs(self.app.result, before)
        self.assertEqual(self.app.filtered_issues(), rows)
        self.assertEqual(self.app.tree.selection(), (item,))
        self.assertEqual(self.app.theme, "dark")
        self.assertEqual(self.app.font_size, 12)
        self.assertEqual(self.app.details["background"], self.app.colors["surface"])

    def test_sample_button_loads_bundled_example_in_background(self):
        self.app.sample_button.invoke()
        self.pump_until(lambda: not self.app.busy)
        self.assertEqual(self.app.result.row_count, 8)
        self.assertEqual(self.app.source_path.name, "sample_scmd.csv")
        self.assertFalse(self.app.export_button.instate(["disabled"]))
        self.assertEqual(self.app.progress.winfo_manager(), "")

    def test_all_categories_are_accessible_at_minimum_size_and_largest_font(self):
        app = self.app
        app.deiconify()
        app.geometry("900x600")
        app.toggle_language()
        app.adjust_font(4)
        app._render_result()
        for _ in range(4):
            app.update()
        for button in [*app.filter_buttons.values(), app.search_button, app.clear_button,
                       app.groups_button, app.clear_group_button, app.filtered_export_button]:
            self.assertTrue(button.winfo_ismapped())
            self.assertGreaterEqual(button.winfo_width(), button.winfo_reqwidth())
            self.assertLessEqual(button.winfo_x()+button.winfo_width(), button.master.winfo_width())
        self.assertGreaterEqual(app.title_label.winfo_width(), app.title_label.winfo_reqwidth())

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

    def test_review_popups_follow_loaded_file_and_survive_failed_load(self):
        self.app.show_groups()
        groups = self.app.winfo_children()[-1]
        self.app.show_summary()
        summary = self.app.winfo_children()[-1]
        self.app.show_coverage()
        coverage = self.app.winfo_children()[-1]
        old_result = self.app.result
        with patch("rxdatalint.gui.validate_csv", side_effect=OSError("broken")), \
             patch("rxdatalint.gui.messagebox.showerror"):
            self.app.load_file("broken.csv")
            self.pump_until(lambda: not self.app.busy)
        self.assertIs(self.app.result, old_result)
        self.assertTrue(all(w.winfo_exists() for w in (groups, summary, coverage)))
        fresh = validate_csv(Path(__file__).parents[1] / "examples" / "sample_scmd.csv")
        with patch("rxdatalint.gui.validate_csv", return_value=fresh):
            self.app.load_file("new.csv")
            self.pump_until(lambda: not self.app.busy)
        self.assertIs(self.app.result, fresh)
        self.assertFalse(any(w.winfo_exists() for w in (groups, summary, coverage)))

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

    def test_group_drilldown_and_filtered_export_retain_exact_scope(self):
        issue = next(i for i in self.app.result.issues if i.rule == "value.negative" and i.row)
        group_key = finding_group(self.app.result, issue, "organisation")[0]
        self.app.select_filter("value.negative")
        self.app.active_group = ("organisation", group_key)
        self.app._render_result()
        expected = self.app.filtered_issues()
        self.assertTrue(expected)
        self.assertTrue(all(finding_group(self.app.result, i, "organisation")[0] == group_key
                            and i.rule == "value.negative" for i in expected))
        with tempfile.TemporaryDirectory() as directory:
            with patch("rxdatalint.gui.filedialog.askdirectory", return_value=directory), \
                 patch("rxdatalint.gui.messagebox.showinfo"):
                self.app.export_filtered()
                self.pump_until(lambda: not self.app.busy)
            payload = json.loads(next(Path(directory).glob("findings-*/filtered-findings.json")).read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_findings"], len(expected))
            self.assertEqual((payload["group_by"], payload["group_key"]), ("organisation", group_key))
        self.app.clear_group()
        self.assertIsNone(self.app.active_group)
        self.assertGreaterEqual(len(self.app.filtered_issues()), len(expected))

    def test_group_overview_opens_and_drills_into_source_finding(self):
        self.app._render_result()
        self.app.show_groups()
        window = self.app.winfo_children()[-1]
        self.addCleanup(lambda: window.destroy() if window.winfo_exists() else None)
        dimension = next(child for child in window.winfo_children() if isinstance(child, ttk.Combobox))
        dimension.current(1)
        dimension.event_generate("<<ComboboxSelected>>")
        frame = next(child for child in window.winfo_children() if isinstance(child, ttk.Frame))
        table = next(child for child in frame.winfo_children() if isinstance(child, ttk.Treeview))
        self.assertTrue(table.get_children())
        table.selection_set(table.get_children()[0])
        expected_key = table.item(table.selection()[0], "values")[0]
        next(child for child in window.winfo_children() if isinstance(child, ttk.Button)).invoke()
        self.assertEqual(self.app.active_group, ("organisation", f"ods:{expected_key}"))
        self.assertTrue(self.app.issue_by_item)
        self.assertTrue(self.app.tree.selection())
        self.assertIn(expected_key, self.app.details.get("1.0", "end"))

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

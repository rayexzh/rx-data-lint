import csv
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from run_analysis import build, safe_cell


class AnalysisTests(unittest.TestCase):
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
            with closing(sqlite3.connect(output / "medicines.sqlite")) as db:
                self.assertEqual(db.execute("SELECT COUNT(*),COUNT(cost_gbp),SUM(cost_gbp) FROM records").fetchone(), (5, 2, 80))
                self.assertIsNone(db.execute("SELECT SUM(cost_gbp) FROM records WHERE product_code='987654321'").fetchone()[0])
                self.assertEqual(db.execute("SELECT cost_status FROM records WHERE row_number=5").fetchone()[0], "invalid")
                self.assertEqual(db.execute("SELECT COUNT(*) FROM findings WHERE rule='row.duplicate_key'").fetchone()[0], 3)
            with self.assertRaises(ValueError):
                build(source, output, "synthetic")

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

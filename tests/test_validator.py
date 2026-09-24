import unittest
import tempfile
from pathlib import Path

from rxdatalint.validator import validate_csv


SAMPLE = Path(__file__).parents[1] / "examples" / "sample_scmd.csv"


class ValidatorTests(unittest.TestCase):
    def test_sample_finds_material_quality_problems(self):
        result = validate_csv(SAMPLE)
        rules = {issue.rule for issue in result.issues}

        self.assertEqual(result.row_count, 8)
        self.assertLess(result.score, 100)
        self.assertIn("value.negative", rules)
        self.assertIn("row.duplicate_key", rules)
        self.assertIn("value.year_month", rules)
        self.assertIn("series.missing_month", rules)
        self.assertIn("series.extreme_quantity", rules)

    def test_current_schema_has_no_missing_required_columns(self):
        result = validate_csv(SAMPLE)
        missing = [issue for issue in result.issues if issue.rule == "schema.required_column"]
        self.assertEqual(missing, [])

    def test_compact_api_month_is_accepted(self):
        header = SAMPLE.read_text(encoding="utf-8").splitlines()[0]
        row = "202607,R1A,42109611000001109,Paracetamol 500mg tablets,428673006,tablet,1000,tablet,1000,25.00"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "api.csv"
            path.write_text(f"{header}\n{row}\n", encoding="utf-8")
            result = validate_csv(path)
        month_issues = [issue for issue in result.issues if issue.rule == "value.year_month"]
        self.assertEqual(month_issues, [])


if __name__ == "__main__":
    unittest.main()

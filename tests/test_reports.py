import json
import tempfile
import unittest
from pathlib import Path

from rxdatalint.reports import write_outputs
from rxdatalint.validator import validate_csv


SAMPLE = Path(__file__).parents[1] / "examples" / "sample_scmd.csv"


class ReportTests(unittest.TestCase):
    def test_all_report_formats_are_created(self):
        result = validate_csv(SAMPLE)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_outputs(result, directory)
            self.assertEqual(set(paths), {"json", "csv", "html"})
            self.assertTrue(all(path.exists() for path in paths.values()))
            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload["row_count"], 8)
            self.assertIn("quality_score", payload)
            self.assertIn("RxDataLint quality report", paths["html"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

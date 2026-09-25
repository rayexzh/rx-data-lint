import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rxdatalint.cli import main
from rxdatalint.reports import write_outputs
from rxdatalint.validator import validate_csv

SAMPLE = Path(__file__).parents[1] / "examples" / "sample_scmd.csv"


class ExportSafetyTests(unittest.TestCase):
    def test_blocked_export_cannot_reuse_previous_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_outputs(validate_csv(SAMPLE), root / "reports")
            original = {key: path.read_bytes() for key, path in first.items()}
            empty = root / "empty.csv"
            empty.write_bytes(b"")
            second = write_outputs(validate_csv(empty), root / "reports")
            self.assertNotEqual(first["json"].parent, second["json"].parent)
            self.assertFalse((second["json"].parent / "normalized-scmd.csv").exists())
            self.assertEqual(original, {key: path.read_bytes() for key, path in first.items()})

    def test_early_stops_have_complete_unique_coverage(self):
        expected = {(c.rule, c.column) for c in validate_csv(SAMPLE).checks}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for content in ("", "YEAR_MONTH,YEAR_MONTH\n202601,202601\n"):
                path.write_text(content, encoding="utf-8")
                result = validate_csv(path)
                keys = [(c.rule, c.column) for c in result.checks]
                self.assertEqual(set(keys), expected)
                self.assertEqual(len(keys), len(expected))
                self.assertTrue(all(c.reason and c.checked_count == 0
                                    for c in result.checks if c.status == "skipped"))

    def test_cli_missing_input_returns_operational_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("sys.argv", ["rx-data-lint", str(Path(directory) / "missing.csv")]):
                with contextlib.redirect_stderr(io.StringIO()) as stream:
                    self.assertEqual(main(), 2)
                self.assertIn("Unable to complete", stream.getvalue())

    def test_cli_header_only_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_text(SAMPLE.read_text(encoding="utf-8-sig").splitlines()[0] + "\n")
            with patch("sys.argv", ["rx-data-lint", str(path), "-o", str(Path(directory) / "reports")]):
                with contextlib.redirect_stdout(io.StringIO()) as stream:
                    self.assertEqual(main(), 1)
                self.assertIn("Assessment: no_data", stream.getvalue())

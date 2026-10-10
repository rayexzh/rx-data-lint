import unittest
import tempfile
import csv
from pathlib import Path

from rxdatalint.validator import validate_csv, _parse_number


SAMPLE = Path(__file__).parents[1] / "examples" / "sample_scmd.csv"


class ValidatorTests(unittest.TestCase):
    def test_extreme_quantity_does_not_pool_different_or_unknown_units(self):
        original = validate_csv(SAMPLE).cleaned_rows[0]
        rows = []
        for quantity, unit in [('1', 'tablet')] * 4 + [('1000', 'pack'), ('1000', '')]:
            row = dict(original)
            row['TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE'] = quantity
            row['VMP_UDFS_UNIT_OF_MEASURE_IDENTIFIER'] = ''
            row['VMP_UDFS_UNIT_OF_MEASURE_NAME'] = unit
            rows.append(row)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'units.csv'
            with path.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(original))
                writer.writeheader()
                writer.writerows(rows)
            result = validate_csv(path)
            self.assertFalse(any(i.rule == 'series.extreme_quantity' for i in result.issues))
            rows[-2]['VMP_UDFS_UNIT_OF_MEASURE_NAME'] = 'TABLET'
            with path.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(original))
                writer.writeheader()
                writer.writerows(rows)
            result = validate_csv(path)
            flagged = [i for i in result.issues if i.rule == 'series.extreme_quantity']
            self.assertEqual([i.row for i in flagged], [6])
            self.assertIn('product/unit median', flagged[0].message)

    def test_numeric_formats_do_not_silently_reinterpret_bad_separators(self):
        for text in ('1,2', '12,34', ',123', '123,', '1,,000', '1_000', 'NaN', 'inf'):
            with self.subTest(text=text):
                self.assertIsNone(_parse_number(text))
        for text, expected in [('1,234.50', 1234.5), ('-1,234', -1234),
                               ('  .5 ', .5), ('1e3', 1000), ('+12', 12), ('0', 0)]:
            with self.subTest(text=text):
                self.assertEqual(_parse_number(text), expected)

    def test_unterminated_quoted_record_is_rejected(self):
        header = SAMPLE.read_text(encoding="utf-8").splitlines()[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "truncated.csv"
            path.write_text(header + '\n2026-07,R1A,42109611000001109,"truncated\n', encoding="utf-8")
            with self.assertRaises(csv.Error):
                validate_csv(path)

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

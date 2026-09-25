import hashlib
import tempfile
import unittest
from pathlib import Path

from rxdatalint.validator import validate_csv
from rxdatalint.reports import write_outputs

HEADER = 'YEAR_MONTH,ODS_CODE,VMP_SNOMED_CODE,VMP_PRODUCT_NAME,TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE,INDICATIVE_COST\n'
ROW = '202607,R1A,42109611000001109,Example,100,25\n'


class EvidenceTests(unittest.TestCase):
    def check_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_bytes(text.encode('utf-8'))
            return validate_csv(path)

    def test_hash_matches_original_bytes_including_bom(self):
        text = '\ufeff' + HEADER + ROW
        result = self.check_text(text)
        self.assertEqual(result.source_sha256, hashlib.sha256(text.encode('utf-8')).hexdigest())
        self.assertEqual(result.source_size_bytes, len(text.encode('utf-8')))
        self.assertTrue(result.checked_at_utc.endswith('+00:00'))

    def test_empty_file_keeps_evidence(self):
        result = self.check_text('')
        self.assertEqual(result.source_sha256, hashlib.sha256(b'').hexdigest())
        self.assertEqual(result.issues[0].rule, 'schema.empty')

    def test_nonfinite_numbers_are_rejected(self):
        for value in ('NaN', 'inf', '-Infinity'):
            with self.subTest(value=value):
                result = self.check_text(HEADER + ROW.replace(',100,', f',{value},'))
                self.assertIn('value.numeric', [i.rule for i in result.issues])

    def test_equivalent_month_formats_are_duplicate(self):
        result = self.check_text(HEADER + ROW + ROW.replace('202607', '2026-07'))
        self.assertIn('row.duplicate_key', [i.rule for i in result.issues])
        self.assertEqual(result.affected_row_count, 1)

    def test_extra_and_missing_fields_report_instead_of_crashing(self):
        for row in (ROW.strip() + ',extra\n', '202607,R1A\n'):
            result = self.check_text(HEADER + row)
            self.assertIn('schema.row_width', [i.rule for i in result.issues])

    def test_export_uses_check_time_evidence_after_source_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_text(HEADER + ROW, encoding='utf-8')
            result = validate_csv(path)
            digest = result.source_sha256
            path.write_text('changed', encoding='utf-8')
            outputs = write_outputs(result, Path(directory) / 'out')
            report = outputs['html'].read_text(encoding='utf-8')
            self.assertIn(digest, report)
            self.assertIn('not proof of correctness', report)
            self.assertEqual(result.source_sha256, digest)

import tempfile
import unittest
from pathlib import Path
from rxdatalint.validator import validate_csv
from rxdatalint.reports import write_outputs

HEADER='YEAR_MONTH,ODS_CODE,VMP_SNOMED_CODE,VMP_PRODUCT_NAME,TOTAL_QUANTITY_IN_VMP_UDFS_UNIT_OF_MEASURE,INDICATIVE_COST'
ROW='202607,R1A,42109611000001109,Example,100,25'

class CoverageTests(unittest.TestCase):
    def run_case(self, text):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.csv'
            p.write_text(text,encoding='utf-8')
            return validate_csv(p)

    def test_missing_cost_has_one_schema_error_and_skipped_numeric_check(self):
        r=self.run_case(HEADER.rsplit(',',1)[0]+'\n'+ROW.rsplit(',',1)[0])
        self.assertEqual(r.assessment,'partial')
        self.assertEqual([i.rule for i in r.issues],['schema.required_column'])
        c=next(c for c in r.checks if c.rule=='value.numeric' and c.column=='INDICATIVE_COST')
        self.assertEqual(c.status,'skipped')
        self.assertEqual(c.checked_count,0)

    def test_duplicate_and_alias_headers_block_export(self):
        for extra in ('YEAR_MONTH',' year month ','TOTAL_QUANITY_IN_VMP_UNIT'):
            r=self.run_case(HEADER+','+extra+'\n'+ROW+',10')
            self.assertEqual(r.assessment,'blocked')
            self.assertEqual(r.cleaned_rows,[])
            with tempfile.TemporaryDirectory() as d:
                paths=write_outputs(r,d)
                self.assertEqual(set(paths),{'json','html'})
                self.assertFalse((Path(d)/'normalized-scmd.csv').exists())

    def test_header_only_is_not_clean_success(self):
        r=self.run_case(HEADER+'\n')
        self.assertEqual(r.assessment,'no_data')
        self.assertIn('schema.no_records',[i.rule for i in r.issues])

    def test_single_month_does_not_claim_series_check_ran(self):
        r=self.run_case(HEADER+'\n'+ROW)
        c=next(c for c in r.checks if c.rule=='series.missing_month')
        self.assertEqual(c.status,'not_applicable')
        self.assertEqual(r.assessment,'completed')
        with tempfile.TemporaryDirectory() as d:
            paths=write_outputs(r,d)
            self.assertEqual(paths['csv'].name,'normalized-scmd.csv')
            self.assertIn('Check coverage',paths['html'].read_text())

    def test_blank_present_cost_is_invalid_not_skipped(self):
        r=self.run_case(HEADER+'\n'+ROW.rsplit(',',1)[0]+',')
        self.assertIn('value.numeric',[i.rule for i in r.issues])
        c=next(c for c in r.checks if c.rule=='value.numeric' and c.column=='INDICATIVE_COST')
        self.assertEqual(c.status,'executed')
        self.assertEqual(c.checked_count,1)

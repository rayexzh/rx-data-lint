import csv
import json
from pathlib import Path
import tempfile
import unittest

from rxdatalint.review import finding_group, group_findings, record_for, summarise, write_filtered_findings
from rxdatalint.validator import Issue, ValidationResult


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.issues = [Issue("value.negative", "warning", "Review", 2, "INDICATIVE_COST", "-3"),
                       Issue("value.negative", "warning", "Review quantity", 2),
                       Issue("series.missing_month", "warning", "Missing month")]
        self.result = ValidationResult("sample.csv", 1, [], self.issues,
            [{"YEAR_MONTH": "202607", "ODS_CODE": "R1A", "VMP_SNOMED_CODE": "123456",
              "VMP_PRODUCT_NAME": "=1+2"}], source_sha256="abc")

    def test_summary_deduplicates_records_and_separates_unlocated_findings(self):
        groups = {r["rule"]: r for r in summarise(self.result)}
        self.assertEqual(groups["value.negative"]["findings"], 2)
        self.assertEqual(groups["value.negative"]["affected_records"], 1)
        self.assertEqual(groups["value.negative"]["organisations"], 1)
        self.assertEqual(groups["series.missing_month"]["unlocated_findings"], 1)
        self.assertEqual(groups["series.missing_month"]["affected_records"], 0)
        self.assertEqual(record_for(self.result, self.issues[-1]), {})

    def test_grouped_review_keeps_exact_identity_and_counts_distinct_rows(self):
        by_org = group_findings(self.result, self.issues, "organisation")
        self.assertEqual([(g["key"], g["findings"], g["affected_records"])
                          for g in by_org], [("ods:R1A", 2, 1), ("__unlocated__", 1, 0)])
        by_product = group_findings(self.result, self.issues, "product")
        self.assertEqual(by_product[0]["key"], "code:123456")
        self.assertEqual(finding_group(self.result, self.issues[-1], "product")[0], "__unlocated__")
        with self.assertRaises(ValueError):
            group_findings(self.result, self.issues, "hospital")

    def test_filtered_export_keeps_scope_context_and_original_json_values(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = write_filtered_findings(self.result, self.issues[:1], directory,
                                           query="R1A", category="value.negative")
            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_findings"], 1)
            self.assertEqual(payload["total_findings"], 3)
            self.assertEqual(payload["query"], "R1A")
            self.assertEqual(payload["group_by"], "")
            self.assertEqual(payload["source_sha256"], "abc")
            self.assertEqual(payload["findings"][0]["value"], "-3")
            with paths["csv"].open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["VMP_PRODUCT_NAME"], "'=1+2")
            self.assertEqual(rows[0]["ODS_CODE"], "R1A")
            self.assertEqual(self.result.cleaned_rows[0]["VMP_PRODUCT_NAME"], "=1+2")
            again = write_filtered_findings(self.result, [], directory)
            self.assertNotEqual(again["json"].parent, paths["json"].parent)


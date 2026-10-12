import importlib.util
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("invoice_demo", ROOT/"examples/invoice-report/report.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class InvoiceTests(unittest.TestCase):
    def test_golden(self):
        output = mod.summarize(ROOT/"examples/invoice-report/input.csv")
        self.assertEqual(output, {"Design":"175.25", "Engineering":"225.00"})
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"bad.csv"
            p.write_text("invoice,department,amount\nA,Team,10\nA,Team,100\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                mod.summarize(p)
    def test_nonnumeric_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"bad.csv"
            p.write_text("invoice,department,amount\nA,Team,N/A\n")
            with self.assertRaisesRegex(ValueError, "Invalid"):
                mod.summarize(p)
    def test_negative_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"bad.csv"
            p.write_text("invoice,department,amount\nA,Team,-1\n")
            with self.assertRaisesRegex(ValueError, "Negative"):
                mod.summarize(p)
    def test_missing_field_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"bad.csv"
            p.write_text("invoice,department,amount\nA,,12\n")
            with self.assertRaisesRegex(ValueError, "Missing"):
                mod.summarize(p)

if __name__=="__main__": unittest.main()

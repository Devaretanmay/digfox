import sqlite3
import unittest

from service import get_invoice


class InvoiceTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "CREATE TABLE invoices (tenant_id TEXT, invoice_id INTEGER, total INTEGER)"
        )
        self.connection.executemany(
            "INSERT INTO invoices VALUES (?, ?, ?)",
            [("alpha", 7, 100), ("beta", 7, 900)],
        )

    def tearDown(self):
        self.connection.close()

    def test_lookup_is_scoped_to_tenant(self):
        invoice = get_invoice(self.connection, "beta", 7)
        self.assertEqual(invoice, {"tenant_id": "beta", "invoice_id": 7, "total": 900})

    def test_missing_tenant_invoice_returns_none(self):
        self.assertIsNone(get_invoice(self.connection, "gamma", 7))


if __name__ == "__main__":
    unittest.main()

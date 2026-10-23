import unittest

from paging import page


class PagingTests(unittest.TestCase):
    def test_limit(self):
        self.assertEqual(page([1, 2, 3], limit=2), [1, 2])

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            page([1, 2, 3], limit=0)


if __name__ == "__main__":
    unittest.main()

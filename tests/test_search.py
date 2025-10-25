"""
Tests for search and filtering operations
"""

import unittest
from pyspl import SPL


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Alice", "age": 30, "city": "NYC", "status": "active"},
            {"name": "Bob", "age": 25, "city": "LA", "status": "inactive"},
            {"name": "Charlie", "age": 35, "city": "NYC", "status": "active"},
            {"name": "David", "age": 28, "city": "SF", "status": "active"},
            {"name": "Eve", "age": 32, "city": "LA", "status": "inactive"},
        ]

    def test_search_all(self):
        spl = SPL(self.data)
        result = spl.search('*')
        self.assertEqual(len(result), 5)

    def test_search_exact_match(self):
        spl = SPL(self.data)
        result = spl.search('city="NYC"')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['city'] == 'NYC' for r in result))

    def test_search_multiple_conditions(self):
        spl = SPL(self.data)
        result = spl.search('city="NYC" status="active"')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['city'] == 'NYC' and r['status'] == 'active' for r in result))

    def test_search_greater_than(self):
        spl = SPL(self.data)
        result = spl.search('age>30')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['age'] > 30 for r in result))

    def test_search_less_than_equal(self):
        spl = SPL(self.data)
        result = spl.search('age<=28')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['age'] <= 28 for r in result))

    def test_search_not_equal(self):
        spl = SPL(self.data)
        result = spl.search('city!="NYC"')
        self.assertEqual(len(result), 3)
        self.assertTrue(all(r['city'] != 'NYC' for r in result))

    def test_where_command(self):
        spl = SPL(self.data)
        result = spl.search('where status="active"')
        self.assertEqual(len(result), 3)


if __name__ == '__main__':
    unittest.main()

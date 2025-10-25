"""
Tests for field manipulation operations
"""

import unittest
from pyspl import SPL


class TestFields(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Alice", "age": 30, "city": "NYC", "status": "active"},
            {"name": "Bob", "age": 25, "city": "LA", "status": "inactive"},
        ]

    def test_fields_include(self):
        spl = SPL(self.data)
        result = spl.search('fields name, age')
        self.assertEqual(len(result), 2)
        self.assertEqual(set(result[0].keys()), {'name', 'age'})

    def test_fields_exclude(self):
        spl = SPL(self.data)
        result = spl.search('fields - status')
        self.assertEqual(len(result), 2)
        self.assertNotIn('status', result[0])
        self.assertIn('name', result[0])

    def test_rename(self):
        spl = SPL(self.data)
        result = spl.search('rename name as full_name, city as location')
        self.assertEqual(len(result), 2)
        self.assertIn('full_name', result[0])
        self.assertIn('location', result[0])
        self.assertNotIn('name', result[0])
        self.assertNotIn('city', result[0])

    def test_table(self):
        spl = SPL(self.data)
        result = spl.search('table name, city')
        self.assertEqual(len(result), 2)
        self.assertEqual(set(result[0].keys()), {'name', 'city'})


if __name__ == '__main__':
    unittest.main()

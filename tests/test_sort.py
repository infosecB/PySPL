"""
Tests for sort, head, and tail operations
"""

import unittest
from pyspl import SPL


class TestSort(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Charlie", "age": 35, "score": 78},
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Bob", "age": 25, "score": 90},
        ]

    def test_sort_ascending(self):
        spl = SPL(self.data)
        result = spl.search('sort age')
        self.assertEqual([r['name'] for r in result], ['Bob', 'Alice', 'Charlie'])

    def test_sort_descending(self):
        spl = SPL(self.data)
        result = spl.search('sort -score')
        self.assertEqual([r['name'] for r in result], ['Bob', 'Alice', 'Charlie'])

    def test_sort_multiple(self):
        data = [
            {"city": "NYC", "name": "Bob"},
            {"city": "LA", "name": "Alice"},
            {"city": "NYC", "name": "Alice"},
        ]
        spl = SPL(data)
        result = spl.search('sort city, name')
        self.assertEqual(result[0]['city'], 'LA')
        self.assertEqual(result[1]['name'], 'Alice')
        self.assertEqual(result[2]['name'], 'Bob')

    def test_head(self):
        spl = SPL(self.data)
        result = spl.search('head 2')
        self.assertEqual(len(result), 2)

    def test_tail(self):
        spl = SPL(self.data)
        result = spl.search('tail 2')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Alice')


if __name__ == '__main__':
    unittest.main()

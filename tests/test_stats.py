"""
Tests for stats aggregation operations
"""

import unittest
from pyspl import SPL


class TestStats(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Alice", "age": 30, "city": "NYC", "score": 85},
            {"name": "Bob", "age": 25, "city": "LA", "score": 90},
            {"name": "Charlie", "age": 35, "city": "NYC", "score": 78},
            {"name": "David", "age": 28, "city": "SF", "score": 92},
            {"name": "Eve", "age": 32, "city": "LA", "score": 88},
        ]

    def test_stats_count(self):
        spl = SPL(self.data)
        result = spl.search('stats count')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['count'], 5)

    def test_stats_count_by(self):
        spl = SPL(self.data)
        result = spl.search('stats count by city')
        self.assertEqual(len(result), 3)
        # Check NYC has 2 records
        nyc_result = [r for r in result if r['city'] == 'NYC'][0]
        self.assertEqual(nyc_result['count'], 2)

    def test_stats_avg(self):
        spl = SPL(self.data)
        result = spl.search('stats avg(age)')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['avg(age)'], 30.0)

    def test_stats_sum(self):
        spl = SPL(self.data)
        result = spl.search('stats sum(score)')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sum(score)'], 433)

    def test_stats_min_max(self):
        spl = SPL(self.data)
        result = spl.search('stats min(age), max(age)')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['min(age)'], 25)
        self.assertEqual(result[0]['max(age)'], 35)

    def test_stats_multiple_agg_by(self):
        spl = SPL(self.data)
        result = spl.search('stats count, avg(score) by city')
        self.assertEqual(len(result), 3)

        # Check LA results
        la_result = [r for r in result if r['city'] == 'LA'][0]
        self.assertEqual(la_result['count'], 2)
        self.assertEqual(la_result['avg(score)'], 89.0)

    def test_stats_distinct_count(self):
        spl = SPL(self.data)
        result = spl.search('stats dc(city)')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['dc(city)'], 3)

    def test_stats_values(self):
        spl = SPL(self.data)
        result = spl.search('stats values(city)')
        self.assertEqual(len(result), 1)
        cities = result[0]['values(city)']
        self.assertEqual(set(cities), {'NYC', 'LA', 'SF'})


if __name__ == '__main__':
    unittest.main()

"""
Tests for stdev (standard deviation) aggregation
"""

import unittest
import math
from pyspl import SPL


class TestStdev(unittest.TestCase):
    def setUp(self):
        # Dataset with known statistics
        self.data = [
            {"group": "A", "value": 2},
            {"group": "A", "value": 4},
            {"group": "A", "value": 4},
            {"group": "A", "value": 4},
            {"group": "A", "value": 5},
            {"group": "A", "value": 5},
            {"group": "A", "value": 7},
            {"group": "A", "value": 9},
            {"group": "B", "value": 10},
            {"group": "B", "value": 20},
            {"group": "B", "value": 30},
        ]

    def test_stdev_basic(self):
        """Test basic stdev calculation"""
        spl = SPL(self.data)
        result = spl.search('stats stdev(value)')

        self.assertEqual(len(result), 1)
        # Should have a stdev value
        self.assertIn('stdev(value)', result[0])
        self.assertGreater(result[0]['stdev(value)'], 0)

    def test_stdev_by_group(self):
        """Test stdev with grouping"""
        spl = SPL(self.data)
        result = spl.search('stats stdev(value) by group')

        self.assertEqual(len(result), 2)

        # Group A: values [2,4,4,4,5,5,7,9], mean=5, stdev=2.0
        group_a = [r for r in result if r['group'] == 'A'][0]
        self.assertAlmostEqual(group_a['stdev(value)'], 2.0, places=4)

        # Group B: values [10,20,30], mean=20, stdev≈8.165
        group_b = [r for r in result if r['group'] == 'B'][0]
        self.assertAlmostEqual(group_b['stdev(value)'], 8.1650, places=3)

    def test_stdev_with_alias(self):
        """Test stdev with 'as' alias"""
        spl = SPL(self.data)
        result = spl.search('stats stdev(value) as std_dev by group')

        group_a = [r for r in result if r['group'] == 'A'][0]
        self.assertIn('std_dev', group_a)
        self.assertNotIn('stdev(value)', group_a)
        self.assertAlmostEqual(group_a['std_dev'], 2.0, places=4)

    def test_stdev_multiple_aggregations(self):
        """Test stdev with other aggregations"""
        spl = SPL(self.data)
        result = spl.search('stats count avg(value) stdev(value) by group')

        group_a = [r for r in result if r['group'] == 'A'][0]
        self.assertEqual(group_a['count'], 8)
        self.assertEqual(group_a['avg(value)'], 5.0)
        self.assertAlmostEqual(group_a['stdev(value)'], 2.0, places=4)

    def test_stdev_sample(self):
        """Test sample standard deviation (stdevs)"""
        spl = SPL(self.data)
        result = spl.search('stats stdevs(value) by group')

        # Sample stdev should be slightly larger than population stdev
        group_a = [r for r in result if r['group'] == 'A'][0]
        # Sample stdev = sqrt(32/7) ≈ 2.1381
        self.assertAlmostEqual(group_a['stdevs(value)'], 2.1381, places=3)

        group_b = [r for r in result if r['group'] == 'B'][0]
        # Sample stdev for [10,20,30] = 10.0
        self.assertAlmostEqual(group_b['stdevs(value)'], 10.0, places=3)

    def test_stdevp_alias(self):
        """Test stdevp (population) alias"""
        spl = SPL(self.data)
        result_stdev = spl.search('stats stdev(value) by group')
        result_stdevp = spl.search('stats stdevp(value) by group')

        # stdev and stdevp should give same results
        for i in range(len(result_stdev)):
            self.assertAlmostEqual(
                result_stdev[i]['stdev(value)'],
                result_stdevp[i]['stdevp(value)'],
                places=10
            )

    def test_stdev_single_value(self):
        """Test stdev with single value (should be 0)"""
        data = [{"value": 10}]
        spl = SPL(data)
        result = spl.search('stats stdev(value)')

        self.assertEqual(result[0]['stdev(value)'], 0.0)

    def test_stdev_empty_data(self):
        """Test stdev with no data"""
        data = []
        spl = SPL(data)
        result = spl.search('stats stdev(value)')

        self.assertEqual(len(result), 0)

    def test_stdev_with_null_values(self):
        """Test stdev ignores null values"""
        data = [
            {"value": 10},
            {"value": 20},
            {"value": None},
            {"value": 30},
        ]
        spl = SPL(data)
        result = spl.search('stats stdev(value)')

        # Should calculate stdev only on [10, 20, 30]
        # Mean = 20, stdev = sqrt(((10-20)^2 + (20-20)^2 + (30-20)^2) / 3) = sqrt(200/3) ≈ 8.165
        self.assertAlmostEqual(result[0]['stdev(value)'], 8.1650, places=3)

    def test_eventstats_stdev(self):
        """Test stdev with eventstats"""
        spl = SPL(self.data)
        result = spl.search('eventstats stdev(value) as group_stdev by group')

        # All events should be preserved
        self.assertEqual(len(result), 11)

        # Group A events should have stdev=2.0
        group_a_events = [r for r in result if r['group'] == 'A']
        for event in group_a_events:
            self.assertAlmostEqual(event['group_stdev'], 2.0, places=4)

        # Group B events should have stdev≈8.165
        group_b_events = [r for r in result if r['group'] == 'B']
        for event in group_b_events:
            self.assertAlmostEqual(event['group_stdev'], 8.1650, places=3)

    def test_stdev_coefficient_of_variation(self):
        """Test using stdev to calculate coefficient of variation"""
        spl = SPL(self.data)
        result = spl.search('stats avg(value) as mean stdev(value) as std by group | eval cv = std / mean')

        group_a = [r for r in result if r['group'] == 'A'][0]
        # CV for A = 2.0 / 5.0 = 0.4
        self.assertAlmostEqual(group_a['cv'], 0.4, places=4)

    def test_stdev_with_filter(self):
        """Test stdev with filtering"""
        spl = SPL(self.data)
        result = spl.search('value>=5 | stats stdev(value)')

        # Filtered values: [5,5,7,9,10,20,30]
        # Should calculate stdev on these values
        self.assertGreater(result[0]['stdev(value)'], 0)


if __name__ == '__main__':
    unittest.main()

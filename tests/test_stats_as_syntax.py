"""
Tests for stats command with 'as' syntax
"""

import unittest
from pyspl import SPL


class TestStatsAsSyntax(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"user": "alice", "category": "electronics", "price": 100},
            {"user": "alice", "category": "books", "price": 50},
            {"user": "bob", "category": "electronics", "price": 200},
            {"user": "bob", "category": "sports", "price": 75},
            {"user": "charlie", "category": "books", "price": 30},
        ]

    def test_stats_with_single_alias(self):
        """Test stats with single 'as' alias"""
        spl = SPL(self.data)
        result = spl.search('stats count as total by user')

        self.assertEqual(len(result), 3)
        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['total'], 2)
        self.assertNotIn('count', alice)

    def test_stats_with_multiple_aliases(self):
        """Test stats with multiple 'as' aliases"""
        spl = SPL(self.data)
        result = spl.search('stats count as total sum(price) as revenue by user')

        self.assertEqual(len(result), 3)
        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['total'], 2)
        self.assertEqual(alice['revenue'], 150)
        self.assertNotIn('count', alice)
        self.assertNotIn('sum(price)', alice)

    def test_stats_space_separated_no_alias(self):
        """Test stats with space-separated aggregations without aliases"""
        spl = SPL(self.data)
        result = spl.search('stats count sum(price) by user')

        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['count'], 2)
        self.assertEqual(alice['sum(price)'], 150)

    def test_stats_mixed_alias_and_no_alias(self):
        """Test stats with mixed aliases and non-aliases"""
        spl = SPL(self.data)
        result = spl.search('stats count as total sum(price) avg(price) as avg_price by user')

        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['total'], 2)
        self.assertEqual(alice['sum(price)'], 150)
        self.assertEqual(alice['avg_price'], 75.0)

    def test_stats_dc_with_alias(self):
        """Test distinct count with alias"""
        spl = SPL(self.data)
        result = spl.search('stats dc(category) as unique_categories by user')

        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['unique_categories'], 2)
        self.assertNotIn('dc(category)', alice)

    def test_stats_user_example(self):
        """Test the exact user example: dc(category) as category count by user"""
        spl = SPL(self.data)
        result = spl.search('stats dc(category) as category count by user')

        # Should have category and count fields
        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['category'], 2)  # dc(category) aliased as 'category'
        self.assertEqual(alice['count'], 2)
        self.assertNotIn('dc(category)', alice)

    def test_eventstats_with_alias(self):
        """Test eventstats with 'as' alias"""
        spl = SPL(self.data)
        result = spl.search('eventstats avg(price) as avg_price by user')

        # All events should be preserved
        self.assertEqual(len(result), 5)

        # Alice's events should have avg_price
        alice_events = [r for r in result if r['user'] == 'alice']
        for event in alice_events:
            self.assertEqual(event['avg_price'], 75.0)
            self.assertNotIn('avg(price)', event)

    def test_backward_compatibility_comma_separated(self):
        """Test backward compatibility with comma-separated format"""
        spl = SPL(self.data)
        result = spl.search('stats count, sum(price), avg(price) by user')

        alice = [r for r in result if r['user'] == 'alice'][0]
        self.assertEqual(alice['count'], 2)
        self.assertEqual(alice['sum(price)'], 150)
        self.assertEqual(alice['avg(price)'], 75.0)

    def test_complex_pipeline_with_alias(self):
        """Test complex pipeline with aliases"""
        spl = SPL(self.data)
        result = spl.search('category="electronics" | stats count as purchases sum(price) as revenue by user | sort -revenue')

        self.assertEqual(len(result), 2)
        # Bob should be first (revenue=200)
        self.assertEqual(result[0]['user'], 'bob')
        self.assertEqual(result[0]['purchases'], 1)
        self.assertEqual(result[0]['revenue'], 200)


if __name__ == '__main__':
    unittest.main()

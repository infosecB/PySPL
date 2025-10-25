"""
Tests for where command with field-to-field comparisons
"""

import unittest
from pyspl import SPL


class TestWhereFieldComparisons(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"user": "alice", "score": 85, "threshold": 80, "bonus": 10},
            {"user": "bob", "score": 75, "threshold": 80, "bonus": 5},
            {"user": "charlie", "score": 90, "threshold": 85, "bonus": 15},
            {"user": "david", "score": 70, "threshold": 75, "bonus": 8},
        ]

    def test_where_field_greater_than_field(self):
        """Test where field > field"""
        spl = SPL(self.data)
        result = spl.search('where score > threshold')

        # alice (85 > 80), charlie (90 > 85)
        self.assertEqual(len(result), 2)
        self.assertIn('alice', [r['user'] for r in result])
        self.assertIn('charlie', [r['user'] for r in result])

    def test_where_field_less_than_field(self):
        """Test where field < field"""
        spl = SPL(self.data)
        result = spl.search('where score < threshold')

        # bob (75 < 80), david (70 < 75)
        self.assertEqual(len(result), 2)
        self.assertIn('bob', [r['user'] for r in result])
        self.assertIn('david', [r['user'] for r in result])

    def test_where_field_equals_field(self):
        """Test where field = field"""
        data = [
            {"a": 5, "b": 5},
            {"a": 10, "b": 20},
            {"a": 15, "b": 15},
        ]
        spl = SPL(data)
        result = spl.search('where a = b')

        self.assertEqual(len(result), 2)

    def test_where_field_not_equals_field(self):
        """Test where field != field"""
        data = [
            {"a": 5, "b": 5},
            {"a": 10, "b": 20},
            {"a": 15, "b": 15},
        ]
        spl = SPL(data)
        result = spl.search('where a != b')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['a'], 10)

    def test_where_with_eventstats(self):
        """Test where with eventstats (the user's use case)"""
        data = [
            {"user": "alice", "count": 10},
            {"user": "bob", "count": 5},
            {"user": "charlie", "count": 8},
            {"user": "david", "count": 3},
        ]

        spl = SPL(data)
        result = spl.search('eventstats avg(count) as avg | where count > avg')

        # alice (10 > 6.5), charlie (8 > 6.5)
        self.assertEqual(len(result), 2)
        self.assertIn('alice', [r['user'] for r in result])
        self.assertIn('charlie', [r['user'] for r in result])

    def test_where_field_comparison_with_stats(self):
        """Test where with stats and eventstats pipeline"""
        spl = SPL(self.data)
        result = spl.search('stats count as event_count by user | eventstats avg(event_count) as avg | where event_count > avg')

        # This mimics the user's original query
        # All users have 1 event, so none should be > average (which is 1)
        # Actually, all have event_count=1, avg=1, so 1 > 1 is False
        self.assertEqual(len(result), 0)

    def test_where_field_comparison_mixed_types(self):
        """Test where field comparison with type coercion"""
        data = [
            {"val1": 10, "val2": 5.5},
            {"val1": 3, "val2": 8.0},
        ]
        spl = SPL(data)
        result = spl.search('where val1 > val2')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['val1'], 10)

    def test_where_still_works_with_literals(self):
        """Ensure where still works with literal values"""
        spl = SPL(self.data)

        # Test with literal number
        result = spl.search('where score > 80')
        self.assertEqual(len(result), 2)  # alice, charlie

        # Test with literal string
        result2 = spl.search('where user = "alice"')
        self.assertEqual(len(result2), 1)
        self.assertEqual(result2[0]['user'], 'alice')

    def test_where_field_comparison_complex_pipeline(self):
        """Test complex pipeline with field comparisons"""
        data = [
            {"product": "A", "sales": 100, "target": 90},
            {"product": "B", "sales": 80, "target": 100},
            {"product": "C", "sales": 120, "target": 110},
            {"product": "D", "sales": 95, "target": 100},
        ]

        spl = SPL(data)
        result = spl.search('where sales > target | stats count as over_target')

        # A (100 > 90), C (120 > 110)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['over_target'], 2)


if __name__ == '__main__':
    unittest.main()

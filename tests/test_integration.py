"""
Integration tests for complex SPL queries
"""

import unittest
from pyspl import SPL


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"timestamp": "2025-01-01", "user": "alice", "action": "login", "duration": 120},
            {"timestamp": "2025-01-01", "user": "bob", "action": "login", "duration": 95},
            {"timestamp": "2025-01-01", "user": "alice", "action": "search", "duration": 45},
            {"timestamp": "2025-01-01", "user": "bob", "action": "search", "duration": 60},
            {"timestamp": "2025-01-01", "user": "alice", "action": "logout", "duration": 10},
            {"timestamp": "2025-01-02", "user": "charlie", "action": "login", "duration": 110},
            {"timestamp": "2025-01-02", "user": "charlie", "action": "search", "duration": 55},
        ]

    def test_search_and_stats(self):
        spl = SPL(self.data)
        result = spl.search('action="login" | stats avg(duration)')
        self.assertEqual(len(result), 1)
        expected_avg = (120 + 95 + 110) / 3
        self.assertEqual(result[0]['avg(duration)'], expected_avg)

    def test_stats_and_sort(self):
        spl = SPL(self.data)
        result = spl.search('stats count by user | sort -count')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['user'], 'alice')
        self.assertEqual(result[0]['count'], 3)

    def test_search_stats_and_fields(self):
        spl = SPL(self.data)
        result = spl.search('stats avg(duration) by action | fields action, avg(duration)')
        self.assertEqual(len(result), 3)
        for r in result:
            self.assertEqual(set(r.keys()), {'action', 'avg(duration)'})

    def test_complex_pipeline(self):
        spl = SPL(self.data)
        result = spl.search('action!="logout" | stats sum(duration) by user | sort -sum(duration) | head 2')
        self.assertEqual(len(result), 2)
        # Alice should be first (login:120 + search:45 = 165)
        self.assertEqual(result[0]['user'], 'alice')

    def test_eval_and_stats(self):
        spl = SPL(self.data)
        result = spl.search('eval duration_minutes = duration / 60 | stats avg(duration_minutes)')
        self.assertEqual(len(result), 1)
        # Average should be in minutes
        self.assertAlmostEqual(result[0]['avg(duration_minutes)'], 70.71428571428571 / 60, places=2)

    def test_rename_and_fields(self):
        spl = SPL(self.data)
        result = spl.search('rename user as username | fields username, action')
        self.assertEqual(len(result), 7)
        self.assertIn('username', result[0])
        self.assertNotIn('user', result[0])

    def test_multiple_conditions_and_aggregation(self):
        spl = SPL(self.data)
        result = spl.search('user="alice" action!="logout" | stats count, sum(duration)')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['count'], 2)
        self.assertEqual(result[0]['sum(duration)'], 165)


if __name__ == '__main__':
    unittest.main()

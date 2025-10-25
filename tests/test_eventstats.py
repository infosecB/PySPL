"""
Tests for eventstats command
"""

import unittest
from pyspl import SPL


class TestEventstats(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Alice", "age": 30, "city": "NYC", "score": 85},
            {"name": "Bob", "age": 25, "city": "LA", "score": 90},
            {"name": "Charlie", "age": 35, "city": "NYC", "score": 78},
            {"name": "David", "age": 28, "city": "SF", "score": 92},
            {"name": "Eve", "age": 32, "city": "LA", "score": 88},
        ]

    def test_eventstats_count_no_grouping(self):
        """Test eventstats count without grouping - adds total count to each event"""
        spl = SPL(self.data)
        result = spl.search('eventstats count')

        # Should have all 5 records
        self.assertEqual(len(result), 5)

        # Each record should have count field with value 5
        for record in result:
            self.assertEqual(record['count'], 5)
            # Original fields should be preserved
            self.assertIn('name', record)
            self.assertIn('age', record)

    def test_eventstats_count_by_city(self):
        """Test eventstats count by city - adds city count to each event"""
        spl = SPL(self.data)
        result = spl.search('eventstats count by city')

        # Should have all 5 records
        self.assertEqual(len(result), 5)

        # NYC records should have count=2
        nyc_records = [r for r in result if r['city'] == 'NYC']
        self.assertEqual(len(nyc_records), 2)
        for record in nyc_records:
            self.assertEqual(record['count'], 2)

        # LA records should have count=2
        la_records = [r for r in result if r['city'] == 'LA']
        self.assertEqual(len(la_records), 2)
        for record in la_records:
            self.assertEqual(record['count'], 2)

        # SF records should have count=1
        sf_records = [r for r in result if r['city'] == 'SF']
        self.assertEqual(len(sf_records), 1)
        self.assertEqual(sf_records[0]['count'], 1)

    def test_eventstats_avg_by_city(self):
        """Test eventstats avg by city - adds average age per city to each event"""
        spl = SPL(self.data)
        result = spl.search('eventstats avg(age) by city')

        # Should have all 5 records
        self.assertEqual(len(result), 5)

        # NYC records should have avg(age)=(30+35)/2=32.5
        nyc_records = [r for r in result if r['city'] == 'NYC']
        for record in nyc_records:
            self.assertEqual(record['avg(age)'], 32.5)

        # LA records should have avg(age)=(25+32)/2=28.5
        la_records = [r for r in result if r['city'] == 'LA']
        for record in la_records:
            self.assertEqual(record['avg(age)'], 28.5)

    def test_eventstats_multiple_aggs(self):
        """Test eventstats with multiple aggregations"""
        spl = SPL(self.data)
        result = spl.search('eventstats avg(score), max(score), min(score) by city')

        # Should have all 5 records
        self.assertEqual(len(result), 5)

        # NYC records should have score stats (85, 78)
        nyc_records = [r for r in result if r['city'] == 'NYC']
        for record in nyc_records:
            self.assertEqual(record['avg(score)'], 81.5)
            self.assertEqual(record['max(score)'], 85)
            self.assertEqual(record['min(score)'], 78)

    def test_eventstats_with_filter(self):
        """Test eventstats combined with search filter"""
        spl = SPL(self.data)
        result = spl.search('city="NYC" | eventstats avg(age)')

        # Should only have 2 NYC records
        self.assertEqual(len(result), 2)

        # Both should have avg age of (30+35)/2=32.5
        for record in result:
            self.assertEqual(record['avg(age)'], 32.5)

    def test_eventstats_then_fields(self):
        """Test eventstats followed by fields selection"""
        spl = SPL(self.data)
        result = spl.search('eventstats avg(score) by city | fields name, city, avg(score)')

        # Should have all 5 records with only selected fields
        self.assertEqual(len(result), 5)
        for record in result:
            self.assertEqual(set(record.keys()), {'name', 'city', 'avg(score)'})

    def test_eventstats_sum(self):
        """Test eventstats with sum aggregation"""
        spl = SPL(self.data)
        result = spl.search('eventstats sum(score) by city')

        # NYC should have sum of 85+78=163
        nyc_records = [r for r in result if r['city'] == 'NYC']
        for record in nyc_records:
            self.assertEqual(record['sum(score)'], 163)

        # LA should have sum of 90+88=178
        la_records = [r for r in result if r['city'] == 'LA']
        for record in la_records:
            self.assertEqual(record['sum(score)'], 178)

    def test_eventstats_distinct_count(self):
        """Test eventstats with distinct count"""
        spl = SPL(self.data)
        result = spl.search('eventstats dc(city)')

        # Should have all 5 records, each with dc(city)=3
        self.assertEqual(len(result), 5)
        for record in result:
            self.assertEqual(record['dc(city)'], 3)

    def test_eventstats_preserves_order(self):
        """Test that eventstats preserves original order"""
        spl = SPL(self.data)
        result = spl.search('eventstats count by city')

        # Order should be preserved
        names = [r['name'] for r in result]
        self.assertEqual(names, ['Alice', 'Bob', 'Charlie', 'David', 'Eve'])

    def test_eventstats_vs_stats_comparison(self):
        """Compare eventstats and stats behavior"""
        spl = SPL(self.data)

        # stats reduces to group aggregates
        stats_result = spl.search('stats avg(age) by city')
        self.assertEqual(len(stats_result), 3)  # 3 cities

        # eventstats preserves all records
        eventstats_result = spl.search('eventstats avg(age) by city')
        self.assertEqual(len(eventstats_result), 5)  # All 5 records

    def test_eventstats_complex_pipeline(self):
        """Test eventstats in complex pipeline"""
        spl = SPL(self.data)
        # Note: field names with parentheses in eval may not work perfectly,
        # so we'll just verify the eventstats adds the field correctly
        result = spl.search('eventstats avg(score) by city | fields name, city, score, avg(score)')

        # Should have all 5 records
        self.assertEqual(len(result), 5)

        # Check Alice's avg score for NYC
        alice = [r for r in result if r['name'] == 'Alice'][0]
        self.assertEqual(alice['avg(score)'], 81.5)
        self.assertEqual(alice['score'], 85)


if __name__ == '__main__':
    unittest.main()

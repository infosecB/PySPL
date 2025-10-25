"""
Tests for eval command
"""

import unittest
from pyspl import SPL


class TestEval(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Alice", "price": 100, "quantity": 5},
            {"name": "Bob", "price": 50, "quantity": 10},
        ]

    def test_eval_arithmetic(self):
        spl = SPL(self.data)
        result = spl.search('eval total = price * quantity')
        self.assertEqual(result[0]['total'], 500)
        self.assertEqual(result[1]['total'], 500)

    def test_eval_addition(self):
        spl = SPL(self.data)
        result = spl.search('eval sum = price + quantity')
        self.assertEqual(result[0]['sum'], 105)
        self.assertEqual(result[1]['sum'], 60)

    def test_eval_constant(self):
        spl = SPL(self.data)
        result = spl.search('eval category = "product"')
        self.assertEqual(result[0]['category'], 'product')
        self.assertEqual(result[1]['category'], 'product')

    def test_eval_if_condition(self):
        spl = SPL(self.data)
        result = spl.search('eval type = if(price > 75, "expensive", "cheap")')
        self.assertEqual(result[0]['type'], 'expensive')
        self.assertEqual(result[1]['type'], 'cheap')


if __name__ == '__main__':
    unittest.main()

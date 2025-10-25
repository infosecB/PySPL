"""
PySPL - Splunk SPL for Python Dictionaries

A lightweight library that allows you to run Splunk SPL (Search Processing Language)
queries against Python dictionaries and lists.

Example:
    >>> from pyspl import SPL
    >>> data = [
    ...     {"name": "Alice", "age": 30, "city": "NYC"},
    ...     {"name": "Bob", "age": 25, "city": "LA"},
    ...     {"name": "Charlie", "age": 35, "city": "NYC"}
    ... ]
    >>> spl = SPL(data)
    >>> result = spl.search('city="NYC" | stats avg(age)')
    >>> print(result)
"""

__version__ = "0.1.0"

from .executor import SPL

__all__ = ["SPL"]

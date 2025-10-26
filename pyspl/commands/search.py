"""
Search and Where command implementations
"""

import re
from typing import List, Dict, Any
from ..utils import evaluate_condition, parse_multiple_conditions


def execute_search(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a search/where command to filter data.

    Supports:
        - field=value
        - field!=value
        - field>value, field>=value, field<value, field<=value
        - Multiple conditions (AND logic with space)
        - OR conditions (field=val1 OR field=val2)
        - Parentheses for grouping
        - Wildcards (*)

    Args:
        data: List of dictionaries to search
        args: Search condition string

    Returns:
        Filtered list of dictionaries
    """
    if not args or args == '*':
        return data

    # Check if there are OR conditions (case-insensitive)
    if re.search(r'\s+OR\s+', args, re.IGNORECASE):
        return execute_search_with_or(data, args)

    # Parse multiple conditions (space-separated = AND logic)
    conditions = parse_multiple_conditions(args)

    results = []
    for record in data:
        # All conditions must be true (AND logic)
        if all(evaluate_condition(record, cond) for cond in conditions):
            results.append(record)

    return results


def execute_search_with_or(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute search with OR logic.

    Handles queries like: (field1="a" OR field1="b" OR field2="c")
    """
    # Remove outer parentheses if present
    args = args.strip()
    if args.startswith('(') and args.endswith(')'):
        args = args[1:-1].strip()

    # Split by OR (case-insensitive)
    or_parts = re.split(r'\s+OR\s+', args, flags=re.IGNORECASE)

    results = []
    for record in data:
        # At least one condition must be true (OR logic)
        for condition in or_parts:
            condition = condition.strip()
            # Handle parentheses in individual conditions
            if condition.startswith('(') and condition.endswith(')'):
                condition = condition[1:-1].strip()

            if evaluate_condition(record, condition):
                results.append(record)
                break  # Don't add the same record multiple times

    return results

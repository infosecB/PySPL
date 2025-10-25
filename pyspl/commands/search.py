"""
Search and Where command implementations
"""

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
        - Wildcards (*)

    Args:
        data: List of dictionaries to search
        args: Search condition string

    Returns:
        Filtered list of dictionaries
    """
    if not args or args == '*':
        return data

    # Parse multiple conditions (space-separated = AND logic)
    conditions = parse_multiple_conditions(args)

    results = []
    for record in data:
        # All conditions must be true (AND logic)
        if all(evaluate_condition(record, cond) for cond in conditions):
            results.append(record)

    return results

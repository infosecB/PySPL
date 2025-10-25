"""
Utility functions for PySPL
"""

import re
from typing import Any, List, Dict


def safe_get(obj: Dict[str, Any], path: str, default=None) -> Any:
    """
    Safely get a nested value from a dictionary using dot notation.

    Args:
        obj: Dictionary to search
        path: Dot-separated path (e.g., "user.name")
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split('.')
    value = obj

    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, default)
        else:
            return default

    return value


def evaluate_condition(record: Dict[str, Any], condition: str) -> bool:
    """
    Evaluate a simple SPL condition against a record.

    Supports:
        - field=value (exact match)
        - field!=value (not equal)
        - field>value, field>=value, field<value, field<=value (comparisons)
        - field="quoted value" (quoted strings)
        - field=* (field exists)
        - * (match all)

    Args:
        record: Dictionary to evaluate
        condition: SPL condition string

    Returns:
        True if condition matches, False otherwise
    """
    condition = condition.strip()

    # Match all
    if condition == '*':
        return True

    # Parse comparison operators
    # Order matters - check >= before >, <= before <, != before =
    operators = [
        ('!=', lambda a, b: a != b),
        ('>=', lambda a, b: a >= b),
        ('<=', lambda a, b: a <= b),
        ('>', lambda a, b: a > b),
        ('<', lambda a, b: a < b),
        ('=', lambda a, b: a == b),
    ]

    for op_str, op_func in operators:
        if op_str in condition:
            parts = condition.split(op_str, 1)
            if len(parts) == 2:
                field = parts[0].strip()
                value_str = parts[1].strip()

                # Get field value from record
                field_value = safe_get(record, field)

                # Handle wildcard (field exists check)
                if value_str == '*':
                    if op_str == '=':
                        return field_value is not None
                    elif op_str == '!=':
                        return field_value is None

                # Parse expected value (handle quotes)
                expected_value = parse_value(value_str)

                if field_value is None:
                    return False

                # Type coercion for comparison
                try:
                    # Try to match types
                    if isinstance(expected_value, (int, float)) and not isinstance(field_value, (int, float)):
                        try:
                            field_value = float(field_value) if '.' in str(field_value) else int(field_value)
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(field_value, (int, float)) and not isinstance(expected_value, (int, float)):
                        try:
                            expected_value = float(expected_value) if '.' in str(expected_value) else int(expected_value)
                        except (ValueError, TypeError):
                            pass

                    return op_func(field_value, expected_value)
                except (TypeError, ValueError):
                    # If comparison fails, try string comparison
                    return op_func(str(field_value), str(expected_value))

    return False


def parse_value(value_str: str) -> Any:
    """
    Parse a value string into appropriate Python type.

    Args:
        value_str: String representation of value

    Returns:
        Parsed value (str, int, float, bool, or None)
    """
    value_str = value_str.strip()

    # Handle quoted strings
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # Handle boolean
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False

    # Handle null
    if value_str.lower() in ('null', 'none'):
        return None

    # Try to parse as number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass

    # Return as string
    return value_str


def parse_multiple_conditions(condition_str: str) -> List[str]:
    """
    Parse multiple AND/OR conditions.
    Currently supports simple AND logic (space-separated conditions).

    Args:
        condition_str: String with multiple conditions

    Returns:
        List of individual conditions
    """
    # For now, simple implementation - split by space
    # In future, could support AND, OR, NOT operators
    conditions = []
    current = []
    in_quotes = False
    quote_char = None

    i = 0
    while i < len(condition_str):
        char = condition_str[i]

        if char in ('"', "'") and (i == 0 or condition_str[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None

        if char == ' ' and not in_quotes:
            if current:
                conditions.append(''.join(current))
                current = []
            i += 1
            continue

        current.append(char)
        i += 1

    if current:
        conditions.append(''.join(current))

    return [c for c in conditions if c.strip()]

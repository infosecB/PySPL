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
        - field>other_field (field-to-field comparisons)
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

                # Check if value_str is a field reference (not quoted)
                # If it's not quoted and exists in record, treat as field reference
                is_field_reference = False
                expected_value = None

                if not (value_str.startswith('"') or value_str.startswith("'")):
                    # Check if this looks like a field name in the record
                    if value_str in record:
                        is_field_reference = True
                        expected_value = record.get(value_str)

                if not is_field_reference:
                    # Parse as literal value (handle quotes)
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

    Handles comparison operators (=, !=, <, >, <=, >=) as single conditions.

    Args:
        condition_str: String with multiple conditions

    Returns:
        List of individual conditions
    """
    # Check if this looks like a single comparison (has comparison operator)
    # If so, return as-is without splitting
    comparison_operators = ['!=', '>=', '<=', '>', '<', '=']

    # Count actual occurrences of operators (checking longer operators first to avoid double-counting)
    operator_count = 0
    temp_str = condition_str
    for op in comparison_operators:  # Already sorted by length (longest first)
        count = temp_str.count(op)
        operator_count += count
        # Remove these occurrences to avoid counting '=' in '>='
        temp_str = temp_str.replace(op, ' ' * len(op))

    # If there's only one comparison operator, treat as single condition
    if operator_count == 1:
        return [condition_str.strip()]

    # Otherwise, parse multiple conditions (space-separated with AND logic)
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
                # Check if current token contains a comparison operator
                token = ''.join(current)
                has_operator = any(op in token for op in comparison_operators)

                if has_operator:
                    # This is a complete condition
                    conditions.append(token)
                    current = []
                elif conditions and not any(op in conditions[-1] for op in comparison_operators):
                    # Append to previous token (multi-word condition)
                    conditions[-1] += ' ' + token
                    current = []
                else:
                    conditions.append(token)
                    current = []
            i += 1
            continue

        current.append(char)
        i += 1

    if current:
        token = ''.join(current)
        has_operator = any(op in token for op in comparison_operators)

        if has_operator or not conditions:
            conditions.append(token)
        else:
            # Append to last condition
            conditions[-1] += ' ' + token

    return [c for c in conditions if c.strip()]

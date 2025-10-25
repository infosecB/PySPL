"""
Eval command implementation for creating/modifying fields
"""

import re
from typing import List, Dict, Any


def execute_eval(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute an eval command to create or modify fields.

    Supports simple expressions:
        eval new_field = field1 + field2
        eval new_field = field1 * 2
        eval new_field = "constant"
        eval status_code = if(response_time > 1000, "slow", "fast")

    Args:
        data: List of dictionaries
        args: Eval expression

    Returns:
        List of dictionaries with new/modified fields
    """
    if not data or not args:
        return data

    # Parse: field_name = expression
    match = re.match(r'(\w+)\s*=\s*(.+)', args)
    if not match:
        return data

    field_name = match.group(1).strip()
    expression = match.group(2).strip()

    results = []
    for record in data:
        new_record = record.copy()

        try:
            # Evaluate the expression
            value = evaluate_expression(expression, record)
            new_record[field_name] = value
        except Exception:
            # If evaluation fails, skip or set to None
            new_record[field_name] = None

        results.append(new_record)

    return results


def evaluate_expression(expr: str, record: Dict[str, Any]) -> Any:
    """
    Evaluate a simple expression with field substitution.

    Supports:
        - Arithmetic: field1 + field2, field1 * 2, etc.
        - String concatenation: field1 . field2
        - Constants: "string", 123, 45.67
        - Simple if: if(condition, true_value, false_value)

    Args:
        expr: Expression string
        record: Dictionary with field values

    Returns:
        Evaluated result
    """
    expr = expr.strip()

    # Handle if() function
    if_match = re.match(r'if\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)', expr, re.IGNORECASE)
    if if_match:
        condition = if_match.group(1).strip()
        true_val = if_match.group(2).strip()
        false_val = if_match.group(3).strip()

        # Evaluate condition
        cond_result = evaluate_simple_condition(condition, record)

        if cond_result:
            return evaluate_simple_value(true_val, record)
        else:
            return evaluate_simple_value(false_val, record)

    # Handle quoted strings
    if (expr.startswith('"') and expr.endswith('"')) or \
       (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]

    # Handle numeric constants
    try:
        if '.' in expr:
            return float(expr)
        else:
            return int(expr)
    except ValueError:
        pass

    # Handle field references and simple arithmetic
    # Replace field names with their values
    safe_expr = expr

    # Find all field references (alphanumeric and underscores)
    fields_in_expr = re.findall(r'\b([a-zA-Z_]\w*)\b', expr)

    # Create a safe evaluation context
    eval_context = {}
    for field in fields_in_expr:
        if field in record:
            value = record[field]
            eval_context[field] = value

    # Replace string concatenation operator '.' with '+'
    safe_expr = safe_expr.replace(' . ', ' + ')

    try:
        # Use eval with restricted context (be careful!)
        # Only allow basic arithmetic and field names
        result = eval(safe_expr, {"__builtins__": {}}, eval_context)
        return result
    except Exception:
        # If eval fails, return the original expression
        return expr


def evaluate_simple_condition(condition: str, record: Dict[str, Any]) -> bool:
    """Evaluate a simple boolean condition"""

    # Support basic comparisons
    operators = [
        ('>=', lambda a, b: a >= b),
        ('<=', lambda a, b: a <= b),
        ('>', lambda a, b: a > b),
        ('<', lambda a, b: a < b),
        ('==', lambda a, b: a == b),
        ('!=', lambda a, b: a != b),
    ]

    for op_str, op_func in operators:
        if op_str in condition:
            parts = condition.split(op_str, 1)
            if len(parts) == 2:
                left = evaluate_simple_value(parts[0].strip(), record)
                right = evaluate_simple_value(parts[1].strip(), record)

                try:
                    return op_func(left, right)
                except (TypeError, ValueError):
                    return False

    return False


def evaluate_simple_value(value_str: str, record: Dict[str, Any]) -> Any:
    """Evaluate a simple value (constant or field reference)"""
    value_str = value_str.strip()

    # Handle quoted strings
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # Try numeric
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass

    # Field reference
    if value_str in record:
        return record[value_str]

    return value_str

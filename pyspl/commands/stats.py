"""
Stats command implementation for aggregations
"""

import re
import math
from typing import List, Dict, Any, Callable
from collections import defaultdict


def execute_stats(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a stats command for aggregations.

    Supports:
        - count, count(field)
        - sum(field), avg(field), min(field), max(field)
        - values(field), list(field)
        - dc(field) - distinct count
        - by field1, field2 - grouping

    Examples:
        stats count
        stats count by status
        stats avg(response_time) by endpoint
        stats count, avg(age) by city

    Args:
        data: List of dictionaries to aggregate
        args: Stats command arguments

    Returns:
        List of dictionaries with aggregated results
    """
    if not data:
        return []

    # Parse the stats command
    # Format: aggregation_func(field), ... by groupby_field1, groupby_field2

    # Split by 'by' keyword
    by_match = re.search(r'\s+by\s+', args, re.IGNORECASE)
    if by_match:
        agg_part = args[:by_match.start()].strip()
        by_part = args[by_match.end():].strip()
        group_by_fields = [f.strip() for f in by_part.split(',')]
    else:
        agg_part = args.strip()
        group_by_fields = []

    # Parse aggregation functions
    agg_funcs = parse_aggregations(agg_part)

    if not agg_funcs:
        return []

    # Group data
    if group_by_fields:
        groups = defaultdict(list)
        for record in data:
            # Create group key from group_by fields
            key_parts = []
            for field in group_by_fields:
                value = record.get(field, None)
                key_parts.append((field, value))
            key = tuple(key_parts)
            groups[key].append(record)

        # Compute aggregations for each group
        results = []
        for key, group_data in groups.items():
            result = {}
            # Add group by fields to result
            for field, value in key:
                result[field] = value

            # Compute aggregations
            for agg_name, agg_func, field_name in agg_funcs:
                result[agg_name] = agg_func(group_data, field_name)

            results.append(result)

        return results
    else:
        # No grouping - compute aggregations over all data
        result = {}
        for agg_name, agg_func, field_name in agg_funcs:
            result[agg_name] = agg_func(data, field_name)

        return [result]


def execute_eventstats(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute an eventstats command to add aggregation fields to events.

    Unlike stats, eventstats preserves all original events and adds
    aggregated values as new fields to each event.

    Supports same aggregations as stats:
        - count, count(field)
        - sum(field), avg(field), min(field), max(field)
        - values(field), list(field)
        - dc(field) - distinct count
        - by field1, field2 - grouping

    Examples:
        eventstats count
        eventstats avg(price) by category
        eventstats max(score) by team

    Args:
        data: List of dictionaries to process
        args: Eventstats command arguments

    Returns:
        List of dictionaries with aggregation fields added
    """
    if not data:
        return []

    # Parse the eventstats command (same format as stats)
    # Format: aggregation_func(field), ... by groupby_field1, groupby_field2

    # Split by 'by' keyword
    by_match = re.search(r'\s+by\s+', args, re.IGNORECASE)
    if by_match:
        agg_part = args[:by_match.start()].strip()
        by_part = args[by_match.end():].strip()
        group_by_fields = [f.strip() for f in by_part.split(',')]
    else:
        agg_part = args.strip()
        group_by_fields = []

    # Parse aggregation functions
    agg_funcs = parse_aggregations(agg_part)

    if not agg_funcs:
        return data

    # Compute aggregations
    if group_by_fields:
        # Group data and compute aggregations for each group
        groups = defaultdict(list)
        for record in data:
            # Create group key from group_by fields
            key_parts = []
            for field in group_by_fields:
                value = record.get(field, None)
                key_parts.append((field, value))
            key = tuple(key_parts)
            groups[key].append(record)

        # Compute aggregations for each group
        group_aggs = {}
        for key, group_data in groups.items():
            agg_values = {}
            for agg_name, agg_func, field_name in agg_funcs:
                agg_values[agg_name] = agg_func(group_data, field_name)
            group_aggs[key] = agg_values

        # Add aggregation fields to each event
        results = []
        for record in data:
            new_record = record.copy()

            # Find which group this record belongs to
            key_parts = []
            for field in group_by_fields:
                value = record.get(field, None)
                key_parts.append((field, value))
            key = tuple(key_parts)

            # Add aggregation fields
            if key in group_aggs:
                for agg_name, agg_value in group_aggs[key].items():
                    new_record[agg_name] = agg_value

            results.append(new_record)

        return results
    else:
        # No grouping - compute aggregations over all data and add to each event
        agg_values = {}
        for agg_name, agg_func, field_name in agg_funcs:
            agg_values[agg_name] = agg_func(data, field_name)

        # Add aggregation fields to each event
        results = []
        for record in data:
            new_record = record.copy()
            for agg_name, agg_value in agg_values.items():
                new_record[agg_name] = agg_value
            results.append(new_record)

        return results


def parse_aggregations(agg_str: str) -> List[tuple]:
    """
    Parse aggregation function strings.

    Supports both formats:
    - Space-separated: "count sum(price) as total dc(category) as categories"
    - Comma-separated (legacy): "count, sum(price), dc(category)"
    - With aliases: "sum(price) as total"

    Returns:
        List of tuples: (result_name, function, field_name)
    """
    agg_funcs = []

    # First check if there are commas (legacy format)
    if ',' in agg_str and ' as ' not in agg_str.lower():
        # Use old comma-based parsing for backward compatibility
        parts = split_by_comma(agg_str)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            result = _parse_single_aggregation(part)
            if result:
                agg_funcs.append(result)
        return agg_funcs

    # New space-separated format with optional "as" aliases
    # Tokenize the string, respecting parentheses
    tokens = _tokenize_aggregations(agg_str)

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Skip empty tokens
        if not token.strip():
            i += 1
            continue

        # Check if this looks like an aggregation function
        if '(' in token or token.lower() in ['count']:
            func_spec = token
            alias = None

            # Check for "as alias" after this token
            if i + 2 < len(tokens) and tokens[i + 1].lower() == 'as':
                alias = tokens[i + 2]
                i += 3  # Skip function, 'as', and alias
            else:
                i += 1

            result = _parse_single_aggregation(func_spec, alias)
            if result:
                agg_funcs.append(result)
        else:
            i += 1

    return agg_funcs


def _tokenize_aggregations(agg_str: str) -> List[str]:
    """
    Tokenize aggregation string into tokens, respecting parentheses.

    Example: "count sum(price) as total" -> ["count", "sum(price)", "as", "total"]
    """
    tokens = []
    current = []
    in_parens = 0

    for char in agg_str:
        if char == '(':
            in_parens += 1
            current.append(char)
        elif char == ')':
            in_parens -= 1
            current.append(char)
        elif char == ' ' and in_parens == 0:
            if current:
                tokens.append(''.join(current))
                current = []
        elif char == ',' and in_parens == 0:
            # Treat comma as space separator for mixed formats
            if current:
                tokens.append(''.join(current))
                current = []
        else:
            current.append(char)

    if current:
        tokens.append(''.join(current))

    return tokens


def _parse_single_aggregation(spec: str, alias: str = None) -> tuple:
    """
    Parse a single aggregation specification.

    Args:
        spec: Aggregation spec like "count", "sum(price)", "dc(category)"
        alias: Optional alias name

    Returns:
        Tuple of (result_name, function, field_name) or None
    """
    spec = spec.strip()
    if not spec:
        return None

    # Check for "as" within the spec itself (legacy comma-separated format)
    if ' as ' in spec.lower():
        as_match = re.search(r'\s+as\s+', spec, re.IGNORECASE)
        if as_match:
            func_part = spec[:as_match.start()].strip()
            alias = spec[as_match.end():].strip()
            spec = func_part

    # Match function(field) or function
    match = re.match(r'(\w+)\s*\(\s*([^)]*)\s*\)', spec)
    if match:
        func_name = match.group(1).lower()
        field_name = match.group(2).strip()

        agg_func = get_aggregation_function(func_name)
        if agg_func:
            # Use alias if provided, otherwise use default name
            if alias:
                result_name = alias
            else:
                result_name = f"{func_name}({field_name})" if field_name else func_name
            return (result_name, agg_func, field_name)
    else:
        # Simple function without parentheses (e.g., 'count')
        func_name = spec.lower()
        agg_func = get_aggregation_function(func_name)
        if agg_func:
            result_name = alias if alias else func_name
            return (result_name, agg_func, None)

    return None


def split_by_comma(s: str) -> List[str]:
    """Split string by comma, respecting parentheses"""
    parts = []
    current = []
    depth = 0

    for char in s:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(''.join(current))
            current = []
            continue

        current.append(char)

    if current:
        parts.append(''.join(current))

    return parts


def get_aggregation_function(func_name: str) -> Callable:
    """Get the aggregation function by name"""

    functions = {
        'count': agg_count,
        'sum': agg_sum,
        'avg': agg_avg,
        'mean': agg_avg,
        'min': agg_min,
        'max': agg_max,
        'stdev': agg_stdev,
        'stdevp': agg_stdev,  # Population stdev (same as stdev)
        'stdevs': agg_stdev_sample,  # Sample stdev
        'values': agg_values,
        'list': agg_list,
        'dc': agg_distinct_count,
        'distinct_count': agg_distinct_count,
    }

    return functions.get(func_name)


def agg_count(data: List[Dict[str, Any]], field: str = None) -> int:
    """Count records or non-null field values"""
    if field:
        return sum(1 for record in data if record.get(field) is not None)
    return len(data)


def agg_sum(data: List[Dict[str, Any]], field: str) -> float:
    """Sum of field values"""
    total = 0
    for record in data:
        value = record.get(field)
        if value is not None:
            try:
                total += float(value)
            except (ValueError, TypeError):
                pass
    return total


def agg_avg(data: List[Dict[str, Any]], field: str) -> float:
    """Average of field values"""
    values = []
    for record in data:
        value = record.get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass

    return sum(values) / len(values) if values else 0


def agg_min(data: List[Dict[str, Any]], field: str) -> Any:
    """Minimum field value"""
    values = []
    for record in data:
        value = record.get(field)
        if value is not None:
            values.append(value)

    return min(values) if values else None


def agg_max(data: List[Dict[str, Any]], field: str) -> Any:
    """Maximum field value"""
    values = []
    for record in data:
        value = record.get(field)
        if value is not None:
            values.append(value)

    return max(values) if values else None


def agg_values(data: List[Dict[str, Any]], field: str) -> List[Any]:
    """Distinct values of field"""
    values = set()
    for record in data:
        value = record.get(field)
        if value is not None:
            # Convert unhashable types to strings
            try:
                values.add(value)
            except TypeError:
                values.add(str(value))

    return sorted(list(values))


def agg_list(data: List[Dict[str, Any]], field: str) -> List[Any]:
    """All values of field (including duplicates)"""
    values = []
    for record in data:
        value = record.get(field)
        if value is not None:
            values.append(value)

    return values


def agg_distinct_count(data: List[Dict[str, Any]], field: str) -> int:
    """Count of distinct field values"""
    return len(agg_values(data, field))


def agg_stdev(data: List[Dict[str, Any]], field: str) -> float:
    """
    Standard deviation of field values (population).

    Uses the population standard deviation formula:
    sqrt(sum((x - mean)^2) / n)
    """
    values = []
    for record in data:
        value = record.get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass

    if len(values) == 0:
        return 0.0

    if len(values) == 1:
        return 0.0

    # Calculate mean
    mean = sum(values) / len(values)

    # Calculate variance
    variance = sum((x - mean) ** 2 for x in values) / len(values)

    # Return standard deviation
    return math.sqrt(variance)


def agg_stdev_sample(data: List[Dict[str, Any]], field: str) -> float:
    """
    Standard deviation of field values (sample).

    Uses the sample standard deviation formula:
    sqrt(sum((x - mean)^2) / (n-1))
    """
    values = []
    for record in data:
        value = record.get(field)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass

    if len(values) <= 1:
        return 0.0

    # Calculate mean
    mean = sum(values) / len(values)

    # Calculate sample variance
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)

    # Return standard deviation
    return math.sqrt(variance)

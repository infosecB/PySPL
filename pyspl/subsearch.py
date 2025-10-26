"""
Subsearch implementation for PySPL

Subsearches are queries enclosed in square brackets that execute first,
then their results are used to filter the main search.

Example:
    [search status="active" | fields user] | stats count by user
"""

import re
from typing import List, Dict, Any, Tuple


def extract_subsearches(query: str) -> Tuple[str, List[Tuple[str, int, int]]]:
    """
    Extract subsearches from a query.

    Subsearches are enclosed in square brackets [...]

    Args:
        query: SPL query string that may contain subsearches

    Returns:
        Tuple of (query, subsearches) where subsearches is a list of
        (subsearch_text, start_pos, end_pos) tuples
    """
    subsearches = []
    depth = 0
    start = -1
    i = 0

    while i < len(query):
        char = query[i]

        if char == '[':
            if depth == 0:
                start = i
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0 and start != -1:
                # Extract subsearch (without the brackets)
                subsearch_text = query[start + 1:i]
                subsearches.append((subsearch_text, start, i + 1))
                start = -1

        i += 1

    return query, subsearches


def format_subsearch_results(results: List[Dict[str, Any]], field_prefix: str = None) -> str:
    """
    Format subsearch results into a search condition.

    The formatting depends on the number of fields and values:
    - Single field, single value: field="value"
    - Single field, multiple values: (field="value1" OR field="value2" OR ...)
    - Multiple fields: generates AND conditions for each result

    Args:
        results: List of dictionaries from subsearch execution
        field_prefix: If provided, the field name that prefixes the subsearch (e.g., "user" in "user=[subsearch]")
                     Note: We always include the field name in the formatted output, the prefix is just for validation

    Returns:
        Formatted search condition string
    """
    if not results:
        # No results means nothing should match
        return "nonsearchfield=impossiblevalue"

    # Determine which fields to use
    if not results[0]:
        return "nonsearchfield=impossiblevalue"

    fields = list(results[0].keys())

    # Single field case
    if len(fields) == 1:
        field = fields[0]
        values = [r[field] for r in results if r.get(field) is not None]

        if not values:
            return "nonsearchfield=impossiblevalue"

        if len(values) == 1:
            # Single value - always include field name
            value = values[0]
            if isinstance(value, str):
                return f'{field}="{value}"'
            else:
                return f'{field}={value}'
        else:
            # Multiple values - use OR, always include field name
            conditions = []
            for value in values:
                if isinstance(value, str):
                    conditions.append(f'{field}="{value}"')
                else:
                    conditions.append(f'{field}={value}')
            return '(' + ' OR '.join(conditions) + ')'

    # Multiple fields case - each result becomes an AND condition, all ORed together
    result_conditions = []
    for result in results:
        field_conditions = []
        for field, value in result.items():
            if value is not None:
                if isinstance(value, str):
                    field_conditions.append(f'{field}="{value}"')
                else:
                    field_conditions.append(f'{field}={value}')

        if field_conditions:
            if len(field_conditions) == 1:
                result_conditions.append(field_conditions[0])
            else:
                result_conditions.append('(' + ' '.join(field_conditions) + ')')

    if not result_conditions:
        return "nonsearchfield=impossiblevalue"

    if len(result_conditions) == 1:
        return result_conditions[0]
    else:
        return '(' + ' OR '.join(result_conditions) + ')'


def execute_subsearch(subsearch_query: str, data: List[Dict[str, Any]], executor, field_prefix: str = None) -> str:
    """
    Execute a subsearch and format its results.

    Args:
        subsearch_query: The subsearch query to execute
        data: The data to search
        executor: SPL executor instance to run the query
        field_prefix: Optional field name that prefixes the subsearch

    Returns:
        Formatted search condition from subsearch results
    """
    # Execute the subsearch
    results = executor.search(subsearch_query)

    # Format the results into a search condition
    return format_subsearch_results(results, field_prefix)


def process_subsearches(query: str, data: List[Dict[str, Any]], executor) -> str:
    """
    Process all subsearches in a query, executing them and replacing them
    with their formatted results.

    Args:
        query: SPL query that may contain subsearches
        data: The data to search
        executor: SPL executor instance

    Returns:
        Query with subsearches replaced by their results
    """
    original_query, subsearches = extract_subsearches(query)

    if not subsearches:
        return query

    # Process subsearches from right to left to maintain positions
    modified_query = query
    for subsearch_text, start_pos, end_pos in reversed(subsearches):
        # Check if there's a field prefix before the subsearch (e.g., "user=[subsearch]")
        field_prefix = None
        actual_start = start_pos

        # Look backwards from start_pos to find field=
        before_subsearch = modified_query[:start_pos].rstrip()
        if before_subsearch and before_subsearch.endswith('='):
            # Found '=' right before subsearch, now find the field name
            # Look for the start of the field name (space, pipe, or start of string)
            i = len(before_subsearch) - 2  # Start before the '='
            while i >= 0 and modified_query[i] not in (' ', '|', '\t'):
                i -= 1
            field_prefix = before_subsearch[i+1:-1].strip()
            actual_start = i + 1  # Include the field name in replacement

        # Execute the subsearch with the field prefix (for validation/context)
        condition = execute_subsearch(subsearch_text, data, executor, field_prefix)

        # Replace the subsearch (and field prefix if present) with results
        # The formatted condition already includes field names, so we don't add the prefix back
        before = modified_query[:actual_start]
        after = modified_query[end_pos:]
        modified_query = before + condition + after

    return modified_query

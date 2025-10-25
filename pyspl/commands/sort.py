"""
Sort, Head, and Tail command implementations
"""

from typing import List, Dict, Any


def execute_sort(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a sort command to sort data by fields.

    Supports:
        sort field1  (ascending)
        sort -field1  (descending)
        sort field1, -field2  (multiple fields)

    Args:
        data: List of dictionaries
        args: Sort command arguments

    Returns:
        Sorted list of dictionaries
    """
    if not data or not args:
        return data

    # Parse sort fields
    sort_specs = []
    for field_spec in args.split(','):
        field_spec = field_spec.strip()
        if field_spec.startswith('-'):
            # Descending
            field_name = field_spec[1:].strip()
            reverse = True
        elif field_spec.startswith('+'):
            # Ascending (explicit)
            field_name = field_spec[1:].strip()
            reverse = False
        else:
            # Ascending (default)
            field_name = field_spec
            reverse = False

        sort_specs.append((field_name, reverse))

    if not sort_specs:
        return data

    # Sort data
    result = data.copy()

    # Sort by each field in reverse order (rightmost field first)
    for field_name, reverse in reversed(sort_specs):
        result.sort(
            key=lambda x: get_sort_key(x.get(field_name)),
            reverse=reverse
        )

    return result


def get_sort_key(value: Any) -> Any:
    """
    Get a sortable key from a value.
    Handles None and mixed types.
    """
    if value is None:
        # None values sort to the end
        return (1, 0)

    # Return tuple (type_priority, value) to handle mixed types
    if isinstance(value, bool):
        return (0, 0, int(value))
    elif isinstance(value, int):
        return (0, 1, value)
    elif isinstance(value, float):
        return (0, 2, value)
    elif isinstance(value, str):
        return (0, 3, value)
    else:
        # Other types - convert to string
        return (0, 4, str(value))


def execute_head(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a head command to get first N records.

    Supports:
        head (default 10)
        head 20

    Args:
        data: List of dictionaries
        args: Head command arguments

    Returns:
        First N records
    """
    if not data:
        return data

    # Parse limit
    limit = 10  # default
    if args:
        try:
            limit = int(args.strip())
        except ValueError:
            pass

    return data[:limit]


def execute_tail(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a tail command to get last N records.

    Supports:
        tail (default 10)
        tail 20

    Args:
        data: List of dictionaries
        args: Tail command arguments

    Returns:
        Last N records
    """
    if not data:
        return data

    # Parse limit
    limit = 10  # default
    if args:
        try:
            limit = int(args.strip())
        except ValueError:
            pass

    return data[-limit:]

"""
Fields, Rename, and Table command implementations
"""

import re
from typing import List, Dict, Any


def execute_fields(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a fields command to select or exclude fields.

    Supports:
        fields field1, field2, field3  (include only these fields)
        fields - field1, field2  (exclude these fields)

    Args:
        data: List of dictionaries
        args: Fields command arguments

    Returns:
        List of dictionaries with selected fields
    """
    if not data or not args:
        return data

    args = args.strip()

    # Check if excluding fields (starts with -)
    if args.startswith('-'):
        exclude_mode = True
        args = args[1:].strip()
    else:
        exclude_mode = False

    # Parse field names
    field_names = [f.strip() for f in args.split(',')]

    results = []
    for record in data:
        if exclude_mode:
            # Exclude specified fields
            new_record = {k: v for k, v in record.items() if k not in field_names}
        else:
            # Include only specified fields
            new_record = {k: record.get(k) for k in field_names if k in record}

        results.append(new_record)

    return results


def execute_rename(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a rename command to rename fields.

    Supports:
        rename old_name as new_name
        rename old1 as new1, old2 as new2

    Args:
        data: List of dictionaries
        args: Rename command arguments

    Returns:
        List of dictionaries with renamed fields
    """
    if not data or not args:
        return data

    # Parse rename mappings
    # Format: old_name as new_name, old_name2 as new_name2
    mappings = {}

    parts = args.split(',')
    for part in parts:
        part = part.strip()
        # Match "old as new" or "old AS new"
        match = re.match(r'(\S+)\s+as\s+(\S+)', part, re.IGNORECASE)
        if match:
            old_name = match.group(1).strip()
            new_name = match.group(2).strip()
            mappings[old_name] = new_name

    if not mappings:
        return data

    results = []
    for record in data:
        new_record = {}
        for key, value in record.items():
            # Use new name if mapping exists, otherwise keep old name
            new_key = mappings.get(key, key)
            new_record[new_key] = value
        results.append(new_record)

    return results


def execute_table(data: List[Dict[str, Any]], args: str) -> List[Dict[str, Any]]:
    """
    Execute a table command (similar to fields, but formats output).

    Args:
        data: List of dictionaries
        args: Table command arguments

    Returns:
        List of dictionaries with selected fields
    """
    # Table is essentially the same as fields for our purposes
    return execute_fields(data, args)

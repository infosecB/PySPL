"""
SPL Query Executor

Main class for executing SPL queries against Python dictionaries.
"""

from typing import List, Dict, Any, Union
from .parser import (
    SPLParser,
    SearchCommand,
    StatsCommand,
    EventstatsCommand,
    FieldsCommand,
    RenameCommand,
    EvalCommand,
    SortCommand,
    HeadCommand,
    TailCommand,
    TableCommand,
)
from .commands import (
    execute_search,
    execute_stats,
    execute_eventstats,
    execute_fields,
    execute_rename,
    execute_table,
    execute_eval,
    execute_sort,
    execute_head,
    execute_tail,
)


class SPL:
    """
    Main SPL executor class.

    Example:
        >>> data = [
        ...     {"name": "Alice", "age": 30, "city": "NYC"},
        ...     {"name": "Bob", "age": 25, "city": "LA"},
        ...     {"name": "Charlie", "age": 35, "city": "NYC"}
        ... ]
        >>> spl = SPL(data)
        >>> result = spl.search('city="NYC" | stats avg(age)')
        >>> print(result)
        [{'avg(age)': 32.5}]
    """

    def __init__(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]):
        """
        Initialize SPL executor with data.

        Args:
            data: List of dictionaries or a single dictionary
        """
        if isinstance(data, dict):
            self.data = [data]
        elif isinstance(data, list):
            self.data = data
        else:
            raise TypeError("Data must be a dictionary or list of dictionaries")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute an SPL query against the data.

        Args:
            query: SPL query string

        Returns:
            List of dictionaries with query results
        """
        # Parse the query
        parser = SPLParser(query)
        commands = parser.parse()

        # Execute commands in sequence
        result = self.data
        for command in commands:
            result = self._execute_command(result, command)

        return result

    def _execute_command(
        self,
        data: List[Dict[str, Any]],
        command
    ) -> List[Dict[str, Any]]:
        """
        Execute a single SPL command.

        Args:
            data: Current data pipeline state
            command: SPLCommand instance to execute

        Returns:
            Transformed data
        """
        if isinstance(command, SearchCommand):
            return execute_search(data, command.args)

        elif isinstance(command, StatsCommand):
            return execute_stats(data, command.args)

        elif isinstance(command, EventstatsCommand):
            return execute_eventstats(data, command.args)

        elif isinstance(command, FieldsCommand):
            return execute_fields(data, command.args)

        elif isinstance(command, RenameCommand):
            return execute_rename(data, command.args)

        elif isinstance(command, TableCommand):
            return execute_table(data, command.args)

        elif isinstance(command, EvalCommand):
            return execute_eval(data, command.args)

        elif isinstance(command, SortCommand):
            return execute_sort(data, command.args)

        elif isinstance(command, HeadCommand):
            return execute_head(data, command.args)

        elif isinstance(command, TailCommand):
            return execute_tail(data, command.args)

        else:
            # Unknown command, return data unchanged
            return data

    def __repr__(self):
        return f"SPL(records={len(self.data)})"

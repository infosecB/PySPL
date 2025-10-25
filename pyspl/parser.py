"""
SPL Query Parser

Parses SPL query strings into a sequence of command objects that can be executed.
"""

import re
from typing import List, Dict, Any, Optional


class SPLCommand:
    """Base class for SPL commands"""

    def __init__(self, args: str):
        self.args = args.strip()

    def __repr__(self):
        return f"{self.__class__.__name__}(args='{self.args}')"


class SearchCommand(SPLCommand):
    """Represents a search or where command"""
    pass


class StatsCommand(SPLCommand):
    """Represents a stats command"""
    pass


class FieldsCommand(SPLCommand):
    """Represents a fields command"""
    pass


class RenameCommand(SPLCommand):
    """Represents a rename command"""
    pass


class EvalCommand(SPLCommand):
    """Represents an eval command"""
    pass


class SortCommand(SPLCommand):
    """Represents a sort command"""
    pass


class HeadCommand(SPLCommand):
    """Represents a head command"""
    pass


class TailCommand(SPLCommand):
    """Represents a tail command"""
    pass


class TableCommand(SPLCommand):
    """Represents a table command"""
    pass


class SPLParser:
    """
    Parses SPL query strings into executable command objects.

    Supports pipe-separated commands like:
    'search status=200 | stats count by method | sort -count'
    """

    COMMAND_MAP = {
        'search': SearchCommand,
        'where': SearchCommand,
        'stats': StatsCommand,
        'fields': FieldsCommand,
        'rename': RenameCommand,
        'eval': EvalCommand,
        'sort': SortCommand,
        'head': HeadCommand,
        'tail': TailCommand,
        'table': TableCommand,
    }

    def __init__(self, query: str):
        self.query = query.strip()
        self.commands: List[SPLCommand] = []

    def parse(self) -> List[SPLCommand]:
        """
        Parse the SPL query into a list of command objects.

        Returns:
            List of SPLCommand objects representing the query pipeline
        """
        if not self.query:
            return []

        # Split by pipe, but be careful with pipes inside quotes or parentheses
        parts = self._split_by_pipe(self.query)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Extract command name
            match = re.match(r'^(\w+)\s*(.*)', part)
            if match:
                cmd_name = match.group(1).lower()
                cmd_args = match.group(2).strip()

                # If no explicit command, treat as search
                if cmd_name not in self.COMMAND_MAP:
                    cmd_class = SearchCommand
                    cmd_args = part
                else:
                    cmd_class = self.COMMAND_MAP[cmd_name]

                self.commands.append(cmd_class(cmd_args))
            else:
                # No command specified, treat as search
                self.commands.append(SearchCommand(part))

        # If first command is not a search, prepend an implicit "search *"
        if self.commands and not isinstance(self.commands[0], SearchCommand):
            self.commands.insert(0, SearchCommand('*'))

        return self.commands

    def _split_by_pipe(self, query: str) -> List[str]:
        """
        Split query by pipes, respecting quotes and parentheses.

        Args:
            query: The SPL query string

        Returns:
            List of command strings
        """
        parts = []
        current = []
        in_quotes = False
        in_parens = 0
        quote_char = None

        i = 0
        while i < len(query):
            char = query[i]

            # Handle quotes
            if char in ('"', "'") and (i == 0 or query[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None

            # Handle parentheses
            elif char == '(' and not in_quotes:
                in_parens += 1
            elif char == ')' and not in_quotes:
                in_parens -= 1

            # Handle pipe
            elif char == '|' and not in_quotes and in_parens == 0:
                parts.append(''.join(current))
                current = []
                i += 1
                continue

            current.append(char)
            i += 1

        if current:
            parts.append(''.join(current))

        return parts

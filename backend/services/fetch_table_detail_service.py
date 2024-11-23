import logging

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword

from backend.config.logging_config import configure_logging

# Configure logging
configure_logging()


class TableNameExtractor:
    def __init__(self):
        pass

    def extract_table_names(self, sql_content):
        """
        Extracts staging and source table names from SQL content using sqlparse.

        Parameters:
            sql_content (str): The SQL query content.

        Returns:
            dict: A dictionary with sets of staging and source table names.
        """
        parsed = sqlparse.parse(sql_content)
        staging_tables = set()
        source_tables = set()

        for statement in parsed:
            if statement.get_type() in ('SELECT', 'UPDATE', 'INSERT', 'DELETE'):
                # Extract staging and source tables from statement
                staging_tables.update(self._extract_staging_tables(statement.tokens))
                source_tables.update(self._extract_source_tables(statement.tokens))

        return {
            'staging_tables': staging_tables,
            'source_tables': source_tables
        }

    def _extract_staging_tables(self, tokens):
        """
        Helper function to extract staging table names from tokens.

        Parameters:
            tokens (list): List of tokens from a parsed SQL statement.

        Returns:
            set: A set of staging table names.
        """
        staging_tables = set()
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() in ('UPDATE', 'TRUNCATE', 'INSERT', 'REPLACE'):
                next_token = self._get_next_token(tokens, token)
                if isinstance(next_token, (IdentifierList, Identifier)):
                    staging_tables.update(self._extract_identifiers(next_token))
        return staging_tables

    def _extract_source_tables(self, tokens):
        """
        Helper function to extract source table names from tokens.

        Parameters:
            tokens (list): List of tokens from a parsed SQL statement.

        Returns:
            set: A set of source table names.
        """
        source_tables = set()
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() in ('FROM', 'JOIN', 'USING', 'MERGE'):
                next_token = self._get_next_token(tokens, token)
                if isinstance(next_token, (IdentifierList, Identifier)):
                    source_tables.update(self._extract_identifiers(next_token))
        return source_tables

    def _get_next_token(self, tokens, current_token):
        """
        Helper function to get the next non-whitespace token after a specified token.

        Parameters:
            tokens (list): List of tokens from a parsed SQL statement.
            current_token: The current token to find the next token from.

        Returns:
            The next token after the current token.
        """
        index = tokens.index(current_token)
        while index + 1 < len(tokens):
            index += 1
            next_token = tokens[index]
            if not next_token.is_whitespace:
                return next_token
        return None

    def _extract_identifiers(self, token):
        """
        Helper function to extract identifiers from a token.

        Parameters:
            token: The token to extract identifiers from.

        Returns:
            set: A set of identifiers (table names).
        """
        if isinstance(token, Identifier):
            return {token.get_real_name()}
        elif isinstance(token, IdentifierList):
            return {identifier.get_real_name() for identifier in token.get_identifiers() if
                    isinstance(identifier, Identifier)}
        return set()

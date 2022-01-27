from pathlib import Path
from typing import List

import pgdumplib
import sqlparse


class Dump:

    def __init__(self, dump_file_path: str):
        self.__dump = pgdumplib.load(Path(dump_file_path))

        self.__tables = []
        for entry in self.__dump.entries:
            if entry.desc == 'TABLE':
                self.__tables.append({
                    'name': entry.tag,
                    'namespace': entry.namespace,
                    'columns': Dump.__get_columns_info(entry.defn)
                })

    @staticmethod
    def __get_columns_info(table_create_statement: str):
        columns_info = []
        parse = sqlparse.parse(table_create_statement)
        for stmt in parse:
            # Get all the tokens except whitespaces
            tokens = [t for t in sqlparse.sql.TokenList(stmt.tokens) if t.ttype != sqlparse.tokens.Whitespace]
            is_create_stmt = False
            for i, token in enumerate(tokens):
                # Is it a create statements ?
                if token.match(sqlparse.tokens.DDL, 'CREATE'):
                    is_create_stmt = True
                    continue

                # If it was a create statement and the current token starts with "("
                if is_create_stmt and token.value.startswith("("):
                    # Get the table name by looking at the tokens in reverse order till you find
                    # a token with None type

                    # Now parse the columns
                    txt = token.value
                    columns = txt[1:txt.rfind(")")].replace("\n", "").split(",")
                    for column in columns:
                        c = ' '.join(column.split()).split()
                        c_name = c[0].replace('\"', "")
                        c_type = c[1]  # For condensed type information
                        # OR
                        # c_type = " ".join(c[1:]) # For detailed type information
                        columns_info.append({'name': c_name, 'data_type': c_type})

                    break

        return columns_info

    @property
    def database_name(self) -> str:
        return self.__dump.dbname

    @property
    def archive_timestamp(self) -> str:
        return self.__dump.timestamp

    @property
    def server_version(self) -> str:
        return self.__dump.server_version

    @property
    def dump_version(self) -> str:
        return self.__dump.dump_version

    def get_tables(self) -> List[dict]:
        return self.__tables.copy()

    def get_table_columns(self, table: str, namespace: str):
        pass

    def get_table_data(self, table: str, namespace: str):
        table_data = []
        for line in self.__dump.table_data(namespace, table):
            table_data.append(line)

        return table_data

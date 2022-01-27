from pathlib import Path
from typing import List

import pgdumplib


class Dump:

    def __init__(self, dump_file_path: str):
        self.__dump = pgdumplib.load(Path(dump_file_path))

        self.__tables = []
        for entry in self.__dump.entries:
            if entry.desc == 'TABLE':
                self.__tables.append({
                    'name': entry.tag,
                    'namespace': entry.namespace
                })

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

    def get_tables(self) -> List[str]:
        return self.__tables.copy()


# for line in dump.table_data('public', 'test_table_1'):
#     print(line)

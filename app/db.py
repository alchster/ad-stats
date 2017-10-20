import sqlite3
import ast
import logging

from .util import get_option_value


class DB:

    _tables = []
    DEFAULT_TYPES = {
        "*": "varchar"
    }

    __all_tables_query = "select table_name, name, fields from tables;"
    __add_table_template = """insert or replace into tables
        values ('%s', '%s', "%s");"""
    __count_table_template = """select count(*) from tables
        where table_name like '%s%%';"""
    __remove_tables_query = "delete from tables;"
    __select_all_active_urls_query = """select site, url, user, password
        from urls where active = 1 order by id;"""
    __select_all_table_template = "select * from %s;"
    __create_table_query_template = "create table if not exists %s (%s);"
    __insert_query_template = "insert or replace into %s values (%s);"
    __drop_table_query_template = "drop table %s;"
    __cleanup_query = "vacuum;"

    def __init__(self, filename, options={}):
        self.types = get_option_value(options, "types", self.DEFAULT_TYPES)
        self.drop_tables = get_option_value(options, "drop_tables", True)
        try:
            self.conn = sqlite3.connect(filename)
            self.cursor = self.conn.cursor()
        except Exception:
            self.conn = None
            logging.error("Database error")
            exit(1)

    def __del__(self):
        if self.conn is not None:
            if self.drop_tables:
                for table in self.tables():
                    self.cursor.execute(
                        self.__drop_table_query_template % table["table_name"])
                self.cursor.execute(self.__remove_tables_query)
                self.commit()
            self.cleanup()
            self.cursor.close()
            self.conn.close()

    def urls(self):
        cursor = self.conn.cursor()
        for (site, url, user, password) \
                in cursor.execute(self.__select_all_active_urls_query):
            yield {
                "site": site,
                "url": url,
                "user": user,
                "password": password
            }
        cursor.close()

    def data(self, table_name):
        query = self.__select_all_table_template % table_name
        for row in self.cursor.execute(query):
            yield row

    def insert(self, table, values):
        if values == []:
            return
        vals = []
        for value in values:
            vals.append("".join(("'", value, "'")))
        query = self.__insert_query_template % (table, ",".join(vals))
        self.cursor.execute(query)

    def create_table(self, name, header):
        (fields_list, fields) = self._fields_list(header)
        table_name = self._add_table(name, fields)
        query = self.__create_table_query_template % (table_name, fields_list)
        self.cursor.execute(query)
        return table_name

    def commit(self):
        self.conn.commit()

    def cleanup(self):
        self.cursor.execute(self.__cleanup_query)

    def tables(self):
        cursor = self.conn.cursor()
        for (table_name, name, fields_str) \
                in cursor.execute(self.__all_tables_query):
            fields = ast.literal_eval(fields_str)
            yield {
                "table_name": table_name,
                "name": name,
                "fields": fields
            }
        cursor.close()

    def _fields_list(self, header):
        fields = {}
        fields_list = []
        for field in header:
            fields[field] = self._get_type(field).partition(" ")[0]
            fields_list.append(" ".join((field, fields[field])))
        return (",".join(fields_list), fields)

    def _construct_table_name(self, name, number):
        return "".join((name, "_", str(number))) if number != 0 else name

    def _get_type(self, field):
        default = self.types["*"] if "*" in self.types else "varchar"
        try:
            return self.types[field]
        except KeyError:
            return default

    def _add_table(self, name, fields, in_db=True):
        table_prefix = DB._safe_name(name)
        num = self._next_number(table_prefix)
        table_name = self._construct_table_name(table_prefix, num)
        query = self.__add_table_template % (name, table_name, str(fields))
        self.cursor.execute(query)
        self.commit()
        return table_name

    def _next_number(self, table_prefix):
        self.cursor.execute(self.__count_table_template % table_prefix)
        (count,) = self.cursor.fetchone()
        return count

    @staticmethod
    def _safe_name(string):
        s = "".join(list(filter(str.isalnum, string)))
        return "".join(("_", s))

import sqlite3
import logging


class DB:

    tables = {}
    DEFAULT_TYPES = {
        "*": "varchar"
    }
    DEFAULT_DROP_TABLES = False

    __select_all_active_urls_query = """select site, url, user, password
        from urls where active = 1 order by id;"""
    __create_table_query_template = """create table if not exists %s (%s);"""
    __insert_query_template = """insert or replace into %s values (%s);"""
    __drop_table_query_template = """drop table %s;"""

    def __init__(self, filename, options={}):
        self.types = options["types"] if "types" in options \
            else self.DEFAULT_TYPES
        self.drop_tables = options["drop_tables"] if "drop_tables" in options \
            else self.DEFAULT_DROP_TABLES
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
                for table in self.tables.keys():
                    for num in range(1, self.tables[table]["count"] + 1):
                        table_name = "".join((table, "_", str(num)))
                        query = self.__drop_table_query_template % table_name
                        self.cursor.execute(query)
            self.cursor.close()
            self.conn.close()

    def get_urls(self):
        result = []
        for (site, url, user, password) \
                in self.cursor.execute(self.__select_all_active_urls_query):
            result.append({
                "site": site,
                "url": url,
                "user": user,
                "password": password
            })
        return result

    def insert(self, table, values):
        if values == []:
            return
        vals = []
        for value in values:
            vals.append("".join(("'", value, "'")))
        query = self.__insert_query_template % (table, ",".join(vals))
        self.cursor.execute(query)

    def commit(self):
        self.conn.commit()

    def create_table(self, name, header):
        table_name = DB._safe_name(name)
        (fields_list, fields) = self._fields_list(header)
        if table_name not in self.tables.keys():
            self.tables[table_name] = {
                "name": name,
                "count": 1,
                "fields": fields
            }
        else:
            self.tables[table_name]["count"] += 1

        table_name = "".join((table_name, "_",
                              str(self.tables[table_name]["count"])))
        query = self.__create_table_query_template % (table_name, fields_list)
        self.cursor.execute(query)
        return table_name

    def _fields_list(self, header):
        fields = {}
        fields_list = []
        for field in header:
            fields[field] = self._get_type(field)
            fields_list.append(" ".join((field, fields[field])))
        return (",".join(fields_list), fields)

    def _get_type(self, field):
        default = self.types["*"] if "*" in self.types else "varchar"
        try:
            return self.types[field]
        except KeyError:
            return default

    @staticmethod
    def _safe_name(string):
        s = "".join(list(filter(str.isalnum, string)))
        return "".join(("_", s))

import logging
import re
import xlrd
import sys

from .util import get_option_value


class Reader:

    def __init__(self, filename, config):
        self._configure(config)
        try:
            self.book = xlrd.open_workbook(filename)
            self.filename = filename
        except Exception as e:
            logging.error("Unable to open input file %s: %s"
                          % (filename, e))
            sys.exit(1)
        self.sheet = self.book.sheet_by_index(self.sheet_number)

    def __enter__(self):
        count = 0
        for index in range(self.sheet.nrows):
            if index >= self.skip_rows:
                values = self.sheet.row_values(index)
                if len(values) >= len(self.columns):
                    row = {}
                    for col in self.columns.keys():
                        v = values[self.columns[col]]
                        if isinstance(v, float):
                            v = int(v)
                        s = self.string(str(v))
                        if col == "name":
                            s = self.sheet_name(s)
                        row[col] = s
                    count += 1
                    yield row
        logging.info("Processed %d lines from %s" % (count, self.filename))

    def __exit__(self, type, message, traceback):
        if type is not None:
            logging.error("Reader: %s" % message)

    def _configure(self, config):
        self.sheet_number = get_option_value(config, "sheet_number", 0)
        self.skip_rows = get_option_value(config, "skip_rows", 1)
        self.columns = {
            "name": get_option_value(config, "name_column", 0),
            "url": get_option_value(config, "url_column", 1),
            "user": get_option_value(config, "username_column", 2),
            "pass": get_option_value(config, "password_column", 3)
        }
        str_re = get_option_value(config, "strings_match_re", r".*")
        self.string = Reader.string_filter(str_re)
        self.sheet_name = Reader.string_filter(r"[^\[\]:*?\/\\]")

    @staticmethod
    def string_filter(regexp):
        compiled_re = re.compile(regexp)

        def filter_func(char):
            return compiled_re.match(char) is not None

        def wrapper(string):
            return "".join(list(filter(filter_func, string)))

        return wrapper

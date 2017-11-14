import logging
import re
import sys
import xlrd


class Reader:
    def __init__(self, file_contents, config=None):
        self._configure(config)
        try:
            self.book = xlrd.open_workbook(file_contents=file_contents)
        except Exception as e:
            logging.error("Unable to read input: %s", e)
            sys.exit(1)
        self.sheet = self.book.sheet_by_index(self.sheet_number)

    def __enter__(self):
        count = 0
        for index in range(self.sheet.nrows):
            if index >= self.skip_rows:
                values = self.sheet.row_values(index)
                if len(values) >= len(self.columns):
                    row = {}
                    for col in self.columns:
                        val = values[self.columns[col]]
                        if isinstance(val, float):
                            val = int(val)
                        str_val = self.string(str(val))
                        if col == "name":
                            str_val = self.string(str_val)
                        row[col] = str_val
                    count += 1
                    yield row
        logging.info("Processed %d lines", count)

    def __exit__(self, type, message, traceback):
        if type is not None:
            logging.error("Reader: %s", message)

    def _configure(self, config):
        self.sheet_number = Reader.get_option_value(config, "sheet_number", 0)
        self.skip_rows = Reader.get_option_value(config, "skip_rows", 1)
        self.columns = {
            "name": Reader.get_option_value(config, "name_column", 0),
            "url": Reader.get_option_value(config, "url_column", 1),
            "username": Reader.get_option_value(config, "username_column", 2),
            "password": Reader.get_option_value(config, "password_column", 3)
        }
        str_re = Reader.get_option_value(config,
                                         "strings_match_re",
                                         r"[\w\/\.,:;%\\\$\^#!@&\*\+\-]")
        self.string = Reader.string_filter(str_re)
        self.sheet_name = Reader.string_filter(r"[^\[\]:*?\/\\]")

    @staticmethod
    def get_option_value(options, option_name, default):
        try:
            return options[option_name]
        except (KeyError, TypeError):
            return default
        except Exception as e:
            logging.error("Error occured while getting option '%s': %s",
                          option_name, e)
            return default

    @staticmethod
    def string_filter(regexp):
        compiled_re = re.compile(regexp)

        def filter_func(char):
            return compiled_re.match(char) is not None

        def wrapper(string):
            return "".join(list(filter(filter_func, string)))

        return wrapper

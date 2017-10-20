import logging
import xlsxwriter
import datetime

from .util import get_option_value


class Writer:

    formats = {}
    DEFAULT_WIDTHS = {
        "varchar": 20,
        "integer": 15,
        "*": 30
    }

    def __init__(self, filename, options={}):
        try:
            self.book = xlsxwriter.Workbook(filename)
        except Exception as e:
            logging.error("Unable to create file '%s'" % (filename))
            return
        self._create_formats(get_option_value(options, "formats", {}))
        self.widths = get_option_value(options, "widths", self.DEFAULT_WIDTHS)
        self.date_format = get_option_value(options, "date_format", "%d/%m/%Y")
        self.autosum = get_option_value(options, "autosum", True)
        self.sheet = None

    def __del__(self):
        if self.book is not None:
            self.book.close()
            pass

    def write_sheet(self, name, header, data_iterator):
        self.sheet = self._create_sheet(name, header)
        for row in data_iterator:
            self._write_line(self.sheet, row)
        self._add_footer(self.sheet, self.row + 1)

    def _create_sheet(self, name, header):
        sheet = self.book.add_worksheet(name)
        self.columns = {}
        self.row = 0
        col = 0

        for field in header.keys():
            fmt = header[field]
            if field.lower() == "date":
                fmt = "date"
            self._add_column(sheet, col, fmt)
            sheet.write(self.row, col, field,
                        get_option_value(self.formats, "header", None))
            col += 1

        return sheet

    def _write_line(self, sheet, data):
        self.row += 1
        col = 0
        for value in data:
            column_info = self.columns[col]
            if column_info[0] == "date":
                value = datetime.datetime.strptime(value, self.date_format)
            sheet.write(self.row, col, value, column_info[1])
            col += 1

    def _add_footer(self, sheet, row_number):
        if self.autosum:
            for col, (fmt, _) in self.columns.items():
                if fmt == "integer":
                    val = "=SUM(%(letter)s%(first)d:%(letter)s%(last)d)" %\
                            {
                                "letter": chr(ord("A") + col),
                                "first": 2,
                                "last": row_number
                            }
                elif fmt == "date":
                    val = "Total"
                else:
                    val = ""
                f = get_option_value(self.formats, "footer", None)
                sheet.write(row_number, col, val, f)
            

    def _get_width(self, data_type):
        try:
            width = self.widths[data_type]
        except KeyError:
            width = get_option_value(self.widths, "*", 0)
        return width

    def _create_formats(self, formats):
        for fmt in formats.keys():
            self.formats[fmt] = self.book.add_format(formats[fmt])

    def _add_column(self, sheet, number, field_type):
        self.columns[number] = (
                field_type,
                get_option_value(self.formats, field_type, None))
        sheet.set_column(number, number, self._get_width(field_type))

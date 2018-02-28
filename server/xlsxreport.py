import logging
import xlsxwriter
import sys
from io import BytesIO


class Writer:

    sheetname_re = r"\w\.:"
    MAX_SAME_NAMES = 50
    FORMATS_DESC = {
        "header": {
            "bold": True,
            "align": "center",
            "bg_color": "gray",
            "top": True,
            "bottom": True,
            "left": True,
            "right": True,
        },
        "date": {
            "num_format": "dd.mm.yyyy",
            "bg_color": "#f0f0f0",
            "left": True,
            "right": True
        },
        "integer": {
            "left": True,
            "right": True,
            "num_format": "#,##0"
        },
        "percent": {
            "color": "gray",
            "num_format": "0.00%"
        },
        "footer": {
            "bold": True,
            "bg_color": "#f0fff0",
            "top": True,
            "bottom": True,
            "left": True,
            "right": True,
            "num_format": "#,##0"
        },
        "error": {
            "bold": True,
            "color": "red",
            "bg_color": "black"
        }
    }
    widths = {
        "integer": 12,
        "date": 10,
        "varchar": 15,
        "*": 15
    }
    types = {
        "date": "date",
        "*": "integer"
    }
    date_format = "%Y-%m-%d"
    autosum = True
    formats = {}

    def __init__(self):
        self.buffer = BytesIO()
        try:
            logging.debug("Creating XLSX report")
            self.book = xlsxwriter.Workbook(self.buffer, {"in_memory": True})
        except Exception as e:
            logging.error("Unable to create XLSX report : %s", e)
            sys.exit(3)
        for fmt, desc in self.FORMATS_DESC.items():
            self.formats[fmt] = self.book.add_format(desc)
        self.columns = {}

    def __del__(self):
        if self.book is not None:
            self.book.close()

    def write_sheet(self, name, header, data):
        (sheet, error) = self._create_sheet(name, header)
        if error:
            self._write_error(sheet, header)
            return
        row = 1

        for line in data:
            self._write_line(sheet, row, line)
            row += 1

        self._add_footer(sheet, row)

    def bytes(self):
        if self.book:
            self.book.close()
        self.buffer.seek(0)
        return self.buffer

    def _create_sheet(self, name, fields):
        sheet = self._add_sheet_to_workbook(name)
        self.columns = {}
        col = 0

        if len(fields) == 1:    # error message
            return (sheet, True)

        for field in fields:
            fmt = self._get_format(field)
            self._add_column(sheet, col, field, fmt)
            sheet.write(0, col, field, self.formats["header"])
            col += 1

        return (sheet, False)

    def _get_format(self, field):
        fmt = self.types["*"]
        for string in self.types:
            if field.lower().find(string) != -1:
                fmt = self.types[string]
                break
        return fmt

    def _add_sheet_to_workbook(self, name):
        sheet = None
        sheet_name = name
        take = 1
        while sheet is None:
            logging.debug("Adding sheet '%s'", sheet_name)
            try:
                sheet = self.book.add_worksheet(sheet_name)
            except Exception as e:
                if take > self.MAX_SAME_NAMES:
                    logging.error("Limit of same names exceeded. Surrender")
                    sys.exit(2)
                logging.warning(
                    "Sheet '%s' is already present. Using new name",
                    sheet_name)
                take += 1
                sheet_name = "-".join((name, str(take)))
        return sheet

    def _write_line(self, sheet, row, data_row):
        starts = 0
        shows = 0
        cols = 0
        for col, value in data_row.items():
            column_info = self.columns[col]
            if col == "starts":
                starts += value
            elif col == "shows":
                shows = value
            sheet.write(row,
                        column_info["column"],
                        value,
                        column_info["format"])
            cols += 1
        try:
            percent = shows / starts
        except ZeroDivisionError:
            percent = 0
        sheet.write(row, cols, percent, self.formats["percent"])

    def _write_error(self, sheet, errmsg):
        logging.debug("Writing error message: %s" % errmsg)
        sheet.set_column(0, 0, 150)
        sheet.write(0, 0, errmsg, self.formats["error"])

    def _add_footer(self, sheet, row_number):
        if self.autosum:
            for col, info in self.columns.items():
                if info["type"] == "integer":
                    if row_number > 2:
                        val = "=SUM(%(letter)s%(first)d:%(letter)s%(last)d)" %\
                                {
                                    "letter": chr(ord("A") + info["column"]),
                                    "first": 2,
                                    "last": row_number
                                }
                    else:
                        val = 0
                elif col == "date":
                    val = "Total"
                else:
                    val = ""
                print(col, val)
                fmt = self.formats["footer"] or None
                sheet.write(row_number, info["column"], val, fmt)
                sheet.autofilter(0, 0, row_number - 1, 4)

    def _get_width(self, data_type):
        try:
            width = self.widths[data_type]
        except KeyError:
            width = self.widths["*"]
        return width

    def _add_column(self, sheet, number, name, field_type):
        self.columns[name] = {
            "column": number,
            "type": field_type,
            "format": self.formats[field_type] or None
        }
        sheet.set_column(number, number, self._get_width(field_type))

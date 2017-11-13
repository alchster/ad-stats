import logging
import xlsxwriter
import datetime
import sys

from .util import get_option_value


class Writer:

    formats = {}
    DEFAULT_WIDTHS = {
        "varchar": 20,
        "integer": 15,
        "*": 30
    }
    DEFAULT_TYPES = {
        "date": "date",
        "*": "integer"
    }
    MAX_SAME_NAMES = 50

    def __init__(self, filename, options={}):
        try:
            logging.debug("Creating %s" % filename)
            self.book = xlsxwriter.Workbook(filename)
        except Exception as e:
            logging.error("Unable to create file '%s' : %s" % (filename, e))
            sys.exit(3)
        self._create_formats(get_option_value(options, "formats", {}))
        self.types = get_option_value(options, "columns", self.DEFAULT_TYPES)
        self.widths = get_option_value(options, "widths", self.DEFAULT_WIDTHS)
        self.date_format = get_option_value(options, "date_format", "%d/%m/%Y")
        self.autosum = get_option_value(options, "autosum", True)
        self.last_days = get_option_value(options, "last_days", 0)
        msg = "All" if self.last_days <= 0 else "Last %d" % self.last_days
        logging.info("%s days will be written", msg)
        # TODO: add first sheet as summary

    def __del__(self):
        if self.book is not None:
            self.book.close()

    def write_sheet(self, name, data_iterator):
        header = next(data_iterator)
        logging.debug(header)
        (sheet, error) = self._create_sheet(name, header)
        if error:
            self._write_error(sheet, header)
            return

        self.after = datetime.date.min if self.last_days <= 0 \
            else datetime.date.today() - \
            datetime.timedelta(days=self.last_days)

        for row in data_iterator:
            logging.debug(row)
            self._write_line(sheet, row)
        self._add_footer(sheet, self.row + 1)

    def _create_sheet(self, name, header):
        sheet = self._add_sheet_to_workbook(name)
        self.columns = {}
        self.row = 0
        col = 0

        fields = header.split(",")
        if len(fields) == 1:    # error message
            return (sheet, True)

        for field in fields:
            fmt = self._get_format(field)
            self._add_column(sheet, col, fmt)
            sheet.write(self.row, col, field,
                        get_option_value(self.formats, "header", None))
            col += 1

        return (sheet, False)

    def _get_format(self, field):
        fmt = get_option_value(self.types, "*", "integer")
        for string in self.types.keys():
            if field.lower().find(string) != -1:
                fmt = self.types[string]
                break
        return fmt

    def _add_sheet_to_workbook(self, name):
        sheet = None
        sheet_name = name
        take = 1
        while sheet is None:
            logging.debug("Adding sheet '%s'" % sheet_name)
            try:
                sheet = self.book.add_worksheet(sheet_name)
            except Exception as e:
                if take > self.MAX_SAME_NAMES:
                    logging.error("Limit of same names exceeded. Surrender")
                    sys.exit(2)
                logging.warning(
                        "Sheet '%s' is already present. Using new name"
                        % sheet_name)
                take += 1
                sheet_name = "-".join((name, str(take)))
        return sheet

    def _write_line(self, sheet, data):
        col = 0
        starts = 0
        shows = 0
        for value in data.split(","):
            column_info = self.columns[col]
            if column_info[0] == "date":
                value = datetime.datetime.strptime(value, self.date_format)
                value = value.date()
                if value < self.after:
                    return
                self.row += 1
            elif column_info[0] == "integer":
                value = int(value)
            if col == 1:
                starts = value
            elif col == 2:
                shows = value
            sheet.write(self.row, col, value, column_info[1])
            col += 1
        try:
            percent = shows/starts
        except ZeroDivisionError:
            percent = 0
        sheet.write(self.row, col, percent, self.formats["percent"])

    def _write_error(self, sheet, errmsg):
        logging.debug("Writing error message: %s" % errmsg)
        sheet.set_column(0, 0, 150)
        sheet.write(0, 0, errmsg, self.formats["error"])

    def _add_footer(self, sheet, row_number):
        if self.autosum:
            for col, (fmt, _) in self.columns.items():
                if fmt == "integer":
                    if row_number > 2:
                        val = "=SUM(%(letter)s%(first)d:%(letter)s%(last)d)" %\
                                {
                                    "letter": chr(ord("A") + col),
                                    "first": 2,
                                    "last": row_number
                                }
                    else:
                        val = 0
                elif fmt == "date":
                    val = "Total"
                else:
                    val = ""
                f = get_option_value(self.formats, "footer", None)
                sheet.write(row_number, col, val, f)
                sheet.autofilter(0, 0, row_number - 1, 4)

    def _get_width(self, data_type):
        try:
            width = self.widths[data_type]
        except KeyError:
            width = get_option_value(self.widths, "*", 0)
        return width

    def _create_formats(self, formats):
        has_error = False
        for fmt in formats.keys():
            if fmt == "error":
                has_error = True
            self.formats[fmt] = self.book.add_format(formats[fmt])
        if not has_error:
            self.formats["error"] = self.book.add_format({
                "bold": True,
                "color": "red",
                "bg_color": "black"
            })

    def _add_column(self, sheet, number, field_type):
        self.columns[number] = (
                field_type,
                get_option_value(self.formats, field_type, None))
        sheet.set_column(number, number, self._get_width(field_type))

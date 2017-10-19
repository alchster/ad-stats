import logging
import xlsxwriter


class Writer:

    class LineType:
        DEFAULT = 0
        HEADER = 1

    formats = {
        "bold": True,
    }

    def __init__(self, filename):
        try:
            self.book = xlsxwriter.Workbook(filename)
        except Exception as e:
            logging.error("Unable to create file '%s'" % (filename))
            return
        self.book.add_format({"bold": True})
        self.sheets = {}

    def write_line(data, line_type=LineType.DEFAULT):
        pass

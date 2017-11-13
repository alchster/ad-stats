import os
import datetime
import logging

from .reader import Reader
from .fetcher import Fetcher
from .writer import Writer
from .util import get_option_value


class Application:

    def __init__(self, config):
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.INFO)
        self._configure(config)

    def run(self):
        writer = Writer(self.output_file, self.writer_options)
        with Reader(self.input_file, self.reader_options) as reader:
            for url_info in reader:
                with Fetcher(url_info) as fetcher:
                    writer.write_sheet(url_info["name"], fetcher)

    def _configure(self, config):
        self.input_file = config["input_file"]
        self.reader_options = get_option_value(config, "reader_options", {})

        output_dir = get_option_value(config, "output_directory", "out")
        filename_fmt = get_option_value(config, "filename_format", "r.xlsx")
        self.output_file = Application._output_file(output_dir, filename_fmt)
        self.writer_options = Application._writer_options(config)

    @staticmethod
    def _output_file(output_dir, fmt):
        return os.path.join(output_dir, datetime.datetime.now().strftime(fmt))

    @staticmethod
    def _writer_options(config):
        return {
            "last_days": get_option_value(config, "last_days", 0),
            "formats": get_option_value(config, "xlsx_formats", {}),
            "date_format": get_option_value(config,
                                            "data_date_format",
                                            "%m/%d/%Y"),
            "widths": get_option_value(config, "xlsx_width", {}),
            "autosum": get_option_value(config,
                                        "autosum_integer_columns",
                                        True)
        }

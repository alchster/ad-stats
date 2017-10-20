import os
import datetime
import logging

from .db import DB
from .fetcher import Fetcher
from .parser import Parser
from .writer import Writer
from .util import get_option_value


class Application:

    def __init__(self, config):
        self.download_data = get_option_value(config, "download_data", False)
        self.output_dir = get_option_value(config, "output_directory", "out")
        self.filename_fmt = get_option_value(config, "filename_fmt", "r.xlsx")
        db_path = get_option_value(config, "database_path", "db/urls.db")
        db_types = get_option_value(config, "database_types", {})
        db_options = { "types": db_types }

        self.db = DB(db_path, db_options)
        self.parser = Parser()
        self.writer = Writer(self._generate_output_filename())

    def run(self):
        if self.download_data:
            logging.info("Downloading data")
            for url in self.db.urls():
                self._process_url(url)
        for table in self.db.tables():
            pass

    def _generate_output_filename(self):
        now = datetime.datetime.now()
        filename = now.strftime(self.filename_fmt)
        return os.path.join(self.output_dir, filename)

    def _process_url(self, url):
        first_line = True
        table = None
        for line in Fetcher.get(url["url"], url["user"], url["password"]):
            parsed = self.parser.parse_line(line)
            if first_line:
                table = self.db.create_table(url["site"], parsed)
                first_line = False
                continue
            self.db.insert(table, parsed)
        self.db.commit()

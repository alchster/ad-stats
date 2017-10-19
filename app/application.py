import os
import datetime
from .db import DB
from .fetcher import Fetcher
from .parser import Parser
from .writer import Writer


class Application:

    def __init__(self, config):
        self.output_dir = config["output_directory"]
        self.db = DB(config["database_path"], config["database_options"])
        self.filename_fmt = config["filename_format"]
        self.parser = Parser()
        self.writer = Writer(self._generate_output_filename())

    def run(self):
        for url in self.db.get_urls():
            self._process_url(url)

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

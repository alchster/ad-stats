import csv
import logging
from codecs import iterdecode

import requests
from requests.auth import HTTPBasicAuth


class Fetcher:

    def __init__(self, url, username=None, password=None, row_handler=None):
        logging.debug("Fetching %s", url)
        self.url = url
        self.auth = None
        if username is not None and username != "":
            self.auth = HTTPBasicAuth(username, password)
        self.reader = None
        self.handler = row_handler

    def __iter__(self):
        with requests.get(self.url, auth=self.auth, stream=False) as resp:
            if resp.status_code != 200:
                resp.raise_for_status()
            self.reader = csv.reader(iterdecode(resp.iter_lines(), "utf-8"),
                                     delimiter=",")
            # skip first row
            next(self.reader)
            return self

    def __next__(self):
        row = next(self.reader)
        if self.handler is not None:
            row = self.handler(row)
        return row

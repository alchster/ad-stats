import urllib.request
import base64
import logging


class Fetcher:

    @staticmethod
    def _prepare(url, username, password):
        request = urllib.request.Request(url)
        if username is not None and username != "":
            user_password_pair = ":".join((username, password)).encode("ascii")
            auth_string = base64.b64encode(user_password_pair).decode("ascii")
            request.add_header("Authorization", "Basic %s" % (auth_string))
        return request

    @staticmethod
    def get(url, username=None, password=None):
        request = Fetcher._prepare(url, username, password)
        try:
            with urllib.request.urlopen(request) as resp:
                for line in resp:
                    yield line.decode("utf-8").rstrip()
        except IOError as e:
            data = None
            logging.error("Unable to fecth URL %s (%s)" % (url, e.msg))

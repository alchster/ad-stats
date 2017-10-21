import urllib.request
import base64
import logging


class Fetcher:

    def __init__(self, url_info):
        logging.debug("Fetching %s" % url_info)
        self.url_info = url_info

    def __enter__(self):
        try:
            with urllib.request.urlopen(Fetcher._request(self.url_info))\
                    as resp:
                for line in resp:
                    yield line.decode("utf-8").rstrip()
        except Exception as e:
            templ = "Unable to fetch %(url)s "\
                "(name: '%(name)s' "\
                "username: '%(user)s' password: '%(pass)s'): %%s"\
                % self.url_info
            errmsg = templ % e
            logging.error(errmsg)
            yield errmsg

    def __exit__(self, type, message, traceback):
        if type is not None:
            logging.error("Fetcher error: %s" % message)

    @staticmethod
    def _request(url_info):
        url = url_info["url"]
        username = url_info["user"]
        password = url_info["pass"]

        request = urllib.request.Request(url)
        if username is not None and username != "":
            user_password_pair = ":".join((username, password)).encode("ascii")
            auth_string = base64.b64encode(user_password_pair).decode("ascii")
            request.add_header("Authorization", "Basic %s" % (auth_string))
        return request

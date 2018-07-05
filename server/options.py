import logging
from configparser import NoOptionError, NoSectionError


class Options(object):

    options = {
        "global": {
            "logfile": ""
        },
        "server": {
            "listen_address": "127.0.0.1",
            "listen_port": 8000,
            "secret_key": None
        },
        "database": {
            "engine": "sqlite",
            "name": "",
            "username": "",
            "password": "",
            "host": "",
            "port": 0
        },
    }

    non_mandatory_options = {
        "oauth": {
            "google_client_id": None,
            "google_secret_key": None,
            "callback_url": None,
            "hosted_domain": None
        },
    }

    def __init__(self, config):
        logging.info("Reading configuration file")
        for section in self.non_mandatory_options:
            if section in config.sections():
                logging.debug("Non-mandatory section '%s' found. Using it...",
                              section)
                self.options[section] = self.non_mandatory_options[section]
        for section in self.options:
            for param in self.options[section]:
                try:
                    if isinstance(self.options[section][param], bool):
                        self.options[section][param] = config.getboolean(
                            section, param)
                    elif isinstance(self.options[section][param], int):
                        self.options[section][param] = config.getint(
                            section, param)
                    else:
                        self.options[section][param] = config.get(
                            section, param)
                except NoOptionError:
                    pass
                except NoSectionError:
                    logging.warning(
                        "No such section '%s' in configuration file", section)
                logging.debug("... %s.%s (%s) = %s", section, param,
                              type(self.options[section][param]).__name__,
                              str(self.options[section][param]))
        logging.debug("Options loaded")

    def db_uri(self):
        uri_template = "%(engine)s://%(username)s:%(password)s" \
                        "@%(host)s:%(port)d/%(name)s"
        if self.options["database"]["engine"] == "sqlite":
            uri_template = "sqlite://%(name)s"
        return uri_template % self.options["database"]

    def has_oauth(self):
        result = True
        if "oauth" in self.options:
            for key, value in self.options["oauth"].items():
                if key != "hosted_domain" and (value is None or value == ""):
                    result = False
                    break
        else:
            result = False
        return result

    def secret_key(self):
        return self.options["server"]["secret_key"]

    def server_options(self):
        return self.options["server"]

    def oauth_options(self):
        return self.options["oauth"]

    def __repr__(self):
        return self.options.__repr__()

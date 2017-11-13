import logging
from configparser import NoOptionError, NoSectionError


class Options(object):

    options = {
        "global": {
            "logfile": ""
        },
        "server": {
            "listen_address": "127.0.0.1",
            "listen_port": 8000
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

    def __init__(self, config):
        logging.info("Reading configuration file")
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
                logging.debug("... %s.%s = %s", section, param,
                              str(self.options[section][param]))
        logging.debug("Options loaded")

    def db_uri(self):
        uri_template = "%(engine)s://%(username)s:%(password)s" \
                        "@%(host)s:%(port)d/%(name)s"
        if self.options["database"]["engine"] == "sqlite":
            uri_template = "sqlite://%(name)s"
        return uri_template % self.options["database"]

    def server_options(self):
        return self.options["server"]

    def __repr__(self):
        return self.options.__repr__()

#!env/bin/python

import logging
import os
import sys

import argparse
import configparser

from werkzeug.contrib.fixers import ProxyFix, HeaderRewriterFix

from server.options import Options
from server import create_server


def get_logger(quiet, verbose):
    lvl = logging.FATAL if quiet \
            else logging.DEBUG if verbose \
            else logging.INFO
    return logging.basicConfig(
        level=lvl,
        format="%(asctime)-25s%(levelname)-10s%(message)s"
    )


def get_command_line_options():
    parser = argparse.ArgumentParser(description="Ad statistics server")
    parser.add_argument("-c", "--config",
                        metavar="CONFIG_FILE",
                        dest="config",
                        type=str,
                        default="options.ini",
                        help="Use specified configuration file")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose",
                           action="store_true",
                           default=False,
                           help="Be more talkative")
    verbosity.add_argument("-q", "--quiet",
                           action="store_true",
                           default=False,
                           help="Suppress any output")
    parser.add_argument("-d", "--daemonize",
                        action="store_true",
                        default=False,
                        help="Start as daemon")
    parser.add_argument("-g", "--gevent",
                        action="store_true",
                        default=False,
                        help="Start through gevent WSGIServer")
    return parser.parse_args()


def read_config(filename):
    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(filename):
        logging.fatal("No such file (%s)", filename)
        sys.exit(-1)
    config = configparser.ConfigParser()
    config.read(filename)
    return Options(config)


def make_server(config, debug=False):
    app = create_server(config, debug)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.wsgi_app = HeaderRewriterFix(app.wsgi_app, remove_headers=['Date'],
                                     add_headers=[('X-Powered-By', 'WSGI')])
    return app


if __name__ == "__main__":
    options = get_command_line_options()
    get_logger(options.quiet, options.verbose)
    config = read_config(options.config)
    opts = config.server_options()
    app = make_server(config, debug=options.verbose)
    app.run(opts["listen_address"],
            port=opts["listen_port"],
            debug=options.verbose)


def make_wsgi_app():
    get_logger(False, False)
    config = read_config('options.ini')
    app = make_server(config, debug=False)
    return app

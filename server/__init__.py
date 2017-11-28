try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ModuleNotFoundError:
    pass

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .views import bp
from .models.base import Base
from .oauth import add_oauth


def register_filters(app):
    from .util import funcs
    for func in list(filter(lambda x: x[:2] != "__", dir(funcs))):
        app.jinja_env.filters[func] = funcs.__dict__[func]


def create_server(options, debug=False):
    app = Flask("Ad-stats server")
    app.config['SQLALCHEMY_DATABASE_URI'] = options.db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = debug
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.secret_key = options.secret_key()
    register_filters(app)
    app.db = SQLAlchemy(app)
    Base.metadata.create_all(app.db.engine)
    app.register_blueprint(bp)
    app.default_url = "ad-stats.main"
    if options.has_oauth():
        add_oauth(app, options)

    return app

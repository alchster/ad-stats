from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .views import bp


def create_server(options):
    app = Flask("server")
    app.config['SQLALCHEMY_DATABASE_URI'] = options.db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.db = SQLAlchemy(app)
    app.register_blueprint(bp)

    return app

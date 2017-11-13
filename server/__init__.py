from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .views import bp
from .models.base import Base


def create_server(options, debug=False):
    app = Flask("server")
    print(debug)
    app.config['SQLALCHEMY_DATABASE_URI'] = options.db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = debug
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.db = SQLAlchemy(app)
    Base.metadata.create_all(app.db.engine)
    app.register_blueprint(bp)

    return app

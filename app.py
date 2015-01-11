from flask import Flask
from flask.ext.babel import Babel
from database import db


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bankroot.db'
    Babel(default_locale='fr').init_app(app)
    db.init_app(app)

    return app
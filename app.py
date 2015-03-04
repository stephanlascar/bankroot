import os
from flask import Flask
from flask.ext.babel import Babel
from database import db
from security import bcrypt, login_manager


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bankroot.db'
    app.secret_key = os.environ.get('SECRET_KEY', 'clef pour les tests')
    Babel(default_locale='fr').init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    return app
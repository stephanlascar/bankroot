# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask.ext.babel import Babel
from database import db
from report import mail
from security import bcrypt, login_manager


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bankroot.db'
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['DEFAULT_MAIL_SENDER'] = os.getenv('DEFAULT_MAIL_SENDER')
    app.secret_key = os.environ.get('SECRET_KEY', 'clef pour les tests')
    Babel(default_locale='fr').init_app(app)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    return app

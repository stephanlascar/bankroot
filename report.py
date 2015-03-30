# -*- coding: utf-8 -*-
from datetime import datetime
import locale
import os
from flask.ext.mail import Mail, Message
from jinja2 import Environment, FileSystemLoader


locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
mail = Mail()
env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + '/templates/'), trim_blocks=True)


def send(user, bank):
    date = datetime.today().strftime('%A %d %B %Y')

    msg = Message(
        subject='Relevé bancaire du %s' % date,
        sender='report@bankroot.com',
        recipients=[user.email],
        html=env.get_template('report.html').render(date=date, bank=bank))
    mail.send(msg)

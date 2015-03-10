# -*- coding: utf-8 -*-

from sqlalchemy import Enum

from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    pusher_key = db.Column(db.String(256))
    banks = db.relationship('Bank', backref='user')


class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(256), nullable=False)
    login = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    type = db.Column(db.Enum('particulier', 'professionnel'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accounts = db.relationship('Account', backref='bank', lazy='dynamic', order_by='Account.label.desc()')


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), unique=True)
    balance = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    label = db.Column(db.String(256), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic', order_by='Transaction.date.desc()')
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_number = db.Column(db.String(30), unique=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(256), nullable=False)
    date = db.Column(db.Date, nullable=False)
    label = db.Column(db.String(256), nullable=False)
    type = db.Column(Enum('INPUT', 'OUTPUT'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

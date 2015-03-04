# -*- coding: utf-8 -*-

from sqlalchemy import Enum

from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    account_id = db.relationship('Account', uselist=False, backref="user")


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.String(30), unique=True)
    balance = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    label = db.Column(db.String(256), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic', order_by='Transaction.date.desc()')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.String(30), unique=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(256), nullable=False)
    date = db.Column(db.Date, nullable=False)
    label = db.Column(db.String(256), nullable=False)
    type = db.Column(Enum('INPUT', 'OUTPUT'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
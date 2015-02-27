# -*- coding: utf-8 -*-
import os
import nltk
from textblob.classifiers import DecisionTreeClassifier
from app import create_app
from database import db
from lcl.browser import LCLBrowser
import models
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', hours=12)
def timed_job():
    app = create_app()
    app.test_request_context().push()
    db.create_all()

    data_train = [(transaction.label, transaction.category) for transaction in models.Transaction.query.distinct(models.Transaction.label)]
    nltk.data.path.append('nltk_data')
    classifier = DecisionTreeClassifier(data_train)

    browser = LCLBrowser(username=os.getenv('BANK_USERNAME'), password=os.getenv('BANK_PASSWORD'))
    for a in browser.get_accounts_list():
        account = models.Account.query.filter_by(bank_id=a.id).first()
        if account:
            account.balance = a.balance
            account.currency = a.currency
            account.label = a.label
            account.type = a.type
            account.date = datetime.datetime.utcnow()
            db.session.merge(account)
        else:
            account = models.Account(bank_id=a.id, balance=a.balance, currency=a.currency, label=a.label, type=a.type, date=datetime.datetime.utcnow())
            db.session.add(account)

        for history in browser.get_history(a):
            transaction = models.Transaction.query.filter_by(bank_id=history.unique_id(account_id=account.bank_id)).first()
            if not transaction and history.label not in [u'Opération Carte', u'Virement Internet', u'Virement', u'Prélèvement']:
                transaction = models.Transaction(bank_id=history.unique_id(account_id=account.bank_id),
                                                 account_id=account.id,
                                                 amount=history.amount,
                                                 category=classifier.classify(history.label),
                                                 date=history.date,
                                                 label=history.label,
                                                 type='INPUT' if history.amount > 0 else 'OUTPUT')
                db.session.add(transaction)

    db.session.commit()


timed_job()
scheduler.start()

# -*- coding: utf-8 -*-
import os
import datetime

from flask import current_app
import nltk
import pushover
from textblob.classifiers import DecisionTreeClassifier
from apscheduler.schedulers.blocking import BlockingScheduler

from app import create_app
from database import db
from lcl.browser import LCLBrowser
import models


scheduler = BlockingScheduler()
pushover.init(os.getenv('PUSHOVER_TOKEN'))


@scheduler.scheduled_job('interval', hours=6, max_instances=1)
def timed_job():
    app = create_app()
    app.test_request_context().push()
    db.create_all()

    data_train = [(transaction.label, transaction.category) for transaction in models.Transaction.query.distinct(models.Transaction.label)]
    nltk.data.path.append('nltk_data')
    classifier = DecisionTreeClassifier(data_train)

    current_app.logger.info('Start fetching new bank operation...')
    users = models.User.query.all()
    for user in users:
        current_app.logger.debug('Working on %s bank operations' % user.email)
        browser = LCLBrowser(username=user.bank.login, password=user.bank.password)

        for browser_account in browser.get_accounts_list():
            account = models.Account.query.filter_by(number=browser_account.id).first()
            if account:
                if not (account.balance < 0) == (browser_account.balance < 0):
                    pushover.Client(user.pusher_key).send_message(u'Solde de votre compte %s (%s): %s €.' % (user.bank.label, account.number,browser_account.balance))

                account.balance = browser_account.balance
                account.currency = browser_account.currency
                account.label = browser_account.label
                account.type = browser_account.type
                account.date = datetime.datetime.utcnow()
                db.session.merge(account)
            else:
                account = models.Account(number=browser_account.id, balance=browser_account.balance, currency=browser_account.currency, label=browser_account.label, type=browser_account.type, date=datetime.datetime.utcnow())
                db.session.add(account)

            for history in browser.get_history(browser_account):
                transaction = models.Transaction.query.filter_by(operation_number=history.unique_id(account_id=account.number)).first()
                if not transaction and history.label not in [u'Opération Carte', u'Virement Internet', u'Virement', u'Prélèvement']:
                    transaction = models.Transaction(operation_number=history.unique_id(account_id=account.number),
                                                     account_id=account.id,
                                                     amount=history.amount,
                                                     category=classifier.classify(history.label),
                                                     date=history.date,
                                                     label=history.label,
                                                     type='INPUT' if history.amount > 0 else 'OUTPUT')
                    db.session.add(transaction)

    db.session.commit()
    current_app.logger.info('Stop fetching new bank operation...')

timed_job()
scheduler.start()

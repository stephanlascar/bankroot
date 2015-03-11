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

    nltk.data.path.append('nltk_data')
    classifier = DecisionTreeClassifier([(transaction.label, transaction.category) for transaction in models.Transaction.query.outerjoin(models.Bank, models.Bank.type == 'personnel').distinct(models.Transaction.label)])

    acurrent_app.logger.info('Start fetching new bank operation...')
    users = models.User.query.all()
    for user in users:
        current_app.logger.debug('Working on %s bank operations' % user.email)

        for bank in user.banks:
            browser = LCLBrowser(username=bank.login, password=bank.password)

            for browser_account in browser.get_accounts_list():
                account = models.Account.query.filter_by(number=browser_account.id).first()
                if account:
                    if not (account.balance < 0) == (browser_account.balance < 0):
                        pushover.Client(user.pusher_key).send_message(u'Solde de votre compte %s (%s): %s €.' % (bank.label, account.number, browser_account.balance))

                    account.balance = browser_account.balance
                    account.currency = browser_account.currency
                    account.label = browser_account.label
                    account.type = browser_account.type
                    account.date = datetime.datetime.utcnow()
                    db.session.merge(account)
                else:
                    account = models.Account(number=browser_account.id, balance=browser_account.balance, currency=browser_account.currency, label=browser_account.label, type=browser_account.type, date=datetime.datetime.utcnow(), bank=bank)
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

                        if abs(transaction.amount) >= 200:
                            pushover.Client(user.pusher_key).send_message(u'Nouvelle transaction de %s € sur le compte %s (%s)' % (transaction.amount, bank.label, account.number))

        db.session.commit()
    current_app.logger.info('Stop fetching new bank operation...')

timed_job()
scheduler.start()

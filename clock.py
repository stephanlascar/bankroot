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
import report


scheduler = BlockingScheduler()
pushover.init(os.getenv('PUSHOVER_TOKEN'))


@scheduler.scheduled_job('cron', day_of_week='mon', hour=8, max_instances=1)
def send_report():
    app = create_app()
    app.test_request_context().push()
    db.create_all()

    users = models.User.query.all()
    for user in users:
        current_app.logger.debug('Working on %s bank operations' % user.email)

        message = []
        for account in user.bank.accounts:
            message.append(u'Solde du compte %s (%s): %s €.' % (user.bank.label, account.number, account.balance))
        pushover.Client(user.pusher_key).send_message('\n'.join(message))

        report.send(user, user.banks)


@scheduler.scheduled_job('cron', hour=12, max_instances=1)
def check_balance():
    app = create_app()
    app.test_request_context().push()
    db.create_all()

    current_app.logger.info('Start fetching new bank balance...')
    banks = models.Bank.query.all()
    for bank in banks:
        browser = LCLBrowser(username=bank.login, password=bank.password)

        for browser_account in browser.get_accounts_list():
            account = models.Account.query.filter_by(number=browser_account.id).first()
            balance = models.Balance(balance=browser_account.balance, date=datetime.datetime.utcnow(), account_id=account.id)
            db.session.merge(balance)

        db.session.commit()
    current_app.logger.info('Stop fetching new bank balance...')


@scheduler.scheduled_job('cron', hour=9, max_instances=1)
@scheduler.scheduled_job('cron', hour=13, max_instances=1)
@scheduler.scheduled_job('cron', hour=20, max_instances=1)
def timed_job():
    app = create_app()
    app.test_request_context().push()
    db.create_all()

    nltk.data.path.append('nltk_data')
    classifier = DecisionTreeClassifier([(transaction.label, transaction.category) for transaction in models.Transaction.query.outerjoin(models.Bank, models.Bank.type == 'personnel').distinct(models.Transaction.label)])

    current_app.logger.info('Start fetching new bank operation...')
    banks = models.Bank.query.all()
    for bank in banks:
        current_app.logger.debug('Working on %s bank operations' % bank.label)

        browser = LCLBrowser(username=bank.login, password=bank.password)

        for browser_account in browser.get_accounts_list():
            account = models.Account.query.filter_by(number=browser_account.id).first()
            if account:
                if not (account.balance < 0) == (browser_account.balance < 0):
                    for user in bank.users:
                        pushover.Client(user.pusher_key).send_message(u'Solde du compte %s (%s): %s €.' % (bank.label, account.number, browser_account.balance))

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
                        for user in bank.users:
                            pushover.Client(user.pusher_key).send_message(u'%s: %s €' % (transaction.label, transaction.amount))

        db.session.commit()
    current_app.logger.info('Stop fetching new bank operation...')

send_report()
scheduler.start()

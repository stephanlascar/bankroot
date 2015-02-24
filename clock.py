# -*- coding: utf-8 -*-
import os
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
                                                 category=models.get_category_for(history.type, history.label, history.amount),
                                                 date=history.date,
                                                 label=history.label,
                                                 type='INPUT' if history.amount > 0 else 'OUTPUT')
                db.session.add(transaction)

    db.session.commit()

#timed_job()
scheduler.start()

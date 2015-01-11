import arrow
from flask import render_template
from sqlalchemy.sql import label, func
from database import db

import models
from app import create_app


app = create_app()


@app.route('/', defaults={'account_id': None}, endpoint='index')
@app.route('/account/<account_id>', endpoint='show_account')
def show_account(account_id):
    all_accounts = models.Account.query.order_by(models.Account.label).all()
    account = models.Account.query.filter_by(bank_id=account_id).first() if account_id else models.Account.query.order_by(models.Account.label).first()
    return render_template('account.html', all_accounts=all_accounts, account=account)


@app.route('/analyse', defaults={'account_id': None}, endpoint='analyse')
@app.route('/analyse/<account_id>', endpoint='show_analyse')
def show_analyse(account_id):
    all_accounts = models.Account.query.order_by(models.Account.label).all()
    account = models.Account.query.filter_by(bank_id=account_id).first() if account_id else models.Account.query.order_by(models.Account.label).first()
    input_transactions = db.session.query(models.Transaction, models.Transaction.category, models.Transaction.type, label('amount', func.abs(func.sum(models.Transaction.amount)))).filter_by(account_id=account.id, type='INPUT').group_by(models.Transaction.category).all()
    output_transactions = db.session.query(models.Transaction, models.Transaction.category, models.Transaction.type, label('amount', func.abs(func.sum(models.Transaction.amount)))).filter_by(account_id=account.id, type='OUTPUT').group_by(models.Transaction.category).all()
    return render_template('analyse.html', all_accounts=all_accounts, account=account, input_transactions=input_transactions, output_transactions=output_transactions)


@app.template_filter()
def humanize(date):
    return arrow.get(date).humanize(locale='FR_fr')
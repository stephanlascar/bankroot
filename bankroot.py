# -*- coding: utf-8 -*-
import locale
from datetime import datetime

import arrow
from flask import render_template, request, url_for, redirect, flash
from flask.ext.login import login_required, login_user, logout_user
from sqlalchemy.sql import label, func, extract

from database import db
from forms.login import LoginForm
import models
from app import create_app
from security import bcrypt
import security


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
app = create_app()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            db_user = models.User.query.filter_by(email=form.email.data).first()
            if db_user and bcrypt.check_password_hash(db_user.password, form.password.data):
                if login_user(security.User(db_user.id), remember=form.remember_me.data):
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    flash(u'Désolé, mais vous ne pouvez pas vous connecter. Contacter l\'administrateur du site.')
            else:
                flash('Utilisateur ou mot de passe non valide.')

    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', defaults={'account_id': None}, endpoint='index')
@app.route('/account/<account_id>', endpoint='show_account')
@login_required
def show_account(account_id):
    all_accounts = models.Account.query.order_by(models.Account.label).all()
    account = models.Account.query.filter_by(bank_id=account_id).first() if account_id else models.Account.query.order_by(models.Account.label).first()
    return render_template('account.html', all_accounts=all_accounts, account=account)


@app.route('/transaction/<transaction_id>', methods=['POST'])
@login_required
def update_transaction(transaction_id):
    updated_category = request.form['category']

    transaction = models.Transaction.query.get(transaction_id)
    transaction.category = updated_category
    db.session.commit()
    return redirect(url_for('show_account', account_id=transaction.account.bank_id))


@app.route('/analyse', defaults={'account_id': None}, endpoint='analyse')
@app.route('/analyse/<account_id>', endpoint='show_analyse', methods=['GET', 'POST'])
@login_required
def show_analyse(account_id):
    all_accounts = models.Account.query.order_by(models.Account.label).all()
    account = models.Account.query.filter_by(bank_id=account_id).first() if account_id else models.Account.query.order_by(models.Account.label).first()

    if request.method == 'POST':
        date = datetime.strptime(request.form['date'].encode('utf-8'), '%B %Y')
    else:
        date = datetime.now()

    input_transactions = db.session.query(models.Transaction, models.Transaction.category, models.Transaction.type, label('amount', func.abs(func.sum(models.Transaction.amount)))).filter_by(account_id=account.id, type='INPUT').filter(extract('year', models.Transaction.date) == date.year).filter(extract('month', models.Transaction.date) == date.month).group_by(models.Transaction.category).all()
    output_transactions = db.session.query(models.Transaction, models.Transaction.category, models.Transaction.type, label('amount', func.abs(func.sum(models.Transaction.amount)))).filter_by(account_id=account.id, type='OUTPUT').filter(extract('year', models.Transaction.date) == date.year).filter(extract('month', models.Transaction.date) == date.month).group_by(models.Transaction.category).all()
    return render_template('analyse.html', all_accounts=all_accounts, account=account, input_transactions=input_transactions, output_transactions=output_transactions, date=unicode(date.strftime('%B %Y'), 'utf-8').title())


@app.template_filter()
def humanize(date):
    return arrow.get(date).humanize(locale='FR_fr')
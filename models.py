# -*- coding: utf-8 -*-
import re
from sqlalchemy import Enum
from database import db
from weboob.capabilities import bank


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.String(30), unique=True)
    balance = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    label = db.Column(db.String(256), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic', order_by='Transaction.date.desc()')


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.String(30), unique=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(256), nullable=False)
    date = db.Column(db.Date, nullable=False)
    label = db.Column(db.String(256), nullable=False)
    type = db.Column(Enum('INPUT', 'OUTPUT'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))


def get_category_for(transaction_type, label, amount):
    if transaction_type == bank.Transaction.TYPE_DEPOSIT or transaction_type == bank.Transaction.TYPE_CHECK:
        if amount > 0:
            return u'Dépôt d\'argent'
        else:
            return u'Retraits, Chèques et Virements'
    else:
        p = [(re.compile('^.*FREE MOBILE|SEPA EDF|SEPA DOMEO.*$'), 'Abonnements'),
             (re.compile('^.*MCDONALDS|CAFE BONHEUR|SARL LE LEPVRIER|COLUMBUS CAFE|LA VIGNERY|KFC|INTERMARCHE|AUCHAN VAL D\'EUR|PETIT CASINO|CARREFOURMARKET|E.LECLERC|PAX WHOLESOME|RARE BAR & GRILL|BUBBY S|APPLEBEES|BLEND HAMBURGER|GOURMET NEW YORK|STARBUCKS|LUIGI.S GRILL|LES DEUX FRERES|LE FORUM|WASABI.*$'), 'Alimentation & Restaurant'),
             (re.compile('^.*FNAC|NOCIBE|CELIO|TERRITOIRE REDSK|INTERSPORT|PHANTOM OF BROAD|THE LEGO STORE|MANGA MULTIMEDIA|ITUNES.COM|DECATHLON|YANKEES CLUBHOUS|LEVIS|AUTREFOIS|DELICE DES PAPES|LA GDE RECRE|ALINEA|SEPA CREALFI SAS|H & M.*$|CASTORAMA'), 'Achats & Shopping'),
             (re.compile('^.*EBOOKERS|USCUSTOMS|SEPA SERVICES MAGAZINES|TOP OF THE ROCK|AMER MUSEUM|AMNH-ADMISSIONS|MTA MVM|ROYAL KIDS|LA SERRE AU CROC|MAG NICOLAS.*$'), 'Loisirs & Sorties'),
             (re.compile('^.*AVANSSUR|SEPA Bip Go|ADP ORLY|PERSONNEL|CARREFMARKETDAC|AUCHAN CARBURANT|S L A|RMG PARKING|STATION AVIA|RANDO PNEUS.*$'), 'Auto & Transport'),
             (re.compile('^.*ADVYS|Virement Internet.*$'), 'Salaires'),
             (re.compile('^.*SEPA PLAN|SEPA PayPal Europe S.a.r.l.*$'), 'Divers'),
             (re.compile(u'^.*Opération Carte|RETRAIT EXPRESS|RETRAIT|Retrait sur distributeurs.*$'), u'Retraits, Chèques et Virements'),
             (re.compile(u'^.*VERDONC|LASCAR.*$'), 'Virements internes'),
             (re.compile('^.*TCHIP|BODY MINUTE|YVAN ET ELODIE.*$'), u'Esthétique & Soins'),
             (re.compile('^.*SANTE|SEPA GROUPAMA|RITE AID STORE|DR JUGIE RONGIE|PHIE DU MIDI|RAM PL PARIS|DOCTEUR GOUEZ|LABM ARMAINVIL.*$'), u'Santé'),
             (re.compile('^.*SEPA GMF|IMMOBILIER ECH.*$'), 'Logement'),
             (re.compile('^.*PRELEV./ACPTE FISCAL|SEPA DIRECTION GENERALE DE.*$'), u'Impôts & Taxes'),
             (re.compile('^.*Societe Gest Prest San|LCL CREDIT SATISFACTION.*$'), 'Remboursements'),
             (re.compile('^.*LCL A LA CARTE|COTISATION MENSUELLE CARTE|INTERETS DEBITEURS|CHQ IRREGUL|SEPA ASSURANCE LCL|PERMANENT|INTERETS.*$'), 'Banque')]
        for pattern, category in p:
            if pattern.match(label):
                return category
    raise Exception('Unable to find category for %s (%s €)' % (label.encode('utf-8'), amount))

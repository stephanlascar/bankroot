# -*- coding: utf-8 -*-
import re

import nltk
from sqlalchemy import Enum
from textblob.classifiers import DecisionTreeClassifier

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
             (re.compile('^.*Societe Gest Prest San|LCL CREDIT SATISFACTION|RAM PL.*$'), 'Remboursements'),
             (re.compile(u'^.*LCL A LA CARTE|COTISATION MENSUELLE CARTE|INTERETS DEBITEURS|CHQ IRREGUL|SEPA ASSURANCE LCL|PERMANENT|INTERETS|PERSONNEL.*$'), 'Banque')]
        for pattern, category in p:
            if pattern.match(label):
                return category
    raise Exception('Unable to find category for %s (%s €)' % (label.encode('utf-8'), amount))


data_train = [
    (u"ADVYS", u"Salaires"), (u"KFC", u"Alimentation & Restaurant"), (u"00003CH 2616424 0000000", u"Dépôt d'argent"), (u"RETRAIT EXPRESS", u"Retraits, Chèques et Virements"), (u"CHQ IRREGUL 7906504 REM 2616424", u"Banque"), (u"ADVYS", u"Salaires"), (u"VERDONC", u"Virements internes"), (u"LASCAR", u"Virements internes"), (u"LASCAR", u"Virements internes"), (u"EDF clients particuli", u"Abonnements"), (u"PLAN INTERNATIONAL FR", u"Divers"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"FNAC", u"Achats & Shopping"), (u"MCDONALDS 869", u"Alimentation & Restaurant"), (u"2616449", u"Retraits, Chèques et Virements"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"CAFE BONHEUR", u"Alimentation & Restaurant"), (u"GMF ASSURANCES", u"Logement"), (u"GROUPAMA GAN VIE", u"Santé"), (u"INTERMARCHE", u"Alimentation & Restaurant"), (u"AVANSSUR", u"Auto & Transport"), (u"AVANSSUR", u"Auto & Transport"), (u"EBK*EBOOKERS", u"Loisirs & Sorties"), (u"USCUSTOMS ESTA A", u"Loisirs & Sorties"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"MCDONALDS 868", u"Alimentation & Restaurant"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"ADP ORLY P0", u"Auto & Transport"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"SNC FORUM SANTE", u"Santé"), (u"INTERETS DEBITEURS AU 31 12 14", u"Banque"), (u"LCL A LA CARTE", u"Banque"), (u"LCL A LA CARTE", u"Banque"), (u"PERSONNEL 301214", u"Auto & Transport"), (u"ASSURANCE LCL", u"Banque"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"MCDONALDS 868", u"Alimentation & Restaurant"), (u"SARL LE LEPVRIER", u"Alimentation & Restaurant"), (u"PETIT CASINO", u"Alimentation & Restaurant"), (u"PayPal Europe S.a.r.l", u"Divers"), (u"ADP ORLY P0", u"Auto & Transport"), (u"INTERSPORT", u"Achats & Shopping"), (u"COTISATION MENSUELLE CARTE 6521", u"Banque"), (u"COTISATION MENSUELLE CARTE 6672", u"Banque"), (u"CARREFMARKETDAC", u"Auto & Transport"), (u"NOCIBE", u"Achats & Shopping"), (u"CELIO 00224", u"Achats & Shopping"), (u"CELIO 00224", u"Achats & Shopping"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"CARREFOURMARKET", u"Alimentation & Restaurant"), (u"YVAN ET ELODIE", u"Esthétique & Soins"), (u"YVAN ET ELODIE", u"Esthétique & Soins"), (u"DOMEO", u"Abonnements"), (u"TCHIP", u"Esthétique & Soins"), (u"COLUMBUS CAFE", u"Alimentation & Restaurant"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"SNC FORUM SANTE", u"Santé"), (u"BODY MINUTE", u"Esthétique & Soins"), (u"BODY MINUTE", u"Esthétique & Soins"), (u"2616447", u"Retraits, Chèques et Virements"), (u"2616448", u"Retraits, Chèques et Virements"), (u"Bip Go", u"Auto & Transport"), (u"TERRITOIRE REDSK", u"Achats & Shopping"), (u"IMMOBILIER ECH 21/12/14", u"Logement"), (u"LASCAR", u"Virements internes"), (u"LASCAR", u"Virements internes"), (u"LASCAR", u"Virements internes"), (u"ADVYS", u"Salaires"), (u"Societe Gest Prest San", u"Remboursements"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"AUCHAN CARBURANT", u"Auto & Transport"), (u"PayPal Europe S.a.r.l", u"Divers"), (u"FREE MOBILE", u"Abonnements"), (u"00001CH 2616423 0000000", u"Dépôt d'argent"), (u"PERMANENT 171214", u"Banque"), (u"SERVICES MAGAZINES", u"Loisirs & Sorties"), (u"YVAN ET ELODIE", u"Esthétique & Soins"), (u"E.LECLERC", u"Alimentation & Restaurant"), (u"LASCAR", u"Virements internes"), (u"PRELEV./ACPTE FISCAL + SOCIAUX", u"Impôts & Taxes"), (u"INTERETS 2014", u"Banque"), (u"LASCAR", u"Virements internes"), (u"LASCAR", u"Virements internes"), (u"INTERETS 2014", u"Banque"), (u"PRELEV./ACPTE FISCAL + SOCIAUX", u"Impôts & Taxes"), (u"INTERETS 2014", u"Banque"), (u"LASCAR", u"Virements internes"), (u"LASCAR", u"Virements internes"), (u"INTERETS AU : 31 12 14", u"Banque"), (u"LASCAR", u"Virements internes"), (u"INTERETS AU : 31 12 14", u"Banque"), (u"BLEND HAMBURGER", u"Alimentation & Restaurant"), (u"S L A", u"Auto & Transport"), (u"DECATHLON 0505", u"Achats & Shopping"), (u"DECATHLON 0505", u"Achats & Shopping"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"AMNH-ADMISSIONS", u"Loisirs & Sorties"), (u"LCL CREDIT SATISFACTION", u"Remboursements"), (u"MTA MVM*23RD STR", u"Loisirs & Sorties"), (u"AMNH-ADMISSIONS", u"Loisirs & Sorties"), (u"LEVIS STORE 1701", u"Achats & Shopping"), (u"LUIGI.S GRILL", u"Alimentation & Restaurant"), (u"00001CH 3900517 0000000", u"Dépôt d'argent"), (u"YANKEES CLUBHOUS", u"Achats & Shopping"), (u"AMER MUSEUM OF N", u"Loisirs & Sorties"), (u"AMER MUSEUM OF N", u"Loisirs & Sorties"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"GOURMET NEW YORK", u"Alimentation & Restaurant"), (u"STARBUCKS .07709", u"Alimentation & Restaurant"), (u"IMMOBILIER ECH 21/01/15", u"Logement"), (u"PAX WHOLESOME FO", u"Alimentation & Restaurant"), (u"RITE AID STORE 3", u"Santé"), (u"PHANTOM OF BROAD", u"Achats & Shopping"), (u"TOP OF THE ROCK", u"Loisirs & Sorties"), (u"RARE BAR & GRILL", u"Alimentation & Restaurant"), (u"PayPal Europe S.a.r.l", u"Divers"), (u"FREE MOBILE", u"Abonnements"), (u"LASCAR", u"Virements internes"), (u"BUBBY S", u"Alimentation & Restaurant"), (u"RARE BAR & GRILL", u"Alimentation & Restaurant"), (u"PERMANENT 190115", u"Banque"), (u"Bip Go", u"Auto & Transport"), (u"SERVICES MAGAZINES", u"Loisirs & Sorties"), (u"THE LEGO STORE", u"Achats & Shopping"), (u"APPLEBEES 973861", u"Alimentation & Restaurant"), (u"DIRECTION GENERALE DE", u"Impôts & Taxes"), (u"DIRECTION GENERALE DE", u"Impôts & Taxes"), (u"DIRECTION GENERALE DE", u"Impôts & Taxes"), (u"2616441", u"Retraits, Chèques et Virements"), (u"ITUNES.COM/BILL", u"Achats & Shopping"), (u"MANGA MULTIMEDIA", u"Achats & Shopping"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"PayPal Europe S.a.r.l", u"Divers"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"DR JUGIE RONGIE", u"Santé"), (u"LASCAR", u"Virements internes"), (u"2616450", u"Retraits, Chèques et Virements"), (u"RAM PL PARIS", u"Remboursements"), (u"VERDONC", u"Virements internes"), (u"ADVYS", u"Salaires"), (u"LASCAR", u"Virements internes"), (u"COTISATION MENSUELLE CARTE 6521", u"Banque"), (u"COTISATION MENSUELLE CARTE 6672", u"Banque"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"CASTORAMA", u"Achats & Shopping"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"ITUNES.COM/BILL", u"Achats & Shopping"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"INTERMARCHE", u"Alimentation & Restaurant"), (u"PERSONNEL 300115", u"Banque"), (u"ASSURANCE LCL", u"Banque"), (u"LCL A LA CARTE", u"Banque"), (u"LCL A LA CARTE", u"Banque"), (u"ADVYS", u"Salaires"), (u"RETRAIT", u"Retraits, Chèques et Virements"), (u"GMF ASSURANCES", u"Logement"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"AVANSSUR", u"Auto & Transport"), (u"GROUPAMA GAN VIE", u"Santé"), (u"AVANSSUR", u"Auto & Transport"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"CREALFI SAS", u"Achats & Shopping"), (u"ITUNES.COM/BILL", u"Achats & Shopping"), (u"AUCHAN VAL D'EUR", u"Alimentation & Restaurant"), (u"H & M 016", u"Achats & Shopping"), (u"PLAN INTERNATIONAL FR", u"Divers"), (u"EDF clients particuli", u"Abonnements"), (u"CARREFMARKETDAC", u"Auto & Transport"), (u"ITUNES.COM/BILL", u"Achats & Shopping"), (u"WASABI 10", u"Alimentation & Restaurant"), (u"LA GDE RECRE 77", u"Achats & Shopping"), (u"MCDONALDS 869", u"Alimentation & Restaurant"), (u"ALINEA 14", u"Achats & Shopping"), (u"2616452", u"Retraits, Chèques et Virements")
]

data_test = [
    ("FISCAL", u"Impôts & Taxes"), ("CARREFOUR", u"Alimentation & Restaurant"), ("H & M", u"Achats & Shopping"),
    ("EDF", u"Abonnements"), ("GDF", u"Abonnements"), ("FREE MOBILE", u"Abonnements"), ("PLAN", u"Divers"), ("QUICK", u"'Alimentation & Restaurant'"),
    ("CAFE", u"'Alimentation & Restaurant'"), ("HURE", u"'Alimentation & Restaurant'"), ("GMF", u"Logement"),
    ("AUCHAN", u"Alimentation & Restaurant"), ("INTERETS", u"Banque"), ("LABM", u"Santé")
]

french_stop_words = [
    u"alors", u"au", u"aucuns", u"aussi", u"autre", u"avant", u"avec", u"avoir", u"bon", u"car", u"ce", u"cela", u"ces", u"ceux", u"chaque", u"ci", u"comme", u"comment", u"dans", u"des", u"du", u"dedans", u"dehors", u"depuis", u"devrait", u"doit", u"donc", u"dos", u"début", u"elle", u"elles", u"en", u"encore", u"essai", u"est", u"et", u"eu", u"fait", u"faites", u"fois", u"font", u"hors", u"ici", u"il", u"ils", u"je 	juste", u"la", u"le", u"les", u"leur", u"là", u"ma", u"maintenant", u"mais", u"mes", u"mine", u"moins", u"mon", u"mot", u"même", u"ni", u"nommés", u"notre", u"nous", u"ou", u"où", u"par", u"parce", u"pas", u"peut", u"peu", u"plupart", u"pour", u"pourquoi", u"quand", u"que", u"quel", u"quelle", u"quelles", u"quels", u"qui", u"sa", u"sans", u"ses", u"seulement", u"si", u"sien", u"son", u"sont", u"sous", u"soyez 	sujet", u"sur", u"ta", u"tandis", u"tellement", u"tels", u"tes", u"ton", u"tous", u"tout", u"trop", u"très", u"tu", u"voient", u"vont", u"votre", u"vous", u"vu", u"ça", u"étaient", u"état", u"étions", u"été", u"être"
]

if __name__ == "__main__":
    nltk.data.path.append('nltk_data')
    cl = DecisionTreeClassifier(data_train)
    print cl.classify("CAFE")
    print cl.classify("DIRECTION GENERALE DE")
    print cl.classify("CARREFOUR")
    print cl.classify("H & M")
    print cl.classify("FREE MOBILE")
    print cl.classify("EDF")
    print cl.classify("TCHIP")
    print cl.classify("GMF")
    print cl.accuracy(data_test)

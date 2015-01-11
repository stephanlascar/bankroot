# -*- coding: utf-8 -*-
from unittest import TestCase
import models


class TestCategory(TestCase):

    def test_abonnements(self):
        self.assertEqual('Abonnements', models.get_category_for('SEPA FREE MOBILE'))

    def test_alimentation_et_restaurant(self):
        self.assertEqual('Alimentation & Restaurant', models.get_category_for('MCDONALDS 869'))
        self.assertEqual('Alimentation & Restaurant', models.get_category_for('KFC'))
        self.assertEqual('Alimentation & Restaurant', models.get_category_for('CAFE BONHEUR'))
        self.assertEqual('Alimentation & Restaurant', models.get_category_for('SARL LE LEPVRIER'))
        self.assertEqual('Alimentation & Restaurant', models.get_category_for('COLUMBUS CAFE'))
        self.assertEqual('Alimentation & Restaurant', models.get_category_for('LA VIGNERY'))

    def test_achat_et_shopping(self):
        self.assertEqual('Achats & Shopping', models.get_category_for('FNAC'))
        self.assertEqual('Achats & Shopping', models.get_category_for('NOCIBE'))
        self.assertEqual('Achats & Shopping', models.get_category_for('CELIO 00224'))
        self.assertEqual('Achats & Shopping', models.get_category_for('TERRITOIRE REDSK'))

    def test_auto_et_transport(self):
        self.assertEqual('Auto & Transport', models.get_category_for('SEPA AVANSSUR'))
        self.assertEqual('Auto & Transport', models.get_category_for('SEPA Bip Go'))

    def test_banque(self):
        self.assertEqual('Banque', models.get_category_for('INTERETS DEBITEURS AU 31 12 14'))
        self.assertEqual('Banque', models.get_category_for('LCL A LA CARTE'))
        self.assertEqual('Banque', models.get_category_for('COTISATION MENSUELLE CARTE 6672'))

    def test_loisirs_et_sorties(self):
        self.assertEqual('Loisirs & Sorties', models.get_category_for('EBK*EBOOKERS'))
        self.assertEqual('Loisirs & Sorties', models.get_category_for('USCUSTOMS ESTA A'))
        self.assertEqual('Loisirs & Sorties', models.get_category_for('SEPA SERVICES MAGAZINES'))

    def test_sante(self):
        self.assertEqual(u'Santé', models.get_category_for('SNC FORUM SANTE'))

    def test_esthetique_et_soins(self):
        self.assertEqual(u'Esthétique & Soins', models.get_category_for('TCHIP'))
        self.assertEqual(u'Esthétique & Soins', models.get_category_for('BODY MINUTE'))
        self.assertEqual(u'Esthétique & Soins', models.get_category_for('YVAN ET ELODIE'))

    def test_salaires(self):
        self.assertEqual(u'Salaires', models.get_category_for('ADVYS'))

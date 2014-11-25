#!/usr/bin/env python
# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import test_view, test_depends
import trytond.tests.test_tryton
import unittest


class StockMoveExtraProductsSupplyTestCase(unittest.TestCase):
    'Test Stock Move Extra Products Supply module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('stock_move_extra_products_supply')

    def test0005views(self):
        'Test views'
        test_view('stock_move_extra_products_supply')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        StockMoveExtraProductsSupplyTestCase))
    return suite

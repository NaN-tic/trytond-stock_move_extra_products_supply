# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class StockMoveExtraProductsSupplyTestCase(ModuleTestCase):
    'Test Stock Move Extra Products Supply module'
    module = 'stock_move_extra_products_supply'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        StockMoveExtraProductsSupplyTestCase))
    return suite

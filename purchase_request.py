# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['PurchaseRequest']


class PurchaseRequest:
    __metaclass__ = PoolMeta
    __name__ = 'purchase.request'

    @classmethod
    def _get_origin(cls):
        return super(PurchaseRequest, cls)._get_origin() | {'stock.move'}

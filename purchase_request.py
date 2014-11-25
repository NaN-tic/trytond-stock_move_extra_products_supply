# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
__all__ = ['PurchaseRequest']

__metaclass__ = PoolMeta


class PurchaseRequest:
    __name__ = 'purchase.request'

    @classmethod
    def origin_get(cls):
        Model = Pool().get('ir.model')
        res = super(PurchaseRequest, cls).origin_get()
        model, = Model.search([
                ('model', '=', 'stock.move'),
                ])
        res.append([model.model, model.name])
        return res

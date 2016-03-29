# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
__all__ = ['ShipmentOut']


class ShipmentOut:
    __metaclass__ = PoolMeta
    __name__ = 'stock.shipment.out'

    def _get_inventory_move(self, move):
        'Return inventory move for the outgoing move: copy of extra products'
        ExtraProduct = Pool().get('stock.move.extra_product')
        inventory_move = super(ShipmentOut, self)._get_inventory_move(move)
        inventory_move.extra_products = ExtraProduct.copy(move.extra_products)
        return inventory_move

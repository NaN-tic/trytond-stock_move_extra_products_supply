# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta
from .move import ExtraProductMixin

__all__ = [
    'BOMInputExtraProduct', 'BOMOutputExtraProduct',
    'BOMInput', 'BOMOutput',
    ]
__metaclass__ = PoolMeta


class BOMInputExtraProduct(ModelSQL, ModelView, ExtraProductMixin):
    'BOM Input Extra Product'
    __name__ = 'production.bom.input.extra_product'
    bom_input = fields.Many2One('production.bom.input', 'BOM Input',
        required=True, ondelete='CASCADE')


class BOMOutputExtraProduct(ModelSQL, ModelView, ExtraProductMixin):
    'BOM Output Extra Product'
    __name__ = 'production.bom.output.extra_product'
    bom_output = fields.Many2One('production.bom.output', 'BOM Output',
        required=True, ondelete='CASCADE')


class BOMInput:
    __name__ = 'production.bom.input'
    extra_products = fields.One2Many('production.bom.input.extra_product',
        'bom_input', 'Extra products',
        help="Additional services from which create purchase requests.")

    def get_rec_name(self, name):
        return ("%s%s %s"
            % (self.quantity, self.uom.symbol, self.product.rec_name))


class BOMOutput:
    __name__ = 'production.bom.output'
    extra_products = fields.One2Many('production.bom.output.extra_product',
        'bom_output', 'Extra products',
        help="Additional services from which create purchase requests.")

    def get_rec_name(self, name):
        return ("%s%s %s"
            % (self.quantity, self.uom.symbol, self.product.rec_name))

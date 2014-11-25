# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.transaction import Transaction
from trytond.pool import PoolMeta, Pool
from .move import ExtraProductMixin
__all__ = [
    'BOMInputExtraProduct', 'BOMOutputExtraProduct',
    'BOMInput', 'BOMOutput',
    'AddExtraProductBOMStart', 'AddExtraProductBOM'
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


class AddExtraProductBOMStart(ModelView):
    'Add extra products to inputs/outputs from BOM'
    __name__ = 'production.bom.extra_product.add.start'


class AddExtraProductBOM(Wizard):
    'Add extra products to inputs/outputs from BOM'
    __name__ = 'production.bom.extra_product.add'
    start = StateView('production.bom.extra_product.add.start',
        'stock_move_extra_products_supply.production_bom_extra_product_add_start_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'add_', 'tryton-ok', default=True),
            ])
    add_ = StateTransition()

    def transition_add_(self):
        pool = Pool()
        Production = pool.get('production')
        BOMInput = pool.get('production.bom.input')
        BOMOutput = pool.get('production.bom.output')
        Move = pool.get('stock.move')

        context = Transaction().context
        production = Production(context['active_id'])
        if not production.bom:
            return 'end'
        bom = production.bom

        for move in production.inputs:
            create = []
            bom_inputs = BOMInput.search([
                    ('bom', '=', bom.id),
                    ('product', '=', move.product.id),
                    ], limit=1)
            if bom_inputs:
                for extra_product in bom_inputs[0].extra_products:
                    create.append({
                        'move': move.id,
                        'product': extra_product.product.id,
                        'quantity': extra_product.quantity,
                        'uom': extra_product.uom.id,
                    })
            data = [('remove', [ep.id for ep in move.extra_products])]
            if create:
                data.append(('create', create))
            Move.write([move], {'extra_products': data})

        for move in production.outputs:
            create = []
            bom_outputs = BOMOutput.search([
                    ('bom', '=', bom.id),
                    ('product', '=', move.product.id),
                    ], limit=1)
            if bom_outputs:
                for extra_product in bom_outputs[0].extra_products:
                    create.append({
                        'move': move.id,
                        'product': extra_product.product.id,
                        'quantity': extra_product.quantity,
                        'uom': extra_product.uom.id,
                    })
            data = [('remove', [ep.id for ep in move.extra_products])]
            if create:
                data.append(('create', create))
            Move.write([move], {'extra_products': data})
        return 'end'

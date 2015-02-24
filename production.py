# This file is part stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = ['Production', 'AddExtraProductBOMStart', 'AddExtraProductBOM']
__metaclass__ = PoolMeta


class Production:
    __name__ = "production"
    extra_products_cost = fields.Function(fields.Numeric('Extra Product Cost',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']),
        'on_change_with_extra_products_cost')
    total_cost = fields.Function(fields.Numeric('Total Cost',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']),
        'on_change_with_total_cost')

    @fields.depends('inputs', 'outputs')
    def on_change_with_extra_products_cost(self, name=None):
        ep_cost = Decimal('0')
        for line in self.inputs + self.outputs:
            for ep in getattr(line, 'extra_products', []):
                ep_cost += ep.cost_price if ep.cost_price else Decimal('0')
        return ep_cost

    @fields.depends('cost', 'extra_products_cost', 'timesheet_cost')
    def on_change_with_total_cost(self, name=None):
        # If production_timesheet is installed the timesheet cost must be added
        ts_cost = self.timesheet_cost if self.timesheet_cost else Decimal('0')
        return self.cost + self.extra_products_cost + ts_cost


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
                        'cost_price': extra_product.cost_price,
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
                        'cost_price': extra_product.cost_price,
                    })
            data = [('remove', [ep.id for ep in move.extra_products])]
            if create:
                data.append(('create', create))
            Move.write([move], {'extra_products': data})
        return 'end'

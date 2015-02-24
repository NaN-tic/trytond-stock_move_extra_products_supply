# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, In
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
__all__ = ['MoveExtraProduct', 'Move']

__metaclass__ = PoolMeta

STATES = {
    'readonly': In(Eval('state'), ['cancel', 'assigned', 'done']),
}


class ExtraProductMixin:
    'Generic Extra Product'
    product = fields.Many2One('product.product', 'Product', required=True,
        select=True,
        domain=[('purchasable', '=', True), ('type', '=', 'service')])
    product_uom_category = fields.Function(
        fields.Many2One('product.uom.category', 'Product Uom Category'),
        'on_change_with_product_uom_category')
    uom = fields.Many2One('product.uom', 'Uom', required=True,
        domain=[
            ('category', '=', Eval('product_uom_category')),
            ],
        depends=['product_uom_category'])
    unit_digits = fields.Function(fields.Integer('Unit Digits'),
        'on_change_with_unit_digits')
    quantity = fields.Float('Quantity', required=True,
        digits=(16, Eval('unit_digits', 2)),
        depends=['unit_digits'])
    cost_price = fields.Numeric('Cost Price',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')

    @staticmethod
    def default_quantity():
        return 1

    @staticmethod
    def default_unit_digits():
        return 2

    @fields.depends('uom')
    def on_change_with_unit_digits(self, name=None):
        if self.uom:
            return self.uom.digits
        return 2

    def on_change_with_currency_digits(self, name=None):
        Company = Pool().get('company.company')
        company = Transaction().context.get('company')
        if company:
            company = Company(company)
            return company.currency.digits
        return 2

    @fields.depends('product')
    def on_change_with_product_uom_category(self, name=None):
        if self.product:
            return self.product.default_uom_category.id

    @fields.depends('product', 'quantity')
    def on_change_product(self):
        res = {}
        if self.product:
            res['uom'] = self.product.default_uom.id
            res['uom.rec_name'] = self.product.default_uom.rec_name
            res['unit_digits'] = self.product.default_uom.digits
            res.update(self.on_change_quantity())
        return res

    @fields.depends('product', 'quantity')
    def on_change_quantity(self):
        res = {}
        if self.product:
            qty = self.quantity or 1
            res['cost_price'] = Decimal(str(qty)) * self.product.cost_price
        return res


class MoveExtraProduct(ModelSQL, ModelView, ExtraProductMixin):
    'Stock Move Extra Product'
    __name__ = 'stock.move.extra_product'
    move = fields.Many2One('stock.move', 'Move', required=True,
        ondelete='CASCADE', states=STATES)
    purchase_request = fields.Many2One('purchase.request', 'Purchase Request',
        ondelete='SET NULL', readonly=True)
    state = fields.Function(fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
        ], 'State'), 'on_change_with_state')

    @classmethod
    def __setup__(cls):
        super(MoveExtraProduct, cls).__setup__()
        cls.product.states = STATES
        cls.product.depends = ['move']
        cls.quantity.states = STATES
        cls.quantity.depends.append('move')
        cls.uom.states = STATES
        cls.uom.depends.append('move')

    def get_purchase_request(self):
        'Return purchase request for the extra product'
        pool = Pool()
        Uom = pool.get('product.uom')
        Request = pool.get('purchase.request')

        if (self.purchase_request and
                self.purchase_request.state in ['purchased', 'done']):
            return

        product = self.product
        supplier, purchase_date = Request.find_best_supplier(product,
            self.move.planned_date)
        uom = product.purchase_uom or product.default_uom
        quantity = Uom.compute_qty(self.uom, self.quantity, uom)
        with Transaction().set_user(0, set_context=True):
            if (self.purchase_request and
                    self.purchase_request.state == 'draft'):
                request = self.purchase_request
            else:
                request = Request()
            request.product = product
            request.party = supplier
            request.quantity = quantity
            request.uom = uom
            request.computed_quantity = quantity
            request.computed_uom = uom
            request.purchase_date = purchase_date
            request.supply_date = self.move.planned_date
            request.company = self.move.company
            request.origin = self.move
            request.warehouse = (self.move.from_location.warehouse or
                self.move.to_location.warehouse)

        return request

    @fields.depends('move')
    def on_change_with_state(self, name=None):
        if self.move:
            return self.move.state
        return None


class Move:
    __name__ = 'stock.move'
    extra_products = fields.One2Many('stock.move.extra_product', 'move',
        'Extra products',
        help="Additional services from which create purchase requests.",
        states={
            'readonly': In(Eval('state'), ['cancel', 'assigned', 'done']),
        },
        depends=['state'])

    def create_purchase_requests(self):
        'Create the purchase requests for the extra products'
        for extra in self.extra_products:
            request = extra.get_purchase_request()
            if not request:
                continue
            request.save()
            extra.purchase_request = request
            extra.save()

    @classmethod
    def assign(cls, moves):
        'Create the purchase requests for extra products of moves '
        'when assing out and internal shipments'
        super(Move, cls).assign(moves)
        for move in moves:
            if (move.from_location.type == 'storage'
                    and move.to_location.type in ('storage', 'production')):
                move.create_purchase_requests()

    @classmethod
    def do(cls, moves):
        'Create the purchase requests for extra products of moves '
        'when receiving in shipments'
        super(Move, cls).do(moves)
        for move in moves:
            if (move.from_location.type in ('supplier', 'production')
                    and move.to_location.type == 'storage'):
                move.create_purchase_requests()

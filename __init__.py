# This file is part of the stock_move_extra_products_supply module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .move import *
from .purchase_request import *
from .shipment import *
from .bom import *


def register():
    Pool.register(
        MoveExtraProduct,
        Move,
        PurchaseRequest,
        ShipmentOut,
        BOMInputExtraProduct,
        BOMOutputExtraProduct,
        BOMInput,
        BOMOutput,
        AddExtraProductBOMStart,
        module='stock_move_extra_products_supply', type_='model')
    Pool.register(
        AddExtraProductBOM,
        module='stock_move_extra_products_supply', type_='wizard')

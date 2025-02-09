# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Custom Purchase Import Wizard",
    "version": "14.0.1.0.0",
    "category": "Hidden/Tools",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "depends": [
        "purchase",
        "base_import_wizard",
        "stock_picking_date_done",
        "purchase_order_shipping_method",
        "stock_move_line_cost",
        "purchase_requisition_line_usability"
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/purchase_import_wizard_security.xml",
        "views/purchase_order_import_line_views.xml",
        "views/purchase_order_import_views.xml",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "installable": True,
}

# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Move Line Report",
    'version': '14.0.1.0.0',
    "author": "Avanzosc",
    "category": "Inventory",
    "website": "http://www.avanzosc.es",
    "depends": [
        "stock",
        "stock_move_line_cost",
        "stock_warehouse_farm",
        "stock_picking_batch_liquidation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/stock_move_line_report_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}

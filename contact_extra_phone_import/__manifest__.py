# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Contact Extra Phone Import",
    "version": "14.0.1.0.0",
    "category": "Hidden/Tools",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "depends": [
        "contacts",
        "base_import_wizard",
        "contact_extra_phone"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_phone_import_line_views.xml",
        "views/res_partner_phone_import_views.xml",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "installable": True,
}
